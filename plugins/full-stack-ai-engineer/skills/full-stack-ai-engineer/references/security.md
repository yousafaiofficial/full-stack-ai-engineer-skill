# Security, Privacy, and Safety

Use defense in depth. Prompts are never the only security boundary.

## Application security
- Least privilege for users, services, agents, and infrastructure.
- Established auth protocols (OIDC/OAuth2), secure session handling, and authorization checks on every protected resource and operation.
- Secrets in a secrets manager or protected environment config; rotate and support revocation. Never commit real secrets.
- Validate and normalize untrusted input. Guard against injection (SQL, command), XSS, CSRF, SSRF, path traversal, and insecure deserialization as relevant.
- Narrow CORS, secure cookies, TLS, and security headers.
- Keep dependencies patched; scan for known vulnerabilities in CI.
- Do not expose stack traces, internal ids, or secrets to clients.

## AI-specific security
- **Prompt injection:** assume user input, retrieved documents, web pages, and tool output may contain hostile instructions. Delimit them as data, never let them expand permissions, and require confirmation before acting on instructions found in them.
- **Output handling:** treat model output as untrusted. Validate before executing, rendering, or persisting. Never pass model output directly to a shell, SQL, or `eval`.
- **Data leakage:** keep system prompts and secrets out of user-visible context. Enforce tenant and user boundaries in retrieval, memory, caches, and logs.
- **Tool safety:** restrict tools by identity, scope, and operation; require explicit confirmation for high-impact actions; set budgets.
- **Abuse and cost:** rate limit, set per-user quotas, cap output length and tool loops.
- **Testing:** include adversarial cases for exfiltration, unsafe tool calls, jailbreaks, and cross-tenant access in your eval set.

## Privacy
- Minimize collection and retention; explain data use where the product requires it.
- Provide deletion and export flows where applicable.
- Redact sensitive fields in logs and traces.
- Review third-party model and service data policies before sending user data; know whether data is retained or used for training.
- Do not claim regulatory compliance (GDPR, HIPAA, SOC 2, etc.) without verifying actual controls and requirements.

## Quick security review checklist
- [ ] Every endpoint has authentication and authorization
- [ ] No secrets in code, logs, prompts, or client bundles
- [ ] Input validated; output encoded or sanitized
- [ ] Tools scoped; destructive actions gated
- [ ] Tenant isolation tested
- [ ] Rate limits and spend caps set
- [ ] Dependencies scanned
- [ ] Logs redacted
