"""MINIVE × LINE FRIENDS の切り出しの確認ページ（public/_review/linefriends.html。Git には入れない）"""
import base64, io, json
from PIL import Image, ImageDraw
import grid
from build2 import *
from albums_linefriends import D, KEYS, NEW
Image.MAX_IMAGE_PIXELS = None
def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()
if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzzzzz_linefriends.json", encoding="utf-8"))["images"]
    by = {(e["members"][0], e["version"]): e for e in out}
    body = ""
    for key, name in KEYS:
        im = grid.load(D + f"{key}_na.jpg"); an = im.crop((2950, 2480, 4500, 3050)); d = ImageDraw.Draw(an)
        for i, v in enumerate(NEW): d.rectangle((int(3105 + 211.4 * i) - 2950 + 3, 2638 - 2480 + 3, int(3105 + 211.4 * i) - 2950 + 191, 2638 - 2480 + 293), outline=(230, 30, 60), width=4)
        cells = "".join(f'<div class="c">{v}<br>' + (f'<img src="{b64(Image.open(CARDS + by[(name, v)]["file"]), 160)}"><br><span class="muted">{Image.open(CARDS + by[(name, v)]["file"]).size[0]}px・{by[(name, v)]["credit"]}</span>' if (name, v) in by else '<span class="muted">画像なし</span>') + '</div>' for v in NEW + ["特典 1", "特典 2"])
        body += f'<h2>{name}</h2><img class="big" src="{b64(an, 700)}"><div class="grid">{cells}</div>'
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MINIVE × LINE FRIENDS の確認</title><style>
body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}h2{{font-size:15px;margin-top:22px}}.muted{{color:#7a5a62;font-size:11px}}.big{{max-width:560px;border-radius:8px;border:1px solid #e3d3d5}}.grid{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}.c{{background:#fff;border:1px solid #e3d3d5;border-radius:8px;padding:6px;font-size:12px;text-align:center;min-width:100px}}.c img{{width:100px;border-radius:6px}}</style></head><body><h1 style="font-size:18px">MINIVE × LINE FRIENDS の切り出しの確認</h1><p class="muted">上は表の位置（赤い枠＝切り出し）、下はアプリに入る画像です。「画像なし」は表にない旧枠（キーリング・特典）です。</p>{body}</body></html>"""
    open(PROJ + "public/_review/linefriends.html", "w", encoding="utf-8").write(page); print("ok")
