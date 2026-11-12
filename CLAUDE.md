# CLAUDE.md — Petit Carnet 法文小筆記

> 給接手這個專案的 AI：開工前先把這份讀完。這裡寫的是「這個網站怎麼長大」的規則。
> 規則和實際檔案對不上時，先把兩邊修成一致，再在 `docs/log.md` 記一筆為什麼。

---

## 1. 這是什麼

- **一個收集日常法文短句的靜態網站，一句一頁。**
- 讀者：會中文、剛開始學法文的人。
- 每一頁都要回答四個問題：**怎麼念、什麼意思、怎麼拆、什麼時候用。**
- 技術：純 HTML ＋ CSS ＋ 一支原生 JS。不用框架、不用建置步驟、不引入任何外部 JS 套件。
- 發佈：GitHub Pages 直接發佈 repo 根目錄（`main` 分支，`/`）。根目錄有 `.nojekyll`，檔案原樣上線。

## 2. 資料夾結構

```
petit-carnet/
├── CLAUDE.md              ← 本檔：專案規則
├── README.md              ← 給人看的專案說明
├── index.html             ← 首頁：介紹＋分類篩選＋所有筆記卡片
├── .nojekyll              ← 讓 GitHub Pages 原樣發佈，不經過 Jekyll
├── .gitignore             ← 擋掉 .local/ 和 __pycache__/
├── .gitattributes         ← 所有文字檔統一用 LF 換行
├── .local/                ← 私人草稿（例如繳交文字），不上傳、AI 不用動
├── assets/
│   ├── style.css          ← 唯一的樣式檔（色票、字體、所有元件）
│   └── carnet.js          ← 唯一的 JS（發音按鈕、首頁篩選）
├── notes/
│   └── <slug>/
│       └── index.html     ← 一句法文 = 一個資料夾 = 一頁
├── templates/
│   └── note.html          ← 新增筆記時複製這份
├── tools/
│   └── check.py           ← 檢查腳本（見 §9）
└── docs/
    └── log.md             ← 新增／修改紀錄，只增不刪
```

- 筆記頁的網址是 `notes/<slug>/`，檔名永遠是 `index.html`。
- 樣式只寫在 `assets/style.css`，互動只寫在 `assets/carnet.js`。**頁面裡不寫 `<style>`、不寫 `style="…"`、不寫 `<script>` 內容。**
- 所有站內連結一律用**相對路徑**（筆記頁回首頁是 `../../`、連到別的筆記是 `../<slug>/`）。不要用 `/` 開頭——GitHub Pages 的網址前面還有一段 `/petit-carnet/`，用 `/` 開頭會壞。
- 不新增其他頂層資料夾。真的需要時，先改這份文件的 §2，再建資料夾。

## 3. 命名規則（slug）

slug 由法文原句轉出來，步驟固定：

1. 去掉重音與特殊字母：`é è ê ë → e`、`à â → a`、`ç → c`、`ô → o`、`î ï → i`、`ù û ü → u`、`œ → oe`、`æ → ae`
2. 全部轉小寫
3. 刪掉撇號 `'`、問號、驚嘆號、句點、逗號
4. 空白和連字號都變成單一個 `-`，頭尾不留 `-`

| 法文原句 | slug |
| --- | --- |
| Dis-moi | `dis-moi` |
| C'est la vie | `cest-la-vie` |
| À demain | `a-demain` |
| Je suis là | `je-suis-la` |
| Ça va ? | `ca-va` |

- slug 只能有 `a-z`、`0-9`、`-`（檢查腳本會擋）。
- **算出來的 slug 已經存在 → 代表這句已經收錄過，去改那一頁，不要另開新頁。**

## 4. 一頁筆記的結構

每頁由上到下固定是這些區塊。每個區塊用 `data-field` 標記，檢查腳本靠它確認有沒有缺：

| 區塊 | `data-field` | 必填 | 寫法 |
| --- | --- | --- | --- |
| 法文原句 | `fr` | ✔ | `<h1 lang="fr" data-speak>`。保留重音和原本的標點（`Ça va ?` 問號前面的空格是法文排版規則，要留）。 |
| 發音 | `ipa` | ✔ | 國際音標，前後用斜線包：`/di mwa/`。 |
| 中文意思 | `meaning` | ✔ | 一句話，20 個字以內。多個意思用頓號分開。 |
| 拆開來看 | `breakdown` | ✔ | `<dl class="breakdown">`，一個字一組 `<dt lang="fr">`＋`<dd>`。`<dd>` 寫中文意思和文法身分（詞性、原形、變化）。 |
| 例句 | `examples` | ✔ | 1～3 句。每句一個 `<li class="ex">`，裡面是 `<p class="ex-fr" lang="fr" data-speak>` 法文＋`<p class="ex-zh">` 中文。 |
| 什麼時候用 | `usage` | ✔ | 場合、對誰說、語氣。有 tu／vous（熟／不熟）差別一定要寫。 |
| 相關說法 | `related` | 選填 | 意思相近或常一起出現的說法。**站內已經有的句子要做成連結**；沒有就只寫文字。 |
| 頁尾 | — | ✔ | 分類標籤 `<span class="chip" data-cat="<分類 id>">` ＋ 加入日期 `<time datetime="YYYY-MM-DD">`。 |

