# ✈️ travel-planner — 旅遊規劃工作環境

> 給自助旅行的人：一鍵載入後，填一張需求調查表，AI 就幫你排出逐日行程，含交通、餐飲、花費估算與雨天備案。

## 這個環境包含什麼

| 零件 | 內容 |
|---|---|
| **指令** | 旅遊行程規劃師（地理動線、每日 3-5 點、交通餐飲花費、備案） |
| **資料檔** | 旅遊需求調查表（目的地、天數、預算、風格、體力限制） |
| **預填對話** | 引導 AI 讀需求調查表並輸出完整行程規劃 |

## 一鍵載入

點下面的連結，AI-IDE 會自動：下載需求調查表 → 匯入並啟用旅遊規劃指令 → 開新對話並預填訊息。

```
aiide://import?datafiles=%5B%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fenvironments%2Ftravel-planner%2Fdata%2F%E6%97%85%E9%81%8A%E9%9C%80%E6%B1%82%E8%AA%BF%E6%9F%A5%E8%A1%A8.md%22%5D&prompts=%5B%22https%3A%2F%2Fraw.githubusercontent.com%2FUsagi-Agent%2Faiide%2Fmain%2Fprompts%2Ftravel-planner.zh-Hant.aiide-prompt%22%5D&chat=%E8%AB%8B%E5%85%88%E8%AE%80%E5%8F%96+%40%5B%E6%97%85%E9%81%8A%E9%9C%80%E6%B1%82%E8%AA%BF%E6%9F%A5%E8%A1%A8.md%5D%EF%BC%8C%E4%BE%9D%E7%85%A7%E6%97%85%E9%81%8A%E8%A1%8C%E7%A8%8B%E8%A6%8F%E5%8A%83%E5%B8%AB%E7%9A%84%E6%8C%87%E4%BB%A4%EF%BC%8C%E6%8E%92%E5%87%BA%E9%80%90%E6%97%A5%E8%A1%8C%E7%A8%8B%E8%A1%A8%EF%BC%88%E5%90%AB%E4%BA%A4%E9%80%9A%E3%80%81%E9%A4%90%E9%A3%B2%E3%80%81%E8%8A%B1%E8%B2%BB%E4%BC%B0%E7%AE%97%E8%88%87%E9%9B%A8%E5%A4%A9%E5%82%99%E6%A1%88%EF%BC%89%E3%80%82
```

## 怎麼改成你自己的

1. 需求調查表可以加「必去景點」「避開區域」等欄位——AI 會照著答。
2. 想連住宿、票券一起排？在 `chat=` 的預填文字裡多寫一句要求。
3. 同一個環境可以出多國版本：把資料檔和預填對話翻譯成目標語言即可。
