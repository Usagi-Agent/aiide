#!/usr/bin/env python3
"""Validate a share repo and (re)generate its two indexes.

    python3 tools/aiide-index.py /path/to/your/repo
    python3 tools/aiide-index.py /path/to/your/repo --check   # validate only
    python3 tools/aiide-index.py /path/to/your/repo --released 1.21.0

Writes `aiide-index.v2.json` (everything, read by AI-IDE 1.21 and later) and
`aiide-index.json` (only what every release since 1.15 can read: builds up
to 1.20 read nothing else, and never look at `appMinVersion`). See FORMAT.md
§2.4.

Reads every `.aiide-*` file the way AI-IDE reads it, so a file this script
accepts is one the app can open. Nothing is written unless every file passed:
a half-correct index is worse than none, because the app trusts the listing
enough to show it.

No dependencies beyond the standard library. FORMAT.md is the spec.
"""
import argparse
import json
import pathlib
import sys
import zipfile

FORMAT = 1
INSTALLABLE = {"prompt", "style", "kb", "brand", "reading", "task", "script",
               "pdfTemplate", "wordTemplate", "excelTemplate", "slidesTemplate",
               "profile", "handbook"}
# Types the app cannot install yet. They are still found and counted, so
# publishing one is safe — the user is told "needs a newer AI-IDE".
RESERVED: set[str] = set()

# The AI-IDE release that first reads each type and each style field — the
# same table as the app's `ShareCompatibility` (FORMAT.md §2.4).
OLDEST = "1.15.0"                    # the first release with sharing at all
LATEST_RELEASED = "1.20.0"           # on the App Store; override with --released
LEGACY_LAST = "1.20.0"               # the last release that reads only aiide-index.json
TYPE_SINCE = {"prompt": "1.15.0", "style": "1.15.0", "kb": "1.15.0",
              "brand": "1.17.0", "reading": "1.17.0", "task": "1.17.0",
              "script": "1.17.0", "profile": "1.17.0", "pdfTemplate": "1.17.0",
              "wordTemplate": "1.17.0", "excelTemplate": "1.17.0",
              "slidesTemplate": "1.17.0", "handbook": "1.21.0"}
FIELD_SINCE = {"refine": "1.15.0", "illustration": "1.15.0", "slideImage": "1.15.0",
               "reportRefine": "1.20.0", "organize": "1.20.0", "expand": "1.20.0",
               "researchPlan": "1.20.0", "researchWrite": "1.20.0",
               "refine.proofread": "1.21.0", "refine.tone.formal": "1.21.0",
               "refine.tone.casual": "1.21.0", "refine.tone.executive": "1.21.0",
               "refine.condense.report": "1.21.0", "refine.condense.deck": "1.21.0",
               "refine.terms": "1.21.0"}
# `brandKit` was reserved in FORMAT.md before the type existed; the app reads
# it as `brand`, so this script must not call it an error either.
TYPE_ALIASES = {"brandKit": "brand"}
STYLE_FIELDS = set(FIELD_SINCE)
MAX_BYTES = {".aiide-prompt": 1 << 20, ".aiide-style": 1 << 20, ".aiide-kb": 10 << 20,
             ".aiide-reading": 1 << 20, ".aiide-brand": 10 << 20,
             ".aiide-pdf": 10 << 20, ".aiide-word": 10 << 20,
             ".aiide-excel": 10 << 20, ".aiide-slides": 40 << 20,
             ".aiide-task": 10 << 20, ".aiide-script": 40 << 20,
             ".aiide-profile": 1 << 20, ".aiide-handbook": 2 << 20}
EXTENSIONS = (".aiide-prompt", ".aiide-style", ".aiide-kb", ".aiide-brand",
              ".aiide-pdf", ".aiide-word", ".aiide-excel", ".aiide-slides",
              ".aiide-reading", ".aiide-task", ".aiide-script",
              ".aiide-profile", ".aiide-handbook")
MANIFEST_KEYS = ("format", "type", "id", "version", "title",
                 "summary", "author", "license", "appMinVersion", "lang", "example",
                 "embeds")

