# 分享來源格式

把你的 repo 做成 AI-IDE 可以讀的分享來源。沒有註冊、沒有審核、沒有中央伺服器——使用者在 App 裡貼上你的 repo 網址就能看到你放的東西。

在 App 中：**設定 → 分享資源 → 新增來源…**，貼上 `https://github.com/你的帳號/你的repo`。

---

## 1. 最小可行範例

一個能被讀到的 repo，最少只需要一個檔案：

```
你的repo/
└── my-prompt.aiide-prompt
```

內容：

```
---
format: 1
type: prompt
title: 我的指令
---

你是一位……
```

推到 GitHub、把 repo 網址貼進 App，這個項目就會出現在瀏覽頁。就這樣。

---

## 2. 掃描器實際上怎麼找檔案

這一段值得先讀，因為它會讓你少做很多不必要的事。

| | |
|---|---|
| **repo 必須是公開的** | 私有 repo 讀不到（App 不會要你的 token，見 §7） |
| **分支** | 預設試 `main`，再試 `master`。其他分支要使用者貼 `.../tree/分支名` 的網址 |
| **哪些檔案會被看到** | **整個 repo、任何深度**，凡是副檔名符合的檔案 |
| **資料夾名稱** | **不影響掃描。** 下面的建議結構純粹是給人看的 |
| **一次掃描的上限** | 沒有索引時最多讀 200 個檔案；超過的部分會在畫面上明說「另有 N 個未讀取」 |

也就是說：**資料夾怎麼分是你的自由**，掃描器只看副檔名和檔案內容。

### 副檔名

| 副檔名 | 內容 | 現在可安裝 |
|---|---|---|
| `.aiide-prompt` | 一個 Prompt 指令 | ✅ |
| `.aiide-style` | 一組文件匯出風格範本 | ✅ |
| `.aiide-kb` | 一包 KB 條目 | ✅ |
| `.aiide-brand` | 品牌套件 | 尚未 |
| `.aiide-pdf` / `.aiide-word` / `.aiide-excel` / `.aiide-slides` | 匯出樣板 | 尚未 |

後面五種現在還不能安裝，但**會被認出來並計數**——使用者看到的是「3 個項目需要更新 App」，不是「這個來源好像沒東西」。所以現在就放進去是安全的。

**副檔名只用來找候選檔案，決定型別的是檔案內容的 `type` 欄位。** 一個被改名成 `.aiide-style` 的 KB 包會被拒絕，不會被當成風格安裝。

---

## 3. 建議的資料夾結構

掃描器不在乎，但別人來看你的 repo 時會在乎：

```
你的repo/
├── README.md              ← 你是誰、這裡有什麼
├── LICENSE
├── aiide-index.json       ← 選用，但強烈建議（見 §5）
├── prompts/
│   ├── research-assistant.aiide-prompt
│   └── doc-proofread.aiide-prompt
├── styles/
│   └── deck-teaching.aiide-style
└── kb/
    └── my-guide.aiide-kb
```

---

## 4. 三種檔案格式

三種都帶同一份 **manifest**，欄位一致：

| 欄位 | 必填 | 說明 |
|---|---|---|
| `format` | **是** | 整數 `1`。這是「讀不讀得懂」的判斷，不是語意版本 |
| `type` | **是** | `prompt` / `style` / `kb` |
| `title` | 建議 | 列表上顯示的名稱。缺了會退而求其次（見各型別） |
| `summary` | 建議 | 一行說明，列表上顯示這一句 |
| `author` | 建議 | 你的名字 |
| `license` | **強烈建議** | 見 §7。App 內匯出時這一欄是必填的 |
| `appMinVersion` | 建議 | 目前寫 `1.15.0` |
| `id` | 建議 | `你的名字.項目名`，例如 `usagi.research-assistant`。**有 `id` 的項目，你之後把檔案搬到別的資料夾也還認得出來**；沒有的話搬家等於換了一個項目 |
| `version` | **強烈建議** | 改內容時**一定要升**。見 §4.4 |

缺少 `title` / `author` / `license` 不會讓檔案被拒收——只有 `format` 與 `type` 是硬性的。

### 4.4 更新：不升 `version`，使用者就收不到通知

App 判斷「有沒有新版」時，只用掃描已經知道的東西——比對內容意味著每次重新整理都要把使用者已安裝的每一個項目重新下載一遍。所以：

