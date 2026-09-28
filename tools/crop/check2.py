"""ラベル（行）× メンバー（列）の確認シート"""
import json, sys, os
from PIL import Image, ImageDraw
SP = os.path.dirname(os.path.abspath(__file__)) + "/"
CARDS = r"C:/Users/kazuk/OneDrive/pocamaster-images/_cards/"
M = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]
name = sys.argv[1]; per = int(sys.argv[2]) if len(sys.argv) > 2 else 40
es = json.load(open(SP + f"out/{name}.json", encoding="utf-8"))["images"]
keys = []
for e in es:
    k = (e["source"], e["version"])
    if k not in keys: keys.append(k)
by = {(e["source"], e["version"], e["members"][0]): e for e in es}
tw, th, lw = 70, 105, 10
for p in range(0, len(keys), per):
    ks = keys[p:p + per]
    S = Image.new("RGB", (lw + 6 * tw, len(ks) * (th + 2)), "white"); d = ImageDraw.Draw(S)
    for i, k in enumerate(ks):
        for c, m in enumerate(M):
            e = by.get((k[0], k[1], m))
            if not e: continue
            im = Image.open(CARDS + e["thumb"]); im.thumbnail((tw - 2, th))
            S.paste(im, (lw + c * tw, i * (th + 2)))
        d.text((0, i * (th + 2) + 40), str(p + i), fill="red")
    S.save(SP + f"c2_{name}_{p // per}.jpg", quality=80); print(f"c2_{name}_{p // per}.jpg")
for i, k in enumerate(keys): print(i, k)
