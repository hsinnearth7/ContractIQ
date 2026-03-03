# ContractIQ — 啟動操作說明

## 目錄

1. [環境需求](#1-環境需求)
2. [安裝步驟](#2-安裝步驟)
3. [設定環境變數](#3-設定環境變數)
4. [啟動 Demo](#4-啟動-demo)
5. [啟動應用程式](#5-啟動應用程式)
6. [頁面功能說明](#6-頁面功能說明)
7. [Neo4j 知識圖譜 (選配)](#7-neo4j-知識圖譜-選配)
8. [測試與驗證](#8-測試與驗證)
9. [常見問題](#9-常見問題)

---

## 1. 環境需求

| 項目 | 版本 | 備註 |
|------|------|------|
| **Python** | **3.12.x** (建議) | 3.14 與 ChromaDB 不相容 |
| OpenAI API Key | — | 需申請 [OpenAI API](https://platform.openai.com/api-keys) |
| Neo4j | 5.20+ (選配) | 僅知識圖譜功能需要 |
| Docker | (選配) | 用於啟動 Neo4j |
| 作業系統 | Windows / macOS / Linux | 皆可 |

---

## 2. 安裝步驟

### 2.1 建立虛擬環境 (推薦)

```bash
# Windows — 使用 py launcher 指定 3.12
py -3.12 -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2.2 安裝依賴

```bash
pip install -r requirements.txt
```

或使用 Make：

```bash
make install
```

### 2.3 驗證安裝

```bash
pytest tests/ -v
```

預期結果：**29 passed**

---

## 3. 設定環境變數

```bash
# 複製範本
cp .env.example .env
```

編輯 `.env`，填入 OpenAI API Key：

```env
# --- 必填 ---
CIQ_OPENAI_API_KEY=sk-your-actual-key-here

# --- 選填 (以下為預設值，可不修改) ---
CIQ_LLM_MODEL=gpt-4o
CIQ_EMBEDDING_MODEL=text-embedding-3-small
CIQ_LLM_TEMPERATURE=0.0
CIQ_LLM_MAX_TOKENS=2048

# 檢索參數
CIQ_RETRIEVAL_TOP_K=20       # 初始檢索數量
CIQ_RERANK_TOP_K=5           # 重排後保留數量
CIQ_HYBRID_ALPHA=0.5         # 向量/BM25 權重 (0=純BM25, 1=純向量)

# 分塊策略
CIQ_CHUNK_STRATEGY=recursive  # 可選: recursive, semantic, clause_aware
CIQ_CHUNK_SIZE=1000
CIQ_CHUNK_OVERLAP=200

# Neo4j (選配)
CIQ_NEO4J_URI=bolt://localhost:7687
CIQ_NEO4J_USERNAME=neo4j
CIQ_NEO4J_PASSWORD=password
```

---

## 4. 啟動 Demo

### 方式一：一鍵啟動 (推薦)

```bash
python scripts/seed_demo.py
```

此腳本會自動執行：
1. 生成 20 份模擬供應商合約 (PDF + DOCX)
2. 建立向量索引 (ChromaDB) + 關鍵字索引 (BM25)
3. 建立知識圖譜 (若 Neo4j 可用，否則自動跳過)

### 方式二：分步執行

```bash
# Step 1: 生成測試合約
python scripts/generate_contracts.py

# Step 2: 建立搜尋索引 (需要 OpenAI API Key)
python scripts/build_index.py

# Step 3: 建立知識圖譜 (選配，需要 Neo4j)
python scripts/build_graph.py
```

### 方式三：使用 Make

```bash
make seed-demo
```

---

## 5. 啟動應用程式

```bash
streamlit run contractiq/ui/app.py
```

或：

```bash
make run
```

啟動後瀏覽器會自動開啟 `http://localhost:8501`。

---

## 6. 頁面功能說明

應用程式共有 **7 個頁面**，透過左側 sidebar 導航：

### Home — 系統總覽

![Home](./demo/screenshots/00_home.png)

- 功能特色一覽表
- 側邊欄顯示系統狀態 (已索引 chunks 數、文件數、Neo4j 連線狀態)
- Getting Started 快速指引

---

### Chat Q&A — 合約智慧問答

![Chat](./demo/screenshots/01_chat.png)

- 自然語言提問，例如：「供應商 Acme 的違約條款是什麼？」
- **側邊欄開關：**
  - **GraphRAG** — 啟用知識圖譜增強回答 (需要 Neo4j)
  - **Query Rewriting** — LLM 自動優化查詢語句
  - **Multi-Query** — 複雜問題自動拆解為子查詢
  - **Cross-Encoder Reranking** — 使用交叉編碼器精排結果
- 每個回答附帶**信心分數** (綠/橙/紅) 和**來源引用** (可展開查看原文)

---

### Upload — 合約上傳與索引

![Upload](./demo/screenshots/02_upload.png)

- **拖放上傳** PDF / DOCX 合約文件
- **索引設定：**
  - 分塊策略選擇 (recursive / semantic / clause_aware)
  - GPT-4o 元資料提取開關 (供應商名稱、合約類型、日期、金額等)
- **Index Sample Contracts** — 一鍵索引範例合約
- **Danger Zone** — 重置所有索引

---

### Comparison — 跨合約比較

![Comparison](./demo/screenshots/03_comparison.png)

- 選擇多個供應商進行條款對比
- 比較維度：付款條件、終止條款、責任限額、保固期、保密期限、服務水準
- 產出結構化比較表格 + 分析摘要

---

### Compliance — 合規儀表板

![Compliance](./demo/screenshots/04_compliance.png)

- 自動檢查 16 項必要條款 (8 critical + 4 major + 4 minor)
- **兩階段檢查：** 關鍵字預篩 → GPT-4o 語義驗證
- 風險評分 (0-100) + 缺漏條款標記 + 改善建議
- 支援單份或批量合約檢查

---

### Knowledge Graph — 知識圖譜

![Knowledge Graph](./demo/screenshots/05_knowledge_graph.png)

- **互動式圖譜視覺化** (Supplier → Contract → Clause → Obligation)
- 預設查詢：所有供應商、供應商合約、條款關係、全域總覽
- 支援自訂 Cypher 查詢
- 需要 Neo4j 運行中 (參見第 7 節)

---

### Evaluation — RAG 品質評估

![Evaluation](./demo/screenshots/06_evaluation.png)

- **RAGAS 四大指標：**
  - Faithfulness (忠實度) — 回答是否忠於來源
  - Answer Relevancy (答案相關性) — 回答是否切題
  - Context Precision (上下文精確度) — 檢索結果是否精確
  - Context Recall (上下文召回率) — 是否找到所有相關段落
- 門檻值：0.80 (高於為通過)
- 一鍵執行評估並儲存結果

---

## 7. Neo4j 知識圖譜 (選配)

Knowledge Graph 和 GraphRAG 功能需要 Neo4j。未安裝時其他功能仍可正常使用。

### 使用 Docker 啟動

```bash
docker run -d \
  --name contractiq-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 驗證連線

- 瀏覽器開啟 `http://localhost:7474`
- 帳號：`neo4j` / 密碼：`password`

### 建立圖譜

```bash
python scripts/build_graph.py
```

---

## 8. 測試與驗證

```bash
# 執行完整測試 (29 個測試)
pytest tests/ -v --cov=contractiq

# 僅執行特定模組
pytest tests/test_chunking.py -v       # 分塊策略
pytest tests/test_compliance.py -v     # 合規檢查
pytest tests/test_hybrid_retriever.py  # 混合檢索
```

---

## 9. 常見問題

### Q: Python 3.14 出現 ChromaDB 錯誤？

ChromaDB 內部使用 Pydantic v1，與 Python 3.14 不相容。請使用 **Python 3.12**：

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Q: `scikit-network` 安裝失敗？

此為 RAGAS 的間接依賴，需要 Microsoft Visual C++ Build Tools。安裝方式：

1. 前往 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. 安裝「使用 C++ 的桌面開發」工作負載
3. 重新執行 `pip install -r requirements.txt`

若不需要 RAGAS 評估功能，可暫時移除 `ragas>=0.2.0`。

### Q: Neo4j 連不上？

- 確認 Docker 容器正在運行：`docker ps`
- 確認 `.env` 中的 `CIQ_NEO4J_URI`、帳號密碼設定正確
- Neo4j 功能為選配，未啟動不影響其他功能

### Q: OpenAI API 呼叫失敗？

- 確認 `.env` 中的 `CIQ_OPENAI_API_KEY` 正確
- 確認 API key 有足夠額度
- 合約生成 (`generate_contracts.py`) 和測試 (`pytest`) 不需要 API key

### Q: 如何重置所有資料？

```bash
make clean
```

或手動刪除：

```bash
rm -rf data/chroma_db data/bm25_index.pkl data/contracts/sample/*
```
