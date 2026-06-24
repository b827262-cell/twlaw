# Opus48 基金截圖 OCR 匯入與報告板型改修執行紀錄

> 來源計畫：`docs/codex/opus48-fund-screenshot-ocr-plan.md`
> 目的：依計畫補上 `/opus48` 的基金截圖 OCR 匯入、`portfolio_snapshot` 正規化、報告輸出與 sample 資料。

## 執行背景

使用者提供的 `commit: 86ce9e3308624f252a98d521f633dd639bc9b477` 在 GitHub 上查得與 `master` 內容相同，沒有額外 diff 可直接套用，因此本次是直接依計畫文件實作。

## 既有狀態

- `/opus48` 已存在 React 頁面，原本是資產重整儀表板。
- `server/fund_ocr.ts` 已有基金截圖 OCR batch 流程。
- `src/components/FundOCRImport.tsx` 已有上傳、OCR、編輯、確認匯入流程。
- `vite.config.ts` 已有 `/api/funds/ocr/*` 路由。
- `data/portfolio.json` 是 `/opus48` 的既有資料來源。

## 實作內容

### 共用 snapshot 與報告模組

新增 [`src/lib/opus48Portfolio.ts`](/home/b822726/project/Anti-G-C1/src/lib/opus48Portfolio.ts)，負責：

- `portfolio_snapshot` 正規化
- `category` / `risk_tag` 推導
- `totals` 重算
- `warnings` 補齊
- 報告與 Markdown 產生

### 型別擴充

更新 [`src/types.ts`](/home/b822726/project/Anti-G-C1/src/types.ts)，新增：

- `PortfolioRiskTag`
- `PortfolioHolding`
- `PortfolioSnapshot`
- `PortfolioReport`

### 前端 OCR 匯入分頁

新增 [`src/components/Opus48PortfolioImport.tsx`](/home/b822726/project/Anti-G-C1/src/components/Opus48PortfolioImport.tsx)，提供：

- 圖片上傳與預覽
- 呼叫 `/api/opus48/ocr`
- 持倉表格編輯
- `confidence < 0.8` 的「需要確認」標示
- `確認資料` 與 `產生報告`
- sample snapshot 載入

並更新 [`src/components/Opus48Page.tsx`](/home/b822726/project/Anti-G-C1/src/components/Opus48Page.tsx)，在既有儀表板旁新增 `截圖匯入` 分頁。

### 後端路由

新增 [`server/opus48.ts`](/home/b822726/project/Anti-G-C1/server/opus48.ts)，並在 [`vite.config.ts`](/home/b822726/project/Anti-G-C1/vite.config.ts) 新增：

- `POST /api/opus48/ocr`
- `POST /api/opus48/snapshot`
- `POST /api/opus48/report`

### sample 與資料複製

- 新增 [`data/opus48/sample_portfolio_snapshot.json`](/home/b822726/project/Anti-G-C1/data/opus48/sample_portfolio_snapshot.json)
- 更新 [`package.json`](/home/b822726/project/Anti-G-C1/package.json) 的 `copy-data`，把 `data/opus48/*.json` 複製到 `public/data/opus48/`

### 樣式與編譯設定

- 更新 [`src/styles.css`](/home/b822726/project/Anti-G-C1/src/styles.css) 增加 snapshot、報告卡與低信心提示樣式
- 更新 [`tsconfig.node.json`](/home/b822726/project/Anti-G-C1/tsconfig.node.json)，讓 server 可共用 `src/lib` 與 `src/types`

## 驗證結果

已執行：

```bash
npm run build
```

結果：`tsc -b` 與 `vite build` 均通過。

## 結論

本次已完成：

- `/opus48` OCR 匯入流程
- `portfolio_snapshot` 正規化
- 使用者可編輯持倉
- 可產生框架式報告
- 可儲存 snapshot
- 提供 sample JSON
- 保留原本 `/opus48` 與 `/antiG` 功能
