#!/usr/bin/env python3
"""ByteForge 7.0 AI Academy local cyber range server.

Dependency-free on purpose: Python 3 is the only runtime requirement.
The server binds to loopback only and provides a guarded local learning judge.
"""

from __future__ import annotations

import argparse
import ast
import json
import mimetypes
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib import request as urllib_request
from urllib import error as urllib_error

from content.quests import QUESTS, get_quest, public_quests

VERSION = "7.0.0"
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST = "127.0.0.1"
DEFAULT_PORTS = (3000, 3001, 3002, 8000, 8765)
MAX_BODY = 80_000
MAX_CODE = 20_000
MAX_REASONING = 6_000
TIME_LIMIT = 3.0
AI_TIMEOUT = float(os.environ.get("BYTEFORGE_AI_TIMEOUT", "12"))
AI_URL = os.environ.get("BYTEFORGE_AI_URL", "").strip()
AI_MODEL = os.environ.get("BYTEFORGE_AI_MODEL", "").strip()
AI_KEY = os.environ.get("BYTEFORGE_AI_KEY", "").strip()
AI_REMOTE_ENABLED = bool(AI_URL and AI_MODEL)

BLOCKED_CALLS = {
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
    "input",
    "breakpoint",
    "help",
    "exit",
    "quit",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "memoryview",
}
BLOCKED_NAMES = {"__builtins__", "__loader__", "__spec__", "__package__"}
BLOCKED_ATTRS = {
    "system",
    "popen",
    "spawn",
    "fork",
    "kill",
    "remove",
    "unlink",
    "rmdir",
    "chmod",
    "chown",
    "connect",
    "bind",
    "listen",
    "accept",
    "send",
    "sendall",
    "recv",
}


VIRTUAL_MODULES = {
    "hashlib": {"sha256"},
    "json": {"loads", "dumps"},
    "ipaddress": {"ip_address"},
    "math": {"ceil", "floor", "sqrt", "log2"},
}


class _VirtualImportTransformer(ast.NodeTransformer):
    """Rewrite approved import syntax to calls into ByteForge virtual modules."""

    def visit_Import(self, node):
        replacements = []
        for alias in node.names:
            if alias.name not in VIRTUAL_MODULES:
                raise ValueError(
                    f"Module {alias.name!r} is not available. ByteForge simulated imports: "
                    + ", ".join(sorted(VIRTUAL_MODULES))
                )
            target = alias.asname or alias.name
            replacements.append(
                ast.Assign(
                    targets=[ast.Name(id=target, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="_bf_virtual_import", ctx=ast.Load()),
                        args=[ast.Constant(alias.name)],
                        keywords=[],
                    ),
                )
            )
        return replacements

    def visit_ImportFrom(self, node):
        if node.level:
            raise ValueError("Relative imports are not available in the ByteForge simulation.")
        module = node.module or ""
        if module not in VIRTUAL_MODULES:
            raise ValueError(
                f"Module {module!r} is not available. ByteForge simulated imports: "
                + ", ".join(sorted(VIRTUAL_MODULES))
            )
        replacements = []
        for alias in node.names:
            if alias.name == "*":
                raise ValueError("Wildcard imports are disabled; import the exact simulated name you need.")
            if alias.name not in VIRTUAL_MODULES[module]:
                raise ValueError(
                    f"{module!r} does not expose {alias.name!r} in the ByteForge simulation. "
                    f"Available: {', '.join(sorted(VIRTUAL_MODULES[module]))}"
                )
            target = alias.asname or alias.name
            replacements.append(
                ast.Assign(
                    targets=[ast.Name(id=target, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="_bf_virtual_from", ctx=ast.Load()),
                        args=[ast.Constant(module), ast.Constant(alias.name)],
                        keywords=[],
                    ),
                )
            )
        return replacements


