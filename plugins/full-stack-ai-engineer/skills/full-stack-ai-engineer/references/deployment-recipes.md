# Deployment Recipes

These are patterns, not copy-paste guarantees. Verify commands, flags, and action versions against current official documentation and the project's setup before running. Never put real secrets in files.

## Environments
- **dev** (local), **staging** (production-like, own database and keys), **production**.
- Separate databases, secrets, API keys, and spend limits per environment. Never point staging at the production database.
- Promote the same built artifact (image or build) from staging to production; do not rebuild per environment.
- Configuration through environment variables injected by the platform or secrets manager.

## Docker Compose for local development

```yaml
services:
  api:
    build: .
    env_file: .env
    ports: ["8000:8000"]
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password   # local dev only
      POSTGRES_DB: appdb
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10
  redis:
    image: redis:7
volumes:
  pgdata:
```

Run: `docker compose up --build`. Run migrations as a separate one-off step (`docker compose run --rm api alembic upgrade head`).

## GitHub Actions: CI

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-timeout 3s --health-retries 10
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt
      - run: ruff check . && ruff format --check .
      - run: pytest -q
      - run: python scripts/validate_project.py .
      - run: python scripts/run_evals.py --dataset evals/dataset.jsonl --target app.eval_target:answer --min-pass-rate 0.9 --baseline evals/baseline.json
```

Pin third-party actions to a major version or commit SHA, give the workflow the minimum `permissions`, and store secrets in the repository's secret store, never in the file. Run live-provider evals only on trusted branches because they cost money and need keys.

## GitHub Actions: deploy (staging then production)

Pattern: build once, deploy to staging automatically, require manual approval (a protected `production` environment) before production.

```yaml
name: deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # build and push an image tagged with the commit SHA to your registry
  staging:
    needs: build
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy image $GITHUB_SHA to staging, run migrations, run smoke tests"
  production:
    needs: staging
    environment: production   # configure required reviewers on this environment
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy the same image $GITHUB_SHA to production, run migrations, smoke test"
```

Replace the `echo` steps with your platform's deploy commands.

## Vercel (Next.js frontend and serverless routes)
1. Connect the repository; pull requests get preview deployments, the main branch deploys to production.
2. Set environment variables per environment (Preview vs Production) in the project settings; keep server-only secrets unprefixed.
3. Mind serverless limits: function duration, request body size, and cold starts. Long-running work (ingestion, OCR, agents) goes to a queue and worker, not a request handler.
4. Streaming responses work for chat routes; confirm duration limits for your plan.
5. Use a managed Postgres and Redis reachable from the functions; use pooling suitable for serverless connections.
6. Rollback: promote a previous deployment from the dashboard or CLI (`vercel rollback`, verify in current docs).

## AWS (container-based API)
A common managed path: ECR for images, ECS on Fargate (or App Runner for simpler cases) behind an Application Load Balancer, RDS PostgreSQL, ElastiCache Redis, S3, Secrets Manager, CloudWatch.
1. Build and push the image to ECR tagged with the commit SHA.
2. Create or update the task definition with the new image; inject secrets from Secrets Manager.
3. Update the service with a rolling deployment; the load balancer health check gates traffic.
4. Run migrations as a one-off task before shifting traffic (see migrations).
5. Use private subnets for the database and tasks; least-privilege IAM roles per service; security groups that only allow required traffic.
6. Define infrastructure as code (Terraform, CDK, or CloudFormation) once there is more than a couple of resources.
7. Rollback: redeploy the previous task definition revision.

## Database migrations during deployment
Use **expand and contract** so old and new code can run at the same time:
1. **Expand:** add new columns/tables as nullable or with defaults; do not drop or rename in the same release.
2. Deploy code that writes to both or reads with fallback.
3. Backfill data in batches (a background job, not the migration transaction for large tables).
4. **Contract:** in a later release, remove old columns after confirming nothing uses them.

Rules:
- Run migrations once per release as a dedicated step, not on every app instance start.
- Take or verify a backup before risky migrations; test the migration on a staging copy.
- Create large indexes concurrently where the database supports it.
- Keep migrations forward-only in production; roll back by deploying fixed code, and write a down-migration only when it is truly safe.

## Zero-downtime and rollback
- Health and readiness checks gate traffic; gracefully drain connections on shutdown.
- Use rolling, blue/green, or canary deployment depending on risk and platform support.
- Keep the previous version deployable at all times; rollback should be one command or click, and rehearsed.
- Use feature flags so risky features ship dark and can be disabled without a deploy.
- Backward-compatible APIs and migrations during the rollout window (expand/contract above).
- Post-deploy smoke tests (health, login, one core AI request); alert and auto-rollback on failed checks where available.

## Release checklist
- [ ] CI green (lint, types, tests, evals, `validate_project.py`)
- [ ] Migration reviewed and tested on staging data
- [ ] Config and secrets present in the target environment
- [ ] Spend limits and rate limits set
- [ ] Smoke test passed on staging
- [ ] Rollback path confirmed
- [ ] Monitoring and alerts active for the new release
