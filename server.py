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
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from content.quests import QUESTS, get_quest, public_quests

VERSION = "7.0.0"
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST = "127.0.0.1"
DEFAULT_PORTS = (3000, 3001, 3002, 8000, 8765)
MAX_BODY = 120_000
MAX_CODE = 20_000
TIME_LIMIT = 3.0

# ByteForge 7.0 supports a deliberately small simulated import surface. Player
# code uses normal Python import syntax, then AST rewriting binds these names to
# safe in-memory facades. No arbitrary filesystem/network/system module import.
SIM_IMPORTS = {
    "hashlib": {"sha256"},
    "json": {"loads", "dumps"},
    "ipaddress": {"ip_address"},
    "math": {"ceil", "floor", "sqrt", "log2"},
}

BLOCKED_CALLS = {
    "open", "exec", "eval", "compile", "__import__", "input", "breakpoint",
    "help", "exit", "quit", "globals", "locals", "vars", "dir", "getattr",
    "setattr", "delattr", "memoryview",
}
BLOCKED_NAMES = {"__builtins__", "__loader__", "__spec__", "__package__"}
BLOCKED_ATTRS = {
    "system", "popen", "spawn", "fork", "kill", "remove", "unlink", "rmdir",
    "chmod", "chown", "connect", "bind", "listen", "accept", "send", "sendall", "recv",
}

class SimImportRewriter(ast.NodeTransformer):
    def __init__(self):
        self.error: str | None = None

    def visit_Import(self, node: ast.Import):
        assigns = []
        for alias in node.names:
            if alias.name not in SIM_IMPORTS:
                self.error = f"Import {alias.name!r} is not available in the ByteForge simulated import lab."
                return node
            target = alias.asname or alias.name
            assigns.append(ast.Assign(
                targets=[ast.Name(id=target, ctx=ast.Store())],
                value=ast.Subscript(
                    value=ast.Name(id="__bf_modules", ctx=ast.Load()),
                    slice=ast.Constant(alias.name),
                    ctx=ast.Load(),
                ),
            ))
        return assigns

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.level or not node.module or node.module not in SIM_IMPORTS:
            self.error = "Only listed ByteForge simulated modules may be imported; relative imports are disabled."
            return node
        allowed = SIM_IMPORTS[node.module]
        assigns = []
        for alias in node.names:
            if alias.name == "*" or alias.name not in allowed:
                self.error = f"from {node.module} import {alias.name} is not available in this lab."
                return node
            target = alias.asname or alias.name
            assigns.append(ast.Assign(
                targets=[ast.Name(id=target, ctx=ast.Store())],
                value=ast.Attribute(
                    value=ast.Subscript(
                        value=ast.Name(id="__bf_modules", ctx=ast.Load()),
                        slice=ast.Constant(node.module),
                        ctx=ast.Load(),
                    ),
                    attr=alias.name,
                    ctx=ast.Load(),
                ),
            ))
        return assigns


def prepare_user_code(code: str) -> tuple[str | None, str | None]:
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

    for node in nodes:
        if isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
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

    rw = SimImportRewriter()
    tree = rw.visit(tree)
    if rw.error:
        return None, rw.error
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree), None
    except Exception:
        return code, None


