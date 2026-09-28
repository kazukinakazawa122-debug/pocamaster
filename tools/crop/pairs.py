"""メンバー別の一覧表からカードを切り出し、2 人の表に同じ写真があればペアとみなす"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
ROOT = r"C:/Users/kazuk/OneDrive/pocamaster-images/"
ENG = ROOT + "IVE English ver. - photocard list-20260927T144026Z-1-001/IVE English ver. - photocard list/"
roots = sorted(f for f in os.listdir(ROOT) if f.lower().endswith(".jpg"))

SETS = {
    "switch": {m: ROOT + roots[i] for m, i in [("ガウル", 27), ("ユジン", 28), ("レイ", 29), ("リズ", 30), ("ウォニョン", 31), ("イソ", 32)]},
    "lucid": {m: ROOT + roots[i] for m, i in [("レイ", 61), ("ユジン", 62), ("ガウル", 63), ("ウォニョン", 64), ("イソ", 65), ("リズ", 66)]},
    "swih": {m: ENG + "world tour/" + f for m, f in [("ガウル", "01-gaeul.JPG"), ("ユジン", "02-yujin.JPG"), ("レイ", "03-rei.JPG"),
                                                   ("ウォニョン", "04-wonyoung.JPG"), ("リズ", "05-liz.JPG"), ("イソ", "06-leeseo.JPG")]},
}

def detect(path, W=1400):
    im = Image.open(path).convert("RGB")
    s = W / im.width
    im = im.resize((W, int(im.height * s)))
    a = np.asarray(im).astype(int)
    gray = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    mask = (gray < 225) | (sat > 40)
    mask = ndimage.binary_opening(mask, iterations=2)
    lab, n = ndimage.label(mask)
    boxes = []
    for sl in ndimage.find_objects(lab):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if w < W * 0.035 or h < W * 0.05: continue
        r = h / w
        if 1.2 < r < 1.75 and w < W * 0.25:
            boxes.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    return im, boxes

def dhash(im, box, n=16):
    x0, y0, x1, y1 = box
    mx, my = (x1 - x0) * 0.12, (y1 - y0) * 0.12
    c = im.crop((x0 + mx, y0 + my, x1 - mx, y1 - my)).convert("L").resize((n + 1, n))
    a = np.asarray(c).astype(int)
    return (a[:, 1:] > a[:, :-1]).flatten()

def run(name):
    cards = []
    for mem, path in SETS[name].items():
        im, boxes = detect(path)
        for b in boxes:
            cards.append({"m": mem, "box": b, "h": dhash(im, b), "im": im})
        print(mem, len(boxes))
    # 他のメンバーの表で似た写真を探す
    matches = []
    for i, a in enumerate(cards):
        for j in range(i + 1, len(cards)):
            b = cards[j]
            if a["m"] == b["m"]: continue
            d = int((a["h"] != b["h"]).sum())
            if d <= 40: matches.append((d, i, j))
    matches.sort()
    # 確認用の画像：左右に並べる
    rows = matches[:60]
    tw = 140; th = 200
    S = Image.new("RGB", (tw * 2 + 260, max(1, len(rows)) * (th + 6)), "white"); d = ImageDraw.Draw(S)
    out = []
    for k, (dist, i, j) in enumerate(rows):
        for col, c in enumerate((cards[i], cards[j])):
            t = c["im"].crop(c["box"]).resize((tw, th)); S.paste(t, (col * tw, k * (th + 6)))
        d.text((tw * 2 + 8, k * (th + 6) + 80), f"#{k} d={dist}", fill="black")
        out.append({"k": k, "d": dist, "a": cards[i]["m"], "b": cards[j]["m"], "ay": cards[i]["box"][1], "by": cards[j]["box"][1], "ax": cards[i]["box"][0], "bx": cards[j]["box"][0]})
    S.save(SP + f"pairs_{name}.jpg", quality=85)
    json.dump(out, open(SP + f"pairs_{name}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(name, "matches", len(matches))
    for o in out: print(o)

if __name__ == "__main__":
    run(sys.argv[1])
