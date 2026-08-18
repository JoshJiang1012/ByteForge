# ByteForge 5.0 Release Notes

## The 100-Mission Range

5.0 replaces the old 55-mission catalog with a new **100-mission sequential white-hat curriculum**. The campaign is organized into ten sectors, each containing nine normal missions and one boss encounter.

The ordering intentionally follows both programming and cybersecurity prerequisites: basic comparison and branching come before access-control policy; string/list/dict work comes before log correlation; isolated control checks come before integrated purple-team decisions.

## Attack / defense without real targets

Three mission perspectives are used:

- **BLUE** — implement a defensive rule or analysis.
- **RED-VIEW** — recognize an attacker-visible weakness or suspicious pattern using supplied synthetic input.
- **PURPLE** — connect attacker observations to defender controls.

RED-VIEW missions remain data-classification exercises. They do not provide live scanning, credential cracking, malware, persistence, or real-target exploitation capability.

## Editor Fidelity Fix

4.x could visually drift because the browser's default `<code>` font did not necessarily match the transparent textarea font. That could make the colored text appear roughly one character away from the real caret.

5.0 fixes the problem by enforcing one editor font contract across:

- native textarea
- syntax `<pre>`
- nested `<code>`
- token spans
- line numbers

Line height is now exactly 22px and font ligatures are disabled. The old character-shaped typing pop is also removed; typing feedback is now a small non-text pulse that cannot be confused with code.

## Verification

The release is considered valid only when:

```text
python server.py --self-test
```

passes all 100 bundled reference solutions.
