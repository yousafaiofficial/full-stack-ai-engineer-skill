# Agents, Tool Use, MCP

## Do you need an agent?
Use an agent only when the task needs dynamic planning or tool selection. For predictable business processes, use a deterministic workflow (fixed steps, optionally with LLM calls inside steps). Escalate in this order: single prompt -> prompt chain -> router -> agent loop -> multi-agent.

## Tool design
- Narrow, single-purpose tools with typed input and output schemas and clear descriptions (what it does, when to use it, what it returns).
- Return concise, structured, model-friendly output with useful error messages the model can act on.
- Enforce authorization inside the tool implementation using the real user identity, not in the prompt.
- Use least-privilege, scoped credentials per tool.
- Validate all arguments; validate returned data before it re-enters context.
- Separate read-only tools from write tools. Mark destructive tools explicitly.

## Agent loop controls
- Budgets: max steps, wall-clock time, tokens, and money per run.
- Per-tool timeouts, cancellation, and bounded retries.
- Loop detection (repeated identical calls or no progress) with a safe stop.
- Human approval for consequential or irreversible actions (payments, deletions, external messages, production changes).
- Persist run state when workflows must survive restarts or span long periods.
- Full audit trace: inputs, tool calls, arguments, results, decisions, cost.
- Safe stopping: on failure, return a useful summary of what was done and what is left.

## Untrusted content
Tool output, web pages, files, emails, and user content can carry injected instructions. Keep them in a clearly delimited data channel, never grant them authority, and do not let them change tool permissions or goals. Require confirmation before any action triggered by instructions found inside retrieved or tool-returned content.

## MCP servers
- Expose a small set of well-described tools; prefer task-oriented tools over thin API wrappers.
- Authenticate and authorize per user; never share one broad token across users.
- Validate inputs, rate-limit, and log calls.
- Document each tool's side effects and required scopes.

## Multi-agent systems
Add multiple agents only for a concrete reason (parallelizable work, context isolation, distinct tool sets). Define for each agent: responsibility, inputs and outputs, communication contract, shared-state rules, coordination strategy, and failure handling. Prefer one orchestrator with focused workers over free-form agent chatter.

## Evaluate agents
Test tool selection, argument correctness, step efficiency, task success, safety behavior (refusals, approval gates), and cost per task. See `testing-and-evals.md`.
