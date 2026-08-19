# ByteForge 7.0 Performance Notes

ByteForge remains dependency-free and performance-first.

- No Node/npm runtime.
- No pip packages.
- Static HTML/CSS/JavaScript plus Python's built-in HTTP server.
- Syntax highlighting updates are batched with `requestAnimationFrame`.
- Draft writes are debounced rather than written on every keystroke.
- Performance Mode disables expensive blur-heavy effects and reduces transition cost.
- Character art is pre-resized and WebP-compressed.
- 6.0's larger tutorial content is compressed in `quests_data.json.gz` and expanded only by the local Python process.
- Detailed tutor sections use native `<details>` elements, so only the learner-opened sections occupy attention and interaction cost.

The editor keeps the 5.0 font-metric lock: textarea, syntax layer, tokens, and line numbers use identical font size, line height, spacing, tab size, and disabled ligatures to avoid caret drift.


## AI requests

Connected AI calls run only when the learner explicitly requests tutor feedback or submits a Hybrid AI grading mission. They are not background polling loops. Local Rubric mode performs no network request.

## 7.0 AI performance

AI requests are event-driven only: grading runs after deterministic tests on Hybrid missions, and tutor requests run only when the learner presses the AI button. There are no continuous AI polling loops. Connected AI calls use a bounded server-side timeout (`BYTEFORGE_AI_TIMEOUT`, default 12 seconds) and automatically fall back locally on failure.
