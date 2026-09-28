"""out/<name>.json の画像を、6 人ずつ 1 行に並べた確認用シートにする"""
import json, sys, os
from PIL import Image, ImageDraw

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
CARDS = r"C:/Users/kazuk/OneDrive/pocamaster-images/_cards/"
ROMA = {"ユジン": "YJ", "ガウル": "GE", "レイ": "RE", "ウォニョン": "WY", "リズ": "LZ", "イソ": "LS"}

name = sys.argv[1]
per_page = int(sys.argv[2]) if len(sys.argv) > 2 else 20
data = json.load(open(SP + f"out/{name}.json", encoding="utf-8"))
imgs = data["images"]
rows = []
for e in imgs:
    key = (e["source"], e["version"])
    if not rows or rows[-1][0] != key:
        rows.append((key, []))
    rows[-1][1].append(e)
tw, th, lw = 90, 135, 150
for p in range(0, len(rows), per_page):
    chunk = rows[p:p + per_page]
    S = Image.new("RGB", (lw + 8 * tw, len(chunk) * (th + 4)), "white")
    d = ImageDraw.Draw(S)
    for i, (key, es) in enumerate(chunk):
        y = i * (th + 4)
        d.text((4, y + 50), f"{p + i}", fill="red")
        for k, e in enumerate(es[:8]):
            im = Image.open(CARDS + e["thumb"])
            im.thumbnail((tw - 4, th))
            S.paste(im, (lw + k * tw, y))
            d.text((lw + k * tw + 2, y + th - 12), "/".join(ROMA.get(m, m) for m in e["members"]), fill="red")
    S.save(SP + f"chk_{name}_{p // per_page}.jpg", quality=80)
    print(SP + f"chk_{name}_{p // per_page}.jpg")
# 行ラベルの一覧（番号 → 入手元）
for i, (key, es) in enumerate(rows):
    print(i, key[0], key[1], len(es))