def _declared_imports(tree: ast.AST) -> set[str]:
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def validate_and_transform_user_code(code: str, required_imports: list[str] | None = None) -> tuple[str | None, str | None]:
    if not isinstance(code, str):
        return None, "Code must be text."
    if len(code) > MAX_CODE:
        return None, f"Code is too long for this training sandbox ({MAX_CODE} characters max)."
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        line = exc.lineno or "?"
        return None, f"SyntaxError on line {line}: {exc.msg}"

    nodes = list(ast.walk(tree))
    if len(nodes) > 6000:
        return None, "Code is too complex for this training sandbox."

    imports = _declared_imports(tree)
    for needed in required_imports or []:
        if needed not in imports:
            return None, f"This mission requires the simulated import {needed!r}. Add `import {needed}` (or an allowed from-import)."

    for node in nodes:
        if isinstance(node, ast.Name):
            if node.id in BLOCKED_NAMES or node.id.startswith("_bf_"):
                return None, f"The name {node.id!r} is disabled in the learning sandbox."
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__") or node.attr.endswith("__"):
                return None, "Dunder attribute access is disabled in the learning sandbox."
            if node.attr in BLOCKED_ATTRS:
                return None, f"The attribute {node.attr!r} is disabled in the learning sandbox."
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                return None, f"The builtin {node.func.id!r} is disabled in the learning sandbox."
            if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKED_ATTRS:
                return None, f"The call .{node.func.attr}(...) is disabled in the learning sandbox."

    try:
        tree = _VirtualImportTransformer().visit(tree)
        ast.fix_missing_locations(tree)
        transformed = ast.unparse(tree)
    except ValueError as exc:
        return None, str(exc)
    return transformed, None


def validate_user_code(code: str) -> str | None:
    """Compatibility helper used by diagnostics; mission Judge uses the transformer."""
    _transformed, error = validate_and_transform_user_code(code)
    return error

def _make_harness(user_code: str, tests: list[dict], marker: str) -> str:
    # Tests are trusted ByteForge content; user_code has already been validated and import-rewritten.
    payload = json.dumps(tests, ensure_ascii=False)
    return f'''# --- ByteForge runtime guard (not part of the mission) ---\ntry:\n    import resource as _bf_resource\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_CPU, (2, 2))\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_FSIZE, (2 * 1024 * 1024, 2 * 1024 * 1024))\nexcept Exception:\n    pass\n\n# --- ByteForge simulated imports (trusted runtime) ---\nimport hashlib as _bf_hashlib\nimport ipaddress as _bf_ipaddress\nimport json as _bf_json_core\nimport math as _bf_math\nclass _BFVirtualModule:\n    __slots__ = (\"_values\",)\n    def __init__(self, values):\n        self._values = values\n    def __getattr__(self, name):\n        try:\n            return self._values[name]\n        except KeyError:\n            raise AttributeError(name)\n_bf_virtual_modules = {{\n    \"hashlib\": _BFVirtualModule({{\"sha256\": _bf_hashlib.sha256}}),\n    \"json\": _BFVirtualModule({{\"loads\": _bf_json_core.loads, \"dumps\": _bf_json_core.dumps}}),\n    \"ipaddress\": _BFVirtualModule({{\"ip_address\": _bf_ipaddress.ip_address}}),\n    \"math\": _BFVirtualModule({{\"ceil\": _bf_math.ceil, \"floor\": _bf_math.floor, \"sqrt\": _bf_math.sqrt, \"log2\": _bf_math.log2}}),\n}}\ndef _bf_virtual_import(name):\n    return _bf_virtual_modules[name]\ndef _bf_virtual_from(module, name):\n    return getattr(_bf_virtual_modules[module], name)\n\n# --- Player code (approved imports already rewritten) ---\n{user_code}\n\n# --- ByteForge judge harness ---\nimport builtins as _bf_builtins\nimport json as _bf_json\n_bf_tests = _bf_json.loads({json.dumps(payload)})\n_bf_results = []\nfor _bf_test in _bf_tests:\n    try:\n        _bf_ns = dict(globals())\n        _bf_setup = _bf_test.get(\"setup\", \"\")\n        if _bf_setup:\n            _bf_builtins.exec(_bf_setup, _bf_ns, _bf_ns)\n        _bf_value = _bf_builtins.eval(_bf_test[\"expression\"], _bf_ns, _bf_ns)\n        _bf_actual_json = _bf_json.dumps(_bf_value, ensure_ascii=False, sort_keys=True, separators=(\",\", \":\"))\n        _bf_expected_json = _bf_json.dumps(_bf_test[\"expected\"], ensure_ascii=False, sort_keys=True, separators=(\",\", \":\"))\n        _bf_results.append({{\n            \"label\": _bf_test[\"label\"],\n            \"hidden\": bool(_bf_test.get(\"hidden\")),\n            \"passed\": _bf_actual_json == _bf_expected_json,\n            \"actual\": _bf_actual_json,\n            \"expected\": _bf_expected_json,\n        }})\n    except BaseException as _bf_error:\n        _bf_results.append({{\n            \"label\": _bf_test[\"label\"],\n            \"hidden\": bool(_bf_test.get(\"hidden\")),\n            \"passed\": False,\n            \"error\": type(_bf_error).__name__ + \": \" + str(_bf_error),\n        }})\n_bf_builtins.print({marker!r} + _bf_json.dumps(_bf_results, ensure_ascii=False))\n'''

