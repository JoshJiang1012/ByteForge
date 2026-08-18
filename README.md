# ByteForge 5.0 — Cyber Range Academy

ByteForge 5.0 is a **local, bilingual, game-like white-hat cybersecurity learning environment** built around a 100-mission sequential cyber range. It combines Python practice, defensive security logic, attacker-view analysis of synthetic data, boss encounters, a VS Code-style editor, and character-guided teaching.

## 5.0 highlights

- **100 sequential missions** — 10 sectors × 10 missions, with every 10th mission as a boss encounter.
- **90 normal missions + 10 bosses** — no daily locks, no cooldowns, no artificial pacing.
- **Three learning perspectives**:
  - **BLUE** — defensive controls, validation, hardening, detection, and response.
  - **RED-VIEW** — recognize attacker-visible weaknesses and suspicious patterns using only supplied synthetic data.
  - **PURPLE** — connect attacker observations to defender decisions.
- **Clear prerequisite order** — programming fundamentals → identity → Linux → Web → network → secrets → detection → incident response → secure coding → purple-team integration.
- **Editor fidelity fix** — the textarea, syntax layer, token spans, and line numbers now share the exact same font metrics. Ligatures are disabled and the old character-shaped typing pop was replaced with a non-text pulse, fixing the apparent “extra space / caret drift” problem.
- **VS Code-style editor** — live Python syntax highlighting, line numbers, status bar, `Ctrl + Enter`, Tab indentation, and autosaved drafts.
- **Clear Mission Contract** — every mission shows the exact target function, visible examples, objectives, core concept, and test count before coding.
- **3-stage hints** — Direction → Structure → Near Solution.
- **Scene-integrated characters**:
  - **Lyra Circuit** — teacher and live syntax tutor.
  - **Patch** — contextual debugging/support NPC.
  - **Warden Null** — recurring boss presence and encounter UI.
- **中文 / English** instant switching.
- **Performance Mode ON by default** — no continuous particle fields or expensive decorative animation loops.
- **Local-only guarded Judge** — imports, file access, network access, and sensitive runtime capabilities are blocked.

## Course map

1. Core Security Automation
2. Identity & Access Control
3. Linux & Host Hardening
4. Web Request Security
5. Network & Firewall
6. Secrets & Crypto Hygiene
7. Detection Engineering
8. Incident Response & Forensics
9. Secure Coding & Vulnerability Defense
10. Purple-Team Integrated Range

See [`COURSE.md`](COURSE.md) for the complete 100-mission list.

## Safety model

All attack/defense exercises run against **synthetic inputs inside ByteForge's local learning sandbox**. RED-VIEW missions are recognition and classification exercises; they do not scan real systems, crack credentials, install persistence, deploy malware, or provide live-target exploitation capability.

## Requirements

- Python 3.10+
- Modern browser
- No Node.js / npm required
- No pip packages required

## Start

### Windows

Double-click:

```text
RUN-BYTEFORGE-WINDOWS.bat
```

### Linux

```bash
bash RUN-BYTEFORGE-LINUX.sh
```

### macOS

```bash
bash RUN-BYTEFORGE-MAC.command
```

Keep the launcher terminal open while playing.

## Self-test

```bash
python server.py --self-test
```

Expected final line:

```text
Self-test: PASS — 100 quests
```

## Editor fidelity

ByteForge uses a transparent native textarea layered over a syntax-highlighted code surface. Version 5.0 locks both layers to the same font family, `13px` font size, `22px` line height, zero letter/word spacing, `tab-size: 4`, and disabled font ligatures. This prevents the highlighted text from drifting away from the real caret.

## Character assets

Optimized runtime assets are stored under:

```text
static/assets/characters/
```

## License

MIT — see [`LICENSE`](LICENSE).
