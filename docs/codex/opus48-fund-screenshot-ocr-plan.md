# Opus48 基金截圖 OCR 匯入與報告板型改修計畫

> 給 Codex 執行用文件。  
> 模組：`/opus48`  
> 目標：讓使用者用「基金截圖」匯入投資項目，透過 Google AI OCR 轉成標準資料，供 Opus48 板型讀取並產出資產配置與調整報告。

---

## 1. 目前服務狀態與連線資訊

目前 TUFA16 前後端服務狀態如下：

| 服務 | 本機網址 | 狀態 |
|---|---|---|
| 前台 Vite | `http://localhost:5174/antiG/` | HTTP 200 OK |
| Opus48 模組 | `http://127.0.0.1:5174/opus48` | 待改修模組 |
| 後台 Flask | `http://localhost:5000` | 持續運行中 |

Vite 已確認監聽：

```text
0.0.0.0:5174
```

手機透過 Tailscale 存取時，正確 IP 為：

```text
http://100.70.207.69:5174/opus48
```

注意：先前誤打成 `100.7.207.69`，會造成 Chrome 顯示 `ERR_ADDRESS_UNREACHABLE`。

---

## 2. 使用者需求摘要

使用者希望 `/opus48` 模組支援以下流程：

```text
基金截圖 / 投資組合截圖
   ↓
上傳至 Opus48
   ↓
Google AI OCR 解析截圖
   ↓
轉成標準 portfolio_snapshot JSON
   ↓
使用者在前端確認與修正資料
   ↓
板型讀取 normalized JSON
   ↓
輸出資產配置、損益、風險集中度與調整報告
```

核心要求：

1. 不要讓報告卡片直接讀 OCR raw text。
2. OCR 後必須先轉成穩定 JSON schema。
3. 使用者必須能在前端修正辨識錯誤。
4. 報告板型只能讀取確認後的 `portfolio_snapshot`。
5. 報告語氣要是「資產配置分析框架」，避免直接投顧式買賣指令。

---

## 3. 建議新增功能

### 3.1 `/opus48` 前端新增區塊

新增「投資截圖匯入」區塊：

```text
上傳基金截圖 / 投資組合截圖
```

支援格式：

```text
.jpg
.jpeg
.png
.webp
```

使用者操作流程：

```text
1. 上傳基金或投資組合截圖
2. 系統呼叫後端 OCR API
3. 前端顯示辨識結果表格
4. 使用者可手動修正基金名稱、成本、現值、損益、報酬率、配置比例
5. 使用者按「確認資料」
6. 使用者按「產生 Opus48 報告」
```

---

## 4. 標準資料格式：portfolio_snapshot

OCR 後必須轉成以下標準 JSON。前端板型與後端報告都應依賴此格式。

```json
{
  "snapshot_date": "2026-06-24",
  "source": "fund_screenshot",
  "currency": "TWD",
  "holdings": [
    {
      "name": "安聯 AI 基金",
      "raw_name": "安聯AI人工智慧基金",
      "category": "科技主題股票",
      "currency": "TWD",
      "cost_amount": 120000,
      "market_value": 132500,
      "unrealized_pnl": 12500,
      "return_pct": 10.42,
      "allocation_pct": 32.5,
      "units": null,
      "nav": null,
      "risk_tag": "high_growth",
      "confidence": 0.93
    },
    {
      "name": "貝萊德黃金基金",
      "raw_name": "貝萊德世界黃金基金",
      "category": "黃金 / 原物料",
      "currency": "TWD",
      "cost_amount": 80000,
      "market_value": 76000,
      "unrealized_pnl": -4000,
      "return_pct": -5.0,
      "allocation_pct": 18.6,
      "units": null,
      "nav": null,
      "risk_tag": "commodity_hedge",
      "confidence": 0.91
    }
  ],
  "totals": {
    "cost_amount": 200000,
    "market_value": 208500,
    "unrealized_pnl": 8500,
    "return_pct": 4.25
  },
  "warnings": [
    "部分欄位由 OCR 推估，請使用者確認"
  ]
}
```

### 4.1 欄位說明

