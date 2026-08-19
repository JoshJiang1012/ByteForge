"""ByteForge 7.0 AI Academy mission catalog loader.

The catalog prefers the compact gzip asset. GitHub/source archives that omit
binary assets can fall back to text-safe Base64 parts shipped beside it.
"""
from __future__ import annotations

import base64
import gzip
import io
import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_GZ = _HERE / "quests_data.json.gz"
_B64 = _HERE / "quests_data.json.gz.b64"

def _load_catalog():
    if _GZ.exists():
        with gzip.open(_GZ, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    if _B64.exists():
        encoded = _B64.read_text(encoding="ascii").strip()
    else:
        parts = sorted(_HERE.glob("quests_data.json.gz.b64.part*"))
        encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    if encoded:
        raw = base64.b64decode(encoded, validate=True)
        with gzip.open(io.BytesIO(raw), "rt", encoding="utf-8") as fh:
            return json.load(fh)
    raise FileNotFoundError(
        "ByteForge mission data is missing. Expected content/quests_data.json.gz "
        "or the text-safe quests_data.json.gz.b64(.part*) fallback. Re-download the complete ByteForge 7.0 release."
    )

QUESTS = _load_catalog()

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