def _make_harness(user_code: str, tests: list[dict], marker: str) -> str:
    payload = json.dumps(tests, ensure_ascii=False)
    return f'''# --- ByteForge runtime guard ---\ntry:\n    import resource as _bf_resource\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_CPU, (2, 2))\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_FSIZE, (2 * 1024 * 1024, 2 * 1024 * 1024))\nexcept Exception:\n    pass\n\nimport builtins as _bf_builtins\nimport hashlib as _bf_hashlib\nimport ipaddress as _bf_ipaddress\nimport json as _bf_json\nimport math as _bf_math\nimport types as _bf_types\n__bf_modules = {{\n    "hashlib": _bf_types.SimpleNamespace(sha256=_bf_hashlib.sha256),\n    "json": _bf_types.SimpleNamespace(loads=_bf_json.loads, dumps=_bf_json.dumps),\n    "ipaddress": _bf_types.SimpleNamespace(ip_address=_bf_ipaddress.ip_address),\n    "math": _bf_types.SimpleNamespace(ceil=_bf_math.ceil, floor=_bf_math.floor, sqrt=_bf_math.sqrt, log2=_bf_math.log2),\n}}\n\n# --- Player code ---\n{user_code}\n\n# --- ByteForge judge harness ---\n_bf_tests = _bf_json.loads({json.dumps(payload)})\n_bf_results = []\nfor _bf_test in _bf_tests:\n    try:\n        _bf_ns = dict(globals())\n        _bf_setup = _bf_test.get("setup", "")\n        if _bf_setup:\n            _bf_builtins.exec(_bf_setup, _bf_ns, _bf_ns)\n        _bf_value = _bf_builtins.eval(_bf_test["expression"], _bf_ns, _bf_ns)\n        _bf_actual_json = _bf_json.dumps(_bf_value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))\n        _bf_expected_json = _bf_json.dumps(_bf_test["expected"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))\n        _bf_results.append({{"label": _bf_test["label"], "hidden": bool(_bf_test.get("hidden")), "passed": _bf_actual_json == _bf_expected_json, "actual": _bf_actual_json, "expected": _bf_expected_json}})\n    except BaseException as _bf_error:\n        _bf_results.append({{"label": _bf_test["label"], "hidden": bool(_bf_test.get("hidden")), "passed": False, "error": type(_bf_error).__name__ + ": " + str(_bf_error)}})\n_bf_builtins.print({marker!r} + _bf_json.dumps(_bf_results, ensure_ascii=False))\n'''


