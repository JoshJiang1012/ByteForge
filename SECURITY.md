# ByteForge 7.0 Security Model

ByteForge is a **local educational sandbox**, not a hardened multi-tenant code-execution service.

## Boundaries

- The HTTP server binds to `127.0.0.1` only.
- Learner code is parsed with Python `ast` before execution.
- File APIs, dynamic evaluation, dunder attribute access, sensitive process/network attributes, and other high-risk capabilities are rejected.
- Code executes in a separate Python subprocess with a 3-second wall-clock timeout.
- On Unix-like platforms, `resource.setrlimit` additionally constrains CPU, address space, and file size where supported.
- On Windows, those Unix `resource` limits are unavailable; the local Judge mainly relies on the timeout plus AST restrictions.

## Simulated imports

6.0 accepts normal-looking `import` / `from ... import ...` syntax only for an explicit virtual allowlist. The AST transformer rewrites those nodes before execution so learner code never receives general module-loading capability.

Virtual modules:

- `hashlib`: `sha256`
- `json`: `loads`, `dumps`
- `ipaddress`: `ip_address`
- `math`: `ceil`, `floor`, `sqrt`, `log2`

`import os`, relative imports, wildcard imports, and non-allowlisted names are rejected.

## Intended use

Use ByteForge for its bundled synthetic missions and learner-authored solutions to those missions. Do not treat it as an isolation boundary for intentionally hostile arbitrary code.

## 7.0 AI boundary

AI is downstream of the sandbox and deterministic Judge. It cannot override AST blocking or turn a failed code test into a pass.

When a connected AI endpoint is configured, ByteForge sends only public mission context, learner code, learner reasoning, and the learner's question. Hidden tests are explicitly excluded. `BYTEFORGE_AI_KEY` remains server-side and is never returned to the browser.

If the connected AI endpoint is unavailable, ByteForge falls back to its local deterministic reasoning rubric and guided tutor so the course remains usable offline.