def run_judge(quest: dict, code: str) -> dict:
    transformed, validation = validate_and_transform_user_code(code, quest.get("required_imports", []))
    if validation:
        return {"passed": False, "output": "", "tests": [], "error": validation}

    marker = "__BYTEFORGE_" + uuid.uuid4().hex + "__"
    script = _make_harness(transformed or "", quest["tests"], marker)

    with tempfile.TemporaryDirectory(prefix="byteforge-") as tmp:
        path = Path(tmp) / "mission.py"
        path.write_text(script, encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-S", str(path)],
                cwd=tmp,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIME_LIMIT,
                env=env,
                creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0),
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "",
                "tests": [],
                "error": "Execution timed out. Check for an infinite loop or runaway recursion.",
            }
        except OSError as exc:
            return {
                "passed": False,
                "output": "",
                "tests": [],
                "error": f"Could not start Python judge: {exc}",
            }

    stdout = completed.stdout[-80_000:]
    stderr = completed.stderr[-20_000:].strip()
    marker_index = stdout.rfind(marker)
    user_output = stdout[:marker_index].rstrip() if marker_index >= 0 else stdout.rstrip()

    if marker_index < 0:
        detail = stderr or "Program ended before ByteForge could run the tests."
        return {"passed": False, "output": user_output, "tests": [], "error": detail}

    try:
        raw_tests = json.loads(stdout[marker_index + len(marker):].strip())
    except json.JSONDecodeError:
        return {
            "passed": False,
            "output": user_output,
            "tests": [],
            "error": "Judge output could not be decoded.",
        }

    display_tests = []
    for item in raw_tests:
        hidden = bool(item.get("hidden"))
        clean = {
            "label": "Hidden test" if hidden else item.get("label", "Test"),
            "hidden": hidden,
            "passed": bool(item.get("passed")),
        }
        if item.get("error"):
            clean["error"] = item["error"]
        elif not hidden:
            clean["actual"] = item.get("actual")
            clean["expected"] = item.get("expected")
        display_tests.append(clean)

    passed = len(raw_tests) == len(quest["tests"]) and all(t.get("passed") for t in raw_tests)
    return {
        "passed": bool(passed),
        "output": user_output,
        "tests": display_tests,
        "error": stderr or None,
    }



def _localized_ai_meta(quest: dict, language: str = "en") -> dict:
    base = dict(quest.get("ai_grading") or {})
    localized = ((quest.get("i18n") or {}).get(language) or {}).get("ai_grading") or {}
    base.update(localized)
    return base


def ai_status_payload() -> dict:
    return {
        "enabled": True,
        "mode": "connected" if AI_REMOTE_ENABLED else "local-rubric",
        "remoteConfigured": AI_REMOTE_ENABLED,
        "model": AI_MODEL if AI_REMOTE_ENABLED else "ByteForge Local Rubric",
        "tutor": "connected" if AI_REMOTE_ENABLED else "guided-fallback",
        "grading": "connected-llm" if AI_REMOTE_ENABLED else "deterministic-rubric",
        "privacy": "API keys stay server-side; hidden tests are never sent to AI.",
    }


def _contains_any(text: str, terms: list[str]) -> int:
    low = text.casefold()
    return sum(1 for term in terms if term and term.casefold() in low)


