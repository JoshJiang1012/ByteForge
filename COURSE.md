# ByteForge 5.0 Course Map

> 100 sequential missions. Every 10th mission is a boss. All data is synthetic and local.

## Sector 01 — Core Security Automation / 資安自動化基礎

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 1 | BLUE | Admin Name Check | 管理員名稱檢查 |
| 2 | BLUE | Failed Login Gate | 登入失敗閘門 |
| 3 | BLUE | Normalize a Username | 使用者名稱正規化 |
| 4 | PURPLE | Suspicious Extension Review | 可疑副檔名檢查 |
| 5 | BLUE | Allowlist Membership | 允許清單成員檢查 |
| 6 | BLUE | Count Failed Events | 計算失敗事件 |
| 7 | BLUE | First Alert Locator | 第一個警示位置 |
| 8 | BLUE | Risk Band | 風險分級 |
| 9 | BLUE | Token Redaction | 權杖遮罩 |
| 10 | PURPLE | BOSS · Gatekeeper Protocol 👑 | BOSS · 閘門守衛協定 |

## Sector 02 — Identity & Access Control / 身分與存取控制

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 11 | BLUE | Password Length Policy | 密碼長度政策 |
| 12 | BLUE | MFA Requirement | MFA 要求判斷 |
| 13 | BLUE | Lockout Window | 帳號鎖定視窗 |
| 14 | BLUE | Role Permission Check | 角色權限檢查 |
| 15 | BLUE | Session Expiry | Session 到期判斷 |
| 16 | PURPLE | Duplicate Account Signal | 重複帳號訊號 |
| 17 | BLUE | Account State Gate | 帳號狀態閘門 |
| 18 | BLUE | Least-Privilege Extras | 最小權限多餘項目 |
| 19 | PURPLE | Authentication Risk Score | 驗證風險分數 |
| 20 | PURPLE | BOSS · Identity Sentinel 👑 | BOSS · 身分哨兵 |

## Sector 03 — Linux & Host Hardening / Linux 與主機強化

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 21 | BLUE | World-Writable Mode | 全域可寫權限 |
| 22 | BLUE | Owner Write Permission | 擁有者寫入權限 |
| 23 | PURPLE | Service Exposure | 服務暴露範圍 |
| 24 | BLUE | Sudo Policy Review | Sudo 政策檢查 |
| 25 | BLUE | Hidden Path Marker | 隱藏路徑標記 |
| 26 | BLUE | Patch Level State | 修補版本狀態 |
| 27 | BLUE | Approved Process List | 核准程序清單 |
| 28 | BLUE | Environment Secret Redaction | 環境變數秘密遮罩 |
| 29 | BLUE | Host Hardening Score | 主機強化分數 |
| 30 | PURPLE | BOSS · Host Bastion 👑 | BOSS · 主機堡壘 |

## Sector 04 — Web Request Security / Web 請求安全

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 31 | BLUE | HTTPS Redirect Decision | HTTPS 重新導向判斷 |
| 32 | BLUE | Secure Cookie Flags | 安全 Cookie 旗標 |
| 33 | BLUE | HTTP Method Allowlist | HTTP Method 允許清單 |
| 34 | BLUE | CORS Origin Allowlist | CORS Origin 允許清單 |
| 35 | BLUE | JSON Content Type | JSON Content-Type 判斷 |
| 36 | BLUE | Input Length Guard | 輸入長度護欄 |
| 37 | RED-VIEW | Script Marker Detection | Script 標記偵測 |
| 38 | RED-VIEW | Traversal Marker Detection | 路徑穿越標記偵測 |
| 39 | RED-VIEW | Injection Signal Review | 注入訊號檢查 |
| 40 | PURPLE | BOSS · Web Shield 👑 | BOSS · Web 護盾 |

## Sector 05 — Network & Firewall / 網路與防火牆

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 41 | BLUE | Port Allowlist | Port 允許清單 |
| 42 | BLUE | Connection State Policy | 連線狀態政策 |
| 43 | BLUE | Firewall Rule Match | 防火牆規則比對 |
| 44 | BLUE | Rate Limit Action | 速率限制動作 |
| 45 | BLUE | Network Zone from Prefix | 從前綴判斷網路區域 |
| 46 | BLUE | Domain Normalization | 網域名稱正規化 |
| 47 | PURPLE | Risky TLD Review | 高風險 TLD 檢查 |
| 48 | BLUE | TLS Version Policy | TLS 版本政策 |
| 49 | PURPLE | Packet Risk Score | 封包風險分數 |
| 50 | PURPLE | BOSS · Firewall Marshal 👑 | BOSS · 防火牆元帥 |

