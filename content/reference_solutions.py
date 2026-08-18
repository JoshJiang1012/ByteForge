"""Reference solutions used only by ByteForge self-test.

The web API never exposes this mapping.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

_DATA = Path(__file__).with_name("solutions_data.json.gz")
with gzip.open(_DATA, "rt", encoding="utf-8") as _fh:
    _raw = json.load(_fh)
SOLUTIONS = {int(key): value for key, value in _raw.items()}
