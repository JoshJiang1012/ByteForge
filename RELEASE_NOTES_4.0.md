# ByteForge 4.0 Release Notes

ByteForge 4.0 is the first **Cyber Academy** release. The campaign remains 50 white-hat labs plus five bosses, but the interface is rebuilt around three priorities: **understand the mission, learn the exact syntax, and keep the app smooth**.

## New learning loop

1. Read the mission goal.
2. Read the Mission Contract: target function, Judge count, and core concept.
3. Check visible examples.
4. Learn the mission-specific syntax from Lyra Circuit.
5. Write code in the editor.
6. Run the local Judge.
7. If it fails, Patch explains the next diagnostic step.
8. Reveal Direction → Structure → Near Solution hints only when needed.
9. Pass and unlock the next mission immediately.

## Performance work

4.0 removes always-running visual effects from 2.1. Performance Mode also disables backdrop blur. Editor syntax highlighting is frame-batched and draft saving is debounced. Character art is resized to small WebP runtime assets.

## Characters

- **Lyra Circuit** — teacher and pedagogical voice.
- **Patch** — support engineer NPC and debugging guide.
- **Warden Null** — recurring antagonist behind sector boss protocols.

## 4.0.1 — Characters now live inside ByteForge

The first 4.0 build still presented character art too much like posters placed inside cards. 4.0.1 rebuilds that integration layer:

- **Lyra Circuit** stands inside a mentor stage, behind some HUD layers and in front of others.
- **Patch** appears contextually as a support scene rather than occupying a permanent card.
- **Warden Null** takes over the visual hierarchy during boss missions through a dedicated Boss Mode.
- Character images use cropped stage assets and edge masking so their original poster boundaries do not define the UI layout.
- The redesign stays performance-first: static compositing replaces continuous animation.
