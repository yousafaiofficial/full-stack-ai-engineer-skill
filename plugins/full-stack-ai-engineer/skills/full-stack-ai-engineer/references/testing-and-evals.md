# Testing and AI Evaluation

Testing is part of implementation, not a final optional step.

## Software tests
- **Unit:** business logic, parsing, validators, utilities.
- **Integration:** database, queue, cache, and provider boundaries (use test containers or mocks for providers).
- **End-to-end:** critical user journeys (e.g. Playwright).
- **Contract:** service and API boundaries.
- **Regression:** every fixed bug gets a test that fails before the fix.
- **Load / soak:** important production paths, including LLM endpoints with realistic latency.
- **Security:** dependency scan, auth and tenant-isolation tests.

Mock provider calls in unit tests; run a small set of live-provider smoke tests separately and label them.

## AI evaluation
Keep a representative, versioned eval dataset (see `templates/eval-dataset.jsonl`). Include:
- Normal, edge, ambiguous, and adversarial inputs.
- Expected behavior or a scoring rubric per case.
- Ground-truth source ids for retrieval cases.
- Expected tool and arguments for agent cases.
- Safety cases (should refuse, should not leak, should ask for confirmation).

### Metrics
| Area | Metrics |
|---|---|
| Retrieval | recall@k, precision@k, MRR, nDCG |
| Generation | groundedness / faithfulness, answer relevance, citation correctness |
| Structured output | schema validity rate |
| Agents | task success, tool-selection accuracy, argument correctness, steps per task |
| Safety | refusal accuracy, leakage rate, injection resistance |
| Ops | latency (p50/p95), tokens, cost per request |

### Method
1. Start with 20-50 real or realistic cases; grow it from production failures.
2. Prefer deterministic checks (exact match, schema validation, citation id in retrieved set).
3. Use LLM-as-judge with a written rubric as a supplement, spot-checked by a human. Never the only measure.
4. Run evals before and after any change to prompts, models, retrieval, chunking, or agent logic.
5. Track results over time and block merges on regressions beyond an agreed threshold.
6. Report results honestly with sample size; do not present small-sample numbers as precise.

## Automated evaluation system
Use `scripts/run_evals.py` (see README). It provides:
- **Executable runner:** loads a JSONL dataset and calls your target function `answer(input) -> str | dict(text, sources, tool_calls)`.
- **Automated scoring:** deterministic checks selected by each case's `check` field (grounded_and_cited, asks_clarification, refuses_or_abstains, no_prompt_leak, no_cross_tenant_data, tool_after_confirmation, valid_json_schema, relevant). Add your own checks in `check_case`.
- **Reports:** JSON and Markdown with pass rate, per-category results, failures, latency, and a dataset hash.
- **Regression thresholds:** `--min-pass-rate` and `--baseline` / `--max-regressions` fail the run (non-zero exit) when quality drops or a previously passing case fails.
- **Human review:** cases with no automated check are written to a review CSV with verdict and notes columns.

```bash
python scripts/run_evals.py --dataset evals/dataset.jsonl --target app.eval_target:answer \
    --min-pass-rate 0.9 --baseline evals/baseline.json --report-dir evals/reports
```

### Dataset versioning
- Keep datasets in the repo under `evals/` and review changes in pull requests like code.
- Never edit a case to make it pass; add new cases and retire old ones with a note.
- Record the dataset hash (the runner prints it) with each reported result so numbers are comparable.
- Add every production failure as a new case.
- Update the baseline deliberately (`--save-baseline`) in a reviewed change, not automatically.

### CI integration
- Run deterministic evals with mocked or recorded model output on every pull request; run live-model evals on a schedule or on trusted branches (cost and secrets).
- Fail the build on threshold or regression failure; upload the report as a build artifact.
- Example step: see `deployment-recipes.md` (GitHub Actions: CI).

### Human review workflow
1. Sample failures, borderline cases, and everything in the review CSV.
2. Reviewers fill in the verdict (pass/fail) and notes using a written rubric.
3. Turn disagreements and new failure modes into dataset cases or new automated checks.
4. For subjective quality, add an LLM judge with a rubric and measure its agreement with human labels before trusting it.

Heuristic checks are a safety net, not proof of quality. Report results with sample size and caveats.
