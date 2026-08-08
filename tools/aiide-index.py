#!/usr/bin/env python3
"""Validate a share repo and (re)generate its aiide-index.json.

    python3 tools/aiide-index.py /path/to/your/repo
    python3 tools/aiide-index.py /path/to/your/repo --check   # validate only

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
INSTALLABLE = {"prompt", "style", "kb"}
RESERVED = {"brandKit", "pdfTemplate", "wordTemplate", "excelTemplate", "slidesTemplate"}
STYLE_FIELDS = {"refine", "illustration", "slideImage"}
MAX_BYTES = {".aiide-prompt": 1 << 20, ".aiide-style": 1 << 20, ".aiide-kb": 10 << 20}
EXTENSIONS = (".aiide-prompt", ".aiide-style", ".aiide-kb", ".aiide-brand",
              ".aiide-pdf", ".aiide-word", ".aiide-excel", ".aiide-slides")
MANIFEST_KEYS = ("format", "type", "id", "version", "title",
                 "summary", "author", "license", "appMinVersion")


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
    found = raw.get("type")
    if found != expected_type:
        raise Problem(f"{where}: 副檔名說是 {expected_type}，但 type 是 {found!r}"
                      "（以 type 為準，App 會拒絕安裝）")
    return {k: raw[k] for k in MANIFEST_KEYS if k in raw}


def read_prompt(path):
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
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


def read_style(path):
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
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
    return manifest


def read_kb(path):
    if not zipfile.is_zipfile(path):
        raise Problem(f"{path.name}: 不是 zip 檔")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "manifest.json" not in names:
            raise Problem(f"{path.name}: zip 裡沒有 manifest.json")
        try:
            raw = json.loads(z.read("manifest.json").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise Problem(f"{path.name}: manifest.json 不是合法的 JSON（{e}）")
        manifest = check_manifest(raw, "kb", path.name)
        entries = [n for n in names if n.startswith("entries/") and n.endswith(".md")]
        if not entries:
            raise Problem(f"{path.name}: entries/ 底下沒有任何 .md 條目")
        usable = 0
        for name in entries:
            _, body = split_front_matter(z.read(name).decode("utf-8", "replace"))
            if body.strip():
                usable += 1
            else:
                print(f"  ⚠️  {path.name}: {name} 內文是空的，會被略過")
        if usable == 0:
            raise Problem(f"{path.name}: 沒有任何一筆條目有內容")
    return manifest


READERS = {".aiide-prompt": read_prompt, ".aiide-style": read_style, ".aiide-kb": read_kb}


# ---------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", type=pathlib.Path, help="repo 的根目錄")
    parser.add_argument("--check", action="store_true",
                        help="只驗證，不寫出 aiide-index.json")
    parser.add_argument("--name", default="", help="索引的 name 欄位")
    parser.add_argument("--summary", default="", help="索引的 summary 欄位")
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
        except Problem as e:
            problems.append(str(e))
            continue
        items.append({"path": rel, "size": size, **manifest})
        print(f"  ✅ {rel}  →  {manifest.get('title', '(無標題)')}")

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

    print(f"\n{len(items)} 個項目全部通過。")
    if args.check:
        return

    index = {"format": FORMAT}
    if args.name:
        index["name"] = args.name
    if args.summary:
        index["summary"] = args.summary
    index["items"] = items
    out = root / "aiide-index.json"
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
    print(f"已寫出 {out}")


if __name__ == "__main__":
    main()
