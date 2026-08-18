#!/usr/bin/env python3
"""ByteForge 5.0 local cyber range server.

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
from urllib.parse import urlparse

from content.quests import QUESTS, get_quest, public_quests

VERSION = "5.0.0"
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST = "127.0.0.1"
DEFAULT_PORTS = (3000, 3001, 3002, 8000, 8765)
MAX_BODY = 80_000
MAX_CODE = 20_000
TIME_LIMIT = 3.0

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


def validate_user_code(code: str) -> str | None:
    if not isinstance(code, str):
        return "Code must be text."
    if len(code) > MAX_CODE:
        return f"Code is too long for this training sandbox ({MAX_CODE} characters max)."
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        line = exc.lineno or "?"
        return f"SyntaxError on line {line}: {exc.msg}"

    nodes = list(ast.walk(tree))
    if len(nodes) > 6000:
        return "Code is too complex for this training sandbox."

    for node in nodes:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "Imports are disabled in ByteForge missions."
        if isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
            return f"The name {node.id!r} is disabled in the learning sandbox."
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__") or node.attr.endswith("__"):
                return "Dunder attribute access is disabled in the learning sandbox."
            if node.attr in BLOCKED_ATTRS:
                return f"The attribute {node.attr!r} is disabled in the learning sandbox."
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                return f"The builtin {node.func.id!r} is disabled in the learning sandbox."
            if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKED_ATTRS:
                return f"The call .{node.func.attr}(...) is disabled in the learning sandbox."
    return None


def _make_harness(user_code: str, tests: list[dict], marker: str) -> str:
    # Tests are trusted ByteForge content; only user_code is validated by AST.
    payload = json.dumps(tests, ensure_ascii=False)
    return f'''# --- ByteForge runtime guard (not part of the mission) ---\ntry:\n    import resource as _bf_resource\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_CPU, (2, 2))\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))\n    _bf_resource.setrlimit(_bf_resource.RLIMIT_FSIZE, (2 * 1024 * 1024, 2 * 1024 * 1024))\nexcept Exception:\n    pass\n\n# --- Player code ---\n{user_code}\n\n# --- ByteForge judge harness ---\nimport builtins as _bf_builtins\nimport json as _bf_json\n_bf_tests = _bf_json.loads({json.dumps(payload)})\n_bf_results = []\nfor _bf_test in _bf_tests:\n    try:\n        _bf_ns = dict(globals())\n        _bf_setup = _bf_test.get("setup", "")\n        if _bf_setup:\n            _bf_builtins.exec(_bf_setup, _bf_ns, _bf_ns)\n        _bf_value = _bf_builtins.eval(_bf_test["expression"], _bf_ns, _bf_ns)\n        _bf_actual_json = _bf_json.dumps(_bf_value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))\n        _bf_expected_json = _bf_json.dumps(_bf_test["expected"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))\n        _bf_results.append({{\n            "label": _bf_test["label"],\n            "hidden": bool(_bf_test.get("hidden")),\n            "passed": _bf_actual_json == _bf_expected_json,\n            "actual": _bf_actual_json,\n            "expected": _bf_expected_json,\n        }})\n    except BaseException as _bf_error:\n        _bf_results.append({{\n            "label": _bf_test["label"],\n            "hidden": bool(_bf_test.get("hidden")),\n            "passed": False,\n            "error": type(_bf_error).__name__ + ": " + str(_bf_error),\n        }})\n_bf_builtins.print({marker!r} + _bf_json.dumps(_bf_results, ensure_ascii=False))\n'''


def run_judge(quest: dict, code: str) -> dict:
    validation = validate_user_code(code)
    if validation:
        return {"passed": False, "output": "", "tests": [], "error": validation}

    marker = "__BYTEFORGE_" + uuid.uuid4().hex + "__"
    script = _make_harness(code, quest["tests"], marker)

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

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._send_json({"error": "Invalid request size."}, HTTPStatus.BAD_REQUEST)
            return

        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._send_json({"error": "Invalid JSON request."}, HTTPStatus.BAD_REQUEST)
            return

        quest_id = body.get("questId")
        code = body.get("code", "")
        try:
            quest_id = int(quest_id)
        except (TypeError, ValueError):
            quest_id = -1
        quest = get_quest(quest_id)
        if quest is None:
            self._send_json({"error": "Unknown quest."}, HTTPStatus.NOT_FOUND)
            return

        result = run_judge(quest, code)
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
    parser = argparse.ArgumentParser(description="Run ByteForge 5.0 locally.")
    parser.add_argument("--port", type=int, default=None, help="Preferred local port (default: try 3000 then fallbacks).")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically.")
    parser.add_argument("--self-test", action="store_true", help="Run all 100 reference solutions and exit.")
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(0 if run_self_test(verbose=True) else 1)

    if sys.version_info < (3, 10):
        print("ByteForge 5.0 requires Python 3.10 or newer.")
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
    print(" BYTEFORGE 5.0 — CYBER ACADEMY")
    print("=" * 60)
    print(f" [OK] Python {sys.version.split()[0]}")
    print(f" [OK] {len(QUESTS)} missions loaded")
    print(f" [OK] Local judge ready ({TIME_LIMIT:.0f}s limit)")
    print(f" [OK] Server bound to loopback only")
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
