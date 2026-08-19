# ByteForge 7.0 Characters

The character art-integration system introduced in ByteForge 4.0.1 changes the character system from **portrait cards** to **scene-integrated roles**. Character art is composited into the interface with crop, mask, shared lighting, foreground HUD layers, and state-driven presence instead of being shown as a rectangular poster.

## Lyra Circuit — Teacher
Role: live tutor, syntax instructor, learning guide.

Lyra now occupies the mentor stage beside the code workspace. Her art sits between background grid/halo layers and foreground syntax HUD panels, so her silhouette and pointer visually connect to the lesson instead of appearing inside an image card.

Runtime asset: `static/assets/characters/lyra-stage.webp`

## Patch — NPC Support Engineer
Role: debugging support and recovery guidance.

Patch no longer consumes a permanent right-column card. A compact launcher stays available, while the full support scene appears only when the learner opens it or when the Judge returns a result. His dialogue changes for syntax errors, sandbox blocks, logic failures, and successful clears.

Runtime assets:
- `static/assets/characters/patch-thumb.webp`
- `static/assets/characters/patch-stage.webp`

## Warden Null — Boss
Role: recurring antagonist and checkpoint presence.

Warden remains visible as a quiet boss radar between normal missions. During boss missions, ByteForge enters **Boss Mode**: the UI shifts toward violet/red protocol lighting, the teacher stage recedes, and Warden becomes a large interface-level presence instead of a banner card.

Runtime asset: `static/assets/characters/warden-stage.webp`


## 7.0 AI roles

- **Lyra Circuit** can use the optional connected AI endpoint to explain the current concept and guide the learner toward the next step. Without a connected model she uses the local guided fallback.
- **Patch** can use the same endpoint for debugging-focused feedback based on the current code and latest Judge error.
- **Warden Null** remains a narrative/Boss presentation layer and is never used as an unrestricted model persona.
