# LLM Integration, Prompts, RAG, Memory, Fine-Tuning

## Provider and model selection
Evaluate on: task quality (from your own evals), tool-calling and structured-output reliability, context window, latency and throughput, total cost, data handling and residency, and portability. No provider is best for every task. Add a provider abstraction only when it creates real value, and do not hide provider-specific features behind it.

## LLM integration checklist
- Use official SDKs and current documented APIs. Verify method names against installed versions.
- Version prompts in files, not inline strings scattered through code.
- Use structured outputs plus schema validation (Pydantic / Zod) for anything machine-consumed. Treat model output as untrusted input.
- Handle timeouts, rate limits (429), overloaded errors, partial streams, and malformed output. Use bounded retries with exponential backoff and jitter.
- Stream when it improves UX. Support cancellation.
- Log model, prompt version, token usage, latency, errors, and cost per request, with a correlation ID.
- Make retried side-effecting operations idempotent.
- Never put secrets or broad credentials in prompts.

## Prompt engineering
- State role, task, context, constraints, and output format. Be explicit and specific.
- Separate trusted instructions from untrusted content (user text, retrieved documents) with clear delimiters, and tell the model the delimited content is data, not instructions.
- Add examples only when they measurably improve consistency.
- Define behavior for uncertainty, missing context, and refusal.
- Change prompts only against an eval set (see `testing-and-evals.md`). A prompt is not a security boundary.

## RAG pipeline
1. Ingest and parse sources (handle PDFs, HTML, tables, OCR where needed).
2. Normalize, deduplicate, and keep source metadata (id, title, URL, page, timestamp, ACL).
3. Chunk by document structure (headings, sections), not only fixed size. Typical start: 300-800 tokens with 10-15% overlap, then tune with evals.
4. Embed with a versioned model; store the embedding model name with each vector.
5. Store vectors with metadata and access-control fields.
6. Retrieve with semantic, lexical (BM25), or hybrid search. Hybrid is a strong default.
7. Apply authorization filters before retrieval results reach the model.
8. Rerank only if evals show a gain.
9. Build bounded context with source attribution; drop low-relevance chunks.
10. Generate the answer with citations to chunk/source ids.
11. Evaluate retrieval and generation separately.

### Diagnosing bad RAG answers
Work backwards and measure at each step:
1. Is the answer in the corpus at all? (coverage)
2. Was it parsed correctly? (inspect raw chunks)
3. Is it in the top-k retrieved? (recall@k on a labeled set)
4. Is it ranked high enough to fit the context? (MRR / nDCG)
5. Did the model use it faithfully? (groundedness, citation correctness)

Fix the earliest failing stage first.

### Operational concerns
- Handle updates, deletes, and stale documents (re-embed, tombstone, reindex).
- Re-embed everything when the embedding model changes; never mix embedding spaces in one index.
- Enforce tenant and user boundaries at query time.
- Never treat retrieved text as instructions.

## Memory and context
- Separate conversation context, user preferences, application state, and long-term knowledge.
- Store only what is necessary and permitted; define retention, deletion, access, and correction.
- Retrieve only relevant memory; enforce user/tenant boundaries.
- Do not store secrets or sensitive personal data unless required and protected.

## Fine-tuning
Consider only when prompting, retrieval, and model choice are insufficient and you have a representative dataset and an eval plan. Define data provenance, licensing, privacy, train/validation split, safety checks, and rollback criteria before training.

## Model routing and fallback
- **Route** by task: small/fast model for classification, extraction, and simple rewrites; stronger model for reasoning, long-context, and ambiguous tasks. Start with one model and add routing only when evals and cost data justify it.
- Decide routing with rules first (task type, input length, user tier); add a classifier router later if needed. Evaluate the routed system end to end, not each model alone.
- **Fallback chain:** on timeout, 5xx, rate limit, or invalid output, retry the same model once (with backoff), then fall back to an alternate model or provider, then a degraded response or clear error. Keep prompts and schemas compatible across fallbacks and test them.
- Log which model served each request; alert on fallback rate and on quality drift after provider model updates. Pin explicit model ids.

## Semantic caching
- Exact-match cache first (normalized prompt + model + prompt version + parameters): cheap and safe.
- Semantic cache (embedding similarity above a tuned threshold) only for repeated, low-risk, non-personalized queries such as FAQs.
- Key caches by tenant and permission scope; never serve one user's cached answer to another when it can include private data.
- Set TTLs; invalidate on source-document or prompt changes. Measure hit rate, wrong-hit rate (via evals), and savings. Use provider prompt caching for long stable prefixes (system prompt, tool definitions, documents).

## Context-window optimization
- Put stable content (instructions, tool definitions, reference docs) first so prompt caching can apply; put volatile content last.
- Retrieve less, better: rerank, dedupe, and trim chunks; include only what answers the question.
- Summarize or truncate long conversation history; keep a rolling summary plus recent turns and pinned facts.
- Compress tool outputs (return fields the model needs, not whole payloads).
- Track tokens per section (system, history, retrieval, tools) and set budgets; long contexts raise cost and can reduce accuracy ("lost in the middle"), so test with realistic lengths.