def local_rubric_review(quest: dict, reasoning: str, language: str = "en") -> dict:
    meta = _localized_ai_meta(quest, language)
    reasoning = (reasoning or "").strip()[:MAX_REASONING]
    keywords = list(meta.get("keywords") or [])
    security_terms = (
        ["資安", "安全", "風險", "驗證", "偵測", "封鎖", "允許", "政策", "權限", "訊號", "可疑", "防禦", "攻擊", "事件", "分類"]
        if language == "zh-Hant"
        else ["security", "risk", "validate", "validation", "detect", "detection", "block", "allow", "policy", "access", "signal", "suspicious", "defense", "defensive", "attack", "incident", "classification"]
    )
    edge_terms = (
        ["邊界", "門檻", "誤報", "例外", "空值", "空字串", "大小寫", "臨界", "極端"]
        if language == "zh-Hant"
        else ["edge", "boundary", "threshold", "false positive", "empty", "case", "casing", "exception", "limit"]
    )
    key_hits = _contains_any(reasoning, keywords)
    sec_hits = _contains_any(reasoning, security_terms)
    edge_hits = _contains_any(reasoning, edge_terms)
    char_len = len(reasoning)
    sentence_marks = sum(reasoning.count(x) for x in (".", "!", "?", "。", "！", "？", ";", "；"))

    correctness = 10 if key_hits >= 2 else 7 if key_hits == 1 else 3 if char_len >= 80 else 0
    security = 10 if sec_hits >= 2 else 6 if sec_hits == 1 else 2 if char_len >= 100 else 0
    edge = 5 if edge_hits >= 1 else 0
    clarity = 5 if char_len >= 70 and sentence_marks >= 1 else 3 if char_len >= 40 else 1 if char_len >= 20 else 0
    criteria_scores = {"correctness": correctness, "security": security, "edge": edge, "clarity": clarity}
    feedback = {
        "correctness": ("有指出這關真正使用的規則／訊號。" if correctness >= 7 else "再明確說出程式實際檢查的規則或訊號。") if language == "zh-Hant" else ("You identified the rule or signal used by the solution." if correctness >= 7 else "State the actual rule or signal your code evaluates."),
        "security": ("有把規則連到資安風險或防禦決策。" if security >= 6 else "補上：這個判斷為什麼對防禦、風險或存取控制重要？") if language == "zh-Hant" else ("You connected the rule to a security decision or risk." if security >= 6 else "Explain why this rule matters to defense, risk, or access control."),
        "edge": ("有考慮邊界／誤報。" if edge else "再補一個邊界值、例外或誤報情境。") if language == "zh-Hant" else ("You considered an edge case or false positive." if edge else "Add one boundary, exception, or false-positive consideration."),
        "clarity": ("說明具有完整句子與可讀結構。" if clarity >= 3 else "請用 2～5 句完整句子，不要只列關鍵字。") if language == "zh-Hant" else ("The explanation is readable and sentence-based." if clarity >= 3 else "Use 2–5 complete sentences instead of isolated keywords."),
    }
    criteria = []
    for item in meta.get("criteria") or []:
        key=item.get("key")
        max_points=int(item.get("points",0))
        score=min(max_points, int(criteria_scores.get(key,0)))
        criteria.append({"key":key,"label":item.get("label",key),"score":score,"max":max_points,"feedback":feedback.get(key,"")})
    score=sum(x["score"] for x in criteria)
    minimum=int(meta.get("min_ai_score",15))
    if language == "zh-Hant":
        summary = f"AI 推理分數 {score}/30。" + (" 已達通關最低要求。" if score >= minimum else " 還沒達最低要求，先依扣分項目補強說明。")
    else:
        summary = f"AI reasoning score {score}/30." + (" Minimum reasoning requirement met." if score >= minimum else " Below the minimum; revise the deducted rubric areas.")
    return {"mode":"local-rubric","score":score,"max":30,"passed":score>=minimum,"minimum":minimum,"criteria":criteria,"summary":summary,"fallback":not AI_REMOTE_ENABLED}


def _extract_ai_text(payload: dict) -> str:
    if isinstance(payload.get("text"), str):
        return payload["text"]
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    try:
        return payload["choices"][0]["message"]["content"]
    except Exception:
        return ""


def _parse_json_from_text(text: str) -> dict:
    text=(text or "").strip()
    if text.startswith("```"):
        text=re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I|re.S).strip()
    try:
        value=json.loads(text)
        return value if isinstance(value,dict) else {}
    except Exception:
        start=text.find("{"); end=text.rfind("}")
        if start>=0 and end>start:
            try:
                value=json.loads(text[start:end+1]); return value if isinstance(value,dict) else {}
            except Exception:
                return {}
        return {}