| 你做的事 | 使用者看到 |
|---|---|
| 改了內容，**升了 `version`** | **「有新版 1.1.0」**，可以一鍵更新 |
| 改了內容，沒升 `version`，但檔案大小變了 | 「可能有更新」（App 明說這是猜的） |
| 改了內容，沒升 `version`，大小剛好一樣 | **什麼都沒有。使用者永遠不會知道。** |

比對是「不相等」，不是「比較大小」——你退回 1.0.0 也算是使用者手上沒有的東西，一樣會通知。

另外兩件你該知道的事：

- **使用者改過的那一份不會被你覆蓋。** App 記得安裝當下寫進去的內容雜湊；對得上才會就地取代，對不上就只提示，並讓使用者自己選「另存為新的一份」或「仍要覆蓋」。
- **更新 prompt 會保留它在使用者那邊的識別**，所以他原本啟用著的指令，更新後仍然是啟用的。

### 4.1 `.aiide-prompt`（純文字）

Markdown 檔，manifest 放在**第一個** `---` front matter 區塊，指令內文原封不動接在後面。**一個檔案恰好一個指令。**

```
---
format: 1
type: prompt
id: yourname.research-assistant
version: 1.0.0
title: 研究助理（查證優先）
summary: 每個事實都要有來源；查不到就說查不到。
author: yourname
license: CC BY 4.0
appMinVersion: 1.15.0
---

# 研究助理

你是一位研究助理……
```

**你的指令可以自己有 front matter。** 這是刻意的：AISA skill 保留原樣，`requires:` 也住在那裡。讀取端只吃第一個區塊，所以第二個區塊完好無損：

```
---
format: 1
type: prompt
title: 銷售報告助理
---

---
name: sales-report
requires: 銷售資料.csv, 產品目錄.md
---

# 銷售報告

只根據附上的檔案作答……
```

- 沒有 `title` 時，取內文第一個 `#` 標題。
- 內文是空的會被拒收。
- 檔案上限 **1 MB**。
- 支援的 YAML 很小：扁平的 `key: value` 與 `[a, b]` 陣列。值裡有 `: # [ ] { } " ,` 或首尾空白時用雙引號包起來。

> **為什麼一檔一個指令**：Prompt 的內文會加在使用者之後**每一輪**對話的最前面。App 因此規定安裝前一定顯示全文、一次只裝一個、而且**不自動啟用**。一個能裝二十個的檔案會讓這條規則無法遵守。

### 4.2 `.aiide-style`（JSON）

頂層就是 manifest，加一個 `styles` 陣列：

```json
{
  "format": 1,
  "type": "style",
  "id": "yourname.deck-teaching",
  "version": "1.0.0",
  "title": "教學簡報組合",
  "summary": "上課用：慢一點、例子多一點。",
  "author": "yourname",
  "license": "CC BY 4.0",
  "appMinVersion": "1.15.0",
  "count": 2,
  "styles": [
    {
      "field": "refine",
      "title": "教學節奏",
      "body": "每頁一個觀念，最多 4 條。每個抽象說法後面接一個具體例子。"
    },
    {
      "field": "illustration",
      "title": "溫暖手繪",
      "body": "warm hand-drawn illustration, soft pencil texture, no text"
    }
  ]
}
```

`field` 只有三個值，**它決定這則範本會出現在哪一個欄位**：

| `field` | 對應設定 | 作用 |
|---|---|---|
| `refine` | AI 精鍊風格 | 文件怎麼被濃縮成投影片（每頁幾條、頁數、語氣） |
| `illustration` | 自動插圖風格 | 「自動插圖」生成的插圖長相 |
| `slideImage` | 整頁圖像風格 | 「整頁圖像」與「圖＋文字框」的視覺風格 |

- **不認得的 `field` 只會少掉那一則**，同檔的其他則照常匯入。所以未來新增欄位時，舊版 App 不會整包失敗。
- `body` 是空的那一則會被略過；沒有 `title` 會用內文第一行當名字。
- 檔案上限 **1 MB**。

### 4.3 `.aiide-kb`（zip）

副檔名是 `.aiide-kb`，內容是一個標準 zip：

```
manifest.json
entries/001-術語表.md
entries/002-會議記錄.md
```

`manifest.json`：

```json
{
  "format": 1,
  "type": "kb",
  "id": "yourname.brand-terms",
  "version": "1.0.0",
  "title": "品牌用語表",
  "summary": "對外文件的統一用字。",
  "author": "yourname",
  "license": "CC BY 4.0",
  "appMinVersion": "1.15.0",
  "count": 2
}
```

每個條目檔：

```
---
title: 術語表
summary: 品牌用語
tags: [品牌, style]
origin: terms.md
---

AI-IDE 一律寫作 AI-IDE，不寫成 AI IDE 或 AIIDE。
```