| 欄位 | 說明 |
|---|---|
| `snapshot_date` | 截圖資料日期，若 OCR 無法辨識則為 `null` |
| `source` | 固定可先用 `fund_screenshot` |
| `currency` | 整體幣別，預設可先用 `TWD` |
| `holdings[]` | 投資項目清單 |
| `name` | 正規化後基金名稱 |
| `raw_name` | OCR 原始辨識名稱 |
| `category` | 基金分類，可由規則推估 |
| `cost_amount` | 投資成本 |
| `market_value` | 目前市值 / 現值 |
| `unrealized_pnl` | 未實現損益 |
| `return_pct` | 報酬率百分比，不含 `%` 符號 |
| `allocation_pct` | 投資組合占比，不含 `%` 符號 |
| `units` | 單位數，無資料則 `null` |
| `nav` | 淨值，無資料則 `null` |
| `risk_tag` | 風險標籤 |
| `confidence` | OCR / 結構化可信度 |
| `totals` | 總成本、總現值、總損益、總報酬率 |
| `warnings` | 辨識警示與資料缺漏提示 |

---

## 5. 後端 API 設計

### 5.1 OCR 匯入 API

```http
POST /api/opus48/ocr
Content-Type: multipart/form-data
```

輸入：

| 欄位 | 型別 | 說明 |
|---|---|---|
| `file` | image | 使用者上傳的基金截圖 |

回傳：

```json
{
  "ok": true,
  "ocr_text": "原始 OCR 文字",
  "portfolio_json": {
    "snapshot_date": null,
    "source": "fund_screenshot",
    "currency": "TWD",
    "holdings": [],
    "totals": {
      "cost_amount": null,
      "market_value": null,
      "unrealized_pnl": null,
      "return_pct": null
    },
    "warnings": []
  }
}
```

### 5.2 儲存確認後快照

```http
POST /api/opus48/snapshot
Content-Type: application/json
```

用途：儲存使用者修正後的 `portfolio_snapshot`。

可先以檔案方式儲存：

```text
data/opus48/portfolio_snapshot_latest.json
```

後續再考慮 SQLite 或資料庫。

### 5.3 產生報告

```http
POST /api/opus48/report
Content-Type: application/json
```

輸入：

```json
{
  "portfolio_snapshot": {}
}
```

回傳：

```json
{
  "ok": true,
  "summary": "目前投資組合偏向科技成長型，黃金作為避險部位...",
  "cards": {
    "total": {},
    "allocation": [],
    "risk": [],
    "adjustment": []
  },
  "report_markdown": "..."
}
```

---

## 6. Google AI OCR Prompt

後端呼叫 Gemini Vision / Google AI 時，請使用嚴格 JSON prompt。

```text
你是基金投資組合截圖 OCR 解析器。

請從圖片中辨識所有投資項目，並轉成 JSON。
只輸出 JSON，不要輸出解釋文字。

請盡量辨識以下欄位：
- 基金名稱
- 幣別
- 投資成本
- 現值
- 損益
- 報酬率
- 配置比例
- 單位數
- 淨值
- 日期

如果圖片沒有該欄位，請填 null。
數字請移除逗號與貨幣符號，轉成 number。
百分比請轉成 number，例如 10.5% 輸出 10.5。
若辨識不確定，confidence 請低於 0.8。

請輸出格式：
{
  "snapshot_date": null,
  "source": "fund_screenshot",
  "currency": null,
  "holdings": [
    {
      "name": "",
      "raw_name": "",
      "category": null,
      "currency": null,
      "cost_amount": null,
      "market_value": null,
      "unrealized_pnl": null,
      "return_pct": null,
      "allocation_pct": null,
      "units": null,
      "nav": null,
      "risk_tag": null,
      "confidence": 0.0
    }
  ],
  "totals": {
    "cost_amount": null,
    "market_value": null,
    "unrealized_pnl": null,
    "return_pct": null
  },
  "warnings": []
}
```

---

## 7. 前端板型建議

`/opus48` 可拆成以下卡片：

```text
1. OCR 上傳卡
2. 投資項目修正表
3. 總資產摘要卡
4. 基金配置卡
5. 風險集中度卡
6. 調整建議卡
7. Markdown 報告輸出區
```

所有卡片都應從同一份資料讀取：

