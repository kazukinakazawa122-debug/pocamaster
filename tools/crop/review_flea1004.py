"""フリマの実物の写真 3 回目（hires_real_1004.py）で差し替えた 73 枚を、どの写真のどこを切り取ったかが見えるページにする（本人の要望、2026-10-03）
→ public/_review/flea_1004.html（Git に入れない）。写真ごとに「元の写真＋切り取った範囲（番号つきの赤い枠）」、続けて 1 枚ずつ
「切り取った画像（いまの ZIP の画像。彩度 ×1.2 後）」と「前の画像（差し替える前）」"""
import base64, glob, html, io, json, os, sys, zipfile
from PIL import Image, ImageDraw
from build2 import *
import hires_real_1004 as T

H = T.H
sys.stdout.reconfigure(encoding="utf-8")


def b64(im, w, q=84):
    im = im.convert("RGB").copy(); im.thumbnail((w, w * 3)); f = io.BytesIO(); im.save(f, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()


def mkey(e):
    return (e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])


def prev_images():
    """差し替える前の画像：1002・1003 の job より前の job で、同じ枠の最後の画像"""
    prev = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        name = os.path.basename(p)[:-5]
        if "real_flea" in name:
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            prev[mkey(e)] = CARDS + e["file"]
    return prev


out = json.load(open(H.OUTJ, encoding="utf-8"))
z = zipfile.ZipFile(H.ZIP)
now = {mkey(e): e for e in json.loads(z.read("manifest.json")) if not e.get("cover")}
prev = prev_images()
files = H.photos()
sections = []
for pi in sorted({o["pi"] for o in out if not o["skip"]}):
    cells = [(n, o) for n, o in enumerate(out) if o["pi"] == pi and not o["skip"]]
    im = Image.open(files[pi]).convert("RGB")
    bx = H.photo_box(im)
    over = im.crop(bx)
    d = ImageDraw.Draw(over)
    rows = []
    for i, (n, o) in enumerate(cells, 1):
        b = [o["box"][0] - bx[0], o["box"][1] - bx[1], o["box"][2] - bx[0], o["box"][3] - bx[1]]
        d.rectangle(b, outline=(255, 0, 60), width=6)
        d.rectangle([b[0], b[1], b[0] + 54, b[1] + 54], fill=(255, 0, 60))
        d.text((b[0] + 8, b[1] + 6), str(i), fill=(255, 255, 255), font_size=40) if hasattr(d, "textbbox") else None
        k = tuple(o["key"])
        e = now[(k[0], tuple(sorted(k[1].split("/"))), k[2], k[3])]
        new = Image.open(io.BytesIO(z.read(e["file"])))
        pk = (k[0], tuple(sorted(k[1].split("/"))), k[2], k[3])
        old = Image.open(prev[pk]) if pk in prev else None
        note = "彩度 ×1.2"
        rows.append(
            f'<div class="row"><div class="n">{i}</div><div class="c"><img src="{b64(new, 600, 90)}">切り取り後（高さ {new.size[1]}px）</div>'
            f'<div class="c">{"<img src=" + chr(34) + b64(old, 600, 90) + chr(34) + ">" if old else "（前の画像なし）"}前の画像（高さ {old.size[1] if old else "-"}px）</div>'
            f'<div class="t"><b>{html.escape(k[1])}</b><br>{html.escape(k[0])}<br>{html.escape(k[2])} {html.escape(k[3])}<br>重なり {o["score"]}'
            f'{"<br>" + note if note else ""}</div></div>')
    sections.append(f'<section><h2>写真 {pi}（{len(cells)} 枚）</h2><div class="ph"><img src="{b64(over, 340)}"><div class="rows">{"".join(rows)}</div></div></section>')

page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>フリマの写真 3 回目の切り取り</title><style>
body{{font-family:system-ui,'Hiragino Sans','Yu Gothic',sans-serif;margin:0;padding:16px;background:#fafafa;color:#222}}
h1{{font-size:18px}}h2{{font-size:15px;margin:24px 0 8px}}.ph{{display:flex;gap:16px;align-items:flex-start}}.ph>img{{width:340px;flex:none;border:1px solid #ddd}}
.rows{{display:flex;flex-direction:column;gap:8px}}.row{{display:flex;gap:10px;align-items:flex-start;background:#fff;border:1px solid #e5e5e5;padding:6px}}
.n{{width:24px;font-weight:700;color:#d00}}.c img{{display:block;width:200px;margin-bottom:2px}}.c{{font-size:11px;color:#666;width:200px}}.t{{font-size:12px;line-height:1.5;width:230px}}
</style></head><body><h1>フリマの実物の写真 3 回目：差し替えた {sum(len(s) > 0 for s in sections) and sum(not o["skip"] for o in out)} 枚</h1>
<p style="font-size:12px;color:#666">左の写真の赤い枠が切り取った範囲（番号は右の行の番号）。「切り取り後」は ZIP に入る画像（彩度 ×1.2 後）、「前の画像」は差し替える前の画像です。</p>{"".join(sections)}</body></html>"""
open(PROJ + "public/_review/flea_1004.html", "w", encoding="utf-8").write(page)
print("ページ", len(page) // 1024, "KB")
