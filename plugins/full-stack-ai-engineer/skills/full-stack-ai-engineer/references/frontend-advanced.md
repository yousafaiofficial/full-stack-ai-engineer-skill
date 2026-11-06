# Advanced Frontend Engineering (Next.js and React)

Always follow the project's existing framework version and conventions. Verify API details against the installed version's docs; Next.js behavior changes between major versions.

## App Router and Server Components
- Default to **Server Components**. Add `"use client"` only for interactivity (state, effects, event handlers, browser APIs). Push the client boundary as far down the tree as possible.
- Fetch data on the server in components or route handlers; pass serializable props to client components.
- Never import server-only code (DB clients, secrets) into client components. Mark such modules server-only.
- Use `loading` and `error` boundaries per route segment, and Suspense for streaming parts of a page.
- Choose caching and revalidation deliberately per request (static, time-based, on-demand). Check what the installed version defaults to rather than assuming.

## Server Actions and API boundaries
- Use **Server Actions** for form mutations tied to the UI; use **route handlers** for public or third-party APIs, webhooks, streaming (SSE), and anything non-browser clients call.
- A Server Action is a public endpoint. Authenticate, authorize, and validate input inside every action (Zod or equivalent). Never trust client-supplied user ids.
- Return typed, serializable results with field-level errors; do not leak internals.
- Keep business logic in a service layer shared by actions and route handlers.

## Authentication and protected routes
- Use an established auth solution (Auth.js, Clerk, Supabase Auth, provider OIDC) rather than hand-rolled sessions.
- Middleware/proxy can redirect unauthenticated users, but **do authorization checks in the data layer and actions too**; do not rely on route-level redirects alone.
- Store sessions in httpOnly, secure, SameSite cookies. Never put tokens in localStorage.
- Protect API routes and actions separately from pages. Test that a logged-out or wrong-tenant user is rejected.

## Component architecture and design systems
- Structure: `app/` (routes), `components/ui/` (primitives), `components/features/` (domain components), `lib/` (utilities, clients), `server/` or `services/` (business logic).
- Build small, composable components with typed props; prefer composition and slots over boolean-prop explosions.
- Use design tokens (colors, spacing, type scale, radii) via Tailwind config or CSS variables; support light/dark from the start.
- Use an accessible primitive library (Radix, shadcn/ui, React Aria) for menus, dialogs, tabs, comboboxes.
- Document key components with examples or Storybook when the team is larger than one.

## AI chat UI patterns
- Stream tokens incrementally; append without re-rendering the whole list; auto-scroll only if the user is at the bottom.
- Stop/cancel button that aborts the request and the upstream model call.
- Message states: sending, streaming, complete, failed with retry, regenerate.
- Render markdown safely (sanitize, no raw HTML); syntax-highlight code lazily.
- Show citations as inline references linked to source panels; show tool activity ("Searching documents...") and uncertainty.
- Persist drafts and conversation state; handle reconnects and duplicate submits (idempotency key).

## Performance and Core Web Vitals
- Targets to measure against: LCP, INP, CLS (use field data where available, Lighthouse/Web Vitals in dev).
- Use the framework image component with explicit dimensions; use font optimization; avoid layout shift.
- Code-split heavy client components (editors, charts, markdown+highlight) with dynamic import.
- Minimize client JavaScript: keep logic on the server, audit bundle size before adding a dependency.
- Avoid waterfalls: fetch in parallel, stream with Suspense, preload critical data.
- Memoize only where profiling shows a problem.

## SEO and metadata
- Per-route metadata (title, description, canonical, Open Graph, Twitter cards) via the framework's metadata API.
- Generate `sitemap` and `robots`; use semantic headings (one `h1` per page) and descriptive link text.
- Server-render content that must be indexed; add structured data (JSON-LD) where it helps.
- Do not index private or authenticated pages.

## Accessibility (and how to test it)
- Semantic HTML, label every control, visible focus, logical tab order, sufficient color contrast, respect reduced motion.
- Announce streaming/AI updates with an appropriate live region without spamming screen readers.
- Test: keyboard-only walkthrough, axe checks in CI (for example via Playwright), and a manual screen-reader pass on critical flows.
- Treat automated tools as a floor; they catch only part of real accessibility problems.

## Frontend security
- Prevent XSS: no `dangerouslySetInnerHTML` with untrusted content; sanitize markdown and model output.
- Set CSP and other security headers; restrict third-party scripts.
- Keep secrets out of client bundles: only variables meant to be public get the public prefix.
- CSRF: rely on SameSite cookies plus the framework's action protections, and verify for custom endpoints.
- Validate and size-limit uploads; check file type server-side.
- Avoid open redirects; validate `returnTo` style parameters.

## Frontend testing
- Component tests with Vitest + Testing Library; end-to-end with Playwright covering sign-in, the main journey, error states, and mobile viewport.
- Mock the model provider at the network boundary; keep a few live smoke tests separate.
