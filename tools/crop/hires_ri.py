"""@ri__chan94 のメンバー別の表（高画質）から、いまの画像と同じ写真を探して大きい画像に差し替える

使い方：python hires_ri.py "<コレクション名>" "<pocamaster-images のフォルダ名>" ["<作者>"]
  フォルダの中の「<何か> YUJIN.png」などメンバー名入りのファイルを読む
結果：out/zz_ri_<フォルダ名>.json（merge.py で最後の方に読むので、同じ枠の古い画像より優先）
確認用：out/ri_report_<フォルダ名>.csv

ぼかし（未公開）のカードは、ぼやけ具合で見分けて使わない
"""
import csv, glob, json, os, re, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from build2 import *

Image.MAX_IMAGE_PIXELS = None
COLL, FOLDER = sys.argv[1], sys.argv[2]
CREDIT = sys.argv[3] if len(sys.argv) > 3 else "@ri__chan94"  # 表の作者
# ぼかし判定のしきい値。表によってくっきり具合が違うので変えられる（そのあと必ず目で確認する）
BLUR_TH = float(sys.argv[4]) if len(sys.argv) > 4 else 450
MEMBERS = {"YUJIN": "ユジン", "GAEUL": "ガウル", "REI": "レイ", "WONYOUNG": "ウォニョン", "LIZ": "リズ", "LEESEO": "イソ"}
TH, MARGIN, GAIN = 0.80, 0.06, 1.25
ID_CREDITS = {"@powerofablink"}  # merge.py と同じ。画像に ID の透かしがある資料


def feat(img):
    w, h = img.size
    a = np.asarray(img.crop((w * .1, h * .1, w * .9, h * .9)).convert("RGB").resize((24, 36), Image.BILINEAR)).astype(float)
    a = a - a.mean(axis=(0, 1))
    a = a / (a.std() + 1e-6)
    return a.flatten() / np.sqrt(a.size)


def sharpness(img):
    """ぼやけ具合：大きいほどくっきり。同じ大きさにそろえて比べる"""
    g = np.asarray(img.convert("L").resize((200, 300))).astype(float)
    return float(ndimage.laplace(g).var())


old = []
for p in sorted(glob.glob(SP + "out/*.json")):
    if os.path.basename(p).startswith("zz_ri_"):
        continue
    old += [e for e in json.load(open(p, encoding="utf-8"))["images"] if e["collection"] == COLL]
if os.path.exists(CARDS + "manifest.json"):
    old += [e for e in json.load(open(CARDS + "manifest.json", encoding="utf-8")) if e["collection"] == COLL]
# 同じ枠の画像が複数あれば、あとのもの（いま使われているもの）だけ
uniq = {}
for e in old:
    uniq[(tuple(sorted(e["members"])), e["source"], e["version"])] = e
old = list(uniq.values())
for e in old:
    im = Image.open(CARDS + e["file"])
    e["_w"], e["_f"] = min(im.size), feat(im)

j = Job("zz_ri_" + re.sub(r"\W+", "_", FOLDER))
rep = []
for path in sorted(glob.glob(ROOT + FOLDER + "/*.png")):
    mem = next((v for k, v in MEMBERS.items() if k in os.path.basename(path).upper()), None)
    if not mem:
        continue
    im = grid.load(path)
    bs = grid.card_boxes(im, ratio=(1.2, 1.8), min_w=0.05, max_w=0.2)
    bs += grid.card_boxes(im, ratio=(0.6, 1.19), min_w=0.07, max_w=0.25)
    news = []
    for b in bs:
        c = im.crop(tuple(int(v) for v in b))
        news.append((c, feat(c), sharpness(c)))
    O = [e for e in old if mem in e["members"]]
    print(mem, os.path.basename(path), "cards", len(news), "old", len(O))
    if not O or not news:
        continue
    S = np.array([[o["_f"] @ f for _, f, _ in news] for o in O])
    for i, o in enumerate(O):
        order = np.argsort(-S[i])
        b = order[0]
        best = S[i, b]
        second = max([S[i, k] for k in order[1:] if news[k][1] @ news[b][1] < 0.9] or [0])
        c, _, sh = news[b]
        blur = sh < BLUR_TH  # ぼかしのカードは 350 以下、くっきりしたカードは 600 以上だった（SECRET で確認）
        # いまの画像が ID 入り（アプリでは使っていない）なら、大きさは問わない
        gain = 0 if o.get("credit") in ID_CREDITS else GAIN
        ok = best >= TH and best - second >= MARGIN and min(c.size) >= o["_w"] * gain and not blur
        rep.append([COLL, "/".join(o["members"]), o["source"], o["version"], o["file"], round(float(best), 3),
                    round(float(second), 3), o["_w"], min(c.size), round(sh), os.path.basename(path), "差し替え" if ok else ""])
        if ok:
            j.add(COLL, o["members"], o["source"], o["version"], c, CREDIT)
j.save()
with open(SP + f"out/ri_report_{re.sub(r'\W+', '_', FOLDER)}.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["collection", "members", "source", "version", "old_file", "best", "second", "old_w", "new_w", "sharp", "sheet", "result"])
    w.writerows(rep)
print("差し替え", sum(1 for r in rep if r[-1]), "/", len(rep))