- **`entries/` 底下的 `.md` 才算條目**，其他檔案（README、LICENSE）會被忽略。
- 檔名建議加流水號前綴（`001-`），這樣**同名條目不會互相覆蓋**，而且 diff 讀起來有順序。
- 條目沒有 front matter **也能匯入**，標題會取第一行。內文空的那一筆會被略過。
- 匯入時以**內容雜湊**去重：同一個包傳兩次，第二次不會多出任何東西。
- 檔案上限 **10 MB**。

用 Markdown 而不是把文件塞進 JSON 字串，是為了讓這些檔案在 GitHub 上讀得下去、diff 得出來。

---

## 5. `aiide-index.json`（選用，但請放）

放在 **repo 根目錄**。有它的話，App 掃描你的 repo **完全不花 GitHub 的查詢額度**（未登入的使用者每小時只有 60 次，而且回 304 也照樣計費）。沒有它也能運作——索引是最佳化，不是必要條件。

```json
{
  "format": 1,
  "name": "某某的 AI-IDE 資源",
  "summary": "一行說明。",
  "homepage": "https://github.com/yourname/yourrepo",
  "items": [
    {
      "path": "prompts/research-assistant.aiide-prompt",
      "size": 1517,
      "format": 1,
      "type": "prompt",
      "id": "yourname.research-assistant",
      "version": "1.0.0",
      "title": "研究助理（查證優先）",
      "summary": "每個事實都要有來源。",
      "author": "yourname",
      "license": "CC BY 4.0",
      "appMinVersion": "1.15.0"
    }
  ]
}
```

每一筆是一個**扁平物件**：`path`（repo 相對路徑）、`size`（選用），加上那個檔案的 manifest 欄位並排放著。

- 壞掉的那一筆只會少掉它自己，不會讓整份索引作廢。
- **索引只是清單。** 使用者按下安裝時，App 會重新下載那個檔案並重新解析——所以索引過期不會裝錯東西，但列表會顯示不存在的項目、點進去才報錯。**改了檔案就重新產生索引。**

用 `tools/aiide-index.py` 產生，不要手寫：

```bash
python3 tools/aiide-index.py /path/to/your/repo
```

它會掃描資料夾、驗證每個檔案、把 `aiide-index.json` 寫回去；有任何檔案讀不過就會告訴你哪一個、為什麼。

---

## 6. 網頁也可以當來源

不想開 repo 也行：任何 HTML 頁面，只要裡面有指向 `.aiide-*` 檔案的 `<a href>` 連結，就能當成來源貼進 App。

```html
<a href="prompts/my-prompt.aiide-prompt">我的指令</a>
<a href="https://example.com/files/my-styles.aiide-style">我的風格</a>
```

相對路徑會依該頁網址解析。同樣最多讀 200 個。

---

## 7. 分享者請遵守的三件事

這三條不是禮貌，是這個機制能不能繼續存在的前提。

### 1. 授權欄位要是真的

**只分享你有權分享的內容。** KB 這一類尤其危險——它是最容易夾帶他人著作的型別。從別處取得的書籍、報告、付費資料或公司內部文件**不能**放進來。App 內匯出時 `license` 是必填的，就是為了逼每個人在按下分享之前先想過這件事。

### 2. 不要放任何可執行的東西

- 沒有腳本、沒有巨集（`.pptm` 一律拒收）
- 沒有會自動請求的外部網址

寫進格式規格，不靠審查。

### 3. Prompt 的內文會進入別人的每一輪對話

所以請假設**每一個字都會被讀到**——App 在安裝前一定會把全文顯示給使用者看。一份要求 AI「忽略先前指示」或連到外部網址的 prompt，會被使用者當場看見。

App 這一端對應的規則：一律不自動安裝、不自動更新、瀏覽是唯讀的，安裝永遠要人按下去。

---

## 8. 檢查清單

推上去之前：

- [ ] repo 是公開的，預設分支是 `main` 或 `master`
- [ ] 每個檔案的 `format` 是 `1`、`type` 正確
- [ ] `license` 是你真的有權給的授權
- [ ] `id` 用 `你的名字.項目名`；**改內容一定要升 `version`**（§4.4）
- [ ] 跑過 `python3 tools/aiide-index.py <你的repo>`，沒有錯誤
- [ ] 用 App 自己貼一次你的 repo 網址，確認看得到、裝得起來

最後一步別跳過。它是唯一會告訴你「別人看到的是什麼」的檢查。
