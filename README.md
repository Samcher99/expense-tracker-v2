# Expense Tracker v2

個人記帳應用程式的後端 API，使用 FastAPI + PostgreSQL 打造，支援使用者註冊、JWT 身分驗證，以及完整的交易紀錄 CRUD 功能，並具備完整的 pytest 自動化測試覆蓋。

這是一個開發中的學習型專案，開發過程中搭配 AI 輔助學習，但每一項技術決策都經過理解、討論與親自驗證後才實作，重點放在扎實理解後端開發的核心概念（資料庫設計、API 驗證、身分驗證機制、資安考量、自動化測試），而非單純堆疊功能。

---

## 技術棧

| 類別 | 技術 |
|---|---|
| 後端框架 | FastAPI |
| 資料庫 | PostgreSQL |
| ORM | SQLAlchemy 2.0（`DeclarativeBase` / `Mapped` 新語法） |
| 資料驗證 | Pydantic v2 |
| 身分驗證 | JWT（PyJWT）+ OAuth2 密碼流程 |
| 密碼雜湊 | Argon2（`pwdlib`） |
| 環境變數管理 | pydantic-settings |
| 測試框架 | pytest + FastAPI `TestClient` |
| 容器化 | Docker + Docker Compose |
| 版本控制 | Git + GitHub |

---

## 專案架構

```
app/
├── main.py                  # 應用程式入口，掛載各路由
├── api/
│   ├── users.py             # 使用者相關端點（註冊、登入、個人資料）
│   └── transactions.py      # 交易相關端點（CRUD + 日期篩選）
├── core/
│   ├── config.py            # 環境變數設定（pydantic-settings）
│   └── security.py          # 密碼雜湊、JWT 產生/驗證、身分驗證邏輯
├── database/
│   ├── db_conn.py           # 資料庫連線（engine、Session、依賴注入）
│   ├── db_users.py          # User 資料表模型
│   └── db_transactions.py   # Transactions 資料表模型、Enum 定義
└── schemas/
    ├── users.py              # User 相關 Pydantic schema
    └── transactions.py       # Transaction 相關 Pydantic schema

tests/
├── conftest.py               # 測試 fixture：獨立測試資料庫連線、
│                              # TestClient 依賴覆寫、已登入使用者憑證
├── test_sanity.py            # 環境驗證測試
├── test_security.py          # 密碼雜湊單元測試
├── test_users_db.py          # 資料庫層單元測試
├── test_users_api.py         # 使用者相關整合測試（註冊、登入、個人資料）
└── test_transactions_api.py  # 交易相關整合測試（CRUD、日期篩選）

test/                          # 開發過程中的手動驗證腳本（歷史紀錄）
pytest.ini                     # pytest 設定（測試路徑、Python 搜尋路徑）
docker-compose.yml             # PostgreSQL 容器設定（含獨立測試資料庫）
requirements.txt               # 套件依賴清單
.env.example                   # 環境變數範本
```

---

## 功能特色

### 使用者系統

- **註冊**（`POST /users`）：密碼以 Argon2 雜湊後儲存，重複 email 會被擋下並回傳明確錯誤訊息
- **登入**（`POST /token`）：採用標準 OAuth2 密碼流程（`OAuth2PasswordRequestForm`），驗證通過後發放 JWT access token
- **查詢個人資料**（`GET /users/me`）：需登入才能存取，示範 FastAPI 依賴注入機制如何串接身分驗證

### 交易紀錄系統

完整 CRUD，並確保使用者只能存取、修改自己的資料：

| 方法 | 路徑 | 說明 |
|---|---|---|
| `POST` | `/transactions` | 新增一筆交易 |
| `GET` | `/transactions` | 查詢自己的交易列表，支援 `start_date`/`end_date` 日期區間篩選 |
| `GET` | `/transactions/{id}` | 查詢單筆交易 |
| `PATCH` | `/transactions/{id}` | 部分更新交易（只需傳想修改的欄位） |
| `DELETE` | `/transactions/{id}` | 刪除交易 |

每個「操作特定資源」的端點都包含兩層防護：查無資料回傳 `404`，資料存在但不屬於自己則回傳 `403`。

### 業務邏輯驗證

- 交易金額（`amount`）必須大於 0
- 交易類型（`type`）為 `income`（收入）或 `expense`（支出）
- `need_type`（需求／想要，對應 50/30/20 理財法則）僅在 `type=expense` 時允許填寫，`income` 交易不應包含此欄位——此規則透過 Pydantic 的 `model_validator` 在新增時驗證，並在修改時於「合併新舊資料後」重新檢查，確保任何一次更新都不會讓資料落入不合理狀態

