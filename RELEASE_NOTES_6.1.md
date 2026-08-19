# ByteForge 6.1 — Tutor Layout Hotfix

6.1 is a focused presentation fix for the expanded 6.0 teaching system.

## Fixed

- Removed the accidental **double left-indent** inside Lyra's expanded tutor accordion.
- Increased desktop mentor rail width so code examples and symbol explanations remain readable.
- Rebalanced Lyra's character crop so the character stays integrated without stealing the reading column.
- Added responsive breakpoints that move the mentor below the editor before the teaching cards become too narrow.
- Made symbol-by-symbol rows shrink safely with `minmax(0, …)` and stack on small screens.
- Hardened code/example wrapping so long Python expressions no longer disappear outside narrow cards.
- Preserved all 6.0 pedagogy, simulated imports, 100 missions, Judge behavior, and saved progress.

No mission logic or sandbox permissions changed in 6.1.
