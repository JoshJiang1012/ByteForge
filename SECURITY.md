# Security Policy

## ByteForge 5.0 training boundary

ByteForge is a **local synthetic cybersecurity learning range**. Missions teach defensive reasoning and secure coding against data supplied by the game.

The bundled server binds to `127.0.0.1` and the learning Judge rejects imports and several capabilities that are unnecessary for mission solutions. It also runs player submissions in an isolated Python invocation with a short execution timeout and resource limits where the operating system supports them.

ByteForge's Judge is a learning guardrail, **not a hardened sandbox for arbitrary hostile code**. Do not expose the local Judge as an internet service and do not use it to execute untrusted submissions from other people.

## Scope

ByteForge missions must remain synthetic or authorized training exercises. Contributions should not add real-target scanning, credential theft, persistence, malware delivery, destructive behavior, or evasion features.

## Reporting a problem

If you discover a bug that weakens the local training boundary, avoid publishing a working bypass immediately. Report the issue privately to the project maintainer when a private reporting channel is available.