def call_connected_ai(system_prompt: str, user_prompt: str) -> str:
    if not AI_REMOTE_ENABLED:
        raise RuntimeError("No connected AI endpoint configured.")
    payload={"model":AI_MODEL,"messages":[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],"temperature":0.1}
    headers={"Content-Type":"application/json","User-Agent":f"ByteForge/{VERSION}"}
    if AI_KEY:
        headers["Authorization"]="Bearer "+AI_KEY
    req=urllib_request.Request(AI_URL,data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),headers=headers,method="POST")
    try:
        with urllib_request.urlopen(req,timeout=AI_TIMEOUT) as resp:
            raw=resp.read(1_000_000).decode("utf-8","replace")
    except urllib_error.HTTPError as exc:
        detail=exc.read(2000).decode("utf-8","replace") if hasattr(exc,"read") else str(exc)
        raise RuntimeError(f"AI endpoint HTTP {exc.code}: {detail[:500]}") from exc
    except Exception as exc:
        raise RuntimeError(f"AI endpoint unavailable: {exc}") from exc
    try:
        obj=json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI endpoint returned non-JSON data.") from exc
    text=_extract_ai_text(obj)
    if not text:
        raise RuntimeError("AI endpoint response did not contain message text.")
    return text[:20_000]


def connected_rubric_review(quest: dict, code: str, reasoning: str, language: str = "en") -> dict:
    meta=_localized_ai_meta(quest,language)
    criteria=meta.get("criteria") or []
    criteria_text="\n".join(f"- {x['key']}: 0-{x['points']} — {x.get('description','')}" for x in criteria)
    system=(
        "You are ByteForge AI Judge, grading a defensive cybersecurity learning exercise. "
        "Grade only the learner's explanation, never reveal or infer hidden tests, and never provide instructions for attacking real systems. "
        "Return strict JSON with keys criteria (array of {key,score,feedback}) and summary. Scores must stay within each rubric maximum."
    )
    user=f"""Mission {quest['id']}: {quest.get('title','')}
Core concept: {quest.get('concept','')}
Public goal: {quest.get('brief','')}
Public objectives: {json.dumps(quest.get('objectives',[]),ensure_ascii=False)}
Rubric:
{criteria_text}
Learner code:
```python
{code[:MAX_CODE]}
```
Learner explanation:
{reasoning[:MAX_REASONING]}
Language for feedback: {language}
Return JSON only."""
    raw=call_connected_ai(system,user)
    parsed=_parse_json_from_text(raw)
    if not parsed:
        raise RuntimeError("AI Judge returned an invalid rubric object.")
    by_key={x.get("key"):x for x in parsed.get("criteria",[]) if isinstance(x,dict)}
    out=[]
    for item in criteria:
        key=item.get("key"); max_points=int(item.get("points",0)); got=by_key.get(key,{})
        try: score=int(round(float(got.get("score",0))))
        except Exception: score=0
        score=max(0,min(max_points,score))
        out.append({"key":key,"label":item.get("label",key),"score":score,"max":max_points,"feedback":str(got.get("feedback","")).strip()[:600]})
    score=sum(x["score"] for x in out); minimum=int(meta.get("min_ai_score",15))
    return {"mode":"connected","score":score,"max":30,"passed":score>=minimum,"minimum":minimum,"criteria":out,"summary":str(parsed.get("summary","")).strip()[:900] or f"AI reasoning score {score}/30.","fallback":False}


def grade_reasoning(quest: dict, code: str, reasoning: str, language: str = "en") -> dict:
    if len(reasoning or "") > MAX_REASONING:
        reasoning=(reasoning or "")[:MAX_REASONING]
    if AI_REMOTE_ENABLED:
        try:
            return connected_rubric_review(quest,code,reasoning,language)
        except Exception as exc:
            result=local_rubric_review(quest,reasoning,language)
            result["notice"]=("Connected AI failed; local rubric fallback was used: " if language!="zh-Hant" else "連線 AI 無法使用，已改用本機 rubric：")+str(exc)[:500]
            return result
    return local_rubric_review(quest,reasoning,language)


