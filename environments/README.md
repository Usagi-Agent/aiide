# environments/ — 工作環境範例庫

> 一個「工作環境」＝ 針對某一種工作，把 **Prompt 指令 + 資料檔 + 預填對話** 打包成一條連結。使用者點一下，AI-IDE 就變成適合做這件事的狀態。

這裡是官方提供的範例環境，全部走 App 的 `aiide://import` deep link 一鍵載入。你可以：

1. **直接用**：挑一個最接近你工作的環境，點連結載入。
2. **照著改**：每個環境的 README 都寫了「它由哪些零件組成」，把資料檔換成你自己的，就是你的環境。
3. **從零自建**：看完 [怎麼自建一個環境](#怎麼自建一個環境)，10 分鐘做出第一個。

---

## 現有範例環境

| 環境 | 適合誰 | 內容 |
|---|---|---|
| [english-tutor](english-tutor/README.md) | 英文老師／家教 | 英文眼鏡＋出題＋學習單＋雙語翻譯，配教師風格 |
| [office-meeting](office-meeting/README.md) | 上班族、PM、會議紀錄苦手 | 會議整理＋文件校對＋研究助理，配辦公室風格 |
| [travel-planner](travel-planner/README.md) | 自助旅行規劃 | 旅遊行程規劃師＋需求調查表 |

---

## 怎麼自建一個環境

一個環境由三個零件組成，全部可以只用 Markdown 編輯器完成：

### 1. 指令（Prompt）

工作時 AI 該扮演什麼角色、遵守什麼規則。例如「你是會議記錄助理，把逐字稿整理成決議、待辦、未解問題三段」。

放在 repo 的 `prompts/`，格式見 [FORMAT.md](../FORMAT.md) §4.3。

### 2. 資料檔（Data files）

工作開始前使用者手上要有的檔案：範本、表單、範例、逐字稿……任何 `.md`／`.csv`／`.txt` 都行。deep link 會把它們下載進使用者的工作目錄，對話裡用 `@檔名` 引用。

### 3. 預填對話（Chat）

載入環境後自動填進輸入框的一句話，引導使用者「先做什麼」。通常寫成：

```
請先讀取 @需求調查表.md，然後依照我的回答規劃行程。
```

### 組裝成一條連結

用官方 deep link 格式（完整規格見 App 專案 doc/12-deeplink.md）：

```
aiide://import?datafiles=["https://raw.githubusercontent.com/你/你的repo/main/environments/你的環境/data/檔名.md"]&prompts=["https://raw.githubusercontent.com/你/你的repo/main/prompts/你的指令.zh-Hant.aiide-prompt"]&chat=你的預填訊息
```

三點注意：

- **raw 網址**：要用 `raw.githubusercontent.com` 的檔案網址，不是 GitHub 的網頁網址。
- **URL 編碼**：`[` `]` `"`、中文、空白都要 percent-encode。用 `URLSearchParams`（JS）或 `urllib.parse.urlencode`（Python）產生最保險。
- **chat 裡的 `@檔名`** 要對應資料檔下載後的實際檔名（＝URL 最後一段），中文檔名用 `@[檔名.md]` 括號寫法。

### 放進你的 repo

照本目錄的結構：

```
你的repo/
├── environments/
│   ├── README.md          ← 你的環境總覽（選用）
│   └── 你的環境/
│       ├── README.md      ← 說明這個環境、放一鍵載入連結
│       └── data/
│           └── 範本.md     ← 資料檔
├── prompts/
│   └── 你的指令.zh-Hant.aiide-prompt
└── aiide-index.json
```

推上 GitHub 後，把 README 裡的一鍵載入連結貼給使用者即可。他們也可以直接把你的 repo 加進「設定 → 分享資源」當來源，瀏覽安裝裡面的 prompt。

---

## 設計原則

1. **一個環境只服務一種工作**。混太多角色，AI 不知道現在該當誰。
2. **指令要寫「怎麼做」而不是「是什麼」**。例：「把逐字稿整理成決議／待辦／未解問題三段」比「你是會議記錄助手」有用。
3. **資料檔要真的用得到**。每個資料檔都該出現在預填對話的 `@` 引用裡，否則就是多餘。
4. **預填對話要能立刻開始**。載入後使用者應該不需要思考「接下來呢」，直接按送出就有產出。
5. **多語環境**：同一環境可出 zh-Hant / zh-Hans / en 三版 README 與資料檔，指令沿用 §4.7 的多語慣例。
