# Full-Stack AI Engineer Skill

Version 3.1.0 (see `CHANGELOG.md`).

A skill that makes Claude behave like a principal-level full-stack AI engineer: it picks the right depth of process, loads only the references a task needs, carries work through run-and-verify cycles, and reports honestly on what was and was not checked.

## What it does
- Chooses **Quick / Standard / Full build** mode so small tasks stay small.
- Runs an **execution loop**: inspect, plan, implement, run checks, fix, verify the user journey, summarize.
- Covers LLM apps, RAG, agents and MCP, multimodal and voice, Next.js frontends, backends, data, security, testing and evals, deployment, and cost.
- Ships **scripts** that actually run evals and validate project hygiene.

## Install
Skills do not sync between Claude surfaces; install on each one you use.
- **Claude.ai:** zip the skill so the archive has one top-level folder named `full-stack-ai-engineer` containing `SKILL.md`. Open Settings > Capabilities > Skills, choose Upload skill, and select the ZIP. Requires a Pro, Max, Team, or Enterprise plan with code execution enabled.
- **Claude Code (skill folder):** copy this folder to `~/.claude/skills/full-stack-ai-engineer/` (personal) or `.claude/skills/full-stack-ai-engineer/` (project).
- **Claude Code (plugin):** if this skill came from the GitHub repo, run `claude plugin marketplace add <owner>/<repo>` then `claude plugin install full-stack-ai-engineer@fsai-skills`.
- **Claude API:** upload through the `/v1/skills` endpoints; see the Agent Skills documentation. Note the API sandbox has no network access, which does not affect this skill's scripts.

## Folder structure

```
full-stack-ai-engineer/
  SKILL.md                  core instructions (always loaded when the skill triggers)
  README.md, CHANGELOG.md
  references/               loaded on demand, one per topic
    architecture.md  llm-and-rag.md  multimodal-ai.md  agents.md  app-and-data.md
    frontend-advanced.md  security.md  testing-and-evals.md
    devops-and-observability.md  deployment-recipes.md
  templates/                starting points to copy into a project
    implementation-plan.md  adr.md  env.example  eval-dataset.jsonl
  scripts/                  runnable helpers (Python 3.9+, standard library only)
    run_evals.py  validate_project.py
```

## How reference loading works
`SKILL.md` contains a routing table. Before implementing in Standard or Full build mode, Claude reads only the reference files whose topics the task touches. Quick tasks skip this. This keeps the always-loaded core short.

## Scripts

```bash
# try the eval runner without a model
python scripts/run_evals.py --dataset templates/eval-dataset.jsonl --demo

# real use: point --target at your function  answer(input) -> str | dict(text, sources, tool_calls)
python scripts/run_evals.py --dataset evals/dataset.jsonl --target app.eval_target:answer \
    --min-pass-rate 0.9 --baseline evals/baseline.json --save-baseline evals/baseline.json

# check a project
python scripts/validate_project.py . --env-file .env
```

`run_evals.py` writes JSON and Markdown reports, tracks a dataset hash, flags regressions against a baseline, exits non-zero when thresholds fail (use it in CI), and writes cases it cannot score automatically to a CSV for human review. Its checks are heuristics; add an LLM judge with a rubric and human spot-checks for subjective quality.

## Example prompts
- "Add a streaming chat endpoint with citations to this FastAPI + Next.js app." (Standard)
- "Fix the bug where uploads over 10 MB fail." (Standard, reproduce first)
- "Build a document Q&A product with auth, RAG, evals, and deploy plan." (Full build)
- "Why are my RAG answers wrong? Diagnose and fix." (Standard, uses the diagnosis checklist)
- "Add voice input to the assistant." (Standard, reads `multimodal-ai.md`)
- "Set up CI and a staging-to-production pipeline on GitHub Actions." (Standard, reads `deployment-recipes.md`)

## Customize
- Change defaults in the stack table in `SKILL.md` (for example Django instead of FastAPI).
- Add company standards as a new reference file and a row in the routing table.
- Edit `templates/env.example` and the check names in `run_evals.py` for your domain.
- Keep `SKILL.md` short; put detail in references.

## Maintain
- Review references when major framework or provider versions change; the skill tells Claude to verify version-sensitive details against current docs.
- Update `CHANGELOG.md` and the version above with each change.
- Test changes against 10-15 realistic tasks (new builds and debugging existing projects) before relying on them. Real task runs, not file inspection, show whether the skill performs.
