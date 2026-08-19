# ByteForge 6.1 — Teaching Depth Update

## Major changes

- Every mission now explains syntax in six layers: definition, symbol breakdown, line walkthrough, execution order, common mistakes, and security relevance.
- Pass requirements are explicit: exact function contract, expected return type, behavior rules, visible checks, and all-test requirement.
- Added AST-rewritten **simulated imports**. Approved modules: `hashlib`, `json`, `ipaddress`, `math`. Arbitrary imports are still rejected.
- Missions 45, 53, and 61 now deliberately teach simulated imports in networking, hashing, and JSON detection contexts.
- The repeated “no import/file/network” sentence was removed from every syntax card and moved to one Environment Note.
- After clearing any mission, ByteForge reveals **3 worked examples + 3 extra practices**.
- Progress migrates from 5.0 localStorage keys.

## Safety

Simulated import syntax never grants general module loading. The AST transformer replaces approved imports with trusted, narrow virtual-module facades inside the local Judge. File and network access remain blocked.
