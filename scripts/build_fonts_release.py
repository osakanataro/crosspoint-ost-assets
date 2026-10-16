#!/usr/bin/env python3
"""Build the files of the sd-fonts-m1-b4 release of crosspoint-ost-assets.

The release mirrors the upstream CrossPoint fonts whose licences declare no
Reserved Font Name used by the converted file, and adds the OST Japanese fonts.

    python3 scripts/build_fonts_release.py --jp-zip fonts-202609080.zip \
        --zh-dir ../fonts-out-zh --out dist/fonts

--zh-dir is the output of build-sd-fonts.py (OST branch feat/japanese-sd-fonts)
run with --config scripts/chinese-fonts/zh-fonts.yaml; see that folder.
"""

import argparse
import io
import json
import shutil
import sys
import urllib.request
import zipfile
import zlib
from pathlib import Path

import yaml

UPSTREAM_RELEASE = "https://github.com/crosspoint-reader/crosspoint-fonts/releases/download/sd-fonts-m1-b4/"
UPSTREAM_YAML = (
    "https://raw.githubusercontent.com/crosspoint-reader/crosspoint-reader/develop/lib/EpdFont/scripts/sd-fonts.yaml"
)
OST_BASE_URL = "https://github.com/osakanataro/crosspoint-ost-assets/releases/download/sd-fonts-m1-b4/"
MANIFEST_VERSION = 1

# Upstream families mirrored here: licence, copyright line(s), and a note.
# Families left out declare a Reserved Font Name that the converted file uses
# (OFL condition 3): Alef, GentiumBookPlus, IBMPlexMono/Sans/Serif, LibreBaskerville,
# Libron, Lora, MaruBuri, MaruBuriSemiBold, Merriweather, OpenDyslexic, Pretendard,
# PretendardMedium, SourceCodePro, SourceSans3, SourceSerif4.
MIRRORED = {
    "Alegreya": ("Copyright 2011 The Alegreya Project Authors (https://github.com/huertatipografica/Alegreya)", ""),
    "Amiri": ("Copyright 2010-2022 The Amiri Project Authors (https://github.com/aliftype/amiri).", ""),
    "AtkinsonHyperlegibleNext": (
        "Copyright 2020-2024 The Atkinson Hyperlegible Next Project Authors "
        "(https://github.com/googlefonts/atkinson-hyperlegible-next)",
        "",
    ),
    "Bitter": (
        "Copyright 2011 The Bitter Project Authors (https://github.com/solmatas/BitterPro) "
        'with Reserved Font Name "Bitter Pro".',
        'The converted file is named "Bitter"; it does not use the Reserved Font Name "Bitter Pro".',
    ),
    "DavidLibre": (
        "Copyright 2016 The David Libre Project Authors (https://github.com/meirsadan/david-libre), "
        "with reserved font name \"Hadash\", \"Gentium\" and 'SIL'.",
        "The converted file is named \"DavidLibre\"; it uses none of the Reserved Font Names.",
    ),
    "Domitian": (
        "Copyright (c) 2014, 2015 by (URW)++ Design & Development\n"
        "Copyright (c) 2019--2020 by Daniel Benjamin Miller",
        "Domitian is offered under AGPL-3 (with font exception), LPPL 1.3c or OFL 1.1, at the user's "
        "option. This copy is distributed under the SIL Open Font License 1.1.",
    ),
    "FrankRuhlLibre": (
        "Copyright 2015 The Frank Ruhl Libre Project Authors (https://github.com/fontef/frankruhllibre)",
        "",
    ),
    "Inter": ("Copyright 2020 The Inter Project Authors (https://github.com/rsms/inter)", ""),
    "LexicaUltralegible": ("Copyright 2020 Braille Institute of America, Inc.", ""),
    "Literata": ("Copyright 2017 The Literata Project Authors (https://github.com/googlefonts/literata)", ""),
    "NotoKufiArabic": ("Copyright 2022 The Noto Project Authors (https://github.com/notofonts/arabic)", ""),
    "NotoNaskhArabicUI": ("Copyright 2022 The Noto Project Authors (https://github.com/notofonts/arabic)", ""),
    "NotoNaskhArabicUISemiBold": (
        "Copyright 2022 The Noto Project Authors (https://github.com/notofonts/arabic)",
        "",
    ),
    "NotoSansExtended": (
        "Copyright 2022 The Noto Project Authors (https://github.com/notofonts/latin-greek-cyrillic)",
        "",
    ),
    "NotoSerifExtended": (
        "Copyright 2022 The Noto Project Authors (https://github.com/notofonts/latin-greek-cyrillic)",
        "",
    ),
    "RIDIBatang": (
        "Copyright (c) 2019 RIDI & Sandoll. Font designed by Sandoll Inc.",
        "RIDI publishes RIDIBatang under the SIL Open Font License 1.1 (https://ridicorp.com/ridibatang/); "
        "selling the font by itself is not allowed. RIDIBatang is a registered trademark of RIDI Corporation.",
    ),
    "Vollkorn": ("Copyright 2017 The Vollkorn Project Authors (https://github.com/FAlthausen/Vollkorn-Typeface)", ""),
}