# The codes the app speaks. BCP-47 rather than shorthand: a private
# abbreviation needs a translation table forever and matches nothing else.
LANGS = {
    "zh-hant": "zh-Hant", "zh_hant": "zh-Hant", "zh-tw": "zh-Hant",
    "zh-hk": "zh-Hant", "tc": "zh-Hant",
    "zh-hans": "zh-Hans", "zh_hans": "zh-Hans", "zh-cn": "zh-Hans", "sc": "zh-Hans",
    "en": "en", "en-us": "en", "en-gb": "en",
}


def normalize_lang(raw):
    """None for anything unrecognised — an item tagged `lang: 中文` is better
    treated as untagged (shown to everyone) than filed under a language nobody
    can select. Bare `zh` is ambiguous and resolves to neither."""
    if not raw:
        return None
    return LANGS.get(str(raw).strip().lower())


def lang_from_filename(name):
    """`slide-outline.zh-Hant.aiide-prompt` -> 'zh-Hant'. A convention for
    humans reading the repo; the manifest is what the app believes."""
    base = name.rsplit(".", 1)[0]
    if "." not in base:
        return None
    return normalize_lang(base.rsplit(".", 1)[1])


class Problem(Exception):
    pass


# --------------------------------------------------------------- front matter

def split_front_matter(text):
    """(fields, body). Only the FIRST `---` block is consumed, so a prompt that
    carries front matter of its own survives untouched."""
    if not text.startswith("---\n"):
        return {}, text
    rest = text[4:]
    end = rest.find("\n---")
    while end != -1:
        after = end + 4
        if after >= len(rest) or rest[after] in "\n\r":
            header, body = rest[:end], rest[after:]
            break
        end = rest.find("\n---", after)
    else:
        return {}, text
    fields = {}
    for line in header.split("\n"):
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key and not key.startswith("#"):
            fields[key] = unquote(value.strip())
    return fields, body


def unquote(value):
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


# ------------------------------------------------------------------- readers

def check_manifest(raw, expected_type, where):
    if raw.get("format") != FORMAT:
        raise Problem(f"{where}: format 必須是 {FORMAT}，實際是 {raw.get('format')!r}")
    found = TYPE_ALIASES.get(raw.get("type"), raw.get("type"))
    if found != expected_type:
        raise Problem(f"{where}: 副檔名說是 {expected_type}，但 type 是 {found!r}"
                      "（以 type 為準，App 會拒絕安裝）")
    manifest = {k: raw[k] for k in MANIFEST_KEYS if k in raw}
    manifest["type"] = found          # the spelling the app will use
    return manifest


def read_prompt(path):
    data = path.read_bytes()
    try:
        # utf-8-sig, not utf-8: Foundation strips a leading BOM when it decodes,
        # so the app opens such a file happily. Refusing it here would report a
        # problem that does not exist.
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise Problem(f"{path.name}: 不是 UTF-8 文字檔")
    fields, body = split_front_matter(text)
    if "format" not in fields or "type" not in fields:
        raise Problem(f"{path.name}: 缺少 front matter 的 format / type"
                      "（第一個 --- 區塊必須是 manifest）")
    raw = dict(fields)
    raw["format"] = int(fields["format"]) if fields["format"].isdigit() else fields["format"]
    manifest = check_manifest(raw, "prompt", path.name)
    if not body.strip():
        raise Problem(f"{path.name}: 指令內文是空的")
    if not manifest.get("title") and not any(
            line.strip().startswith("# ") for line in body.split("\n")):
        raise Problem(f"{path.name}: 沒有 title，內文也沒有 # 標題可以取名")
    return manifest


