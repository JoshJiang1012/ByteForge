# ByteForge 5.0 Troubleshooting

## Browser says connection refused

The browser UI depends on the local Python server. Keep the launcher terminal open. Restart ByteForge and use the exact `OPEN:` URL printed in that terminal.

ByteForge normally tries port 3000, then falls back automatically when that port is occupied.

## Check server health

With ByteForge running, open the printed URL and append `/api/health`. A healthy 5.0 server reports `ok: true`, version `5.0.0`, and `100` missions.

## Run the full test suite

```bash
python3 server.py --self-test
```

Expected final line:

```text
Self-test: PASS — 100 quests
```

## Syntax colors look misaligned

Use a current Chrome, Edge, Firefox, or Safari build. The editor requires normal browser font/layout APIs but no extension. Browser zoom at unusual values can slightly change monospace metrics; 100% zoom is the best reference.

## Typing animation is missing

ByteForge respects `prefers-reduced-motion`. If your operating system asks apps to reduce motion, the input pulse animation is intentionally disabled while syntax highlighting remains active.