```js
portfolioSnapshot.holdings
portfolioSnapshot.totals
portfolioSnapshot.warnings
```

範例：

```js
const holdings = portfolioSnapshot.holdings || [];

const totalMarketValue = holdings.reduce(
  (sum, h) => sum + Number(h.market_value || 0),
  0
);

const highGrowthFunds = holdings.filter(
  (h) => h.risk_tag === "high_growth"
);

const lowConfidenceRows = holdings.filter(
  (h) => Number(h.confidence || 0) < 0.8
);
```

---

## 8. 風險標籤規則建議

可先用簡單 keyword rule，不需一開始就做複雜分類模型。

| 關鍵字 | `category` | `risk_tag` |
|---|---|---|
| AI、科技、半導體、納斯達克、創新 | 科技主題股票 | `high_growth` |
| 黃金、礦業、貴金屬 | 黃金 / 原物料 | `commodity_hedge` |
| 債、收益、固定收益 | 債券 / 收益 | `defensive_income` |
| 環球資產配置、平衡、配置 | 平衡 / 多資產 | `balanced_core` |
| 歐洲、日本、新興市場、印度 | 區域股票 | `regional_equity` |
| 高股息、收益、入息 | 收益型股票 | `income_equity` |

---

## 9. 報告輸出原則

報告內容應分為：

### 9.1 資產配置

說明目前組合偏向：

```text
科技成長
全球核心
黃金避險
債券防禦
區域押注
現金部位
```

### 9.2 集中度

檢查：

```text
科技 / AI 類基金是否過高
單一產業是否過高
黃金是否只是避險而非主核心
債券下降後防禦性是否不足
全球核心是否不足
```

### 9.3 損益狀態

說明：

```text
哪些基金獲利
哪些基金虧損
哪些基金是避險用途，不應只用短線績效判斷
```

### 9.4 調整建議

使用框架式語氣：

```text
保留
觀察
降低比重
補全球核心
不建議再加碼
```

避免輸出：

```text
明天買進
立刻賣出
保證獲利
一定上漲
```

---

## 10. Codex 執行任務

請 Codex 依照以下任務進行最小可行版本改修。

```text
請修改 opus48 模組，加入基金截圖 OCR 匯入功能。

需求：
1. 在 /opus48 頁面新增「上傳投資截圖」區塊。
2. 支援上傳 jpg/png/webp 圖片。
3. 前端呼叫 POST /api/opus48/ocr。
4. 後端 Flask 使用 Google Gemini Vision OCR 讀取圖片。
5. OCR 結果必須轉成標準 portfolio_snapshot JSON：
   - snapshot_date
   - source
   - currency
   - holdings[]
   - totals
   - warnings
6. 前端顯示可編輯表格，讓使用者修正：
   - 基金名稱
   - 成本
   - 現值
   - 損益
   - 報酬率
   - 配置比例
   - 幣別
   - 分類
7. 使用者按下「產生報告」後，前端依 JSON 產出：
   - 總資產摘要
   - 投資項目表
   - 資產配置卡
   - 風險集中度卡
   - 調整建議報告
8. 不要讓報告卡片直接讀 OCR raw text，必須讀 normalized JSON。
9. 若 OCR confidence 低於 0.8，該列在前端標示為「需要確認」。
10. 保留原本 /opus48 頁面功能，不破壞既有路由。
11. 若環境沒有 GEMINI_API_KEY，後端應回傳清楚錯誤，不要讓前端白畫面。
12. 新增一份 sample JSON，方便無 API key 時測試前端板型。

請先檢查現有專案結構，再新增最小可行版本。
```

---

## 11. 建議檔案位置

Codex 需先檢查實際專案結構，以下僅為建議：

```text
frontend/src/pages/Opus48.jsx
frontend/src/components/opus48/OcrUploadCard.jsx
frontend/src/components/opus48/HoldingsEditTable.jsx
frontend/src/components/opus48/PortfolioSummaryCards.jsx
frontend/src/components/opus48/PortfolioReport.jsx
backend/routes/opus48.py
backend/services/google_ocr_service.py
backend/services/portfolio_normalizer.py
data/opus48/sample_portfolio_snapshot.json
```

如果目前專案已有不同命名，請沿用既有架構，不要硬改目錄。

---

