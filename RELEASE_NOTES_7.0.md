# ByteForge 7.0 — AI Academy

ByteForge 7.0 adds AI-assisted teaching and hybrid mission grading without giving up the dependency-free local Judge.

## AI grading

- 70 BLUE missions remain deterministic: passing all tests is enough.
- 30 PURPLE / RED-VIEW missions use **Hybrid Grade**:
  - deterministic Judge: 70 points
  - security reasoning review: 30 points
  - mission clear requires all code tests plus a total score of at least 85/100
- The reasoning rubric grades correctness, security reasoning, edge cases / false positives, and clarity.
- Hidden tests are never sent to the AI layer.

## AI modes

ByteForge always remains playable offline.

- **LOCAL RUBRIC** — zero-network deterministic reasoning fallback. This is not presented as an LLM; it keeps the course playable when no model is connected.
- **CONNECTED** — optional Chat-Completions-compatible LLM endpoint configured only on the local Python server.
- If a connected model fails, grading automatically falls back to the local rubric rather than blocking the campaign.

## Lyra AI + Patch

- Lyra can inspect the current public mission context and learner code, then guide the *next step* without pasting a full final solution.
- Patch can use the same AI layer for contextual debugging after Judge failures.
- Tutor prompts explicitly exclude hidden tests and live-target offensive instructions.

## Privacy

Connected AI is opt-in. API URL, model name, and API key are read from server-side environment variables; the browser never receives the key.

```text
BYTEFORGE_AI_URL
BYTEFORGE_AI_MODEL
BYTEFORGE_AI_KEY       # optional
BYTEFORGE_AI_TIMEOUT   # optional, default 12 seconds
```

`BYTEFORGE_AI_URL` should point to a Chat-Completions-compatible POST endpoint. If it is not configured, ByteForge uses the local rubric and guided tutor fallback.

## Preserved from 6.4

- 100 missions / 10 bosses
- bilingual Traditional Chinese / English UI
- simulated import labs
- detailed syntax tutor
- 3 worked examples + 3 extra exercises after each clear
- 6.4 readability layout
- zero npm / zero pip runtime