def run_judge(quest: dict, code: str) -> dict:
    prepared, validation = prepare_user_code(code)
    if validation:
        return {"passed": False, "output": "", "tests": [], "error": validation}
    marker = "__BYTEFORGE_" + uuid.uuid4().hex + "__"
    script = _make_harness(prepared or "", quest["tests"], marker)
    with tempfile.TemporaryDirectory(prefix="byteforge-") as tmp:
        path = Path(tmp) / "mission.py"
        path.write_text(script, encoding="utf-8")
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            completed = subprocess.run([sys.executable, "-I", "-S", str(path)], cwd=tmp, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", timeout=TIME_LIMIT, env=env, creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0))
        except subprocess.TimeoutExpired:
            return {"passed": False, "output": "", "tests": [], "error": "Execution timed out. Check for an infinite loop or runaway recursion."}
        except OSError as exc:
            return {"passed": False, "output": "", "tests": [], "error": f"Could not start Python judge: {exc}"}
    stdout = completed.stdout[-80_000:]
    stderr = completed.stderr[-20_000:].strip()
    marker_index = stdout.rfind(marker)
    user_output = stdout[:marker_index].rstrip() if marker_index >= 0 else stdout.rstrip()
    if marker_index < 0:
        return {"passed": False, "output": user_output, "tests": [], "error": stderr or "Program ended before ByteForge could run the tests."}
    try:
        raw_tests = json.loads(stdout[marker_index + len(marker):].strip())
    except json.JSONDecodeError:
        return {"passed": False, "output": user_output, "tests": [], "error": "Judge output could not be decoded."}
    display_tests = []
    for item in raw_tests:
        hidden = bool(item.get("hidden"))
        clean = {"label": "Hidden test" if hidden else item.get("label", "Test"), "hidden": hidden, "passed": bool(item.get("passed"))}
        if item.get("error"):
            clean["error"] = item["error"]
        elif not hidden:
            clean["actual"] = item.get("actual")
            clean["expected"] = item.get("expected")
        display_tests.append(clean)
    passed = len(raw_tests) == len(quest["tests"]) and all(t.get("passed") for t in raw_tests)
    return {"passed": bool(passed), "output": user_output, "tests": display_tests, "error": stderr or None}


def _ai_config():
    url = os.environ.get("BYTEFORGE_AI_URL", "").strip()
    model = os.environ.get("BYTEFORGE_AI_MODEL", "").strip()
    key = os.environ.get("BYTEFORGE_AI_KEY", "").strip()
    timeout = float(os.environ.get("BYTEFORGE_AI_TIMEOUT", "12") or 12)
    return {"url": url, "model": model, "key": key, "timeout": timeout, "connected": bool(url and model)}


def _local_ai_grade(explanation: str) -> dict:
    text = (explanation or "").strip()
    lower = text.lower()
    correctness = 10 if len(text) >= 30 else 5 if len(text) >= 10 else 2
    security = 10 if any(k in lower for k in ("security", "attack", "risk", "安全", "攻擊", "風險", "惡意", "權限")) else 5
    edge = 5 if any(k in lower for k in ("edge", "false positive", "boundary", "邊界", "誤判", "例外")) else 2
    clarity = 5 if len(text) >= 80 else 3 if len(text) >= 30 else 1
    score = correctness + security + edge + clarity
    return {"score": score, "breakdown": {"correctness": correctness, "security_reasoning": security, "edge_cases": edge, "clarity": clarity}, "feedback": "LOCAL RUBRIC: explain what the code detects, why it matters for security, and at least one edge case or false positive."}


def _remote_chat(system: str, user: str) -> str | None:
    cfg = _ai_config()
    if not cfg["connected"]:
        return None
    payload = json.dumps({"model": cfg["model"], "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.2}, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cfg["key"]:
        headers["Authorization"] = "Bearer " + cfg["key"]
    try:
        with urlopen(Request(cfg["url"], data=payload, headers=headers, method="POST"), timeout=cfg["timeout"]) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
    except Exception:
        return None


def ai_grade(quest: dict, code: str, explanation: str) -> dict:
    local = _local_ai_grade(explanation)
    remote = _remote_chat("You are ByteForge's security-learning evaluator. Score only the learner's reasoning from 0 to 30. Return concise JSON with score, feedback, and breakdown keys correctness, security_reasoning, edge_cases, clarity. Never reveal hidden tests.", f"Mission: {quest.get('title')}\nCode:\n{code}\nLearner explanation:\n{explanation}")
    if not remote:
        return {**local, "mode": "local"}
    try:
        raw = remote.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(raw)
        score = max(0, min(30, int(parsed.get("score", local["score"]))))
        return {"score": score, "breakdown": parsed.get("breakdown", local["breakdown"]), "feedback": parsed.get("feedback", remote), "mode": "connected"}
    except Exception:
        return {**local, "feedback": remote, "mode": "connected"}


def run_self_test(verbose: bool = True) -> bool:
    try:
        from content.reference_solutions import SOLUTIONS
    except Exception as exc:
        if verbose: print(f"[FAIL] Could not load reference solutions: {exc}")
        return False
    ok = True
    started = time.time()
    for quest in QUESTS:
        result = run_judge(quest, SOLUTIONS[quest["id"]])
        if not result["passed"]:
            ok = False
            if verbose: print(f"[FAIL] Quest {quest['id']:02d} {quest['title']}: {result.get('error') or result['tests']}")
        elif verbose:
            print(f"[ OK ] Quest {quest['id']:02d} {quest['title']}")
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
        if args and str(args[1]).startswith(("4", "5")): super().log_message(fmt, *args)
    def _send_json(self, payload, status=HTTPStatus.OK):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(raw))); self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff"); self.end_headers(); self.wfile.write(raw)
    def _send_file(self, path: Path):
        if not path.is_file(): self.send_error(HTTPStatus.NOT_FOUND); return
        raw = path.read_bytes(); mime, _ = mimetypes.guess_type(str(path))
        if path.suffix == ".js": mime = "text/javascript"
        self.send_response(HTTPStatus.OK); self.send_header("Content-Type", (mime or "application/octet-stream") + ("; charset=utf-8" if (mime or "").startswith(("text/", "application/javascript")) else "")); self.send_header("Content-Length", str(len(raw))); self.send_header("Cache-Control", "no-cache"); self.send_header("X-Content-Type-Options", "nosniff"); self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/api/health", "/health"):
            self._send_json({"ok": True, "version": VERSION, "quests": len(QUESTS), "python": sys.version.split()[0]}); return
        if path == "/api/quests": self._send_json({"version": VERSION, "quests": public_quests()}); return
        if path == "/api/version": self._send_json({"version": VERSION}); return
        if path == "/api/ai/status":
            cfg = _ai_config(); self._send_json({"connected": cfg["connected"], "mode": "remote" if cfg["connected"] else "local", "model": cfg["model"] or None}); return
        if path == "/": self._send_file(STATIC / "index.html"); return
        candidate = (STATIC / path.lstrip("/")).resolve()
        try: candidate.relative_to(STATIC.resolve())
        except ValueError: self.send_error(HTTPStatus.FORBIDDEN); return
        self._send_file(candidate)
    def do_POST(self):
        path = urlparse(self.path).path
        try: length = int(self.headers.get("Content-Length", "0"))
        except ValueError: length = 0
        if length <= 0 or length > MAX_BODY: self._send_json({"error": "Invalid request size."}, HTTPStatus.BAD_REQUEST); return
        try: body = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception: self._send_json({"error": "Invalid JSON request."}, HTTPStatus.BAD_REQUEST); return
        if path == "/api/run":
            try: quest_id = int(body.get("questId"))
            except (TypeError, ValueError): quest_id = -1
            quest = get_quest(quest_id)
            if quest is None: self._send_json({"error": "Unknown quest."}, HTTPStatus.NOT_FOUND); return
            result = run_judge(quest, body.get("code", ""))
            if result["passed"] and quest.get("ai_grading"):
                ai = ai_grade(quest, body.get("code", ""), body.get("explanation", "")); result["ai"] = ai; result["judge_score"] = 70; result["total_score"] = 70 + ai["score"]; result["passed"] = ai["score"] >= 15 and result["total_score"] >= 85
            self._send_json(result); return
        if path == "/api/ai/tutor":
            try: quest_id = int(body.get("questId"))
            except (TypeError, ValueError): quest_id = -1
            quest = get_quest(quest_id)
            if quest is None: self._send_json({"error": "Unknown quest."}, HTTPStatus.NOT_FOUND); return
            question = str(body.get("question", ""))[:4000]
            remote = _remote_chat("You are Lyra, ByteForge's cyber academy tutor. Guide with hints and concepts; do not reveal hidden tests or hand out the full answer unless the learner explicitly asks after trying.", f"Mission: {quest.get('title')}\nLearning objective: {quest.get('objective','')}\nStudent code:\n{body.get('code','')}\nQuestion: {question}")
            fallback = quest.get("teaching", {}).get("why") or quest.get("description") or "Review the mission rules, then test one small assumption at a time."
            self._send_json({"answer": remote or fallback, "mode": "connected" if remote else "local"}); return
        if path == "/api/ai/debug":
            try: quest_id = int(body.get("questId"))
            except (TypeError, ValueError): quest_id = -1
            quest = get_quest(quest_id)
            if quest is None: self._send_json({"error": "Unknown quest."}, HTTPStatus.NOT_FOUND); return
            remote = _remote_chat("You are Patch, ByteForge's debugging coach. Diagnose the likely next check without revealing hidden tests or immediately writing the final solution.", f"Mission: {quest.get('title')}\nCode:\n{body.get('code','')}\nLatest judge result:\n{json.dumps(body.get('result',{}), ensure_ascii=False)}")
            self._send_json({"answer": remote or "Start with the first failing visible test. Compare expected vs actual, then check input normalization, boundary conditions, and return type.", "mode": "connected" if remote else "local"}); return
        self.send_error(HTTPStatus.NOT_FOUND)


def make_server(port: int | None = None):
    candidates = [port] if port is not None else list(DEFAULT_PORTS) + [0]
    last_error = None
    for candidate in candidates:
        try: return ByteForgeHTTPServer((HOST, candidate), Handler)
        except OSError as exc: last_error = exc
    raise OSError(f"Could not bind a local port: {last_error}")


def main():
    parser = argparse.ArgumentParser(description="Run ByteForge 7.0 locally.")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: raise SystemExit(0 if run_self_test(verbose=True) else 1)
    if sys.version_info < (3, 10): print("ByteForge 7.0 requires Python 3.10 or newer."); raise SystemExit(2)
    try: server = make_server(args.port)
    except OSError as exc: print(f"\n[ERROR] {exc}"); raise SystemExit(1)
    actual_port = server.server_address[1]; url = f"http://127.0.0.1:{actual_port}"
    print("\n" + "=" * 60); print(" BYTEFORGE 7.0 — AI ACADEMY"); print("=" * 60); print("\nThis window IS the ByteForge local server.\nKeep it open while you play.\n"); print(f"Open: {url}\n")
    if not args.no_browser: threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try: server.serve_forever(poll_interval=0.4)
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == "__main__":
    main()
