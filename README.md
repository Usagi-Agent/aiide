# AI-IDE 官方資源

[AI-IDE](https://apps.apple.com/app/id6752530533) 的官方預設來源。裡面是可以直接在 App 裡瀏覽並安裝的分享檔。

在 App 中：**設定 → 分享資源**。這個來源預設就在清單裡，也可以移除——它是起點，不是守門員。

## 內容

| 目錄 | 型別 | 副檔名 |
|---|---|---|
| `prompts/` | Prompt 庫的指令 | `.aiide-prompt` |
| `styles/` | 文件匯出風格範本 | `.aiide-style` |
| `kb/` | KB 庫條目包 | `.aiide-kb` |

`aiide-index.json` 是選用的加速檔：有它，App 掃描這個 repo 時就不必逐檔抓 manifest。它不是必要條件——沒有索引的來源一樣掃得出來。

## 檔案格式

三種都帶同一份 manifest（`format` / `type` / `id` / `version` / `title` / `summary` / `author` / `license` / `appMinVersion`）：

- **`.aiide-prompt`** — Markdown。manifest 放在**第一個** `---` front matter 區塊，指令內文原封不動接在後面。因此一個自己就有 front matter 的 prompt（例如宣告 `requires:` 的）會成為第二個區塊而完好無損。**一個檔案恰好一個指令。**
- **`.aiide-style`** — JSON，頂層是 manifest，`styles` 陣列裡每一則帶 `field`（`refine` / `illustration` / `slideImage`）、`title`、`body`。
- **`.aiide-kb`** — zip，含 `manifest.json` 與 `entries/*.md`，每個條目一個 Markdown 檔（front matter 放 title / summary / tags / origin）。

副檔名可以被改，所以判斷一律以檔案內容與 manifest 的 `type` 為準。

**多語版本**：同一個 `id`、不同的 `lang`（`zh-Hant` / `zh-Hans` / `en`），檔名帶語言後綴當慣例。App 會把它們收成一列，顯示讀者語言的那一版。見 [FORMAT.md](FORMAT.md) §4.5。

## 投稿

歡迎 PR。請確認：

1. **授權欄位是真的。** 從別處取得的書籍、報告、付費資料或公司內部文件**不能**放進來——KB 這一類尤其要小心。
2. **沒有可執行內容**：沒有腳本、沒有巨集、沒有會自動請求的外部網址。
3. `id` 用 `<你的名字>.<項目名>` 的形式，改內容時記得升 `version`。
4. 如果你動了 `prompts/`、`styles/` 或 `kb/`，也更新 `aiide-index.json`。

Prompt 的內文會進入使用者之後每一輪對話的最前面，所以 App 在安裝前一定會把全文顯示給使用者看，而且一次只裝一個。請假設每一個字都會被讀到。

## 授權

程式碼與索引依 [MIT](LICENSE)。各項目的授權以各自 manifest 的 `license` 欄位為準。