---

## 自動化測試

專案具備 pytest 建構的完整測試套件，共 **23 個測試**，涵蓋三個層次：

- **單元測試**：密碼雜湊與驗證邏輯（不依賴資料庫）
- **資料庫測試**：直接驗證 SQLAlchemy model 與資料庫互動
- **整合測試**：透過 FastAPI `TestClient` 模擬真實 HTTP 請求，驗證完整的 API 端點行為

測試環境採用**獨立的 PostgreSQL 測試資料庫**（與開發資料庫完全隔離，不同 port），每個測試前後自動建表/清空，確保測試之間互不干擾、不污染開發資料。

測試覆蓋範圍包含正常情境、業務邏輯驗證失敗、以及資安權限檢查（例如模擬兩個不同使用者，驗證無法存取或竄改他人資料）：

| 端點 | 測試涵蓋 |
|---|---|
| `POST /users` | 成功註冊、email 重複、密碼確實雜湊 |
| `POST /token` | 成功登入、密碼錯誤 |
| `GET /users/me` | 成功查詢、Token 無效 |
| `POST /transactions` | 成功新增、業務邏輯驗證失敗 |
| `GET /transactions` | 查全部、日期區間篩選 |
| `GET /transactions/{id}` | 成功查詢、查無資料、權限不足 |
| `PATCH /transactions/{id}` | 部分更新成功、合併後驗證失敗、權限不足 |
| `DELETE /transactions/{id}` | 成功刪除、權限不足 |

---

## 安全性設計

- 密碼使用 Argon2 演算法雜湊，絕不明文儲存
- JWT `SECRET_KEY` 與資料庫密碼皆透過 `.env` 管理，不進版本控制
- 登入驗證流程包含計時攻擊（timing attack）防護：即使帳號不存在，仍執行一次密碼比對運算，避免攻擊者透過回應時間差異枚舉已註冊帳號
- 所有資料庫查詢皆使用 SQLAlchemy ORM，未手動拼接 SQL 字串，天生具備 SQL Injection 防護
- 交易相關端點皆檢查資源擁有權（`user_id` 比對），防止使用者存取或竄改他人資料，並有對應的整合測試驗證此防護確實生效

---

## 環境需求

- Python 3.12
- Docker（用於執行 PostgreSQL，含開發與測試兩個獨立資料庫）

---

## 安裝與啟動

### 1. 複製專案並建立虛擬環境

```powershell
git clone https://github.com/Samcher99/expense-tracker-v2.git
cd expense-tracker-v2
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
```

### 2. 安裝套件

```powershell
pip install -r requirements.txt
```

### 3. 設定環境變數

複製 `.env.example` 為 `.env`，並填入實際的資料庫帳密與 JWT 密鑰：

```powershell
Copy-Item .env.example .env
```

`SECRET_KEY` 建議用以下指令產生一組隨機值：

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 啟動資料庫（含開發與測試用兩個獨立容器）

```powershell
docker-compose up -d
```

### 5. 建立資料表

```powershell
python create_tables.py
```

### 6. 啟動應用程式

```powershell
uvicorn app.main:app --reload
```

啟動後，可透過 Swagger UI 互動式文件測試所有 API：

```
http://127.0.0.1:8000/docs
```

### 7. 執行測試

```powershell
pytest
```

測試會自動使用獨立的測試資料庫（`docker-compose.yml` 裡的 `test_db` 服務），不會影響開發資料庫裡的資料。

---

## 開發紀錄

開發過程中的詳細技術決策、踩坑紀錄與解決方式，皆記錄於個人 Notion 開發日誌中，涵蓋：

- 資料庫層與環境變數安全管理
- SQLAlchemy 2.0 model 設計與 Pydantic schema 驗證邏輯
- JWT 身分驗證機制與 OAuth2 標準流程實作
- API 端點的依賴注入、錯誤處理、跨欄位業務邏輯驗證
- 部分更新（PATCH）情境下的驗證邏輯設計考量
- pytest 測試環境建置、fixture 分層設計、獨立測試資料庫的實作與踩坑

---

## 開發規劃

- [x] pytest 自動化測試（含獨立測試資料庫）— 23 個測試，涵蓋單元/資料庫/整合三個層次
- [ ] GitHub Actions CI/CD
- [ ] Vue 3 前端介面
- [ ] Fiscal Rating 財務評分系統（套用 50/30/20 法則、儲蓄率、緊急預備金等指標）
- [ ] Rate Limiting、依賴套件漏洞掃描等正式上線前的資安強化

---

## 授權

此專案為個人學習與求職作品集用途。
