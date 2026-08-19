# ByteForge 6.4 — Global Readability Recovery

6.4 fixes the full-screen layout regression visible on 4K/high-DPI and medium-width desktop windows.

## Fixed
- Removed the independent scrolling viewport from the right Tutor rail.
- Raised excessively small 8–10px interface text to readable desktop sizes.
- Expanded the mission editor and learning cards.
- At widths below 1760px, Lyra's entire tutor deck moves below the main mission column instead of squeezing all three columns.
- At widths below 1080px, the mission navigation also joins normal page flow.
- Kept Tutor details in natural-height vertical flow and preserved 6.0 simulated imports / 3+3 post-clear labs.

## Preserved
- 100 missions / 10 bosses.
- Simulated Import allowlist.
- Local AST-guarded Judge.
- 中文 / English.
- Editor caret-alignment fix.