## 12. 驗收條件

完成後需確認：

```text
1. 開啟 http://127.0.0.1:5174/opus48 可正常顯示。
2. 手機可用 http://100.70.207.69:5174/opus48 開啟。
3. 上傳 jpg/png/webp 圖片不會造成前端錯誤。
4. 若無 GEMINI_API_KEY，前端顯示明確提示。
5. OCR 回傳後可看到 holdings 表格。
6. 使用者可手動修改表格資料。
7. 按下產生報告後，報告卡片讀取 normalized JSON。
8. confidence < 0.8 的資料會標記需要確認。
9. 原本 /antiG 模組不受影響。
10. 後端 Flask 仍可正常運行。
```

---

## 13. 最小測試資料

可建立：

```text
data/opus48/sample_portfolio_snapshot.json
```

內容：

```json
{
  "snapshot_date": "2026-06-24",
  "source": "sample",
  "currency": "TWD",
  "holdings": [
    {
      "name": "貝萊德環球資產配置",
      "raw_name": "貝萊德環球資產配置",
      "category": "平衡 / 多資產",
      "currency": "TWD",
      "cost_amount": 100000,
      "market_value": 106000,
      "unrealized_pnl": 6000,
      "return_pct": 6.0,
      "allocation_pct": 30.0,
      "units": null,
      "nav": null,
      "risk_tag": "balanced_core",
      "confidence": 0.98
    },
    {
      "name": "安聯 AI 基金",
      "raw_name": "安聯 AI 基金",
      "category": "科技主題股票",
      "currency": "TWD",
      "cost_amount": 120000,
      "market_value": 132000,
      "unrealized_pnl": 12000,
      "return_pct": 10.0,
      "allocation_pct": 37.0,
      "units": null,
      "nav": null,
      "risk_tag": "high_growth",
      "confidence": 0.94
    },
    {
      "name": "貝萊德黃金基金",
      "raw_name": "貝萊德黃金基金",
      "category": "黃金 / 原物料",
      "currency": "TWD",
      "cost_amount": 80000,
      "market_value": 76000,
      "unrealized_pnl": -4000,
      "return_pct": -5.0,
      "allocation_pct": 21.0,
      "units": null,
      "nav": null,
      "risk_tag": "commodity_hedge",
      "confidence": 0.91
    },
    {
      "name": "PIMCO 全球債券",
      "raw_name": "PIMCO 全球債券",
      "category": "債券 / 收益",
      "currency": "TWD",
      "cost_amount": 40000,
      "market_value": 41000,
      "unrealized_pnl": 1000,
      "return_pct": 2.5,
      "allocation_pct": 12.0,
      "units": null,
      "nav": null,
      "risk_tag": "defensive_income",
      "confidence": 0.89
    }
  ],
  "totals": {
    "cost_amount": 340000,
    "market_value": 355000,
    "unrealized_pnl": 15000,
    "return_pct": 4.41
  },
  "warnings": []
}
```

---

## 14. 實作注意事項

1. OCR 結果很容易把負數看錯，尤其是 `-12,500` 與 `12,500`，因此前端確認表格必要。
2. 基金名稱可能出現錯字，例如「貝萊德」被辨識成「貝菜德」，需保留 `raw_name` 與 `name`。
3. 百分比欄位要統一存 number，不要存字串。
4. 金額欄位要移除逗號與幣別符號。
5. 若總數與明細加總不一致，請在 `warnings` 加入提示。
6. 報告輸出不可依賴 OCR raw text。
7. 原始 OCR text 可以保留供 debug，但不可作為報告主資料來源。
8. 若使用者未確認資料，不建議產生正式報告，可先顯示「草稿分析」。

---

## 15. 本次文件結論

`/opus48` 應改造成「投資截圖轉報告」模組：

```text
Google AI OCR
→ 標準投資 JSON
→ 使用者確認修正
→ 板型讀資料
→ 產出 Opus48 報告
```

此設計未來可擴充到：

```text
基金截圖
ETF 截圖
股票庫存截圖
債券部位截圖
保單投資帳戶截圖
```

同一套 `portfolio_snapshot` 可以讓前端板型穩定讀取，避免每次因 OCR 文字格式不同而破壞報告輸出。
