"""お守りカードの切り出しの確認ページ（public/_review/amulet.html。Git には入れない）"""
import base64, io, json
from PIL import Image, ImageDraw
from build2 import *
from albums_amulet import D, M, CFG, k

def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()

if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzzz_amulet.json", encoding="utf-8"))["images"]
    body = ""
    for f, coll, title in (("EMPATHY_amulet.png", "IVE EMPATHY", "IVE EMPATHY「Amulet Card (Tokyo 3/29)」（既存の画像と同じ写真で並びを確認済み）"), ("BeAlright_amulet.png", "Be Alright", "Be Alright「Amulet Card (お守りカード)」（新しい枠。並びは同じと見なした）")):
        cs, rs = CFG[f]; im = Image.open(D + f).convert("RGB"); an = im.copy(); d = ImageDraw.Draw(an)
        for i, m in enumerate(M):
            (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]; d.rectangle((int(x0 * k) + 3, int(y0 * k) + 3, int(x1 * k) - 3, int(y1 * k) - 3), outline=(230, 30, 60), width=6); d.text((int(x0 * k) + 12, int(y0 * k) + 10), f"{i+1}:{m}", fill=(230, 30, 60))
        cells = "".join(f'<div class="c"><b>{e["members"][0]}</b><br><img src="{b64(Image.open(CARDS + e["file"]), 200)}"></div>' for e in out if e["collection"] == coll)
        body += f'<h2>{title}</h2><img class="big" src="{b64(an.crop((0, 700, 1284, 2100)), 500)}"><div class="grid">{cells}</div>'
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>お守りカードの確認</title><style>
body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}h2{{font-size:15px;margin-top:24px}}.big{{max-width:420px;border-radius:8px;border:1px solid #e3d3d5}}.grid{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}.c{{background:#fff;border:1px solid #e3d3d5;border-radius:10px;padding:8px;font-size:13px;text-align:center}}.c img{{width:140px;border-radius:6px}}</style></head><body><h1 style="font-size:18px">お守りカード（Amulet Card）の切り出し</h1>{body}</body></html>"""
    open(PROJ + "public/_review/amulet.html", "w", encoding="utf-8").write(page); print("ok")
