"""アプリで切り取った画像（import_app_images.py で取り込んだもの）が、どの枠に対応したかを見るページ（本人の要望、2026-10-04）
→ public/_review/app_images.html（Git に入れない）。1 枚ずつ「切り取った画像」「差し替える前の画像」「対応した枠」を並べる。
python tools/crop/review_app_images.py [job の名前の一部。省略すると、アプリから取り込んだ job をすべて]"""
import base64, glob, html, io, json, os, sys
from PIL import Image
from build2 import *

sys.stdout.reconfigure(encoding="utf-8")


def b64(im, w=360, q=88):
    im = im.convert("RGB").copy(); im.thumbnail((w, w * 2)); f = io.BytesIO(); im.save(f, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()


def mkey(e):
    return (e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])


pat = sys.argv[1] if len(sys.argv) > 1 else "_app_"
paths = sorted(glob.glob(SP + "out/*.json"))
app = [p for p in paths if pat in os.path.basename(p)]
# 差し替える前の画像：アプリの job より前に読まれる job の、同じ枠の最後の画像
prev = {}
for p in paths:
    if p in app or "_app_" in os.path.basename(p):
        continue
    for e in json.load(open(p, encoding="utf-8"))["images"]:
        prev[mkey(e)] = CARDS + e["file"]

rows = []
n = 0
for p in app:
    for e in json.load(open(p, encoding="utf-8"))["images"]:
        n += 1
        new = Image.open(CARDS + e["file"])
        old = Image.open(prev[mkey(e)]) if mkey(e) in prev else None
        rows.append(
            f'<div class="row"><div class="n">{n}</div>'
            f'<div class="c"><img src="{b64(new)}">切り取った画像（{new.size[0]}×{new.size[1]}px）</div>'
            f'<div class="c">{"<img src=" + chr(34) + b64(old) + chr(34) + ">" if old else "（前の画像なし）"}前の画像（{"%d×%d" % old.size + "px" if old else "-"}）</div>'
            f'<div class="t"><b>{html.escape("・".join(e["members"]))}</b><br>{html.escape(e["collection"])}<br>{html.escape(e["source"])} {html.escape(e["version"])}</div></div>'
        )

page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>アプリで切り取った画像の対応</title><style>
body{{font-family:system-ui,'Hiragino Sans','Yu Gothic',sans-serif;margin:0;padding:16px;background:#fafafa;color:#222}}
h1{{font-size:18px}}.row{{display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid #e5e5e5;padding:8px;margin-bottom:8px}}
.n{{width:28px;font-weight:700;color:#d00}}.c img{{display:block;width:230px;margin-bottom:2px}}.c{{font-size:11px;color:#666;width:230px}}.t{{font-size:14px;line-height:1.6;min-width:220px}}
</style></head><body><h1>アプリで切り取った画像 {n} 枚の対応</h1>
<p style="font-size:12px;color:#666">左が切り取った画像、中が差し替える前の画像、右が対応した枠（コレクション・入手元・バージョン・メンバー）です。</p>{"".join(rows)}</body></html>"""
open(PROJ + "public/_review/app_images.html", "w", encoding="utf-8").write(page)
print("ページ", n, "枚", len(page) // 1024, "KB")
