# ByteForge 6.3 — Tutor Flow Layout

6.3 replaces the remaining two-column tutor explanation layout with a width-safe vertical flow.

## Fixed
- Structured syntax rows now render code first and explanation below it.
- Removed the layout condition that caused long Chinese explanations to make rows hundreds of pixels tall.
- Tutor code snippets wrap naturally instead of being clipped by hidden overflow.
- Lyra is isolated inside a dedicated mentor header and no longer participates in lesson width calculation.
- At <=1320px the entire tutor rail moves below the editor as one full-width column.
- Accordion content uses natural height only; no lesson content has a fixed/minimum height.
