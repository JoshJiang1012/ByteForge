# ByteForge 7.0 — AI Academy

> 本機、零 npm、零 pip 的雙語白帽資安學習遊戲。100 關 Cyber Range、10 個 Boss、VS Code 風格編輯器、Simulated Import、Lyra / Patch 教學角色，以及 7.0 新增的 **AI Judge + AI Tutor**。

**Current version:** `7.0.0`

ByteForge 的核心原則仍然是：**先用可重現的 deterministic Judge 驗程式，再讓 AI 評估需要語意理解的資安推理。** AI 不會凌駕 AST 安全閘門，也不會取得 hidden tests。

## 特色

- 100 個依序解鎖任務：10 Sector × 10 Missions
- 90 個一般關卡 + 10 Boss
- 70 個 BLUE deterministic missions
- 30 個 PURPLE / RED-VIEW **Hybrid AI missions**
- Traditional Chinese / English 即時切換
- Python 3.10+，不需要 Node.js / npm / pip
- AST sandbox + `127.0.0.1` loopback-only server
- Simulated Import：`hashlib`、`json`、`ipaddress`、`math`
- VS Code 風格 Python syntax highlighting
- 每關超詳細語法教學、明確通關規格、3 段提示
- 通關後 3 個 worked examples + 3 份 extra practice
- Lyra Circuit AI Tutor
- Patch contextual AI debugging
- Warden Null Boss encounters
- 6.4 的全域可讀性 / 高 DPI responsive layout 完整保留

## 快速開始

### Windows

雙擊：

```text
RUN-BYTEFORGE-WINDOWS.bat
```

### Linux

```bash
bash RUN-BYTEFORGE-LINUX.sh
```

### macOS

```bash
bash RUN-BYTEFORGE-MAC.command
```

終端機就是本機 ByteForge server，遊玩期間請保持開啟。

## 7.0 通關方式

### BLUE missions

完全 deterministic：

```text
AST Safety Gate
      ↓
Visible + Hidden Tests
      ↓
100 / 100
      ↓
MISSION CLEAR
```

### PURPLE / RED-VIEW missions

需要 **程式 + 資安推理**：

```text
AST Safety Gate
      ↓
Deterministic Judge
      ↓
Code tests ALL PASS = 70 points
      ↓
AI / Local Rubric Review = 0–30 points
      ↓
Total >= 85 / 100
      ↓
MISSION CLEAR
```

AI rubric：

| 項目 | 分數 |
|---|---:|
| Reasoning correctness | 10 |
| Security reasoning | 10 |
| Edge cases / false positives | 5 |
| Clarity | 5 |
| **Total** | **30** |

程式測試沒有全部通過時，不會用 AI 分數硬救過關。反過來，程式全過但推理太薄弱時，畫面會顯示 **CODE PASSED · REASONING NEEDS REVISION**，只需修改推理說明，不必重寫已正確的程式。

## AI 模式

ByteForge 7.0 不會因為沒有 LLM 就不能玩。

### LOCAL RUBRIC（預設）

沒有設定外部模型時：

- 程式 Judge 正常運作
- 30 個 Hybrid missions 使用本機 rubric fallback
- Lyra / Patch 使用 guided fallback
- 完全不需要網路

Local Rubric 是 deterministic fallback，**不是假裝成 LLM**。UI 會明確顯示 `LOCAL RUBRIC`。

### CONNECTED AI（選用）

ByteForge 可透過 Python 標準函式庫 `urllib.request` 呼叫一個 **Chat-Completions-compatible** POST endpoint。

在啟動 ByteForge 前設定：

```text
BYTEFORGE_AI_URL=<完整 chat completions endpoint>
BYTEFORGE_AI_MODEL=<model name>
BYTEFORGE_AI_KEY=<optional API key>
BYTEFORGE_AI_TIMEOUT=12
```

例如你的本機模型服務或遠端 AI gateway 若提供相容 endpoint，就可直接接入。ByteForge 不需要額外 Python 套件。

安全 / 隱私規則：

