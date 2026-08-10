# styles/ — 文件匯出風格範本

這裡放 `.aiide-style`：一組文件匯出風格。安裝後，每一則 `styles[]` 會出現在 AI-IDE 對應的設定欄位（AI 精鍊風格／自動插圖風格／整頁圖像風格）。

本目錄同時是「怎麼設計一個好風格」的範例庫：

| 檔案 | 用途 | 適合誰 |
|---|---|---|
| `example-basic.zh-Hant` / `.en` | **入門範例**：三種 field 各一則，格式最簡，照著改就能做自己的風格 | 第一次寫風格的人 |
| `persona-teacher.zh-Hant` / `.en` | 教師工作包：教案結構、課程重點、課本插圖、教室投影 | 教師、講師 |
| `persona-researcher.zh-Hant` / `.en` | 研究員工作包：文獻彙整、資料整理、學術圖表、研討會發表 | 研究生、學者 |
| `persona-office.zh-Hant` / `.en` | 辦公室工作包：競品分析、產業調查、供應商分析、社群反應分析 | 上班族、PM、行銷 |
| `persona-student.zh-Hant` / `.en` | 學生學習包：學術搜尋彙整、資料整理、筆記塗鴉、課堂報告 | 學生 |

## 三個 field 的差別

| `field` | 對應設定 | body 怎麼寫 |
|---|---|---|
| `refine` | AI 精鍊風格 | 用**中文規則句**描述文件怎麼被濃縮成投影片：每頁幾條、頁數上限、結構順序、語氣。寫「要做什麼」而不是「不要什麼」。 |
| `illustration` | 自動插圖風格 | 用**英文 prompt**（生圖模型吃英文比較穩）：媒材、顏色、構圖、留白。結尾加 `no text` 防止模型亂畫字。 |
| `slideImage` | 整頁圖像風格 | 用**英文 prompt**：背景、主體、配色、留白位置（通常預留給文字的一側要明說）。同樣結尾 `no text`。 |

## 設計原則（範例庫的共同約定）

1. **以使用者類型打包**：每個 persona 一個檔案，把該角色常用的 refine、illustration、slideImage 放進同一個 `styles[]`，使用者安裝一次就拿到整套。`count` 與 `styles[]` 長度一致。
2. **refine 要具體到可以照做**：例如「每頁最多 3 條、先講結論再講依據」比「條理清晰」有用。描述結構與順序，讓 AI 知道每一頁怎麼長。
3. **生圖 body 用英文、結尾 `no text`**：模型對英文指示較穩，`no text` 避免出現亂碼文字。
4. **多語版本共用同一個 `id`**：`persona-teacher.zh-Hant` 與 `persona-teacher.en` 是同一項目的兩個語言（`lang` 不同、`id` 相同），App 會收成一列、依讀者語言顯示。改內容記得升 `version`。

## 發布流程

```bash
# 新增或修改 styles/ 之後，在 repo 根目錄重新產生索引（會用 App 的讀法驗證每個檔案）
python3 tools/aiide-index.py .

# 只驗證不寫入：
python3 tools/aiide-index.py . --check
```

索引有驗證過才會寫出；任一檔案讀不過就什麼都不寫。完整格式規格見 [FORMAT.md](../FORMAT.md)。
