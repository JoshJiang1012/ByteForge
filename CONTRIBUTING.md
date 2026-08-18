# Contributing to ByteForge

Thanks for improving ByteForge. Keep contributions focused on educational clarity, deterministic tests, and a safe local-first runtime.

## Development

ByteForge has no third-party runtime dependencies. Use Python 3.10+.

```bash
python3 server.py --self-test
python3 server.py
```

## Mission quality bar

A mission should:

1. teach one clear programming idea or deliberately combine earlier ideas in a Boss mission;
2. contain deterministic public and hidden tests;
3. avoid requiring network access, files, imports, or external services;
4. include concise objectives and progressive hints;
5. include both English content and a Traditional Chinese translation;
6. include a syntax tutor entry (`title`, `body`, `example`, `command`, `command_note`); beginner missions should also include `why`, `try_it`, and `steps`;
7. introduce new syntax gradually in normal missions and reserve Boss missions for integration;
8. have a reference solution that passes every test.

After adding or changing missions, run:

```bash
python3 server.py --self-test
```

## Translation rules

Python keywords, identifiers, code samples, protocol tokens, and expected literal outputs should stay unchanged unless the mission explicitly tests text localization. Translate the explanation around the code, not Python itself.

## Security scope

Security-themed missions must stay defensive or isolated. Do not add missions that target real third-party systems, credentials, malware delivery, evasion, persistence, or destructive behavior.

## Pull requests

Keep changes small enough to review. Explain what changed, why, and how it was tested.