## Sector 06 — Secrets & Crypto Hygiene / 秘密與密碼學衛生

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 51 | BLUE | Sensitive Key Name | 敏感 Key 名稱 |
| 52 | BLUE | Mask a Secret | 秘密值遮罩 |
| 53 | BLUE | SHA-256 Hex Format | SHA-256 Hex 格式檢查 |
| 54 | BLUE | Known Digest Compare | 已知摘要比對 |
| 55 | BLUE | Character-Class Diversity | 字元種類多樣性 |
| 56 | BLUE | Rotation Due | 秘密輪替到期 |
| 57 | BLUE | Config Secret Inventory | 設定檔秘密清單 |
| 58 | BLUE | Certificate Expiry State | 憑證到期狀態 |
| 59 | BLUE | Key Strength Policy | 金鑰強度政策 |
| 60 | PURPLE | BOSS · Vault Keeper 👑 | BOSS · 秘密保管者 |

## Sector 07 — Detection Engineering / 偵測工程

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 61 | BLUE | Normalize Severity | 嚴重度正規化 |
| 62 | BLUE | Count a Severity | 計算指定嚴重度 |
| 63 | BLUE | Failed Logins by User | 依使用者統計登入失敗 |
| 64 | BLUE | Top Event Source | 最多事件來源 |
| 65 | BLUE | IOC Substring Hits | IOC 子字串命中 |
| 66 | BLUE | Burst Alert | 短時間爆量警示 |
| 67 | PURPLE | Fail-Fail-Success Sequence | 失敗失敗成功序列 |
| 68 | BLUE | Rule Matcher | 偵測規則比對器 |
| 69 | BLUE | Triage Priority | 事件分流優先級 |
| 70 | PURPLE | BOSS · Detection Engine 👑 | BOSS · 偵測引擎 |

## Sector 08 — Incident Response & Forensics / 事件應變與鑑識

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 71 | BLUE | IR Next Step | IR 下一步 |
| 72 | BLUE | Containment Order | 隔離優先順序 |
| 73 | BLUE | Evidence Timeline | 證據時間線 |
| 74 | BLUE | Duplicate Evidence Hashes | 重複證據 Hash |
| 75 | BLUE | Chain-of-Custody Completeness | 證據保管鏈完整性 |
| 76 | PURPLE | Metadata Mismatch | 檔案中繼資料不一致 |
| 77 | PURPLE | Startup Persistence Signal | 啟動項持久化訊號 |
| 78 | BLUE | Affected Users | 受影響使用者 |
| 79 | BLUE | Recovery Readiness | 復原就緒度 |
| 80 | PURPLE | BOSS · Incident Commander 👑 | BOSS · 事件指揮官 |

## Sector 09 — Secure Coding / 安全程式設計

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 81 | BLUE | Safe Integer Parsing | 安全整數解析 |
| 82 | BLUE | Basic HTML Escaping | 基礎 HTML Escaping |
| 83 | BLUE | Safe Filename Boundary | 安全檔名邊界 |
| 84 | BLUE | Command Argument Validator | 命令參數驗證器 |
| 85 | BLUE | Parameterized Query Shape | 參數化 Query 形狀 |
| 86 | BLUE | CSRF Token Equality | CSRF Token 比對 |
| 87 | BLUE | Object Authorization | 物件層授權 |
| 88 | BLUE | Upload Policy | 上傳政策 |
| 89 | BLUE | Safe Error Exposure | 安全錯誤訊息曝露 |
| 90 | PURPLE | BOSS · Secure Code Review 👑 | BOSS · 安全程式碼審查 |

## Sector 10 — Purple-Team Integrated Range / Purple Team 綜合攻防

| # | Mode | Mission | 中文 |
|---:|---|---|---|
| 91 | PURPLE | Service Exposure Triage | 服務暴露分流 |
| 92 | PURPLE | Credential-Attack Defense | 憑證攻擊防禦 |
| 93 | RED-VIEW | Phishing Signal Score | 釣魚郵件訊號分數 |
| 94 | RED-VIEW | Web Attack Classification | Web 攻擊類型分類 |
| 95 | PURPLE | Endpoint Alert Action | 端點警示動作 |
| 96 | RED-VIEW | Lateral-Movement Signal | 橫向移動訊號 |
| 97 | PURPLE | Egress Anomaly Action | 外連流量異常動作 |
| 98 | BLUE | Backup Resilience Posture | 備份韌性姿態 |
| 99 | PURPLE | Purple-Team Summary | Purple Team 摘要 |
| 100 | PURPLE | FINAL BOSS · Fortress Decision 👑 | FINAL BOSS · 堡壘最終決策 |
