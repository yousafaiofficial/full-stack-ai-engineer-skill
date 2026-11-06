# Backend, Frontend, and Data

## Backend
**Stacks:** Python (FastAPI, Pydantic, SQLAlchemy, Alembic, asyncio) or TypeScript (NestJS, Express, Hono, or framework-native routes). Use REST by default; SSE or WebSocket for streaming; GraphQL only when clients need flexible queries. Background jobs: Celery, BullMQ, or managed queues.

**Standards**
- Typed request/response schemas; validate all external input at the boundary.
- Keep business rules out of route handlers (service layer).
- Consistent error shape and correct HTTP status codes.
- Pagination, filtering, sorting, and versioning where needed.
- Authentication and authorization are separate concerns; check authorization on every protected operation.
- Rate limits, quotas, and abuse controls (important for LLM endpoints, which cost money).
- Transactions for related writes; idempotency keys for retryable operations.
- Timeouts and bounded retries with exponential backoff and jitter.
- Config via environment, never in source. Generate API docs (OpenAPI).

**Streaming endpoint tips:** send incremental tokens with SSE, include a final event with usage and citations, handle client disconnects by cancelling the upstream model call.

## Frontend
**Stack:** React / Next.js with TypeScript, Tailwind, an accessible component library (e.g. shadcn/ui), TanStack Query or framework data fetching. Add a client state library only when shared client state warrants it.

**Standards**
- Accessible, responsive, keyboard-friendly UI; semantic HTML; visible focus states.
- Always handle loading, empty, error, success, and retry states.
- Validate forms on client and server.
- Keep server state separate from local UI state.
- Prevent XSS: never render model or user output as raw HTML; sanitize markdown.
- AI chat: streaming render, stop/cancel button, reconnect behavior, message retry, and clear display of citations and uncertainty.
- Verify critical flows at mobile and desktop widths.

## Database and data
**Choosing storage**
- PostgreSQL for relational data and transactions (default).
- pgvector for embeddings at small-to-medium scale; a dedicated vector DB when scale or features justify it.
- Redis for cache, ephemeral state, rate limiting, queues.
- Document store only when access patterns clearly fit.
- Object storage for files and large blobs.

**Standards**
- Explicit schemas, constraints, relationships, and indexes.
- All schema changes through migrations.
- Check query plans for important queries; avoid N+1 and unbounded reads.
- Connection pooling; sensible transaction boundaries.
- Tenant isolation (row-level security where appropriate).
- Plan backup, restore (and test it), retention, archival, and deletion.
- Encrypt in transit and at rest; never log credentials or unnecessary personal data.

## Typical AI-app tables
`users`, `conversations`, `messages` (role, content, model, prompt_version, tokens, cost), `documents`, `chunks` (document_id, text, embedding, metadata, acl), `runs` / `tool_calls` (agent traces), `usage` (per user or tenant), `eval_runs`.