- API key 只存在 Python server process，不送到 browser。
- AI 只收到 public mission context、你的程式碼與你輸入的推理說明。
- **Hidden tests 永遠不會送給 AI。**
- AI endpoint 失敗時，自動退回 Local Rubric，不阻塞進度。

## Lyra AI Tutor

右側 Lyra AI 可以讀取：

- 當前 public mission contract
- 當前程式碼
- 語法 / sandbox validation 結果
- 你主動提出的問題

Lyra 的 system rule 明確要求：

- 只引導下一步
- 不直接貼完整最終解法
- 不透露 hidden tests
- 不提供對真實目標的攻擊操作

沒有連接 LLM 時，Lyra 仍會依照關卡語法、提示與目前程式狀態提供 guided fallback。

## Patch Support

Patch 專門處理「我到底錯在哪」：

- Syntax / indentation 問題
- Sandbox capability 被阻擋
- Visible test expected / actual 不一致
- Code 已通過，但 AI reasoning 分數不足

7.0 的 Patch 可以走 connected AI；沒有 LLM 時則使用本機診斷邏輯。

## 100 關課程順序

1. Core Security Automation — 1–10
2. Identity & Access Control — 11–20
3. Linux & Host Hardening — 21–30
4. Web Request Security — 31–40
5. Network & Firewall — 41–50
6. Secrets & Crypto Hygiene — 51–60
7. Detection Engineering — 61–70
8. Incident Response & Forensics — 71–80
9. Secure Coding — 81–90
10. Purple-Team Integrated Range — 91–100

每第 10 關為 Boss。

完整任務表見 [`COURSE.md`](COURSE.md)。

## Simulated Import

ByteForge 不直接開放 Python 任意 import。指定關卡允許正常 Python import 語法，但 AST 會把它改寫到 ByteForge 虛擬模組。

目前：

```python
import hashlib
import json
import ipaddress
import math
```

或允許的精確 `from ... import ...`。

以下仍會被拒絕：

```python
import os
import subprocess
from something import *
```

這樣可以學 `import` 語法，又不必把本機系統能力交給 student code。

## Safety model

ByteForge 是**本機教學沙盒**，不是通用 hostile-code isolation product。

安全層包括：

- `ast.parse()` 靜態檢查
- 阻擋 `eval`、`exec`、`open`、`__import__` 等能力
- 阻擋 dunder attribute access
- 任意 module imports 禁止；只有 Simulated Import 白名單
- server 只綁定 `127.0.0.1`
- student code 子程序有 3 秒 timeout
- Unix-like 系統另外嘗試 `resource.setrlimit`

### Windows resource-limit note

Windows 沒有 Python `resource.setrlimit` 的同等支援，因此 Windows Judge 主要依賴 **3 秒執行 timeout + AST sandbox restrictions** 來處理 runaway code。這適合 ByteForge 的本機學習用途，但不應被視為 hardened boundary for hostile untrusted code。

## AI safety boundary

AI layer 只負責教學與語意 rubric：

```text
AST Safety Gate
    ↓
Deterministic Judge
    ↓
AI Review (if required)
```

AI 不能 override AST sandbox，也不能讓一份 deterministic tests 失敗的程式通關。

## Self-test

```bash
python server.py --self-test
```

正常最後一行：

```text
Self-test: PASS — 100 quests
```

Self-test 同時驗證：

- 100 reference solutions
- 90 normal / 10 boss structure
- Simulated Import allowlist
- arbitrary import blocking
- 30 Hybrid AI missions
- Local Rubric good / weak calibration

## Editor fidelity

ByteForge 的 textarea 與 syntax-highlight layer 使用完全一致的字型度量：

- same monospace font stack
- same font size / line height
- zero letter / word spacing
- `tab-size: 4`
- ligatures disabled

用來避免 caret 與 syntax color layer 漂移。

## Project structure

```text
ByteForge/
├── server.py
├── content/
│   ├── quests.py
│   ├── quests_data.json.gz
│   ├── reference_solutions.py
│   └── solutions_data.json.gz
├── static/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── assets/characters/
├── .github/workflows/self-test.yml
└── VERSION
```

## License

MIT — see [`LICENSE`](LICENSE).