def local_tutor_response(quest: dict, code: str, question: str, language: str = "en", role: str = "lyra", judge_error: str = "") -> str:
    localized=((quest.get("i18n") or {}).get(language) or {})
    syntax=localized.get("syntax") or quest.get("syntax") or {}
    hints=localized.get("hints") or quest.get("hints") or []
    _transformed, validation=validate_and_transform_user_code(code,quest.get("required_imports",[]))
    q=(question or "").strip()[:1500]
    q_low=q.casefold()

    # Offline tutor remains deterministic but tries to answer the exact syntax token
    # the learner asked about before falling back to the generic mission guide.
    matched=[]
    for item in syntax.get("breakdown") or []:
        token=str(item.get("code","")).strip("` ")
        bare=re.sub(r"[^a-zA-Z0-9_]+", " ", token).strip().casefold()
        candidates=[x for x in {token.casefold(), bare, *(bare.split())} if len(x)>=2]
        if q and any(x in q_low for x in candidates):
            matched.append((token,str(item.get("meaning","")).strip()))
    if matched:
        # If the learner names multiple operators (for example lower() + endswith()),
        # explain the relationship instead of returning the first token only.
        def mention_pos(pair):
            token=pair[0].casefold()
            bare=re.sub(r"[^a-zA-Z0-9_]+", "", token)
            positions=[p for p in (q_low.find(token), q_low.find(bare)) if p >= 0]
            return min(positions) if positions else 9999
        matched=sorted(matched,key=mention_pos)[:2]
        if language=="zh-Hant":
            pieces="；".join(f"`{token}`：{meaning}" for token,meaning in matched)
            return f"Lyra：你問到的是兩個連在一起的步驟。{pieces}。Python 會由左往右先得到前一個方法的結果，再把那個結果交給下一個方法；這一關可對照 `{syntax.get('example','')}` 逐段追蹤。"
        pieces="; ".join(f"`{token}`: {meaning}" for token,meaning in matched)
        return f"Lyra: you are asking about chained steps. {pieces}. Python evaluates the chain from left to right, so the result of the earlier method becomes the value used by the next one. Trace that flow inside `{syntax.get('example','')}`."

    if language=="zh-Hant":
        if validation:
            return f"先處理這個問題：{validation}。先不要改整個解法，只修正錯誤指出的語法／沙盒條件，再重新執行。"
        if judge_error:
            return "Patch 判斷：程式已經進到 Judge。先比較第一個失敗測試的預期與實際值，鎖定是哪一條規則造成差異；再檢查邊界值，而不是整段重寫。"
        if q and ("為什麼" in q or "怎麼" in q or "意思" in q):
            return f"Lyra：這關的核心是「{syntax.get('title',quest.get('concept',''))}」。{syntax.get('definition','')} 資安上它的用途是：{syntax.get('why',quest.get('brief',''))}"
        if "pass" in code and hints:
            return f"Lyra：先完成第一個可執行步驟。{hints[0]} 我不會直接貼完整答案；你可以先把這一步寫出來，再執行一次。"
        return f"Lyra：這關的核心是「{syntax.get('title',quest.get('concept',''))}」。{syntax.get('definition','')} 先對照任務規格與目前程式，找出你還沒完成的第一個 objective。"
    if validation:
        return f"Fix this first: {validation}. Do not rewrite the whole solution; correct the reported syntax or sandbox condition, then run again."
    if judge_error:
        return "Patch: your code reached the Judge. Compare the first failing expected/actual pair, identify which rule can produce that difference, then inspect a boundary case before rewriting anything."
    if q and any(x in q_low for x in ("why", "how", "what does", "meaning")):
        return f"Lyra: the core idea is “{syntax.get('title',quest.get('concept',''))}”. {syntax.get('definition','')} Its security purpose here is: {syntax.get('why',quest.get('brief',''))}"
    if "pass" in code and hints:
        return f"Lyra: start with the first executable step. {hints[0]} I will not paste the full solution; implement that step and run once."
    return f"Lyra: the core idea is “{syntax.get('title',quest.get('concept',''))}”. {syntax.get('definition','')} Compare the mission contract with your current code and identify the first unfinished objective."


def ai_tutor_reply(quest: dict, code: str, question: str, language: str = "en", role: str = "lyra", judge_error: str = "") -> dict:
    fallback=local_tutor_response(quest,code,question,language,role,judge_error)
    if not AI_REMOTE_ENABLED:
        return {"mode":"guided-fallback","reply":fallback}
    public={k:v for k,v in quest.items() if k not in {"tests","i18n","post_clear"}}
    public.pop("starter",None)
    persona=("You are Lyra Circuit, a patient cybersecurity coding teacher." if role!="patch" else "You are Patch, a concise debugging support engineer.")
    system=(persona+" This is a local defensive learning range. Never reveal hidden tests or full final solution code. "
            "Use Socratic guidance: identify the next concept, explain one error or edge case, and ask the learner to make the next edit. "
            "Do not provide instructions for attacking real systems. Keep the answer under 180 words.")
    user=f"""Mission public context: {json.dumps(public,ensure_ascii=False)[:9000]}
Learner code:
```python
{code[:MAX_CODE]}
```
Question: {question[:1500]}
Known Judge error (public/safe): {judge_error[:1000]}
Reply language: {language}"""
    try:
        text=call_connected_ai(system,user).strip()
        return {"mode":"connected","reply":text[:2500]}
    except Exception as exc:
        return {"mode":"guided-fallback","reply":fallback,"notice":str(exc)[:500]}

