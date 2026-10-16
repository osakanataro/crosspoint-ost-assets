# crosspoint-ost-assets

OST版 CrossPoint Reader（[osakanataro/crosspoint-reader-mod](https://github.com/osakanataro/crosspoint-reader-mod)）の
実機検証用に、本体が Wi-Fi で取りに来るファイルを置く場所です。ファイルは各リリースの添付として置きます。

This repository hosts files that test builds of the OST edition of CrossPoint Reader download over
Wi-Fi: SD-card fonts and UI language packs. The files are release assets.

## リリース / Releases

| タグ / tag | 中身 / contents | 本体側の取得先 / used by |
|---|---|---|
| `sd-fonts-m1-b4` | `.cpfont`（一覧形式 v1・フォント形式 v4）、`fonts.json`、`NOTICE.txt`、`OFL-1.1.txt` | Settings > System > Manage fonts（`FONT_MANIFEST_URL`） |
| `ui-lang-p2` | 画面の言語ファイル `<code>.cplang`（形式 v2、言語コード8文字まで）。中国語（簡体字・繁体字）と韓国語を含む38言語 | 言語選択でファイルが無いとき（`LANG_PACK_BASE_URL`） |
| `ui-lang-p1` | 旧形式 v1 の言語ファイル（35言語）。proto3 までの試験版用 | 同上（旧版） |

### フォント / Fonts

- 本家 CrossPoint Reader が [crosspoint-fonts](https://github.com/crosspoint-reader/crosspoint-fonts/releases/tag/sd-fonts-m1-b4)
  で配っている書体のうち、許諾で名前が予約されていない（OFL の Reserved Font Name を変換後の名前が使わない）17書体を、
  そのまま複製しています。CRC は本家の一覧と照合済みです。
- 日本語3書体（BIZUDGothic、BIZUDMincho、NotoSansJP）は OST版の `fonts-202609080.zip` と同じものです。
- 中国語2書体（NotoSansSC＝簡体字、NotoSansTC＝繁体字）は Noto Sans CJK SC/TC 2.004 から作りました。
  漢字は GB 2312（6,763字）と Big5（13,053字）に絞っています。作り方は `scripts/chinese-fonts/` にあります。
- 書体ごとの著作権者と取得元は `NOTICE.txt` にあります。すべて SIL Open Font License 1.1 です。
- 作り直すときは `scripts/build_fonts_release.py` を使います。

Seventeen upstream families whose converted files use no Reserved Font Name are mirrored unchanged
(CRC-checked against the upstream manifest), plus three Japanese and two Chinese families
(Noto Sans CJK SC/TC, hanzi cut to GB 2312 / Big5). See `NOTICE.txt`.

### 言語ファイル / UI language packs

- `feat/ui-language-packs` 枝の組み立てで `.pio/lang/` に出力される `.cplang` です。
  訳文は CrossPoint Reader の翻訳（MIT License, Copyright (c) 2025 CrossPoint Reader organization）から作っています。
  中国語の訳は CrossPoint Reader CJK（MIT License, Copyright (c) 2025 aBER）の簡体字・繁体字から、
  韓国語の訳は CrossPoint Reader KO（MIT License）から取りました。
  英語の原文が後から書き換わって意味が変わった項目（中国語11、韓国語10）は、訳を入れず英語で出します。
- 韓国語の画面は、フォント一覧の RIDIBatang（8/10/12pt あり、標準のみ）で表示できます。
- ファイルには英語と異なる文字列だけが入っています。本体は、選んだ言語のファイルを SD の `/lang` から
  内蔵メモリへ写して使います。

The packs are built by `gen_i18n.py` on the `feat/ui-language-packs` branch from CrossPoint Reader's
translations (MIT License); the Chinese strings come from CrossPoint Reader CJK and the Korean ones from CrossPoint Reader KO (both MIT License).
