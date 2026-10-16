# 中国語フォントの作り方 / Building the Chinese fonts

OST版の `feat/japanese-sd-fonts` 枝の `lib/EpdFont/scripts/` に、ここの3ファイルを置いて変換します。
`chinese_*.txt` は `codepoints/` に置きます。

    python3 build-sd-fonts.py --config zh-fonts.yaml --output-dir ../../../../fonts-out-zh

- `chinese_gb2312.txt`: GB 2312 の漢字 6,763字（Python の gb2312 codec から作成）
- `chinese_big5.txt`: Big5 の漢字 13,053字（同じく big5 codec から作成）
- 画面の中国語訳に使われる漢字は、どちらの一覧にもすべて入っています。

Copy these files into `lib/EpdFont/scripts/` (the lists into `codepoints/`) of the OST branch
`feat/japanese-sd-fonts` and run the command above.