def version_key(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except ValueError:
        return None


def newer(a, b):
    """a > b as releases; 1.20 == 1.20.0."""
    ka, kb = version_key(a) or (), version_key(b) or ()
    n = max(len(ka), len(kb))
    return ka + (0,) * (n - len(ka)) > kb + (0,) * (n - len(kb))


def read_style(path):
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Problem(f"{path.name}: 不是合法的 JSON（{e}）")
    if not isinstance(raw, dict):
        raise Problem(f"{path.name}: 最外層必須是物件")
    manifest = check_manifest(raw, "style", path.name)
    styles = raw.get("styles")
    if not isinstance(styles, list) or not styles:
        raise Problem(f"{path.name}: styles 必須是非空陣列")
    usable = 0
    for i, item in enumerate(styles, 1):
        if not isinstance(item, dict) or not str(item.get("body", "")).strip():
            raise Problem(f"{path.name}: 第 {i} 則沒有 body")
        field = item.get("field")
        if field in STYLE_FIELDS:
            usable += 1
        else:
            # Not fatal — an older app skips exactly this one entry — but a
            # typo here silently costs the user a template, so say it.
            print(f"  ⚠️  {path.name}: 第 {i} 則的 field 是 {field!r}，"
                  f"不在 {sorted(STYLE_FIELDS)} 之中，會被略過")
    if usable == 0:
        raise Problem(f"{path.name}: 沒有任何一則的 field 是可用的")
    fields = [item.get("field") for item in styles if item.get("field") in FIELD_SINCE]
    needs = OLDEST
    for f in fields:
        if newer(FIELD_SINCE[f], needs):
            needs = FIELD_SINCE[f]
    # Kept apart from the manifest the index lists: what the file NEEDS, and
    # whether a build up to 1.20 would still find something in it.
    manifest["_needs"] = needs
    manifest["_legacy_ok"] = any(FIELD_SINCE[f] == OLDEST for f in fields)
    return manifest


def read_kb(path):
    if not zipfile.is_zipfile(path):
        raise Problem(f"{path.name}: 不是 zip 檔")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "manifest.json" not in names:
            raise Problem(f"{path.name}: zip 裡沒有 manifest.json")
        try:
            raw = json.loads(z.read("manifest.json").decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise Problem(f"{path.name}: manifest.json 不是合法的 JSON（{e}）")
        manifest = check_manifest(raw, "kb", path.name)
        entries = [n for n in names if n.startswith("entries/") and n.endswith(".md")]
        if not entries:
            raise Problem(f"{path.name}: entries/ 底下沒有任何 .md 條目")
        usable = 0
        for name in entries:
            _, body = split_front_matter(z.read(name).decode("utf-8-sig", "replace"))
            if body.strip():
                usable += 1
            else:
                print(f"  ⚠️  {path.name}: {name} 內文是空的，會被略過")
        if usable == 0:
            raise Problem(f"{path.name}: 沒有任何一筆條目有內容")
    return manifest


def read_json_pack(path, expected_type, payload_key, payload_desc):
    """The JSON types that are a manifest plus one object."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Problem(f"{path.name}: 不是合法的 JSON（{e}）")
    if not isinstance(raw, dict):
        raise Problem(f"{path.name}: 最外層必須是物件")
    manifest = check_manifest(raw, expected_type, path.name)
    if not isinstance(raw.get(payload_key), dict):
        raise Problem(f"{path.name}: 缺少 {payload_key} 物件（{payload_desc}）")
    return manifest, raw[payload_key]


def read_reading(path):
    manifest, appearance = read_json_pack(path, "reading", "appearance", "閱讀外觀的設定")
    # Every field is optional, so there is nothing to require — but a colour
    # given only for one scheme is invisible in the other, and that is the
    # mistake nobody notices until someone switches to dark mode.
    for key in ("text", "heading", "link", "background"):
        value = appearance.get(key)
        if isinstance(value, dict) and not ("light" in value and "dark" in value):
            print(f"  ⚠️  {path.name}: {key} 只給了 "
                  f"{sorted(value)}，淺色／深色要各給一個（§4.8）")
    return manifest


def read_profile(path):
    manifest, profile = read_json_pack(path, "profile", "profile", "Provider 的連線設定")
    if not profile.get("baseURL"):
        raise Problem(f"{path.name}: profile 少了 baseURL（§4.10a）")
    # The one check worth making on a publisher's machine: a header name that
    # arrived carrying its value is how a credential gets published. The app
    # trims it on read, but by then the file is already in the repo.
    for name in profile.get("headerNames") or []:
        if ":" in str(name):
            raise Problem(f"{path.name}: headerNames 的 {name!r} 看起來夾了值進去。"
                          f"只能放標頭名稱——值絕對不要推上來（§4.10a）")
    for leaked in ("apiKey", "key", "customHeaders", "headers"):
        if leaked in profile:
            raise Problem(f"{path.name}: profile 不該有 {leaked!r} 這個欄位（§4.10a）")
    return manifest


def read_handbook(path):
    manifest, handbook = read_json_pack(path, "handbook", "handbook", "一份簡報輸出手冊")
    if not isinstance(handbook.get("layouts"), list) or not handbook["layouts"]:
        raise Problem(f"{path.name}: handbook.layouts 必須是非空陣列")
    return manifest


def read_excel_template(path):
    return read_json_pack(path, "excelTemplate", "template", "樣板的設定")[0]


def read_zip_pack(path, expected_type, required, checks=()):
    """The zip types: a manifest at the top level plus named parts."""
    if not zipfile.is_zipfile(path):
        raise Problem(f"{path.name}: 不是 zip 檔")
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "manifest.json" not in names:
            raise Problem(f"{path.name}: zip 裡沒有 manifest.json")
        try:
            raw = json.loads(z.read("manifest.json").decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise Problem(f"{path.name}: manifest.json 不是合法的 JSON（{e}）")
        manifest = check_manifest(raw, expected_type, path.name)
        for part in required:
            if part not in names:
                raise Problem(f"{path.name}: zip 裡沒有 {part}")
        # Macros are the one thing this format refuses outright (FORMAT.md §7).
        for name in names:
            if name.lower().endswith(".pptm"):
                raise Problem(f"{path.name}: 內含 {name}——帶巨集的簡報一律拒收")
        # `embeds` is what the install screen promises the reader BEFORE
        # anything is written, so a wrong one is a promise broken on their
        # device rather than a cosmetic slip here.
        declared = set(manifest.get("embeds") or [])
        actual = set()
        if any(n.startswith("brand/") for n in names):
            actual.add("brandkit")
        if "deck.pptx" in names:
            actual.add("pptx")
        if any(n.startswith("prompts/") for n in names):
            actual.add("prompts")
        if any(n.startswith("kb/") and n.endswith(".md") for n in names):
            actual.add("kb")
        if any(n.startswith("files/") for n in names):
            actual.add("files")
        if declared != actual:
            print(f"  ⚠️  {path.name}: embeds 寫 {sorted(declared) or '（沒寫）'}，"
                  f"實際帶的是 {sorted(actual) or '（什麼都沒有）'}")
        for check in checks:
            check(path, names, manifest)
    return manifest


def _wants_brand(path, names, manifest):
    """PDF and Word templates take colours and fonts entirely from a Brand Kit.
    One that ships without gets the recipient's default brand — installable,
    but not the design that was published."""
    if "brand/brand.json" not in names:
        print(f"  ⚠️  {path.name}: 沒有內嵌 brand/brand.json，"
              "對方匯入後會套用他自己的預設品牌（§4.7）")


def read_brand(path):
    return read_zip_pack(path, "brand", ("brand.json",))


def _task_references_resolve(path, names, manifest):
    """A task points at its prompts and KB entries by TITLE, so one that ships
    without them installs as a shell that resolves to nothing (FORMAT.md §4.9).
    Not fatal — the app reports the gap and installs anyway — but it is almost
    always an oversight in packing rather than a decision."""
    import re
    with zipfile.ZipFile(path) as z:
        try:
            task = json.loads(z.read("task.json").decode("utf-8-sig"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            return
        if not isinstance(task, dict):
            return
        titles = set()
        for name in names:
            if not (name.startswith("prompts/") or name.startswith("kb/")):
                continue
            fields, _ = split_front_matter(z.read(name).decode("utf-8-sig", "replace"))
            if fields.get("title"):
                titles.add(fields["title"].strip())
        wanted = [t for t in (task.get("promptTitles") or []) if isinstance(t, str)]
        message = task.get("messageTemplate") or ""
        wanted += re.findall(r"(?<!~)~\[([^\]\n]+)\]", message)
        for title in wanted:
            if title.strip() not in titles:
                print(f"  ⚠️  {path.name}: 工作指向「{title}」，"
                      f"但 prompts/ 與 kb/ 裡沒有同名的項目（§4.9）")


def _script_carries_what_it_reads(path, names, manifest):
    """A script names its fixtures by workspace-relative path, so one shipped
    without them stops at its first `prompt file=` (FORMAT.md §4.10). Not fatal
    — the app installs it and reports the gap — but it is nearly always a
    packing oversight."""
    import re
    with zipfile.ZipFile(path) as z:
        try:
            script = z.read("script.aiide").decode("utf-8-sig")
        except (KeyError, UnicodeDecodeError):
            return
    carried = {n[len("files/"):] for n in names if n.startswith("files/")}
    # Only the unambiguous readers: enough to catch a forgotten fixture without
    # re-implementing the app's own command table here.
    wanted = []
    for line in script.splitlines():
        line = line.split("#", 1)[0].strip()
        for pattern in (r'^(?:open|read|kb_add)\s+"?([^"\s]+)',
                        r'\b(?:file|reply|outline|images_dir)=\"?([^\"\s]+)'):
            for hit in re.findall(pattern, line):
                if "$" not in hit:
                    wanted.append(hit)
    for want in wanted:
        if want in carried:
            continue
        # A folder (`images_dir=`) is carried as its members.
        if any(c.startswith(want.rstrip("/") + "/") for c in carried):
            continue
        print(f"  ⚠️  {path.name}: 腳本會讀取「{want}」，但 files/ 裡沒有（§4.10）")


def read_script(path):
    return read_zip_pack(path, "script", ("script.aiide",),
                         (_script_carries_what_it_reads,))


def read_task(path):
    return read_zip_pack(path, "task", ("task.json",), (_task_references_resolve,))


def read_pdf_template(path):
    return read_zip_pack(path, "pdfTemplate", ("template.json",), (_wants_brand,))


def read_word_template(path):
    return read_zip_pack(path, "wordTemplate", ("template.json",), (_wants_brand,))


def read_slides_template(path):
    return read_zip_pack(path, "slidesTemplate", ("template.json",))


READERS = {".aiide-prompt": read_prompt, ".aiide-style": read_style, ".aiide-kb": read_kb,
           ".aiide-reading": read_reading, ".aiide-brand": read_brand,
           ".aiide-pdf": read_pdf_template, ".aiide-word": read_word_template,
           ".aiide-excel": read_excel_template, ".aiide-slides": read_slides_template,
           ".aiide-task": read_task, ".aiide-script": read_script,
           ".aiide-profile": read_profile, ".aiide-handbook": read_handbook}


def check_language(manifest, path, rel, problems):
    """The filename suffix and `lang:` must agree, because only one of them is
    what the app believes — and a disagreement always means one of them is a
    typo nobody would otherwise notice."""
    declared = manifest.get("lang")
    if declared is not None:
        normalized = normalize_lang(declared)
        if normalized is None:
            problems.append(f"{rel}: lang 是 {declared!r}，不是 zh-Hant / zh-Hans / en")
            return
        manifest["lang"] = normalized
    from_name = lang_from_filename(path.name)
    if from_name and manifest.get("lang") and from_name != manifest["lang"]:
        problems.append(f"{rel}: 檔名說是 {from_name}，但 lang 寫 {manifest['lang']}"
                        "（以 lang 為準，改一邊）")
    elif from_name and not manifest.get("lang"):
        # Filling it in rather than nagging: the author already said it once.
        manifest["lang"] = from_name
        print(f"  ℹ️  {rel}: 從檔名補上 lang: {from_name}")


def check_example(manifest, rel, problems):
    url = manifest.get("example")
    if url and not str(url).startswith("https://"):
        problems.append(f"{rel}: example 必須是 https 網址，實際是 {url!r}")


# ---------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", type=pathlib.Path, help="repo 的根目錄")
    parser.add_argument("--check", action="store_true",
                        help="只驗證，不寫出 aiide-index.json")
    parser.add_argument("--name", default="", help="索引的 name 欄位")
    parser.add_argument("--summary", default="", help="索引的 summary 欄位")
    parser.add_argument("--released", default=LATEST_RELEASED,
                        help=f"App Store 上最新的 AI-IDE 版本（預設 {LATEST_RELEASED}）。"
                             "需要更新版本的檔案會被擋下，不寫進索引")
    args = parser.parse_args()

    root = args.repo.resolve()
    if not root.is_dir():
        sys.exit(f"找不到資料夾：{root}")

    # Same rule as the app: every file in the tree, any depth, chosen by
    # extension. Folder names are a convention for humans, nothing more.
    files = sorted(p for p in root.rglob("*")
                   if p.is_file() and p.suffix.lower() in EXTENSIONS
                   and ".git" not in p.parts)
    if not files:
        sys.exit("這個資料夾裡沒有任何 .aiide-* 檔案。")

    items, problems, skipped = [], [], []
    for path in files:
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        limit = MAX_BYTES.get(path.suffix.lower())
        if limit and size > limit:
            problems.append(f"{rel}: {size} bytes 超過上限 {limit}")
            continue
        reader = READERS.get(path.suffix.lower())
        if reader is None:
            skipped.append(rel)          # a reserved type this script cannot read
            continue
        try:
            manifest = reader(path)
            if isinstance(manifest, tuple):
                manifest = manifest[0]
            check_language(manifest, path, rel, problems)
            check_example(manifest, rel, problems)
            needs, legacy_ok = check_versions(manifest, rel, args.released, problems)
        except Problem as e:
            problems.append(str(e))
            continue
        items.append(({"path": rel, "size": size, **manifest}, legacy_ok))
        mark = "" if not newer(needs, OLDEST) else f"（需要 {needs}）"
        print(f"  ✅ {rel}  →  {manifest.get('title', '(無標題)')}{mark}")

    for rel in skipped:
        print(f"  ⏭️  {rel}：這個型別本腳本還不會讀，會原樣列在 repo 裡")
    if problems:
        # stdout first, or the error block lands above the per-file lines it
        # is meant to summarise.
        sys.stdout.flush()
        print("\n讀不過的檔案：", file=sys.stderr)
        for p in problems:
            print(f"  ❌ {p}", file=sys.stderr)
        sys.exit(f"\n{len(problems)} 個檔案有問題，沒有寫出索引。")

    legacy = [item for item, ok in items if ok]
    every = [item for item, _ in items]
    print(f"\n{len(every)} 個項目全部通過；舊索引（1.15–1.20 讀的）列 {len(legacy)} 個。")
    if not legacy:
        # An empty or missing aiide-index.json sends builds 1.17–1.20 walking
        # the whole repo, where they would meet everything this split hides.
        sys.exit("舊索引會是空的：至少要有一個 1.15 就能讀的項目，否則舊版 App 會改為掃描整個 repo。")
    if args.check:
        return

    write_index(root / "aiide-index.v2.json", every, args)
    write_index(root / "aiide-index.json", legacy, args)


def check_versions(manifest, rel, released, problems):
    """What the file needs, against what it claims and what has shipped.

    Returns (needs, legacy_ok): legacy_ok is False for a file that builds up
    to 1.20 would call broken rather than "needs a newer AI-IDE" — a style
    pack with no field from 1.15 — so it stays out of aiide-index.json.
    """
    needs = manifest.pop("_needs", None) or TYPE_SINCE.get(manifest.get("type"), OLDEST)
    legacy_ok = manifest.pop("_legacy_ok", True)
    if newer(TYPE_SINCE.get(manifest.get("type"), OLDEST), needs):
        needs = TYPE_SINCE[manifest["type"]]
    # Builds up to 1.20 never see what needs more than they are.
    legacy_ok = legacy_ok and not newer(needs, LEGACY_LAST)
    if newer(needs, released):
        problems.append(f"{rel}: 需要 AI-IDE {needs}，但 App Store 上最新是 {released}。"
                        "等新版上架後再放（或用 --released 指定新版本）")
    claimed = manifest.get("appMinVersion")
    if not claimed:
        manifest["appMinVersion"] = needs
        if newer(needs, OLDEST):
            print(f"  ⚠️  {rel}: 沒寫 appMinVersion，索引裡以 {needs} 列出；建議寫進檔案")
    elif version_key(claimed) is None:
        problems.append(f"{rel}: appMinVersion {claimed!r} 不是版本號（例如 1.17.0）")
    elif newer(needs, claimed):
        problems.append(f"{rel}: appMinVersion 寫 {claimed}，但這個檔案需要 {needs}")
    if newer(needs, OLDEST) and needs not in str(manifest.get("summary", "")) \
            and needs.rsplit(".0", 1)[0] not in str(manifest.get("summary", "")):
        # 1.15–1.20 never read appMinVersion; the summary is what they show.
        print(f"  ⚠️  {rel}: 需要 AI-IDE {needs}，建議在 summary 寫明，舊版使用者才看得到")
    return needs, legacy_ok


def write_index(out, items, args):
    index = {"format": FORMAT}
    if args.name:
        index["name"] = args.name
    if args.summary:
        index["summary"] = args.summary
    index["items"] = items
    existing = {}
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    # Keep whatever descriptive fields were already there unless overridden.
    for key in ("name", "summary", "homepage"):
        if key in existing and key not in index:
            index[key] = existing[key]
    index = {k: index[k] for k in ("format", "name", "summary", "homepage", "items")
             if k in index}
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已寫出 {out}（{len(items)} 個項目）")


if __name__ == "__main__":
    main()
