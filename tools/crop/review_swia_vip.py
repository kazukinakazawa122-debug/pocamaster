"""SHOW WHAT I AM VIP Perks Japan の切り出しと対応の確認ページ（public/_review/swia_vip.html。Git には入れない）"""
import base64, io, json
from PIL import Image, ImageDraw
from build2 import *
from albums_swia_vip_add import D, ORDER, BOX, k
def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()
if __name__ == "__main__":
    out = {e["members"][0]: e for e in json.load(open(SP + "out/zzzzzzzzzzzzzzzzz_swia_vip.json", encoding="utf-8"))["images"]}
    im = Image.open(D + "VIP_Perks_Japan_実物.png").convert("RGB"); an = im.copy(); d = ImageDraw.Draw(an)
    for m, b in zip(ORDER, BOX): d.rectangle(tuple(int(v * k) for v in b), outline=(230, 30, 60), width=6); d.text((int(b[0] * k) + 14, int(b[1] * k) + 10), m, fill=(230, 30, 60))
    cells = "".join(f'<div class="c"><b>{m}</b><br><img src="{b64(Image.open(CARDS + out[m]["file"]), 180)}"></div>' for m in ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"])
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SWIA VIP Perks Japan の確認</title><style>body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}.muted{{color:#7a5a62;font-size:12px}}.big{{max-width:380px;border-radius:8px;border:1px solid #e3d3d5}}.grid{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}.c{{background:#fff;border:1px solid #e3d3d5;border-radius:10px;padding:8px;font-size:13px;text-align:center}}.c img{{width:140px;border-radius:6px}}</style></head><body><h1 style="font-size:18px">SHOW WHAT I AM VIP Perks Japan の切り出しと対応</h1><p class="muted">赤い枠が切り出し位置、名前が割り当てたメンバーです。並びは標準ではなく、上段＝ユジン・ガウル・イソ／下段＝レイ・ウォニョン・リズ（@idalshiro のメンバー別の表の同じカードと写真を突き合わせて決めた）。</p><img class="big" src="{b64(an.crop((0,700,1284,2100)), 420)}"><div class="grid">{cells}</div></body></html>"""
    open(PROJ + "public/_review/swia_vip.html", "w", encoding="utf-8").write(page); print("ok")