def run_self_test(verbose: bool = True) -> bool:
    try:
        from content.reference_solutions import SOLUTIONS
    except Exception as exc:
        if verbose:
            print(f"[FAIL] Could not load reference solutions: {exc}")
        return False

    ok = True
    started = time.time()
    for quest in QUESTS:
        result = run_judge(quest, SOLUTIONS[quest["id"]])
        if not result["passed"]:
            ok = False
            if verbose:
                print(f"[FAIL] Quest {quest['id']:02d} {quest['title']}: {result.get('error') or result['tests']}")
        elif verbose:
            print(f"[ OK ] Quest {quest['id']:02d} {quest['title']}")
    # Verify that virtual imports work and arbitrary imports stay blocked.
    virtual_probe, virtual_error = validate_and_transform_user_code("import hashlib\ndef f(x):\n    return hashlib.sha256(x.encode(\"utf-8\")).hexdigest()")
    if virtual_error or "_bf_virtual_import" not in (virtual_probe or ""):
        ok = False
        if verbose:
            print(f"[FAIL] Simulated import transformer: {virtual_error or virtual_probe}")
    _blocked, blocked_error = validate_and_transform_user_code("import os\ndef f():\n    return 1")
    if not blocked_error:
        ok = False
        if verbose:
            print("[FAIL] Arbitrary import was not blocked")
    hybrid = [q for q in QUESTS if (q.get("ai_grading") or {}).get("required")]
    if len(hybrid) != 30:
        ok = False
        if verbose:
            print(f"[FAIL] Expected 30 hybrid AI-graded missions, got {len(hybrid)}")
    if hybrid:
        good = local_rubric_review(hybrid[0], "This rule detects a suspicious security signal and blocks risky input. The threshold is defensive, but a boundary value or false positive should be reviewed.", "en")
        weak = local_rubric_review(hybrid[0], "ok", "en")
        if good.get("score",0) < 15 or weak.get("score",99) >= 15:
            ok = False
            if verbose:
                print(f"[FAIL] Local AI rubric calibration: good={good.get('score')} weak={weak.get('score')}")
    if verbose:
        elapsed = time.time() - started
        print(f"\nSelf-test: {'PASS' if ok else 'FAIL'} — {len(QUESTS)} quests in {elapsed:.2f}s")
    return ok


class ByteForgeHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(BaseHTTPRequestHandler):
    server_version = f"ByteForge/{VERSION}"

    def log_message(self, fmt: str, *args):
        # Keep the launcher readable; only show non-trivial errors.
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)

    def _send_json(self, payload, status=HTTPStatus.OK):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def _send_file(self, path: Path):
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        raw = path.read_bytes()
        mime, _ = mimetypes.guess_type(str(path))
        if path.suffix == ".js":
            mime = "text/javascript"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", (mime or "application/octet-stream") + ("; charset=utf-8" if (mime or "").startswith(("text/", "application/javascript")) else ""))
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/api/health", "/health"):
            self._send_json({"ok": True, "version": VERSION, "quests": len(QUESTS), "python": sys.version.split()[0]})
            return
        if path == "/api/quests":
            self._send_json({"version": VERSION, "quests": public_quests()})
            return
        if path == "/api/version":
            self._send_json({"version": VERSION})
            return
        if path == "/api/ai/status":
            self._send_json(ai_status_payload())
            return
        if path == "/":
            self._send_file(STATIC / "index.html")
            return

        # Static-only routing with traversal protection.
        candidate = (STATIC / path.lstrip("/")).resolve()
        try:
            candidate.relative_to(STATIC.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        self._send_file(candidate)

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            return None, "Invalid request size."
        try:
            return json.loads(self.rfile.read(length).decode("utf-8")), None
        except Exception:
            return None, "Invalid JSON request."

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in ("/api/run", "/api/ai/tutor"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body, body_error = self._read_json_body()
        if body_error:
            self._send_json({"error": body_error}, HTTPStatus.BAD_REQUEST)
            return
        quest_id = body.get("questId")
        try:
            quest_id = int(quest_id)
        except (TypeError, ValueError):
            quest_id = -1
        quest = get_quest(quest_id)
        if quest is None:
            self._send_json({"error": "Unknown quest."}, HTTPStatus.NOT_FOUND)
            return
        code = body.get("code", "")
        language = "zh-Hant" if body.get("language") == "zh-Hant" else "en"

        if parsed.path == "/api/ai/tutor":
            question = str(body.get("question", ""))[:1500]
            role = "patch" if body.get("role") == "patch" else "lyra"
            judge_error = str(body.get("judgeError", ""))[:1000]
            self._send_json(ai_tutor_reply(quest, code, question, language, role, judge_error))
            return

        result = run_judge(quest, code)
        result["judgePassed"] = bool(result.get("passed"))
        meta = _localized_ai_meta(quest, language)
        if meta.get("required"):
            judge_points = int(meta.get("judge_points", 70))
            ai_points = int(meta.get("ai_points", 30))
            reasoning = str(body.get("reasoning", ""))[:MAX_REASONING]
            if result["judgePassed"]:
                ai = grade_reasoning(quest, code, reasoning, language)
                total = judge_points + int(ai.get("score", 0))
                final_pass = bool(ai.get("passed")) and total >= int(meta.get("pass_score", 85))
            else:
                ai = {"mode":"skipped","score":0,"max":ai_points,"passed":False,"minimum":int(meta.get("min_ai_score",15)),"criteria":[],"summary":"AI review runs after deterministic tests pass."}
                total = 0
                final_pass = False
            result["aiReview"] = ai
            result["grading"] = {"mode":"hybrid","judgeScore":judge_points if result["judgePassed"] else 0,"judgeMax":judge_points,"aiScore":int(ai.get("score",0)),"aiMax":ai_points,"totalScore":total,"passScore":int(meta.get("pass_score",85)),"passed":final_pass}
            result["passed"] = final_pass
        else:
            result["grading"] = {"mode":"deterministic","judgeScore":100 if result["judgePassed"] else 0,"judgeMax":100,"aiScore":0,"aiMax":0,"totalScore":100 if result["judgePassed"] else 0,"passScore":100,"passed":result["judgePassed"]}
        self._send_json(result)


def make_server(port: int | None = None):
    candidates = [port] if port is not None else list(DEFAULT_PORTS) + [0]
    last_error = None
    for candidate in candidates:
        try:
            return ByteForgeHTTPServer((HOST, candidate), Handler)
        except OSError as exc:
            last_error = exc
            continue
    raise OSError(f"Could not bind a local port: {last_error}")


def main():
    parser = argparse.ArgumentParser(description="Run ByteForge 7.0 AI Academy locally.")
    parser.add_argument("--port", type=int, default=None, help="Preferred local port (default: try 3000 then fallbacks).")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically.")
    parser.add_argument("--self-test", action="store_true", help="Run all 100 reference solutions and exit.")
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(0 if run_self_test(verbose=True) else 1)

    if sys.version_info < (3, 10):
        print("ByteForge 7.0 requires Python 3.10 or newer.")
        raise SystemExit(2)

    try:
        server = make_server(args.port)
    except OSError as exc:
        print(f"\n[ERROR] {exc}")
        print("Close any program using port 3000, or run: python server.py --port 8000")
        raise SystemExit(1)

    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}"

    print("\n" + "=" * 60)
    print(" BYTEFORGE 7.0 — AI ACADEMY")
    print("=" * 60)
    print(f" [OK] Python {sys.version.split()[0]}")
    print(f" [OK] {len(QUESTS)} missions loaded")
    print(f" [OK] Local judge ready ({TIME_LIMIT:.0f}s limit)")
    print(f" [OK] Server bound to loopback only")
    print(f" [OK] AI mode: {ai_status_payload()['mode']} ({ai_status_payload()['model']})")
    if actual_port != 3000:
        print(f" [INFO] Port 3000 was unavailable; using {actual_port} instead.")
    print(f"\n OPEN: {url}")
    print(" Keep this terminal window open while playing.")
    print(" Press Ctrl+C to stop ByteForge.\n")

    if not args.no_browser:
        threading.Timer(0.55, lambda: webbrowser.open(url, new=2)).start()

    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping ByteForge...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
