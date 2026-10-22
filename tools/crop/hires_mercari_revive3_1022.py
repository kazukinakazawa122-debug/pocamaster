"""2026-10-22（3 回目）：メルカリの出品写真で REVIVE+ の粗いカードの画質を上げる（本人「お願い」「どんどん進めて」。67 件の保存は本人の了承ずみ）
資料：新しい資料 2026-10-22/メルカリ REVIVE+ 3/（お店の名前_出品番号.jpg。各出品の 1 枚目の写真。withmuu・QQ Music・Ktown4U・KMStation）
やり方は hires_mercari_revive2_1022.py と同じ（2〜6 枚セットの写真も、いちばん重なる 1 枚だけを見る）

python tools/crop/hires_mercari_revive3_1022.py find … 写真全体を幅 100px にして REVIVE+ の全カードと重ね（hires_real_1004.find_singles と同じ）、上位 8 枚を locate で決める
"""
import glob, io, json, os, sys, zipfile
import numpy as np
from PIL import Image
from build2 import *
from hires_real_0930 import locate, gray, ncc
import hires_real_1002 as H

sys.stdout.reconfigure(encoding="utf-8")
D = ROOT + "新しい資料 2026-10-22/メルカリ REVIVE+ 3/"
OUTJ = SP + "review/1022/mercari_revive3.json"
JOB = "zzzzzzzzzzzzzzzzzzzzz_z_mercari_revive3_1022"  # 1・2 回目よりあとに読まれる名前


def find():
    z = zipfile.ZipFile(ROOT + "pocamaster-images.zip")
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover") and e["collection"] == "REVIVE+"]
    thumbs = [Image.open(io.BytesIO(z.read(e["thumb"]))).convert("RGB") for e in entries]
    out = []
    for f in sorted(glob.glob(D + "*.jpg")):
        im = Image.open(f).convert("RGB")
        cell = (0, 0, im.width, im.height)
        g = gray(im.resize((100, int(im.height * 100 / im.width))))
        res = []
        for t in thumbs:
            ar = t.height / t.width
            best = -2
            for w in (40, 52, 64, 76):
                th = int(w * ar)
                if th >= g.shape[0] or w >= g.shape[1]:
                    continue
                best = max(best, float(ncc(g, gray(t.resize((w, th)))).max()))
            res.append(best)
        best = None
        for k in np.argsort(-np.array(res))[:8]:
            old = Image.open(io.BytesIO(z.read(entries[int(k)]["file"]))).convert("RGB")
            box, sc = locate(im, cell, old, lo=0.3, hi=0.95)
            if box and (best is None or sc > best[1]):
                best = (int(k), sc, box)
        k, sc, box = best
        e = entries[k]
        old_h = Image.open(io.BytesIO(z.read(e["file"]))).size[1]
        out.append({"photo": os.path.basename(f), "box": box, "score": round(sc, 3), "key": list(H.key(e)), "old_h": old_h})
        print(os.path.basename(f)[:24], round(sc, 3), e["members"], e["source"], e["version"], "新", box[3] - box[1], "いま", old_h, flush=True)
        os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
        json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 目で見比べた結果（2026-10-22）：枠ごとに点数のいちばん高い写真（0.68 以上・1.15 倍以上）31 組のうち、同じカードは下の 20 組。
# #3・#16・#25・#30・#34・#35・#51・#63 はちがうカード、#37（「@」）・#61（出品者の文字）はカードに文字。
# #50（withmuu 10.0 リズ）：いまの画像に K·MONSTAR のロゴがあり、写真にはない → いまの画像が別のお店のカードかもしれないので本人に聞く（差し替えない）
# 大きくして確かめたら、#0・#2（KMStation）・#20（Ktown4U）に出品者の薄い透かし（「メルカリ…」）→ 使わない
# #50（withmuu 10.0 リズ）：本人が見比べて「同じ」（2026-10-23）→ いまの画像の K·MONSTAR のロゴは資料の側のもの。ロゴのないメルカリの写真に差し替える
OK = [1, 9, 10, 11, 12, 17, 22, 26, 27, 40, 46, 50, 52, 55, 59, 64, 65, 66]
# 端に背景が残ったもの：その辺だけ内側に寄せる（左・上・右・下）
TRIM = {0: (0, 0, 0, .03), 2: (0, 0, .02, .03), 12: (0, 0, .04, 0), 17: (.03, 0, 0, 0), 46: (0, .02, .05, 0), 52: (.02, 0, 0, 0),
        59: (0, 0, .03, 0), 64: (0, 0, .02, 0), 66: (0, 0, .03, .01)}


def crops():
    out = json.load(open(OUTJ, encoding="utf-8"))
    res = []
    for n in OK:
        o = out[n]
        im = Image.open(D + o["photo"]).convert("RGB")
        box, ok = H.snap(im, o["box"], band=0.08)
        if n in TRIM:
            l, t, r, b = TRIM[n]; w, h = box[2] - box[0], box[3] - box[1]
            box = [int(box[0] + w * l), int(box[1] + h * t), int(box[2] - w * r), int(box[3] - h * b)]
        res.append((n, o, im.crop(tuple(box)), ok))
    return res


def apply():
    j = Job(JOB)
    for n, o, img, ok in crops():
        c, m, src, ver = o["key"]
        j.add(c, m.split("/"), src, ver, img, "メルカリの出品写真")
    j.save()


if __name__ == "__main__":
    {"find": find, "apply": apply}[sys.argv[1]]()
