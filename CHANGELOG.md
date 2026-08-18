# Changelog

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

## 5.0.0 — 100-Mission Cyber Range

### Added
- Replaced the old 55-mission catalog with a 100-mission sequential white-hat curriculum.
- Added 10 sectors with 10 missions each; missions 10, 20, ..., 100 are boss encounters.
- Added BLUE, RED-VIEW, and PURPLE mission perspectives using synthetic local data only.
- Added full course map in `COURSE.md`.
- Added 100 bundled reference solutions for release self-testing.

### Changed
- Reordered the curriculum around actual prerequisites: programming fundamentals → identity → Linux → Web → networking → secrets → detection → incident response → secure coding → purple-team integration.
- Updated release verification to require all 100 reference solutions to pass the Judge.

### Fixed
- Fixed editor caret/highlight drift by enforcing identical font metrics across textarea, syntax layer, `<code>`, token spans, and line numbers.
- Disabled font ligatures in the editor.
- Replaced the character-shaped typing pop with a non-text pulse so typing feedback cannot be mistaken for an extra character or space.
