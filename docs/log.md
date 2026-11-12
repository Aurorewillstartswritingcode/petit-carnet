# 新增／修改紀錄

只增不刪。格式：`日期｜誰｜做了什麼｜slug｜檢查結果`

- 2026-11-13｜Claude｜建立專案：CLAUDE.md、範本、樣式、檢查腳本、首頁｜—｜—
- 2026-11-13｜Claude｜新增第一批五句｜dis-moi、je-suis-la、bonne-nuit、a-demain、cest-la-vie｜check.py 全部通過
- 2026-11-13｜Claude｜新增一句 Pas de souci（對話用語），首頁卡片放最上面；站內沒有相關句子，相關說法只寫文字｜pas-de-souci｜check.py 全部通過（6 則筆記，0 警告）
- 2026-11-13｜Claude｜驗收沒看過聊天的 AI 加的 pas-de-souci：法文內容正確；de 的文法身分改成「冠詞的否定形」、補 Désolée 註明。依它回報的規則模糊處更新 CLAUDE.md：§2 列出 .gitignore／.gitattributes／.local/、§7 範本註解要刪、§7 log 統一五欄、§10 加性別寫法與文法術語；check.py 新增「殘留 HTML 註解」檢查｜pas-de-souci｜check.py 全部通過
- 2026-11-13｜Codex（OpenAI）｜依 CLAUDE.md 複製範本新增一句，更新首頁卡片及 Je suis là 的雙向連結，README 補獨立接手紀錄；本次只留在本機，未 commit／push｜prends-ton-temps｜check.py 七則筆記全部通過（0 警告）；桌機與 375px 預覽、分類篩選及雙向連結通過；發音按鈕可操作，實際音訊待人工確認
- 2026-11-13｜Claude｜依 Codex 複核修正：bonne-nuit、je-suis-la、pas-de-souci 的用法補上例句 tu 形式對應的 vous 說法；pas-de-souci 的 de 說明限定在 Il n'y a pas… 句型、pas 說明改為省略 Il n'y a；CLAUDE.md §9／§10 補規則；check.py 擋只有標題沒有內容的區塊；整理 prends-ton-temps 多餘空行；README 附上盲測原始指令｜bonne-nuit、je-suis-la、pas-de-souci、prends-ton-temps｜check.py 七則筆記全部通過
