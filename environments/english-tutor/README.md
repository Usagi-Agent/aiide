# 🎓 english-tutor — 英文教學工作環境

> 給英文老師／家教：一鍵載入後，AI-IDE 就是你的英文教學助手——診斷學生程度、出學習單、出考卷、雙語翻譯，全部配好。

## 這個環境包含什麼

| 零件 | 內容 |
|---|---|
| **指令** | 英文眼鏡（程度診斷）＋學習單產生器＋考卷產生器＋雙語翻譯 |
| **資料檔** | 學生英文需求調查表（下載後填寫即可） |
| **預填對話** | 引導 AI 先讀需求調查表、判斷程度、建議教學重點並出暖身測驗 |

## 一鍵載入

點下面的連結，AI-IDE 會自動：下載需求調查表 → 匯入並啟用 4 個指令 → 開新對話並預填訊息。

```
aiide://import?datafiles=%5B%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fenvironments%2Fenglish-tutor%2Fdata%2F%E5%AD%B8%E7%94%9F%E8%8B%B1%E6%96%87%E9%9C%80%E6%B1%82%E8%AA%BF%E6%9F%A5%E8%A1%A8.md%22%5D&prompts=%5B%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Fenglish-glasses.zh-Hant.aiide-prompt%22%2C+%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Fworksheet-generator.zh-Hant.aiide-prompt%22%2C+%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Fexam-generator.zh-Hant.aiide-prompt%22%2C+%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Ftranslate-bilingual.zh-Hant.aiide-prompt%22%5D&chat=%E8%AB%8B%E5%85%88%E8%AE%80%E5%8F%96+%40%5B%E5%AD%B8%E7%94%9F%E8%8B%B1%E6%96%87%E9%9C%80%E6%B1%82%E8%AA%BF%E6%9F%A5%E8%A1%A8.md%5D%EF%BC%8C%E6%A0%B9%E6%93%9A%E5%85%A7%E5%AE%B9%E5%88%A4%E6%96%B7%E5%AD%B8%E7%94%9F%E7%9A%84%E7%A8%8B%E5%BA%A6%E8%88%87%E7%9B%AE%E6%A8%99%EF%BC%8C%E7%84%B6%E5%BE%8C%E5%BB%BA%E8%AD%B0%E9%80%99%E5%A0%82%E8%AA%B2%E7%9A%84%E6%95%99%E5%AD%B8%E9%87%8D%E9%BB%9E%EF%BC%8C%E4%B8%A6%E5%87%BA%E4%B8%80%E4%BB%BD+5+%E9%A1%8C%E7%9A%84%E6%9A%96%E8%BA%AB%E5%B0%8F%E6%B8%AC%E9%A9%97%E3%80%82
```

## 怎麼改成你自己的

1. 把 `data/學生英文需求調查表.md` 的題目改成你習慣的版本（或直接用）。
2. 想加文法指令？把 repo 裡 `prompts/grammar-*.aiide-prompt` 的 raw 網址加進 `prompts=` 陣列。
3. 換掉 `chat=` 的文字，改成你希望 AI 先做的事。
4. 產生連結時記得 URL 編碼（見 [environments/README.md](../README.md#怎麼自建一個環境)）。
