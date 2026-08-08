# AI-IDE 官方資源

[AI-IDE](https://apps.apple.com/app/id6752530533) 的官方預設來源。裡面是可以直接在 App 裡瀏覽並安裝的分享檔。

在 App 中：**設定 → 分享資源**。這個來源預設就在清單裡，也可以移除——它是起點，不是守門員。

## 內容

| 目錄 | 型別 | 副檔名 |
|---|---|---|
| `prompts/` | Prompt 庫的指令 | `.aiide-prompt` |
| `styles/` | 文件匯出風格範本 | `.aiide-style` |
| `kb/` | KB 庫條目包 | `.aiide-kb` |
| `tools/` | 給分享者用的驗證／索引產生腳本 | — |

`aiide-index.json` 是選用的加速檔：有它，App 掃描這個 repo 時就不必逐檔抓 manifest。它不是必要條件——沒有索引的來源一樣掃得出來。

## 檔案格式

完整規格見 **[FORMAT.md](FORMAT.md)**。摘要：

- **`.aiide-prompt`** — Markdown。manifest 放在**第一個** `---` front matter 區塊，指令內文原封不動接在後面，所以一個自己就有 front matter 的 prompt（例如宣告 `requires:` 的）完好無損。**一個檔案恰好一個指令。**
- **`.aiide-style`** — JSON，頂層是 manifest，`styles` 陣列裡每一則帶 `field`（`refine` / `illustration` / `slideImage`）、`title`、`body`。
- **`.aiide-kb`** — zip，含 `manifest.json` 與 `entries/*.md`。

副檔名可以被改，所以判斷一律以檔案內容與 manifest 的 `type` 為準。

## 想做自己的分享 repo？

不需要問任何人，也不需要 fork 這裡。照 **[FORMAT.md](FORMAT.md)** 放檔案、把 repo 網址貼進 App 的「設定 → 分享資源 → 新增來源…」就能用。

**掃描器不在乎你的資料夾怎麼分**——它會走遍整個 repo，只看副檔名和檔案內容。上面的目錄結構純粹是給人看的。

推上去之前跑一次驗證：

```bash
python3 tools/aiide-index.py /path/to/your/repo
```

它會用 AI-IDE 讀檔的方式檢查每一個檔案，全部通過才寫出 `aiide-index.json`；有問題會告訴你是哪一個、為什麼。

## 投稿

歡迎 PR。請確認：

1. **授權欄位是真的。** 從別處取得的書籍、報告、付費資料或公司內部文件**不能**放進來——KB 這一類尤其要小心。
2. **沒有可執行內容**：沒有腳本、沒有巨集、沒有會自動請求的外部網址。
3. `id` 用 `<你的名字>.<項目名>` 的形式，改內容時記得升 `version`。
4. 如果你動了 `prompts/`、`styles/` 或 `kb/`，跑 `python3 tools/aiide-index.py .` 重新產生 `aiide-index.json`。

Prompt 的內文會進入使用者之後每一輪對話的最前面，所以 App 在安裝前一定會把全文顯示給使用者看，而且一次只裝一個。請假設每一個字都會被讀到。

## 授權

程式碼與索引依 [MIT](LICENSE)。各項目的授權以各自 manifest 的 `license` 欄位為準。
