"""ByteForge 7.0 AI Academy mission catalog loader.

The 100-mission catalog is stored as compressed JSON to keep the runtime
dependency-free while avoiding one enormous generated Python literal.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

_DATA = Path(__file__).with_name("quests_data.json.gz")
with gzip.open(_DATA, "rt", encoding="utf-8") as _fh:
    QUESTS = json.load(_fh)

assert len(QUESTS) == 100
assert sum(1 for q in QUESTS if q["boss"]) == 10
assert sum(1 for q in QUESTS if not q["boss"]) == 90
assert [q["id"] for q in QUESTS] == list(range(1, 101))

def get_quest(quest_id: int):
    for quest in QUESTS:
        if quest["id"] == quest_id:
            return quest
    return None

def public_quests():
    """Return learner-safe quest data without exposing hidden test expressions."""
    result = []
    for quest in QUESTS:
        item = {k: v for k, v in quest.items() if k != "tests"}
        item["test_count"] = len(quest["tests"])
        item["hidden_test_count"] = sum(1 for t in quest["tests"] if t.get("hidden"))
        item["visible_tests"] = [
            {"label": t.get("label", "Test"), "expression": t["expression"], "expected": t["expected"]}
            for t in quest["tests"] if not t.get("hidden")
        ]
        first_line = next((line.strip() for line in quest.get("starter", "").splitlines() if line.strip().startswith("def ")), "")
        item["function_signature"] = first_line[:-1] if first_line.endswith(":") else first_line
        result.append(item)
    return result
