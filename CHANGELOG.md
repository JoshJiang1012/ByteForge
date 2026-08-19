## 7.0.0

- Added AI Academy hybrid grading for 30 PURPLE / RED-VIEW missions.
- Added optional connected LLM support through a Chat-Completions-compatible endpoint using only Python stdlib.
- Added Lyra AI Tutor and Patch AI debugging.
- Added 70-point deterministic Judge + 30-point reasoning rubric, with 85/100 clear threshold.
- Added LOCAL RUBRIC fallback so the full course remains playable offline.
- Hidden tests are never sent to the AI layer.
- Preserved 6.4 responsive readability layout and editor fidelity fixes.

# Changelog

## 7.0.0 — AI Academy

- Added hybrid AI-assisted grading to 30 RED-VIEW / PURPLE missions.
- Deterministic Judge remains authoritative for executable correctness and sandbox safety.
- Added 70/30 Judge + reasoning score display and fixed rubric feedback.
- Added Lyra AI Tutor and Patch AI Debug endpoints/UI.
- Added offline Local Rubric fallback and optional OpenAI-compatible connected LLM mode.
- Added `/api/ai/status` and `/api/ai/tutor`.
- Hidden tests are never sent to AI; API credentials stay server-side.
- Preserved the 6.4 global readability and performance architecture.

## 6.4.0
- Rebuilt the full-page responsive layout around readability instead of fitting three columns at all costs.
- Removed the right tutor rail's independent viewport-height scrollbar; tutor content now follows normal page flow.
- Increased micro-UI text throughout missions, navigation, Judge output, and Lyra tutor cards.
- At <=1760px the tutor deck moves below the main learning column instead of shrinking into a miniature dashboard.
- Increased editor font and line height while preserving the 5.0 caret/highlight metric lock.

## 6.3.0
- Rebuilt Tutor structured rows as vertical flows to eliminate narrow-column overflow and giant row heights.
- Isolated Lyra art inside a dedicated mentor header.
- Removed clipping from tutor code examples and accordion bodies.

## 6.2.0
- Rebuilt tutor layout so all lesson content is full-width.
- Confined Lyra artwork to the mentor header region.
- Fixed narrow accordion and code clipping regressions.


## 6.1.0

- Fixed Lyra tutor accordion double-indentation that could compress teaching content into a narrow strip.
- Increased the desktop mentor rail and reading column widths.
- Rebalanced Lyra's crop so character art remains integrated without stealing tutor text space.
- Added responsive breakpoints that move the tutor below the editor before readability degrades.
- Added safe wrapping and small-screen stacking for syntax breakdown rows and code examples.
- Preserved all 6.0 mission logic, simulated imports, Judge behavior, 100 missions, and local progress.

## 6.0.0

- Expanded every mission tutorial into structured, explicit syntax teaching.
- Added exact pass-requirement panels.
- Added safe AST-rewritten simulated imports (`hashlib`, `json`, `ipaddress`, `math`).
- Added three dedicated simulated-import missions.
- Added post-clear 3-example + 3-practice study lab for every mission.
- Moved repeated sandbox wording into one Environment Note.
- Preserved 100-mission / 10-boss progression and 5.0 editor alignment fix.

## 4.0.0 — Cyber Academy Update

### Added
- Lyra Circuit live teacher panel.
- Patch reactive support NPC.
- Warden Null recurring boss preview.
- Optimized WebP character assets.
- Performance Mode toggle, ON by default.
- Mission Contract with target function, visible tests, Judge summary, and explicit objectives.
- Three-stage hint presentation: Direction / Structure / Near Solution.
- Public visible test examples without exposing hidden test expressions.

### Changed
- Complete Cyber Academy visual redesign.
- Removed continuous animated auroras, scan beams, orbiting rings, and decorative pulses.
- Syntax highlighting now batches work through `requestAnimationFrame`.
- Draft saves are debounced.
- Version bumped to 4.0.0.

### Preserved
- 50 cybersecurity labs + 5 bosses.
- Immediate sequential unlocking; no daily limit.
- 中文 / English switching.
- Dependency-free Python local server and guarded Judge.

## 4.0.1 — Art Integration Pass

### Changed
- Replaced rectangular character portrait cards with scene-integrated character composition.
- Lyra Circuit now lives inside a layered mentor stage with background grid, halo, foreground tutor HUD, and pointer line.
- Patch is now a contextual support NPC that enters from the lower-right only when requested or after Judge feedback.
- Warden Null now triggers an interface-level Boss Mode on boss missions instead of remaining a static preview image.
- Added soft masking/cropping and shared UI lighting to reduce the "sticker on top of the interface" look.
- Kept all character effects static or event-triggered; no continuous particles or decorative animation were reintroduced.
- Removed unused portrait assets and kept only optimized stage assets.

### Preserved
- 50 cybersecurity labs + 5 bosses.
- Performance Mode ON by default.
- VS Code-style live syntax highlighting and key-pop input feedback.
- 中文 / English switching.
- Existing 4.x local progress keys and saved drafts.
