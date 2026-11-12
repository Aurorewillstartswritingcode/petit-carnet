#!/usr/bin/env python3
"""Petit Carnet 檢查腳本。

在 repo 根目錄執行：python tools/check.py
全部通過時結束碼為 0；有錯誤時列出每一項並以 1 結束。
檢查項目見 CLAUDE.md §9。只用 Python 標準函式庫。
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 分類的權威清單。要新增分類：這裡、首頁篩選按鈕、CLAUDE.md §5 一起改。
CATEGORIES = {
    "greeting": "問候道別",
    "conversation": "對話用語",
    "feeling": "心情感受",
    "tenderness": "溫柔話",
}

REQUIRED_FIELDS = ["fr", "ipa", "meaning", "breakdown", "examples", "usage"]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}
SITE_SUFFIX = " · Petit Carnet"


# ---------- 極簡 HTML 樹 ----------

class Node:
    def __init__(self, tag: str, attrs: dict, parent: "Node | None"):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list = []

    def text(self) -> str:
        parts = [c if isinstance(c, str) else c.text() for c in self.children]
        return " ".join("".join(parts).split())

    def iter(self):
        for c in self.children:
            if isinstance(c, Node):
                yield c
                yield from c.iter()

    def has_class(self, name: str) -> bool:
        return name in (self.attrs.get("class") or "").split()

    def find_all(self, pred):
        return [n for n in self.iter() if pred(n)]

    def find(self, pred):
        for n in self.iter():
            if pred(n):
                return n
        return None


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur = self.root

    @staticmethod
    def _attrs(attrs):
        return {k: ("" if v is None else v) for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        node = Node(tag, self._attrs(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, self._attrs(attrs), self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse(source: str) -> Node:
    b = TreeBuilder()
    b.feed(source)
    b.close()
    return b.root


# ---------- 檢查 ----------

errors: list[str] = []
warnings: list[str] = []


def err(where: Path | str, msg: str):
    errors.append(f"{rel(where)}: {msg}")


def warn(where: Path | str, msg: str):
    warnings.append(f"{rel(where)}: {msg}")


def rel(p: Path | str) -> str:
    if isinstance(p, Path):
        try:
            return p.relative_to(ROOT).as_posix()
        except ValueError:
            return str(p)
    return p


def check_common(path: Path, source: str, tree: Node):
    """所有頁面共用：不寫 style、站內連結都存在且是相對路徑。"""
    if tree.find(lambda n: n.tag == "style"):
        err(path, "頁面裡有 <style>；樣式只能寫在 assets/style.css")
    if tree.find(lambda n: "style" in n.attrs):
        err(path, "頁面裡有 style=\"…\"；樣式只能寫在 assets/style.css")
    if tree.find(lambda n: n.tag == "script" and not n.attrs.get("src")):
        err(path, "頁面裡有 inline <script>；互動只能寫在 assets/carnet.js")

    for n in tree.iter():
        for attr in ("href", "src"):
            url = n.attrs.get(attr)
            if url is None:
                continue
            if re.match(r"^(https?:|mailto:|tel:|data:|#|//)", url):
                continue
            if url.startswith("/"):
                err(path, f"{attr}=\"{url}\" 用了 / 開頭；站內連結要用相對路徑")
                continue
            target = (path.parent / url.split("#")[0].split("?")[0]).resolve()
            if url.endswith("/") or url in ("", ".", "./", "..") or target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                err(path, f"{attr}=\"{url}\" 指到不存在的檔案")


def check_note(slug: str, path: Path) -> dict | None:
    source = path.read_text(encoding="utf-8")
    tree = parse(source)
    check_common(path, source, tree)

    if "{{" in source or "}}" in source:
        err(path, "還有沒換掉的 {{…}} 佔位字")
    if "<!--" in source:
        err(path, "還留著 HTML 註解；範本的註解填完要刪掉")

    html = tree.find(lambda n: n.tag == "html")
    if not html or html.attrs.get("lang") != "zh-Hant":
        err(path, "<html> 要有 lang=\"zh-Hant\"")

    fields = {}
    for n in tree.iter():
        f = n.attrs.get("data-field")
        if f:
            fields.setdefault(f, n)
    for f in REQUIRED_FIELDS:
        if f not in fields:
            err(path, f"缺少必填區塊 data-field=\"{f}\"")

    fr_node = fields.get("fr")
    fr = fr_node.text() if fr_node else ""
    if fr_node is not None:
        if fr_node.tag != "h1":
            err(path, "法文原句（data-field=\"fr\"）要放在 <h1>")
        if fr_node.attrs.get("lang") != "fr":
            err(path, "<h1> 要有 lang=\"fr\"")
        if "data-speak" not in fr_node.attrs:
            err(path, "<h1> 要有 data-speak（才會出現「聽」按鈕）")

    ipa = fields["ipa"].text() if "ipa" in fields else ""
    if "ipa" in fields and not re.match(r"^/.+/$", ipa):
        err(path, f"IPA 要用斜線包起來，現在是「{ipa}」")

    meaning = fields["meaning"].text() if "meaning" in fields else ""
    if "meaning" in fields and not (1 <= len(meaning) <= 20):
        err(path, f"中文意思要 1～20 字，現在 {len(meaning)} 字")

    if "breakdown" in fields:
        dts = fields["breakdown"].find_all(lambda n: n.tag == "dt")
        if not dts:
            err(path, "「拆開來看」至少要有一組 <dt>/<dd>")
        for dt in dts:
            if dt.attrs.get("lang") != "fr":
                err(path, f"拆解的字「{dt.text()}」的 <dt> 要有 lang=\"fr\"")

    if "examples" in fields:
        exs = fields["examples"].find_all(lambda n: n.has_class("ex"))
        if not 1 <= len(exs) <= 3:
            err(path, f"例句要 1～3 句，現在 {len(exs)} 句")
        for ex in exs:
            ex_fr = ex.find(lambda n: n.has_class("ex-fr"))
            ex_zh = ex.find(lambda n: n.has_class("ex-zh"))
            if not ex_fr or ex_fr.attrs.get("lang") != "fr" or "data-speak" not in ex_fr.attrs:
                err(path, "每個例句都要有 <p class=\"ex-fr\" lang=\"fr\" data-speak>")
            if not ex_zh or not ex_zh.text():
                err(path, "每個例句都要有中文翻譯 <p class=\"ex-zh\">")

    title_node = tree.find(lambda n: n.tag == "title")
    title = title_node.text() if title_node else ""
    if fr and title != fr + SITE_SUFFIX:
        err(path, f"<title> 要是「{fr}{SITE_SUFFIX}」，現在是「{title}」")

    desc_node = tree.find(lambda n: n.tag == "meta" and n.attrs.get("name") == "description")
    desc = desc_node.attrs.get("content", "") if desc_node else ""
    if fr and meaning and desc != f"{fr}：{meaning}":
        err(path, f"description 要是「{fr}：{meaning}」，現在是「{desc}」")

    main = tree.find(lambda n: n.tag == "main" and n.has_class("note"))
    category = main.attrs.get("data-category", "") if main else ""
    if category not in CATEGORIES:
        err(path, f"<main class=\"note\"> 的 data-category「{category}」不在分類清單裡")

    meta = tree.find(lambda n: n.has_class("note-meta"))
    chip = meta.find(lambda n: n.has_class("chip")) if meta else None
    if not chip:
        err(path, "頁尾缺少分類標籤 .chip")
    elif category in CATEGORIES:
        if chip.attrs.get("data-cat") != category or chip.text() != CATEGORIES[category]:
            err(path, f"頁尾分類標籤要是 data-cat=\"{category}\"、文字「{CATEGORIES[category]}」")

    time = meta.find(lambda n: n.tag == "time") if meta else None
    date = time.attrs.get("datetime", "") if time else ""
    if not DATE_RE.match(date):
        err(path, f"頁尾 <time datetime> 要是 YYYY-MM-DD，現在是「{date}」")

    links = set()
    if "related" in fields:
        for a in fields["related"].find_all(lambda n: n.tag == "a"):
            m = re.match(r"^\.\./([a-z0-9-]+)/$", a.attrs.get("href", ""))
            if m:
                links.add(m.group(1))

    return {"fr": fr, "meaning": meaning, "category": category, "date": date, "links": links}


def check_home(notes: dict):
    path = ROOT / "index.html"
    if not path.is_file():
        err("index.html", "首頁不存在")
        return
    source = path.read_text(encoding="utf-8")
    tree = parse(source)
    check_common(path, source, tree)

    m = re.search(r"<!-- NOTES:START -->(.*?)<!-- NOTES:END -->", source, re.S)
    if not m:
        err(path, "找不到 <!-- NOTES:START --> 和 <!-- NOTES:END --> 標記")
        return
    region = parse(m.group(1))
    cards = region.find_all(lambda n: n.tag == "a" and n.has_class("card"))

    seen = []
    dates = []
    for card in cards:
        href = card.attrs.get("href", "")
        hm = re.match(r"^notes/([a-z0-9-]+)/$", href)
        if not hm:
            err(path, f"卡片 href=\"{href}\" 格式要是 notes/<slug>/")
            continue
        slug = hm.group(1)
        if slug in seen:
            err(path, f"卡片 {slug} 重複出現")
        seen.append(slug)
        note = notes.get(slug)
        if note is None:
            err(path, f"卡片 {slug} 沒有對應的 notes/{slug}/index.html")
            continue

        def part(cls):
            n = card.find(lambda x: x.has_class(cls))
            return n

        fr_n, zh_n = part("card-fr"), part("card-zh")
        chip = part("chip")
        time = card.find(lambda x: x.tag == "time")
        if not fr_n or fr_n.text() != note["fr"] or fr_n.attrs.get("lang") != "fr":
            err(path, f"卡片 {slug} 的法文要和筆記頁一致（「{note['fr']}」），且有 lang=\"fr\"")
        if not zh_n or zh_n.text() != note["meaning"]:
            err(path, f"卡片 {slug} 的中文意思要和筆記頁一致（「{note['meaning']}」）")
        cat = note["category"]
        if card.attrs.get("data-category") != cat:
            err(path, f"卡片 {slug} 的 data-category 要是「{cat}」")
        if not chip or chip.attrs.get("data-cat") != cat or chip.text() != CATEGORIES.get(cat):
            err(path, f"卡片 {slug} 的分類標籤要是 data-cat=\"{cat}\"、文字「{CATEGORIES.get(cat)}」")
        date = time.attrs.get("datetime", "") if time else ""
        if date != note["date"]:
            err(path, f"卡片 {slug} 的日期要和筆記頁一致（{note['date']}），現在是「{date}」")
        dates.append((date, slug))

    for slug in notes:
        if slug not in seen:
            err(path, f"notes/{slug}/ 在首頁沒有卡片")

    for (d1, s1), (d2, s2) in zip(dates, dates[1:]):
        if d1 < d2:
            err(path, f"卡片要由新到舊排：{s1}（{d1}）不該排在 {s2}（{d2}）前面")

    filters = {n.attrs.get("data-filter") for n in tree.iter() if "data-filter" in n.attrs}
    filters.discard("all")
    if filters != set(CATEGORIES):
        err(path, f"篩選按鈕 {sorted(filters)} 和分類清單 {sorted(CATEGORIES)} 不一致")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    notes_dir = ROOT / "notes"
    notes: dict = {}
    for d in sorted(p for p in notes_dir.iterdir() if p.is_dir()) if notes_dir.is_dir() else []:
        slug = d.name
        if not SLUG_RE.match(slug):
            err(d, f"slug「{slug}」只能有 a-z、0-9 和 -（見 CLAUDE.md §3）")
        page = d / "index.html"
        if not page.is_file():
            err(d, "資料夾裡沒有 index.html")
            continue
        info = check_note(slug, page)
        if info:
            notes[slug] = info

    check_home(notes)

    for slug, info in notes.items():
        for other in info["links"]:
            if other not in notes:
                continue  # 壞連結已在 check_common 報過
            if slug not in notes[other]["links"]:
                warn(f"notes/{other}/index.html",
                     f"{slug} 的相關說法連到這裡，但這頁沒有連回 {slug}")

    for w in warnings:
        print(f"⚠ {w}")
    for e in errors:
        print(f"✗ {e}")
    if errors:
        print(f"\n✗ {len(errors)} 個錯誤、{len(warnings)} 個警告（共 {len(notes)} 則筆記）")
        return 1
    print(f"✓ {len(notes)} 則筆記全部通過" + (f"（{len(warnings)} 個警告）" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
