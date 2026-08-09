# AI-IDE 分享來源格式規格

**格式版本：`format: 1`**　　對應 App 版本：1.15.0 以上

把你的 repo 做成 AI-IDE 可以讀的分享來源。沒有註冊、沒有審核、沒有中央伺服器——使用者在 App 裡貼上你的 repo 網址就能看到你放的東西。

在 App 中：**設定 → 分享資源 → 新增來源…**，貼上 `https://github.com/你的帳號/你的repo`。

這份文件是完整規格：照著它做出來的檔案，AI-IDE 讀得到。文件裡凡是寫「會 / 不會 / 上限」的地方，都對應程式裡真實存在的判斷，不是建議。

---

## 目錄

| | |
|---|---|
| [§1](#1-最小可行範例) | 最小可行範例 |
| [§2](#2-掃描器實際上怎麼找檔案) | 掃描器實際上怎麼找檔案（含快取、上限、可貼的網址形式） |
| [§3](#3-建議的資料夾結構) | 建議的資料夾結構 |
| [§4](#4-三種檔案格式) | manifest 與三種檔案格式（含編碼規則、YAML 子集、`version` / `lang` / `example`） |
| [§5](#5-aiide-indexjson選用但請放) | `aiide-index.json` |
| [§6](#6-網頁也可以當來源) | 網頁來源 |
| [§6a](#6a-一鍵安裝連結) | 一鍵安裝連結 |
| [§7](#7-分享者請遵守的三件事) | 分享者請遵守的三件事 |
| [§8](#8-推上去前的檢查清單) | 檢查清單 |
| [§9](#9-疑難排解) | 疑難排解 |
| [§10](#10-相容性承諾) | 相容性承諾與保留型別 |
| [附錄 A](#附錄-a三個可直接複製的完整範例) | 三個可直接複製的完整範例 |

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

實務上你會想再加 `id`、`version`、`license`、`author`（§4）。但硬性條件只有 `format` 和 `type` 兩個。

---

## 2. 掃描器實際上怎麼找檔案

這一段值得先讀，因為它會讓你少做很多不必要的事。

| | |
|---|---|
| **repo 必須是公開的** | 私有 repo 讀不到（App 不會要你的 token，見 §7） |
| **分支** | 預設試 `main`，再試 `master`。其他分支要使用者貼 `.../tree/分支名` 的網址 |
| **哪些檔案會被看到** | **整個 repo、任何深度**，凡是副檔名符合的檔案 |
| **資料夾名稱** | **不影響掃描。** §3 的建議結構純粹是給人看的 |
| **一次掃描的上限** | 沒有索引時最多讀 200 個檔案；超過的部分會在畫面上明說「另有 N 個未讀取」 |
| **列表排序** | 依 `title` 排序（在地化比較）。你無法指定順序，也不需要用 `01-` 前綴去排 |
| **檔名可以用中文** | 路徑會正確編碼。限制只在 **帳號名與 repo 名**（見下方「可以貼的網址」） |

也就是說：**資料夾怎麼分是你的自由**，掃描器只看副檔名和檔案內容。

### 2.1 快取：推上去之後不會立刻出現

**掃描結果快取一小時。** 使用者在瀏覽頁按「重新整理」會強制重掃，但不按的話，你剛推的更新最久要一小時才會出現。App 也**不會在啟動時自動掃描**任何來源。

這不是為了省事：GitHub 對未登入的使用者是每小時 60 次查詢，而且**回 304 也照樣計費**——所以「只是看看有沒有變」並不便宜，不能放在計時器上。

你自己在測試時，記得按重新整理，不要以為沒生效。

### 2.2 可以貼的網址

以下每一種使用者貼進去都會被認成同一個 repo：

```
https://github.com/owner/repo
https://github.com/owner/repo.git
https://github.com/owner/repo/tree/main
https://github.com/owner/repo/tree/某分支          ← 指定分支的唯一方法
https://raw.githubusercontent.com/owner/repo/main/…
owner/repo
```

**`owner` 與 `repo` 只允許 `A-Z a-z 0-9 . _ -`。** 這是安全限制（這兩段字串會被組進我們去抓的網址），不是風格偏好。GitHub 本來就不允許其他字元，所以正常情況你不會遇到。

不是 GitHub 的網址，會被當成**網頁來源**處理（§6）。

### 2.3 副檔名

| 副檔名 | 內容 | 現在可安裝 |
|---|---|---|
| `.aiide-prompt` | 一個 Prompt 指令 | ✅ |
| `.aiide-style` | 一組文件匯出風格範本 | ✅ |
| `.aiide-kb` | 一包 KB 條目 | ✅ |
| `.aiide-brand` | 品牌套件 | 尚未 |
| `.aiide-pdf` / `.aiide-word` / `.aiide-excel` / `.aiide-slides` | 匯出樣板 | 尚未 |

後面五種現在還不能安裝，但**會被認出來並計數**——使用者看到的是「3 個項目需要更新 App」，不是「這個來源好像沒東西」。所以現在就放進去是安全的。

副檔名比對**不分大小寫**（`.AIIDE-PROMPT` 也讀得到），但請一律小寫。

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
│   ├── research-assistant.zh-Hant.aiide-prompt
│   └── doc-proofread.zh-Hant.aiide-prompt
├── styles/
│   └── deck-teaching.zh-Hant.aiide-style
└── kb/
    └── my-guide.zh-Hant.aiide-kb
```

檔名裡的 `.zh-Hant` 是給人看的慣例，見 §4.6。

---

## 4. 三種檔案格式

### 4.0 三種檔案共通的規則

**編碼與行尾——這一條最容易踩到：**

| | |
|---|---|
| 編碼 | **UTF-8**，**不要 BOM**。解不出 UTF-8 的檔案會被整個拒收 |
| 行尾 | **LF（`\n`）**。純文字格式的 manifest 必須從檔案的第一個位元組開始、正好是 `---` 加換行；**CRLF（`\r\n`）會讓整份 manifest 讀不到**，檔案就變成「不是一個有效的分享檔」 |
| 開頭 | `---` 之前不能有空行、空白或註解 |

Windows 上編輯時請確認編輯器是 LF；`.gitattributes` 裡如果有 `* text=auto` 而你的工作目錄是 CRLF，推上去的內容通常仍是 LF（Git 會轉回來），但**直接用網頁介面貼上、或用會強制 CRLF 的工具產生**就會壞。不確定的話跑一次 §5 的檢查工具。

**其他共通規則：**

- **不認得的欄位一律忽略**，不會讓檔案失敗。你可以放自己的欄位，但別期待 App 會顯示它。
- `title` 也接受寫成 `name`（早期檔案的相容別名）。兩個都有時以 `title` 為準。
- 檔案大小上限見各型別；超過就整份拒收，不會截斷。

### 4.1 manifest 欄位（三種格式共用）

三種檔案都帶同一份 **manifest**，欄位完全一致，只是放的位置不同（front matter／JSON 頂層／`manifest.json`）。

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| `format` | 整數 | **是** | 一定是 `1`。這是「讀不讀得懂」的判斷，不是語意版本。比對**相等**，不是大小——寫 `2` 的檔案今天的 App 一律拒收 |
| `type` | 字串 | **是** | `prompt` / `style` / `kb`。必須和檔案實際內容相符 |
| `title` | 字串 | 建議 | 列表上顯示的名稱。缺了會退而求其次（見各型別） |
| `summary` | 字串 | 建議 | 一行說明，列表與安裝畫面都會顯示 |
| `author` | 字串 | 建議 | 你的名字。安裝畫面會顯示 |
| `license` | 字串 | **強烈建議** | 見 §7。安裝畫面會顯示；App 內匯出時這一欄是必填的 |
| `appMinVersion` | 字串 | 選填 | 目前寫 `1.15.0`。**目前只是記錄，App 不會據此擋下任何東西**；真正的相容判斷是 `format` |
| `id` | 字串 | **強烈建議** | `你的名字.項目名`，例如 `usagi.research-assistant`。見 §4.5 |
| `version` | 字串 | **強烈建議** | 改內容時**一定要升**。見 §4.5 |
| `count` | 整數 | 選填 | 包內項目數（`style` / `kb`）。純資訊，App 以實際解析結果為準 |
| `lang` | 字串 | 建議 | 這個項目**寫給人看的語言**：`zh-Hant` / `zh-Hans` / `en`。見 §4.6 |
| `example` | 字串 | 選填 | 使用教學／範例頁面的 **https** 網址。見 §4.7 |

缺少 `title` / `author` / `license` 不會讓檔案被拒收——**只有 `format` 與 `type` 是硬性的**。

**使用者實際看得到什麼：** 列表上是 `title`、`summary`、型別、語言徽章、以及「已安裝／有新版」狀態；點進去再加上 `author`、`license`、`version`、`example` 連結、以及**完整內容**。`id`、`format`、`appMinVersion`、`count` 不會顯示給使用者，它們是機制用的。

### 4.2 純文字格式支援的 YAML 子集

`.aiide-prompt` 的 manifest 和 `.aiide-kb` 的條目 front matter，用的是同一套**極小的 YAML 子集**。它不是 YAML 剖析器，請當成「一種長得像 YAML 的格式」來寫：

| 規則 | |
|---|---|
| 區塊界線 | 檔案開頭的 `---` 起，到**單獨一行正好是 `---`** 為止 |
| 只吃第一個區塊 | 後面再出現的 `---` 區塊完全不碰（§4.3 靠這一點） |
| 一行一欄位 | `key: value`，**以第一個冒號切開**。所以值裡可以有冒號 |
| 註解 | **只支援整行註解**（該行以 `#` 開頭）。**行尾註解不會被去掉**——`title: 甲  # 說明` 的值是 `甲  # 說明` |
| 重複的 key | 後面的蓋掉前面的 |
| 引號 | 只認**雙引號**。單引號會被當成值的一部分。雙引號裡可用 `\"` 與 `\\` |
| 何時要引號 | 值的首尾有空白，或值裡有 `: # [ ] { } " ,` 時 |
| 陣列 | 只支援單行 `tags: [a, b]`。**不支援 `- item` 的多行寫法** |
| 不支援 | 巢狀、多行字串（`\|` / `>`）、anchor、`null`／布林的特殊語意（一律當字串） |

沒有結尾 `---` 的話，整個檔案都被當成內文，manifest 讀不到 → 檔案被拒收。

### 4.3 `.aiide-prompt`（純文字）

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
lang: zh-Hant
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

| | |
|---|---|
| 沒有 `title` | 取內文第一個 `# ` 標題（井號後面要有空白）；找不到就顯示 `prompt` |
| 內文是空的 | **拒收** |
| 檔案上限 | **1 MB** |
| 內文前後的空行 | 會被去掉；中間一切原封不動 |
| 額外欄位 | `source:` 會被保留（原始出處，例如一個 AISA skill 的網址） |

> **為什麼一檔一個指令**：Prompt 的內文會加在使用者之後**每一輪**對話的最前面。App 因此規定安裝前一定顯示全文、一次只裝一個、而且**不自動啟用**。一個能裝二十個的檔案會讓這條規則無法遵守。

### 4.4 `.aiide-style`（JSON）

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
  "lang": "zh-Hant",
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

| | |
|---|---|
| 不認得的 `field` | **只會少掉那一則**，同檔其他則照常匯入。所以未來新增欄位時，舊版 App 不會整包失敗 |
| `body` 是空的 | 那一則被略過 |
| 沒有 `title` | 取 `body` 開頭當名字 |
| 每一則都無效 | 整份拒收（「這個檔案裡沒有任何內容」） |
| `styles` 缺席或不是陣列 | 同上，拒收 |
| 檔案上限 | **1 MB** |

`field` / `title` / `body` 三個 key 都必須是字串。任何一則缺 key 會讓那一則消失（不是整份失敗）。

### 4.5 `.aiide-kb`（zip）

副檔名是 `.aiide-kb`，內容是一個標準 zip：

```
manifest.json          ← 必須在壓縮檔的最上層
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
  "lang": "zh-Hant",
  "count": 2
}
```

每個條目檔（front matter 用 §4.2 的子集）：

```
---
title: 術語表
summary: 品牌用語
tags: [品牌, style]
origin: terms.md
---

AI-IDE 一律寫作 AI-IDE，不寫成 AI IDE 或 AIIDE。
```

條目 front matter 的四個欄位都是選填：`title`（缺了取內文開頭 24 字）、`summary`、`tags`（單行陣列）、`origin`（原始檔名，純記錄）。

**規則：**

| | |
|---|---|
| 哪些算條目 | **只有 `entries/` 開頭、`.md` 結尾的檔案**。大小寫有意義（`.MD` 不算）。其他檔案（README、LICENSE、圖片）會被忽略 |
| `manifest.json` | 從 repo 分享時**必須有**。沒有它，掃描器讀不出型別，這個檔案會被歸進「無法開啟」而不是列出來 |
| 條目順序 | **依壓縮檔內的實際順序，不是檔名順序。** 檔名的流水號前綴（`001-`）只保證同名條目不會互相覆蓋、diff 讀起來有序；要讓顯示順序也對，打包時得**照順序把檔案一個個加進去**（見下方指令）——`zip -r entries` 用的是目錄的實際順序，出來常常是亂的 |
| 沒有 front matter | 也能匯入，標題取內文開頭 |
| 內文空的條目 | 略過；全部都空則整份拒收 |
| 去重 | 匯入時以**內容雜湊**去重：同一個包傳兩次，第二次不會多出任何東西 |
| 檔案上限 | **10 MB**（壓縮後的檔案大小） |

**壓縮方式有硬性限制**，因為 App 用的是自帶的最小 zip 讀取器：

- 只支援 **stored（method 0）與 deflate（method 8）**。
- **不支援 zip64、加密**，也不支援**以 streaming 方式寫出、本地標頭沒有記下大小的項目**（data descriptor）。
- 檔名用 UTF-8。

實務上這代表：

```bash
# 在包的資料夾「裡面」壓，manifest.json 才會在最上層；
# 用 entries/*.md 而不是 -r entries，條目順序才會照檔名
cd my-pack && zip -qX ../brand-terms.aiide-kb manifest.json entries/*.md
```

```python
# Python 也可以，寫到「檔案路徑」而不是 stream
import zipfile
with zipfile.ZipFile("brand-terms.aiide-kb", "w", zipfile.ZIP_DEFLATED) as z:
    z.write("manifest.json")
    z.write("entries/001-術語表.md")
```

⚠️ **不要用 Finder 的「壓縮」對整個資料夾右鍵**——那會把所有東西包在一層 `my-pack/` 底下，`manifest.json` 就不在最上層，`entries/` 前綴也對不上，結果是一個看起來沒問題但完全讀不到的檔案。（多出來的 `__MACOSX/`、`.DS_Store` 本身無害，會被忽略。）

用 Markdown 而不是把文件塞進 JSON 字串，是為了讓這些檔案在 GitHub 上讀得下去、diff 得出來。

### 4.6 更新：不升 `version`，使用者就收不到通知

App 判斷「有沒有新版」時，只用掃描已經知道的東西——比對內容意味著每次重新整理都要把使用者已安裝的每一個項目重新下載一遍。所以：

| 你做的事 | 使用者看到 |
|---|---|
| 改了內容，**升了 `version`** | **「有新版 1.1.0」**，可以一鍵更新 |
| 改了內容，沒升 `version`，但檔案大小變了 | 「可能有更新」（App 明說這是猜的） |
| 改了內容，沒升 `version`，大小剛好一樣 | **什麼都沒有。使用者永遠不會知道。** |

比對是「不相等」，不是「比較大小」——你退回 1.0.0 也算是使用者手上沒有的東西，一樣會通知。版本字串沒有格式規定，但請用 `1.2.3` 這種形式，它會原樣顯示給使用者看。

**`id` 是身分。** 有 `id` 的項目，你之後把檔案搬到別的資料夾、改檔名，使用者手上那一份還認得出是同一個東西，更新照樣送得到。沒有 `id` 的項目只能靠「在哪個來源的哪個路徑」認人，搬家等於換了一個項目——使用者會看到一個新的、和舊的並存。

`id` 請用 `你的名字.項目名`，並且**永不重複使用**：兩個不同的東西共用一個 `id`，會讓其中一個把另一個蓋掉。

另外兩件你該知道的事：

- **使用者改過的那一份不會被你覆蓋。** App 記得安裝當下寫進去的內容雜湊；對得上才會就地取代，對不上就只提示，並讓使用者自己選「另存為新的一份」或「仍要覆蓋」。
- **更新 prompt 會保留它在使用者那邊的識別**，所以他原本啟用著的指令，更新後仍然是啟用的。

### 4.7 `lang`：同一個項目的多語版本

一個項目要出三種語言，就發三個檔案，**用同一個 `id`、不同的 `lang`**：

```
prompts/
├── slide-outline.zh-Hant.aiide-prompt   id: usagi.slide-outline   lang: zh-Hant
├── slide-outline.zh-Hans.aiide-prompt   id: usagi.slide-outline   lang: zh-Hans
└── slide-outline.en.aiide-prompt        id: usagi.slide-outline   lang: en
```

**共用 `id` 才是重點**——App 靠它知道這三個是同一個東西：清單上只佔一列，顯示讀者語言的那一版，其餘在詳情頁一鍵切換。三個不同的 `id` 就會變成三個互不相干的項目，而且清單長度直接乘三。

| 規則 | |
|---|---|
| 代碼 | 標準寫法是 `zh-Hant`、`zh-Hans`、`en`。也認得 `zh-TW` / `zh-HK` / `zh-CN` / `zh-SG` / `tc` / `sc` / `zht` / `zhs` / `en-US` / `en-GB` / `zh-Hant-TW` 這類寫法並自動轉換（不分大小寫）。**但 `zh` 不行**——繁簡對讀者不能互換，猜錯不如不標 |
| 認不得的值 | 當成沒標。不會讓檔案失敗 |
| 沒標 `lang` | 對所有人顯示。不會被藏起來 |
| 檔名後綴 | **給人看的慣例，不是判斷依據**。App 以 `lang` 為準（副檔名可以被改，§2.3）。`tools/aiide-index.py` 會在兩者不一致時報錯 |
| 沒有讀者的語言時 | 顯示最接近的：繁中讀者拿到簡中版而不是英文版，反之亦然。**絕不會因為沒有他的語言就什麼都不給** |
| 已安裝狀態 | 只有讀者母語的那一版可以繼承「早期沒標語言時安裝的那一筆」。所以英文版不會對只裝過中文版的人謊稱「已安裝」 |

**`lang` 指的是「使用者會讀到的語言」，不是產出語言。** 官方的 `english-level-rewrite` 指令是中文寫的、產出英文，它是 `zh-Hant`；`illustration-pack` 的標題是中文、`body` 是英文（生圖模型吃英文比較穩），它也是 `zh-Hant`。用產出語言標會把兩者都放錯格。

> 這一條我們自己踩過：曾經把一個檔名結尾是 `-en` 的檔案標成 `lang: en`，而它的內文其實整篇是中文。**不要看檔名決定 `lang`，要看內容。**
>
> 如果你想提供「中文介面、英文產出」和「中文介面、中文產出」兩個版本，那是**兩個不同的項目**（各自的 `id`），不是同一項目的兩個語言。

### 4.8 `example`：使用教學／範例網址

```
example: https://your-site.example/tutorials/slide-outline
```

指向一個「這東西怎麼用」的頁面——教學文、範例輸出、示範影片。App 在檢視畫面上放一個連結，**並且顯示網域**，讓使用者在按下去之前知道會連到哪裡。

- **只接受 https。** `http:`、`javascript:`、`file:`、以及沒有網域的值一律忽略（連結不顯示，檔案不會失敗）。
- **App 絕不會自己去抓這個網址**，只有使用者按下去才開。§7 的「不得有會自動請求的外部 URL」對這個欄位一樣成立。

---

## 5. `aiide-index.json`（選用，但請放）

放在 **repo 根目錄**、檔名一字不差。有它的話，App 掃描你的 repo **完全不花 GitHub 的查詢額度**（未登入的使用者每小時只有 60 次，而且回 304 也照樣計費）。沒有它也能運作——索引是最佳化，不是必要條件。

```json
{
  "format": 1,
  "name": "某某的 AI-IDE 資源",
  "summary": "一行說明。",
  "homepage": "https://github.com/yourname/yourrepo",
  "items": [
    {
      "path": "prompts/research-assistant.zh-Hant.aiide-prompt",
      "size": 1517,
      "type": "prompt",
      "id": "yourname.research-assistant",
      "version": "1.0.0",
      "title": "研究助理（查證優先）",
      "summary": "每個事實都要有來源。",
      "author": "yourname",
      "license": "CC BY 4.0",
      "appMinVersion": "1.15.0",
      "lang": "zh-Hant"
    }
  ]
}
```

**頂層**：`format`（必填，`1`）、`items`（必填，且**不能是空陣列**）、`name`／`summary`／`homepage`（選填，`homepage` 目前不顯示）。頂層 `format` 不是 `1`、或 `items` 是空的，索引會被整份忽略、退回慢速掃描——**而且沒有任何錯誤訊息**。

**每一筆 item** 是一個**扁平物件**：`path`（repo 相對路徑，必填）、`size`（選用，位元組），加上那個檔案的 manifest 欄位並排放著（`type` 必填，其餘同 §4.1）。

- **每一筆的 `format` 可以省略**，會沿用頂層的。要寫也可以。
- 壞掉的那一筆只會少掉它自己，不會讓整份索引作廢。
- 列在索引裡但型別還不能安裝的項目，一樣會被算進「需要更新 App」的計數。
- **索引只是清單。** 使用者按下安裝時，App 會重新下載那個檔案並重新解析——所以索引過期不會裝錯東西，但**列表會顯示不存在的項目、點進去才報錯**。改了檔案就重新產生索引。

因為索引和檔案本身是兩份會各自漂移的資料，請**不要手寫**，用工具產生：

```bash
python3 tools/aiide-index.py /path/to/your/repo
```

```bash
python3 tools/aiide-index.py /path/to/your/repo --check
```

它會掃描資料夾、**用 App 讀檔的方式驗證每一個檔案**、把 `aiide-index.json` 寫回去；有任何檔案讀不過就會告訴你哪一個、為什麼，並且**什麼都不寫出來**（半對的索引比沒有索引更糟）。它也會檢查檔名的語言後綴和 `lang` 是否一致。

只需要 Python 3 標準庫，沒有其他相依。這個檔案可以直接複製到你自己的 repo 用。

---

## 6. 網頁也可以當來源

不想開 repo 也行：任何 HTML 頁面，只要裡面有指向 `.aiide-*` 檔案的 `<a href>` 連結，就能當成來源貼進 App。

```html
<a href="prompts/my-prompt.aiide-prompt">我的指令</a>
<a href="https://example.com/files/my-styles.aiide-style">我的風格</a>
```

- 相對路徑依該頁網址解析；只接受 http(s)。
- 重複的連結只算一次。同樣最多讀 200 個。
- 每個檔案本身的格式要求和 §4 完全相同——**網頁只是換一種列出檔案的方式**，不是換一種格式。
- 檔案要能被直接下載（不能是需要登入或會轉址到登入頁的連結）。

---

## 6a. 一鍵安裝連結

除了讓人加你的 repo 當來源，你也可以在部落格、教學文或 README 上直接放單一項目的安裝連結：

```
aiide://import?item=https://raw.githubusercontent.com/你的帳號/你的repo/main/prompts/x.aiide-prompt
```

Markdown 寫法：

```markdown
[在 AI-IDE 中安裝](aiide://import?item=https://raw.githubusercontent.com/你的帳號/你的repo/main/prompts/x.aiide-prompt)
```

幾點要知道：

- **網址要用 raw 連結**（`raw.githubusercontent.com/...`），不是 GitHub 的網頁連結。
- **只有 https 且副檔名是 `.aiide-*` 的網址通得過**。指向 `.md`、`.html`、`.sh` 的連結會被直接丟掉——這是設計，不是限制。
- **連結不會安裝任何東西。** App 只會顯示檔名、型別與**你的網域**，使用者按下去才下載，然後看到完整內容再決定。你放的連結不能替使用者做決定。
- 想一次放多個，用逗號或 JSON 陣列：`item=https://…/a.aiide-prompt,https://…/b.aiide-kb`。
- 這條連結和 `datafiles=` / `prompts=` / `chat=` **不能混用**——帶了 `item=`，其他參數會被忽略。
- 使用者也可以直接把 `.aiide-*` 檔案存到裝置上，從「檔案」App 或 Finder 打開，走的是同一個檢視與安裝流程。

---

## 7. 分享者請遵守的三件事

這三條不是禮貌，是這個機制能不能繼續存在的前提。

### 1. 授權欄位要是真的

**只分享你有權分享的內容。** KB 這一類尤其危險——它是最容易夾帶他人著作的型別。從別處取得的書籍、報告、付費資料或公司內部文件**不能**放進來。App 內匯出時 `license` 是必填的，就是為了逼每個人在按下分享之前先想過這件事。

### 2. 不要放任何可執行的東西

- 沒有腳本、沒有巨集（`.pptm` 一律拒收）
- 沒有會自動請求的外部網址（`example` 也一樣，見 §4.8）

寫進格式規格，不靠審查。

### 3. Prompt 的內文會進入別人的每一輪對話

所以請假設**每一個字都會被讀到**——App 在安裝前一定會把全文顯示給使用者看。一份要求 AI「忽略先前指示」或連到外部網址的 prompt，會被使用者當場看見。

App 這一端對應的規則：一律不自動安裝、不自動更新、瀏覽是唯讀的，安裝永遠要人按下去。

---

## 8. 推上去前的檢查清單

- [ ] repo 是公開的，預設分支是 `main` 或 `master`
- [ ] 檔案是 UTF-8、LF、沒有 BOM（§4.0）
- [ ] 每個檔案的 `format` 是 `1`、`type` 和內容相符
- [ ] `license` 是你真的有權給的授權
- [ ] `id` 用 `你的名字.項目名`，而且沒有和你其他項目撞號
- [ ] **改內容一定要升 `version`**（§4.6）
- [ ] 多語版本共用同一個 `id`、各自標 `lang`，而且 `lang` 是**看過內容**決定的（§4.7）
- [ ] KB 包的 `manifest.json` 在壓縮檔最上層，條目在 `entries/*.md`（§4.5）
- [ ] 跑過 `python3 tools/aiide-index.py <你的repo>`，沒有錯誤
- [ ] 重新產生過 `aiide-index.json` 並一起推上去
- [ ] **用 App 自己貼一次你的 repo 網址，確認看得到、裝得起來**

最後一步別跳過。它是唯一會告訴你「別人看到的是什麼」的檢查。記得按重新整理（§2.1）。

---

## 9. 疑難排解

| 症狀 | 幾乎一定是這個原因 |
|---|---|
| 整個來源加不進去 | repo 不是公開的；或網址不是 §2.2 的形式；或帳號／repo 名含有 `A-Za-z0-9._-` 以外的字元 |
| 「找不到這個來源」 | 預設分支不是 `main` / `master`——貼 `.../tree/你的分支` |
| 剛推的更新沒出現 | 快取一小時（§2.1）。按重新整理 |
| 某個檔案完全沒出現在列表 | 副檔名不對；或 manifest 讀不到（CRLF／BOM／少了結尾 `---`／`format` 不是 1）；或 `type` 和副檔名對不上 |
| 檔案被算進「需要更新 App」 | `type` 不是 `prompt` / `style` / `kb`——通常是拼錯，或 KB 包少了 `manifest.json` |
| 列表顯示了我已經刪掉的項目 | `aiide-index.json` 過期了。重新產生（§5） |
| 索引明明放了卻好像沒生效 | 頂層 `format` 不是 `1`、`items` 是空的、或 JSON 語法錯誤——整份會被忽略且沒有訊息。跑 `--check` |
| 列表少了很多項目 | 超過一次 200 個的上限，或 GitHub 回報 repo 太大（畫面上會明說少了幾個）。放索引可以解決 |
| KB 條目的顯示順序和檔名對不上 | 用了 `zip -r entries`——那是目錄順序。改成 `zip … manifest.json entries/*.md`（§4.5） |
| KB 包點進去說「不是有效的分享檔」 | 用 Finder 壓的（多一層資料夾）、或壓縮工具寫出了 data descriptor / zip64（§4.5） |
| 風格包少了幾則 | 那幾則的 `field` 不是三個合法值之一，或 `body` 是空的（§4.4） |
| 標題顯示成檔名或內文開頭 | manifest 沒有 `title` |
| 改了內容但使用者沒收到更新 | 沒升 `version`，而且檔案大小剛好沒變（§4.6） |
| 使用者說「已安裝」但他沒裝過 | 你把兩個不同的東西用了同一個 `id` |
| 「GitHub 的查詢額度用完了」 | 未登入每小時 60 次，和你的 repo 無關。放索引能讓你的來源完全不佔額度 |

---

## 10. 相容性承諾

- **`format: 1` 的檔案會一直讀得到。** 需要不相容的改動時會升到 `format: 2`，而不是偷偷改變 `1` 的意思。
- **不認得的欄位會被忽略，不是錯誤**，所以新欄位可以加在 `1` 裡（`lang` 和 `example` 就是這樣加的）。舊版 App 少顯示一個欄位，不會壞。
- **不認得的 `type` 會被計數並顯示成「需要更新 App」**，所以下列尚未實作的型別現在就放進 repo 是安全的：

| 副檔名 | 預定的 `type` |
|---|---|
| `.aiide-brand` | `brandKit` |
| `.aiide-pdf` | `pdfTemplate` |
| `.aiide-word` | `wordTemplate` |
| `.aiide-excel` | `excelTemplate` |
| `.aiide-slides` | `slidesTemplate` |

這五種的內部結構尚未定案，這份文件會在定案時更新。在那之前請不要自行猜測它們的內容格式。

---

## 附錄 A：三個可直接複製的完整範例

### A.1 `prompts/meeting-summary.zh-Hant.aiide-prompt`

```
---
format: 1
type: prompt
id: yourname.meeting-summary
version: 1.0.0
title: 會議記錄整理
summary: 把逐字稿整理成決議、待辦與未解問題三段。
author: yourname
license: CC BY 4.0
appMinVersion: 1.15.0
lang: zh-Hant
example: https://your-site.example/aiide/meeting-summary
---

# 會議記錄整理

把我給你的逐字稿整理成三段：

1. **決議**——已經拍板的事，一條一句。
2. **待辦**——誰、要做什麼、什麼時候前。沒講到負責人就寫「未指定」。
3. **未解問題**——討論過但沒有結論的。

逐字稿裡沒有的東西不要補。聽不出來的人名就寫「（未辨識）」。
```

### A.2 `styles/deck-teaching.zh-Hant.aiide-style`

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
  "lang": "zh-Hant",
  "count": 2,
  "styles": [
    {
      "field": "refine",
      "title": "教學節奏",
      "body": "每頁一個觀念，最多 4 條。每個抽象說法後面接一個具體例子。專有名詞第一次出現時用一句話解釋。"
    },
    {
      "field": "illustration",
      "title": "溫暖手繪",
      "body": "warm hand-drawn illustration, soft pencil texture, muted palette, no text"
    }
  ]
}
```

### A.3 `kb/brand-terms.zh-Hant.aiide-kb`

壓縮前的資料夾：

```
brand-terms/
├── manifest.json
└── entries/
    ├── 001-用語表.md
    └── 002-禁用字.md
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
  "lang": "zh-Hant",
  "count": 2
}
```

`entries/001-用語表.md`：

```
---
title: 用語表
summary: 產品名稱的正確寫法
tags: [品牌, 用語]
---

AI-IDE 一律寫作 AI-IDE，不寫成 AI IDE 或 AIIDE。
```

打包：

```bash
cd brand-terms && zip -qX ../kb/brand-terms.zh-Hant.aiide-kb manifest.json entries/*.md
```

---

有問題或發現這份文件和 App 實際行為不符，請開 issue——**以 App 的行為為準，那代表這份文件錯了**。
