"""画質を上げる：店舗ごとの表（カードが大きい）から切り出し直す

いま入っている画像（全体表・メンバー別の表から切り出した小さい画像）と、店舗ごとの表のカードを
「同じ写真かどうか」で突き合わせ、見つかったものだけ大きい画像に差し替える。
枠（コレクション・メンバー・入手元・バージョン）は、いまの画像のものをそのまま使う。

結果は out/zz_hires.json（merge.py で最後に読むので、同じ枠の古い画像より優先される）
確認用：out/hires_report.csv（差し替えた枠・似ている度合い・どの表から切ったか）
"""
import csv, glob, json, os
import numpy as np
from PIL import Image
from build2 import *

FOLDERS = {  # 店舗ごとの表のフォルダ → コレクション
    "01 - eleven": "ELEVEN",
    "02 - love dive": "LOVE DIVE",
    "03 - after like": "After LIKE",
    "04 - IveIVE": "I've IVE",
    "I_VE MINE": "I've MINE",
    "09 - fancon": "1st FAN CONCERT 'The Prom Queens'",
    "world tour": "1st WORLD TOUR 'SHOW WHAT I HAVE'",
}
MIN_W = 185      # この横幅（px）より小さいカードの表は使わない（いまと変わらないため）
GAIN = 1.25      # いまの画像より 1.25 倍以上大きくなるときだけ差し替える
TH = 0.80        # 同じ写真とみなす似ている度合い（相関）
MARGIN = 0.06    # 2 番目に似ているものとの差がこれ以上あること

# 使わない表（カードの大きさを測った一覧から、横幅が MIN_W 以上のものだけ使う）
sizes = {}
for r in csv.DictReader(open(SP + "out/cardsizes.csv", encoding="utf-8")):
    sizes[(r["folder"], r["file"])] = int(r["card_w"] or 0)


def feat(img):
    """中央 80% を 24×36 に縮め、明るさ・色の差をならした特徴"""
    w, h = img.size
    if w > h:
        img = img.rotate(90, expand=True)
        w, h = img.size
    a = np.asarray(img.crop((w * .1, h * .1, w * .9, h * .9)).convert("RGB").resize((24, 36), Image.BILINEAR)).astype(float)
    a = a - a.mean(axis=(0, 1))
    a = a / (a.std() + 1e-6)
    return a.flatten() / np.sqrt(a.size)


# いまの画像（枠つき）
old = []
for p in sorted(glob.glob(SP + "out/*.json")):
    if os.path.basename(p) == "zz_hires.json":
        continue
    old += json.load(open(p, encoding="utf-8"))["images"]
if os.path.exists(CARDS + "manifest.json"):
    old += [e for e in json.load(open(CARDS + "manifest.json", encoding="utf-8")) if e["collection"] == "After LIKE"]
cols = set(FOLDERS.values())
old = [e for e in old if e["collection"] in cols and not e["source"].startswith("グッズ｜")]
for e in old:
    im = Image.open(CARDS + e["file"])
    e["_w"] = min(im.size)
    e["_f"] = feat(im)
print("いまの画像", len(old))

# 店舗ごとの表からカードを探す
new = []
for folder, coll in FOLDERS.items():
    key = "IVE English ver. - photocard list-20260927T144026Z-1-001/IVE English ver. - photocard list/" + folder
    for f in sorted(os.listdir(ENG + folder)):
        if sizes.get((key, f), 0) < MIN_W:
            continue
        im = grid.load(ENG + folder + "/" + f)
        bs = grid.card_boxes(im, ratio=(1.2, 1.8), min_w=0.06, max_w=0.45)
        bs += grid.card_boxes(im, ratio=(0.55, 0.84), min_w=0.1, max_w=0.6)
        for b in bs:
            c = im.crop(tuple(int(v) for v in b))
            if min(c.size) < MIN_W * 0.8:
                continue
            new.append({"coll": coll, "src": f"{folder}/{f}", "box": [int(v) for v in b], "img": c, "_f": feat(c), "_w": min(c.size)})
print("店舗ごとの表のカード", len(new))

j = Job("zz_hires")
rep = []
for coll in cols:
    O = [e for e in old if e["collection"] == coll]
    N = [n for n in new if n["coll"] == coll]
    if not O or not N:
        continue
    S = np.array([[o["_f"] @ n["_f"] for n in N] for o in O])
    for i, o in enumerate(O):
        order = np.argsort(-S[i])
        b = order[0]
        best = S[i, b]
        # 2 番目：同じ写真の別の切り出し（best と同じもの）は数えない
        second = max([S[i, k] for k in order[1:] if N[k]["_f"] @ N[b]["_f"] < 0.9] or [0])
        ok = best >= TH and best - second >= MARGIN and N[b]["_w"] >= o["_w"] * GAIN
        rep.append([coll, "/".join(o["members"]), o["source"], o["version"], o["file"], round(float(best), 3), round(float(second), 3),
                    o["_w"], N[b]["_w"], N[b]["src"], "差し替え" if ok else ""])
        if ok:
            j.add(coll, o["members"], o["source"], o["version"], N[b]["img"], "@reina831wy")
j.seed = []
j.save()
with open(SP + "out/hires_report.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["collection", "members", "source", "version", "old_file", "best", "second", "old_w", "new_w", "sheet", "result"])
    w.writerows(sorted(rep))