JP_FAMILIES = {
    "BIZUDGothic": "Japanese UD gothic (BIZ UD Gothic, JIS X 0213, vertical punctuation)",
    "BIZUDMincho": "Japanese UD mincho (BIZ UD Mincho, JIS X 0213, vertical punctuation)",
    "NotoSansJP": "Japanese sans-serif (Noto Sans CJK JP, JIS X 0213, vertical punctuation)",
}
JP_GROUP = {"tag": "japanese", "label": "Japanese"}

ZH_FAMILIES = {
    "NotoSansSC": (
        "Simplified Chinese sans-serif (Noto Sans CJK SC, GB 2312)",
        "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-{style}.otf",
        "chinese_gb2312.txt (GB 2312 hanzi)",
    ),
    "NotoSansTC": (
        "Traditional Chinese sans-serif (Noto Sans CJK TC, Big5)",
        "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-{style}.otf",
        "chinese_big5.txt (Big5 hanzi)",
    ),
}
ZH_GROUP = {"tag": "chinese", "label": "Chinese"}
ZH_COPYRIGHT = "\u00a9 2014-2021 Adobe (http://www.adobe.com/). Noto is a trademark of Google LLC."
NOTO_MATH = "https://github.com/notofonts/notofonts.github.io/raw/main/fonts/NotoSansMath/hinted/ttf/NotoSansMath-Regular.ttf"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jp-zip", required=True, type=Path)
    ap.add_argument("--zh-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--licence", default=Path(__file__).resolve().parent.parent / "licenses" / "OFL-1.1.txt", type=Path)
    args = ap.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    upstream = json.loads(fetch(UPSTREAM_RELEASE + "fonts.json"))
    if upstream.get("version") != MANIFEST_VERSION:
        sys.exit(f"unexpected upstream manifest version {upstream.get('version')}")
    sources = {f["name"]: f for f in yaml.safe_load(fetch(UPSTREAM_YAML))["families"]}

    families = []
    notice = []
    for fam in upstream["families"]:
        name = fam["name"]
        if name not in MIRRORED:
            continue
        for f in fam["files"]:
            dest = out / f["name"]
            if not (dest.exists() and dest.stat().st_size == f["size"]):
                print(f"download {f['name']}", flush=True)
                dest.write_bytes(fetch(UPSTREAM_RELEASE + f["name"]))
            data = dest.read_bytes()
            if len(data) != f["size"] or zlib.crc32(data) != f["crc32"]:
                sys.exit(f"{f['name']}: size or CRC differs from the upstream manifest")
        families.append(fam)
        copyright_line, note = MIRRORED[name]
        urls = sorted({s.get("url") or f"crosspoint-reader lib/EpdFont/{s.get('path')}" for s in sources[name]["styles"].values()})
        notice.append(f"== {name} ==")
        notice.append("  files: " + ", ".join(f["name"] for f in fam["files"]))
        notice.append("  converted by CrossPoint Reader (crosspoint-reader/crosspoint-fonts) from:")
        notice += [f"    {u}" for u in urls]
        notice += [f"  {line}" for line in copyright_line.split("\n")]
        notice.append("  licence: SIL Open Font License 1.1 (OFL-1.1.txt)")
        if note:
            notice.append(f"  note: {note}")
        notice.append("")
    missing = set(MIRRORED) - {f["name"] for f in families}
    if missing:
        sys.exit(f"not in the upstream manifest: {sorted(missing)}")

    with zipfile.ZipFile(args.jp_zip) as z:
        jp_notice = z.read("fonts/NOTICE.txt").decode()
        for jp in JP_FAMILIES:
            files = []
            for info in sorted(z.infolist(), key=lambda i: i.filename):
                p = Path(info.filename)
                if p.suffix != ".cpfont" or p.parent.name != jp:
                    continue
                data = z.read(info)
                (out / p.name).write_bytes(data)
                files.append({"name": p.name, "size": len(data), "crc32": zlib.crc32(data)})
            if not files:
                sys.exit(f"{jp}: no files in {args.jp_zip}")
            families.append(
                {
                    "name": jp,
                    "description": JP_FAMILIES[jp],
                    "styles": ["regular", "bold"],
                    "scripts": [JP_GROUP["tag"]],
                    "files": files,
                }
            )

    zh_notice = []
    for zh, (description, url, kept) in ZH_FAMILIES.items():
        files = []
        for src in sorted((args.zh_dir / zh).glob(f"{zh}_*.cpfont"), key=lambda p: int(p.stem.rsplit("_", 1)[1])):
            data = src.read_bytes()
            (out / src.name).write_bytes(data)
            files.append({"name": src.name, "size": len(data), "crc32": zlib.crc32(data)})
        if not files:
            sys.exit(f"{zh}: no files in {args.zh_dir}")
        families.append(
            {"name": zh, "description": description, "styles": ["regular", "bold"], "scripts": [ZH_GROUP["tag"]], "files": files}
        )
        zh_notice += [
            f"== {zh} ==",
            "  files: " + ", ".join(f["name"] for f in files),
            "  converted for the OST field test from (version 2.004):",
            f"    regular {url.format(style='Regular')}",
            f"    bold    {url.format(style='Bold')}",
            f"  fallback for code points the source lacks: Noto Sans (bundled with CrossPoint), {NOTO_MATH}",
            f"  hanzi kept: {kept}, plus the Latin/Greek/Cyrillic/symbol/kana ranges of NotoSansJP",
            f"  {ZH_COPYRIGHT}",
            "  licence: SIL Open Font License 1.1 (OFL-1.1.txt); no Reserved Font Name is declared",
            "",
        ]

    families.sort(key=lambda f: f["name"])
    used = {t for f in families for t in f["scripts"]}
    groups = [g for g in upstream["scriptGroups"] if g["tag"] in used] + [JP_GROUP, ZH_GROUP]
    manifest = {"version": MANIFEST_VERSION, "baseUrl": OST_BASE_URL, "scriptGroups": groups, "families": families}
    (out / "fonts.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    header = (
        "Fonts in the sd-fonts-m1-b4 release of osakanataro/crosspoint-ost-assets\n\n"
        "Every .cpfont file is a bitmap conversion of the source fonts named below, made for\n"
        "CrossPoint Reader. All sources are published under the SIL Open Font License 1.1\n"
        "(OFL-1.1.txt); the converted files are distributed under the same licence.\n"
        "Copyright remains with the respective copyright holders.\n\n"
        "Part 1: unchanged copies of the files that CrossPoint Reader publishes at\n"
        f"{UPSTREAM_RELEASE}\n\n"
    )
    text = (
        header
        + "\n".join(notice)
        + "\nPart 2: Chinese fonts converted for OST版\n\n"
        + "\n".join(zh_notice)
        + "\nPart 3: Japanese fonts converted for OST版 (fonts zip NOTICE follows)\n\n"
        + jp_notice
    )
    (out / "NOTICE.txt").write_text(text)
    shutil.copyfile(args.licence, out / "OFL-1.1.txt")
    total = sum(f["size"] for fam in families for f in fam["files"])
    print(f"{len(families)} families, {sum(len(f['files']) for f in families)} files, {total / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
