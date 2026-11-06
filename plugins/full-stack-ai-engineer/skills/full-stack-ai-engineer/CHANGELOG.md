# Changelog

All notable changes to this skill. Versioning: MAJOR when the skill's behavior or structure changes in a breaking way, MINOR for new capabilities or reference files, PATCH for fixes and wording.

## 3.1.0 - 2026-11-06
### Added
- Autonomous execution loop in `SKILL.md` (inspect, plan, implement, run, fix, verify, summarize) with retry caps and no-silent-weakening rules.
- Mandatory reference loading before implementation in Standard and Full build modes.
- `references/frontend-advanced.md`: App Router, Server Components and Actions, auth, performance, SEO, accessibility testing, frontend security.
- `references/multimodal-ai.md`: vision, audio, voice and real-time, video, OCR and document intelligence, workflow orchestration, streaming structured outputs.
- `references/deployment-recipes.md`: Docker Compose, GitHub Actions CI and deploy, Vercel, AWS, expand/contract migrations, zero-downtime and rollback.
- `llm-and-rag.md`: model routing and fallback, semantic caching, context-window optimization.
- `scripts/run_evals.py`: executable runner with automated checks, JSON and Markdown reports, thresholds, baseline regression detection, dataset hashing, human-review CSV.
- `scripts/validate_project.py`: env template, secret, CI, test, lockfile, and Dockerfile hygiene checks.
- `templates/implementation-plan.md`, `README.md`, this changelog.

### Changed
- `templates/env.example` now tags every variable `[required]` or `[optional]` (read by `validate_project.py`).
- Docker example hardened (multi-stage, pinned tags, non-root, `.dockerignore`).
- `testing-and-evals.md` documents CI integration, dataset versioning, and human review.

### Removed
- Arbitrary "1,000 requests per minute" sizing rule in `architecture.md`; replaced by guidance to scale from measured bottlenecks.

## 3.0.0 - 2026-11-06
- Restructured into a lean core `SKILL.md` plus on-demand reference files and templates.
- Added Quick / Standard / Full build modes and a user-override rule.

## 2.0.0
- Single large file covering architecture, AI, backend, frontend, security, testing, and operations.
