# 🏢 office-meeting — 會議紀錄工作環境

> 給上班族／PM：一鍵載入後，把會議逐字稿丟給 AI，自動整理成決議、待辦、未解問題三段。附文件校對指令。

## 這個環境包含什麼

| 零件 | 內容 |
|---|---|
| **指令** | 會議記錄整理（決議／待辦／未解問題三段）＋文件校對 |
| **資料檔** | 會議逐字稿範例（練習用，換成你真實的逐字稿即可） |
| **預填對話** | 引導 AI 讀逐字稿並依指令輸出三段式會議記錄 |

## 一鍵載入

點下面的連結，AI-IDE 會自動：下載範例逐字稿 → 匯入並啟用 2 個指令 → 開新對話並預填訊息。

```
aiide://import?datafiles=%5B%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fenvironments%2Foffice-meeting%2Fdata%2F%E6%9C%83%E8%AD%B0%E9%80%90%E5%AD%97%E7%A8%BF%E7%AF%84%E4%BE%8B.md%22%5D&prompts=%5B%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Fmeeting-summary.zh-Hant.aiide-prompt%22%2C+%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Fdoc-proofread.zh-Hant.aiide-prompt%22%5D&chat=%E8%AB%8B%E5%85%88%E8%AE%80%E5%8F%96+%40%5B%E6%9C%83%E8%AD%B0%E9%80%90%E5%AD%97%E7%A8%BF%E7%AF%84%E4%BE%8B.md%5D%EF%BC%8C%E4%BE%9D%E7%85%A7%E6%9C%83%E8%AD%B0%E8%A8%98%E9%8C%84%E6%95%B4%E7%90%86%E6%8C%87%E4%BB%A4%EF%BC%8C%E8%BC%B8%E5%87%BA%E6%B1%BA%E8%AD%B0%E3%80%81%E5%BE%85%E8%BE%A6%E8%88%87%E6%9C%AA%E8%A7%A3%E5%95%8F%E9%A1%8C%E4%B8%89%E6%AE%B5%E3%80%82
```

## 怎麼改成你自己的

1. 把 `data/會議逐字稿範例.md` 換成你真正的會議錄音逐字稿（可用 AI 語音轉文字產出）。
2. 想加「產業調查」或「研究助理」？把對應 prompt 的 raw 網址加進 `prompts=`。
3. 想配簡報風格？另載入 repo 的 `styles/persona-office.zh-Hant.aiide-style`（AI 精鍊時用）。
