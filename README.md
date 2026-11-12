# Petit Carnet · 法文小筆記

一句一頁的法文小筆記網站。每一頁都寫清楚一句日常法文**怎麼念、什麼意思、怎麼拆、什麼時候用**，並可以按「聽」用瀏覽器內建語音播放發音。

- 網站：<https://aurorewillstartswritingcode.github.io/petit-carnet/>
- 專案規則（給 AI 看的）：[CLAUDE.md](CLAUDE.md)

## 專案結構

| 路徑 | 內容 |
| --- | --- |
| `index.html` | 首頁：介紹、分類篩選、所有筆記卡片 |
| `notes/<slug>/index.html` | 一句法文一頁 |
| `templates/note.html` | 新增筆記用的範本 |
| `assets/style.css`、`assets/carnet.js` | 唯一的樣式檔和 JS |
| `tools/check.py` | 檢查腳本 |
| `docs/log.md` | 新增／修改紀錄 |

純 HTML／CSS／原生 JS，沒有建置步驟，GitHub Pages 直接發佈 `main` 分支根目錄。

## 本機預覽與檢查

```bash
python -m http.server 8000
```

打開 <http://localhost:8000/>。

```bash
python tools/check.py
```

## 新增一句的時候，規則怎麼幫 AI 接手

AI 不需要知道之前聊過什麼，只要讀 `CLAUDE.md` 就能照同一套方式加下去：

1. **網址怎麼取**：§3 把法文原句轉成 slug 的固定步驟（去重音、小寫、刪標點、空白變 `-`），附對照表。算出來已經存在就代表收錄過，改舊頁不開新頁。
2. **頁面長什麼樣**：§4 規定每頁必填的區塊（原句、IPA、意思、拆解、1～3 個例句、用法）和對應的 `data-field`；§7 給範本 `templates/note.html` 和每個 `{{佔位字}}` 要換成什麼。
3. **還要更新哪裡**：§7 規定首頁卡片的完整格式、插在最上面、內容要和筆記頁一字不差；相關說法要雙向連結；§8 列出每種修改要連帶改的地方。
4. **長得一不一樣**：§6 固定色票、字體、元件，禁止在頁面裡寫新色碼或 inline 樣式。
5. **做完怎麼確認**：§9 的 `tools/check.py` 會自動檢查上面這些規則（缺欄位、卡片和頁面不一致、排序、壞連結、殘留佔位字），全部通過才算完成，並在 `docs/log.md` 記一筆。

## 規則真的能讓別的 AI 接手嗎？

2026-11-13 做了一次實測：找一個**完全沒看過建站對話**的 AI，只告訴它專案位置和「新增一則筆記：Pas de souci」。它自己讀 `CLAUDE.md`，做出了 `notes/pas-de-souci/`、首頁卡片和紀錄，檢查腳本一次通過。

它也回報了四個規則寫得不夠清楚的地方（沒列出的資料夾、範本註解要不要刪、紀錄格式前後不一、性別變化的寫法），已經補進 `CLAUDE.md`，檢查腳本也多了一項。過程記在 [docs/log.md](docs/log.md)。
