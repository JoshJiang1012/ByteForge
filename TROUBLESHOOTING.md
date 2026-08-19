# ByteForge 7.0 Troubleshooting

## Browser says connection refused

Keep the launcher terminal open. ByteForge prints the exact local URL it successfully bound to. If port 3000 is busy it can fall back to another local port.

## Run the full integrity check

```bash
python server.py --self-test
```

Expected final line:

```text
Self-test: PASS — 100 quests
```

## A simulated import is rejected

Only the ByteForge virtual allowlist is accepted:

```text
hashlib     sha256
json        loads, dumps
ipaddress   ip_address
math        ceil, floor, sqrt, log2
```

Arbitrary, wildcard, and relative imports are intentionally unavailable.

## A mission says an import is required

Missions 45, 53, and 61 deliberately teach simulated import syntax. Keep the required `import ...` or allowed `from ... import ...` statement in your solution.

## Windows timeout

Windows does not support Python's Unix `resource.setrlimit`. The Judge still uses AST restrictions and a 3-second execution timeout, but ByteForge is not intended to execute hostile untrusted programs.
