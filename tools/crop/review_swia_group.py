"""SWIA ランダムトレカの全員のカード 4 枚の切り出し確認ページ（public/_review/swia_group.html。Git には入れない）"""
import base64, io, json
from PIL import Image, ImageDraw
from build2 import *
from albums_swia_group_add import D, BOX
def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()
if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzzzzzzzzzzzz_swia_group.json", encoding="utf-8"))["images"]
    im = Image.open(D + "SWIA_MD_TradingCard_Amazingk.jpg").convert("RGB"); an = im.copy(); d = ImageDraw.Draw(an)
    for i, b in enumerate(BOX, start=1): d.rectangle(b, outline=(230, 30, 60), width=3); d.text((b[0] - 18, b[1] + 4), f"IVE{i}", fill=(230, 30, 60))
    cells = "".join(f'<div class="c"><b>IVE {e["version"][-1]}</b><br><img src="{b64(Image.open(CARDS + e["file"]), 150)}"><br><span class="muted">{Image.open(CARDS + e["file"]).size[0]}×{Image.open(CARDS + e["file"]).size[1]}px</span></div>' for e in out)
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SWIA 全員カードの確認</title><style>body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}.muted{{color:#7a5a62;font-size:12px}}.big{{max-width:420px;border-radius:8px;border:1px solid #e3d3d5}}.grid{{display:flex;gap:8px;margin-top:10px}}.c{{background:#fff;border:1px solid #e3d3d5;border-radius:10px;padding:8px;font-size:13px;text-align:center}}.c img{{width:110px;border-radius:6px}}</style></head><body><h1 style="font-size:18px">SHOW WHAT I AM ランダムトレカの全員のカード</h1><p class="muted">右端の縦 4 枚を、上から IVE 1・2・3・4 と見なしました。順番が違えば教えてください。</p><img class="big" src="{b64(an, 500)}"><div class="grid">{cells}</div></body></html>"""
    open(PROJ + "public/_review/swia_group.html", "w", encoding="utf-8").write(page); print("ok")