- `<main class="note" data-category="<分類 id>">` 上要標分類。
- `<title>` 固定格式：`<法文原句> · Petit Carnet`。
- `<meta name="description">` 固定格式：`<法文原句>：<中文意思>`。
- 有 `data-speak` 的元素，JS 會自動在後面加「聽」按鈕（用瀏覽器內建的法文語音念出來）。不要手動寫按鈕。

## 5. 分類

| id | 中文標籤 | 收什麼 |
| --- | --- | --- |
| `greeting` | 問候道別 | 見面、道別、晚安、祝福 |
| `conversation` | 對話用語 | 聊天時接話、提問、回應用的句子 |
| `feeling` | 心情感受 | 描述或抒發情緒、態度 |
| `tenderness` | 溫柔話 | 安慰、陪伴、關心別人 |

- 一句只放一個分類。猶豫時選「說這句話的目的」最接近的那個。
- 權威清單是 `tools/check.py` 裡的 `CATEGORIES`。**要新增分類，三個地方一起改**：`CATEGORIES`、首頁的篩選按鈕、上面這張表。

## 6. 視覺規範

風格關鍵字：**米白紙張、深藍墨水、一條酒紅色的筆記本邊線。** 安靜、留白多、像手寫筆記本。

### 色票（定義在 `assets/style.css` 的 `:root`）

| token | 淺色 | 深色 | 用途 |
| --- | --- | --- | --- |
| `--paper` | `#FBF7F0` | `#16181F` | 頁面底色 |
| `--card` | `#FFFDF9` | `#1E212B` | 卡片底色 |
| `--ink` | `#1F2A44` | `#ECE5D8` | 主要文字 |
| `--ink-soft` | `#5A6378` | `#A7A2B3` | 次要文字、IPA、中文翻譯 |
| `--line` | `#E6DCCB` | `#323645` | 邊框、分隔線 |
| `--accent` | `#A63D52` | `#E68A9D` | 酒紅：邊線、小標、連結、按鈕 |
| `--accent-soft` | `#F5E3E6` | `#3A2730` | 分類標籤底色 |

- 深色模式跟著系統 `prefers-color-scheme` 切換，不另做開關。
- **不要在任何地方直接寫色碼。** 需要新顏色時，先在 `:root`（淺色＋深色兩組）加 token，再補進上表。

### 字體

| token | 字體 | 用在 |
| --- | --- | --- |
| `--font-fr` | Cormorant Garamond（Google Fonts） | 所有法文：標題、例句、拆解的字、卡片上的原句 |
| `--font-zh` | Noto Sans TC（Google Fonts） | 所有中文 |
| `--font-ipa` | 系統無襯線字（Segoe UI／Helvetica Neue） | IPA 音標（Cormorant 缺部分音標字元） |

### 版面與元件

- 內容最大寬度 `760px`，左右留 `16px`。手機 375px 寬時**不能出現水平捲動**。
- 首頁卡片：`.cards` 格狀排列，每張 `.card` 顯示法文、中文意思、分類標籤、日期。
- 筆記頁標題區 `.note-head` 左側有一條 `--accent` 邊線（筆記本的紅線）。
- 區塊小標 `<h2>` 用 `--accent` 色。
- 新元件一律寫成 class 放進 `style.css`，沿用既有 token，不另起一套。

## 7. 新增一則筆記（標準流程）

依序做，不要跳步：

1. **算 slug**（§3），確認 `notes/<slug>/` 不存在。
2. **複製範本**：`templates/note.html` → `notes/<slug>/index.html`。
3. **填內容**：把所有 `{{…}}` 換掉。對照表：

   | 佔位字 | 換成 |
   | --- | --- |
   | `{{FR}}` | 法文原句（出現在 `<title>`、description、`<h1>`） |
   | `{{IPA}}` | `/…/` 國際音標 |
   | `{{MEANING}}` | 中文意思 |
   | `{{WORD}}`／`{{WORD_NOTE}}` | 拆解的每個字和說明；`<div>` 依字數複製 |
   | `{{EX_FR}}`／`{{EX_ZH}}` | 例句；`<li class="ex">` 依句數複製或刪除（1～3 句） |
   | `{{USAGE}}` | 什麼時候用 |
   | `{{RELATED}}` | 相關說法；沒有就把整個 `related` 區塊刪掉 |
   | `{{CATEGORY}}`／`{{CATEGORY_LABEL}}` | 分類 id 和中文標籤（§5） |
   | `{{DATE}}` | 今天日期 `YYYY-MM-DD` |

   範本裡給人看的 HTML 註解（`<!-- … -->`）填完後全部刪掉，筆記頁裡不留註解。

