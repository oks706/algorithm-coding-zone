"""Embed subsetted IBM Plex fonts into the deck HTML.

usage: python3 -I build_deck.py SRC_HTML OUT_HTML FONT_DIR_KR FONT_DIR_MONO
"""
import base64
import io
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

src, out, kr_dir, mono_dir = sys.argv[1:5]
html = open(src, encoding="utf-8").read()

chars = {c for c in html if ord(c) >= 0x20}
chars |= {chr(c) for c in range(0x20, 0x7F)}
chars |= set("→←↑↓≤≥×−–—…‹›①②③④⑤·∞Θ²")
text = "".join(sorted(chars))

FACES = [
    ("Plex KR", 400, f"{kr_dir}/IBMPlexSansKR-Regular.woff2"),
    ("Plex KR", 500, f"{kr_dir}/IBMPlexSansKR-Medium.woff2"),
    ("Plex KR", 700, f"{kr_dir}/IBMPlexSansKR-Bold.woff2"),
    ("Plex Mono", 400, f"{mono_dir}/IBMPlexMono-Regular.woff2"),
    ("Plex Mono", 500, f"{mono_dir}/IBMPlexMono-Medium.woff2"),
    ("Plex Mono", 600, f"{mono_dir}/IBMPlexMono-SemiBold.woff2"),
]

rules = []
total = 0
for family, weight, path in FACES:
    font = TTFont(path)
    cmap = font.getBestCmap()
    if family == "Plex KR":
        missing = sorted({c for c in chars if ord(c) not in cmap and not c.isspace()})
        if missing:
            print(f"{family} {weight}: no glyph for {''.join(missing)!r} (system font fallback)")
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = buf.getvalue()
    total += len(data)
    b64 = base64.b64encode(data).decode("ascii")
    rules.append(
        f'@font-face{{font-family:"{family}";font-weight:{weight};font-style:normal;'
        f'font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2")}}'
    )
    print(f"{family} {weight}: {len(data)/1024:.1f} KB")

marker = "/*@FONTS@*/"
assert html.count(marker) == 1, "font marker missing"
html = html.replace(marker, "\n".join(rules))
open(out, "w", encoding="utf-8").write(html)
print(f"fonts total {total/1024:.1f} KB, output {len(html.encode('utf-8'))/1024:.1f} KB, chars {len(chars)}")
