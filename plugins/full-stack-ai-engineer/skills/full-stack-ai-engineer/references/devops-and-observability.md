# DevOps, Deployment, Observability, Cost

## Delivery
- Docker where it improves reproducibility; provide local dev setup and `.env.example`.
- CI: format, lint, type check, tests, dependency and secret scanning, and evals for AI changes.
- CD: staged rollout, health checks, and a tested rollback path.
- Separate dev, staging, and production; Infrastructure as Code when infra complexity warrants it.

## Platform choice
Pick by workload, team skill, compliance, cost, and operational burden: Vercel, Fly.io, Railway, AWS, GCP, Azure. Kubernetes is not a default; use it only when you need what it provides.

## Reliability
- Define SLOs for critical paths.
- Health and readiness endpoints.
- Bounded retries, circuit breakers, and graceful degradation (e.g. fall back to a cheaper model or a cached answer, or show a clear error).
- Queue consumers must tolerate duplicate delivery and replay; use dead-letter queues for repeatedly failing jobs.
- Back up databases and test restores.
- Document incident response and recovery steps.
- Feature flags for risky changes.

## Production Dockerfile pattern (Python API)
Multi-stage build, pinned versions, non-root user, no build tools in the final image.

```dockerfile
# Pin an explicit version (and ideally a digest) instead of :latest.
FROM python:3.12.7-slim AS builder
WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.lock .
# requirements.lock should be fully pinned (ideally with hashes: pip install --require-hashes)
RUN pip wheel --wheel-dir /wheels -r requirements.lock

FROM python:3.12.7-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels
COPY . .
RUN useradd --system --uid 10001 app && chown -R app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Hardening checklist:
- Pin base image tag (digest for production) and all dependencies; rebuild regularly to pick up patches.
- Add a `.dockerignore` (`.git`, `.env`, `node_modules`, tests, local data) so secrets and junk never enter the image.
- Never bake secrets into the image or `ENV`/`ARG`; inject at runtime.
- Run as non-root; where the platform allows, use a read-only root filesystem, drop capabilities, and set CPU/memory limits.
- Scan images for vulnerabilities in CI.
- Set per-environment configuration (log level, origins, model, limits) through environment variables, not separate images.
- Run one process per container, handle SIGTERM for graceful shutdown, and expose `/health` and `/ready`.

For deployment-specific workflows (Compose, GitHub Actions, Vercel, AWS, migrations, rollback) see `deployment-recipes.md`.

## Observability
Scale to product maturity. Start with structured, redacted logs and basic metrics; add tracing as complexity grows.
- Structured logs with correlation IDs across requests, jobs, and tool calls.
- Metrics: throughput, error rate, latency, saturation, queue depth, business outcomes.
- Tracing across services and tool boundaries (OpenTelemetry).
- AI traces: prompt version, model, retrieved chunks, tool calls, tokens, latency, cost (Langfuse, LangSmith, or equivalent).
- Alerts on actionable thresholds; dashboards for critical workflows.

## Cost and performance
- Attribute model and infra spend by feature, user, or tenant.
- Watch tokens per request, cache hit rate, queue depth, and DB performance.
- Use prompt caching and response caching where freshness and privacy allow.
- Route simple tasks to smaller models only when evals show acceptable quality.
- Set budgets, quotas, and alerts; cap max output tokens and agent steps.
- Work from a measured baseline and report cost / latency / quality trade-offs together, not one metric in isolation.