4. **更新首頁**：在 `index.html` 的 `<!-- NOTES:START -->` 正下方插入一張卡片（**最新的放最上面**）：

   ```html
   <li><a class="card" href="notes/<slug>/" data-category="<分類 id>">
     <span class="card-fr" lang="fr"><法文原句></span>
     <span class="card-zh"><中文意思></span>
     <span class="card-meta"><span class="chip" data-cat="<分類 id>"><中文標籤></span><time datetime="<YYYY-MM-DD>"><YYYY-MM-DD></time></span>
   </a></li>
   ```

   卡片上的法文、中文意思、分類、日期必須和筆記頁**一字不差**。
5. **補雙向連結**：如果「相關說法」連到站內某一句，也到那一句的頁面把連結加回來。
6. **跑檢查**：`python tools/check.py`，必須顯示全部通過（0 個錯誤）。
7. **本機預覽**（§9）：首頁看得到新卡片、分類篩選正常、點進去版面和其他頁一致、「聽」按鈕會念。
8. **記錄**：在 `docs/log.md` 最下面加一行，照檔案開頭的五欄格式：`日期｜誰｜做了什麼｜slug｜檢查結果`。

## 8. 修改既有內容

| 要改的東西 | 同時要改 |
| --- | --- |
| 法文原句 | 依新句子重算 slug；slug 變了就把資料夾改名，並更新首頁卡片的 `href` 和所有指向它的「相關說法」連結 |
| 中文意思 | 筆記頁 `meaning`、`<meta name="description">`、首頁卡片 `.card-zh` |
| 分類 | 筆記頁 `<main data-category>` 和頁尾 chip、首頁卡片 `data-category` 和 chip |
| 樣式 | 只改 `assets/style.css`；動到色票或字體要回來更新 §6 |
| 刪除一則 | 刪資料夾、刪首頁卡片、刪其他頁指向它的連結 |
| 範本結構 | 改 `templates/note.html` 後，**所有既有筆記頁也要改成同樣結構**，再更新 §4 |

每次修改都要跑 `python tools/check.py`，並在 `docs/log.md` 記一行。

## 9. 預覽、檢查、發佈

在 repo 根目錄執行：

```bash
python -m http.server 8000
```

打開 <http://localhost:8000/>。**不要直接雙擊 html 檔開**——相對路徑 `../../` 在 `file://` 下會打開資料夾列表而不是首頁。

```bash
python tools/check.py
```

檢查腳本會確認：

- 每個 `notes/<slug>/` 的 slug 格式正確、有 `index.html`
- 每頁的必填 `data-field` 都在、`<h1>` 有 `lang="fr"`、IPA 有斜線、例句 1～3 句、沒有殘留的 `{{…}}` 或範本註解
- `<title>`、description 符合 §4 格式；分類在清單裡、日期格式正確
- 頁面沒有 `<style>` 或 `style="…"`
- 首頁卡片和筆記頁一一對應（不多不少），法文／意思／分類／日期一致，且依日期由新到舊排
- 首頁篩選按鈕和分類清單一致
- 所有站內 `href`／`src` 都指得到真的檔案，且沒有用 `/` 開頭
- （警告）相關說法沒有做成雙向連結

發佈：commit 後 push 到 GitHub 的 `main`，GitHub Pages 會自動更新，網址是 `https://<GitHub 帳號>.github.io/petit-carnet/`。

## 10. 內容品質

- IPA 以標準巴黎法語為準；有連音（liaison）要標出來。
- 例句要短、日常，法文 12 個字以內。
- 例句裡有會因性別變化的字（例如 Désolé／Désolée），要在「什麼時候用」註明另一種寫法。
- 文法術語要準：否定句裡取代 un／des 的 de 是冠詞的變化，不是介系詞。
- **不確定的意思或用法寧可不寫，不要編造。** 少一個例句比寫錯好。
- 中文用臺灣繁體、全形標點。
- 網站是公開的：不放真實人名、私人對話或聯絡資料。

## 11. 收尾前自己核對

- [ ] slug 照 §3 算出來，資料夾是 `notes/<slug>/index.html`
- [ ] §4 的必填區塊都有，`{{…}}` 一個都沒剩
- [ ] 首頁卡片插在最上面，內容和筆記頁一致
- [ ] 相關說法的站內連結是雙向的
- [ ] `python tools/check.py` 全部通過
- [ ] 本機預覽看過首頁和新頁面
- [ ] `docs/log.md` 記了一行
