"""2026-10-22：メルカリの出品写真（6 枚コンプ）で REVIVE+ の粗いカードの画質を上げる（本人「粗いカードも探せる？メルカリも使ってよい」「多いのから」）
資料：新しい資料 2026-10-22/メルカリ REVIVE+/（保存は本人の了承ずみ。ファイル名に出品番号）
使わない写真：裏面だけ（03_…_2・06_…_2・09_…_2）、出品者の文字がカードにかかる（08 OLIVE YOUNG「6種コンプリート」・09 LOVED IVE「匿名配送」）、
  カードが小さい（12 Digipack）、ぬいぐるみの写真（10_…_1・2）

python tools/crop/hires_mercari_revive_1022.py find  … 3 列 × 2 段のマスを REVIVE+ の全カードと比べて枠を決める（hires_real_1002 と同じ。顔では決めない）
python tools/crop/hires_mercari_revive_1022.py apply … 目で確かめた結果（OK）のうち、いまの画像より 1.15 倍以上大きいものだけ差し替える
"""
import io, json, os, sys, zipfile
import numpy as np
from PIL import Image
from build2 import *
from hires_real_0930 import locate
import hires_real_1002 as H

sys.stdout.reconfigure(encoding="utf-8")
D = ROOT + "新しい資料 2026-10-22/メルカリ REVIVE+/"
OUTJ = SP + "review/1022/mercari_revive.json"
JOB = "zzzzzzzzzzzzzzzzzzzzz_y_mercari_revive_1022"
# 写真ごとの、カードが並んでいる範囲（x0, y0, x1, y1。写真を見て決めた）
AREA = {
    "01_tower_shibuya_m23653949225_1.jpg": (15, 25, 1065, 1050),
    "02_tower_m28022738642_1.jpg": (25, 15, 1065, 1065),
    "03_offline_tokyo_m59411130216_1.jpg": (25, 40, 1065, 1065),
    "04_offline_osaka_b_m47780145929_1.jpg": (25, 25, 1065, 1065),
    "04_offline_osaka_m97682699008_1.jpg": (25, 165, 1065, 1080),
    "05_withmuu_lucky6_m24585745335_1.jpg": (150, 110, 945, 900),
    "06_nymusic_m64346024263_1.jpg": (70, 95, 1025, 1040),
    "07_asmart_m88272166246_1.jpg": (135, 80, 945, 945),
    "10_petit_ive_m32037618905_3.jpg": (25, 0, 1065, 966),
    "10_petit_ive_m32037618905_4.jpg": (25, 0, 1065, 971),
    "11_withmuu4_m53922455969_1.jpg": (110, 80, 970, 1025),
}


def find():
    z = zipfile.ZipFile(ROOT + "pocamaster-images.zip")
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover") and e["collection"] == "REVIVE+"]
    thumbs = [Image.open(io.BytesIO(z.read(e["thumb"]))).convert("RGB") for e in entries]
    M = np.stack([H.desc(t) for t in thumbs])
    out = []
    for f, (x0, y0, x1, y1) in AREA.items():
        im = Image.open(D + f).convert("RGB")
        cw, ch = (x1 - x0) / 3, (y1 - y0) / 2
        for r in range(2):
            for c in range(3):
                cell = (int(x0 + c * cw), int(y0 + r * ch), int(x0 + (c + 1) * cw), int(y0 + (r + 1) * ch))
                inner = im.crop((cell[0] + cw * .12, cell[1] + ch * .1, cell[2] - cw * .12, cell[3] - ch * .1))
                cands = np.argsort(-(M @ H.desc(inner)))[:12]
                best = None
                for k in cands:
                    old = Image.open(io.BytesIO(z.read(entries[k]["file"]))).convert("RGB")
                    box, sc = locate(im, cell, old, lo=0.5, hi=1.15)
                    if box and (best is None or sc > best[1]):
                        best = (int(k), sc, box)
                k, sc, box = best
                e = entries[k]
                old_h = Image.open(io.BytesIO(z.read(e["file"]))).size[1]
                out.append({"photo": f, "r": r, "c": c, "cell": cell, "box": box, "score": round(sc, 3), "key": list(H.key(e)), "old_h": old_h})
                print(f[:22], r, c, round(sc, 3), e["members"], e["source"], e["version"], "新", box[3] - box[1], "いま", old_h)
    os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
    json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 目で見比べた結果（2026-10-22）：今より 1.15 倍以上大きい 35 組のうち、#24・#27・#29・#59 はちがうカード（大阪の 2 つ目の写真・PETIT-IVE のキャラクターの写真）
# 見比べる前に hires_real_1002.refine（写真のシリーズの中で決め直す）をかけた
NG = {24, 27, 29, 59}


# 切り出しの範囲は、照らし合わせの範囲（手本の画像に合わせたもの）だとカードの端とずれるので、全部を方眼で読み取った（2026-10-22）
# QUAD：傾いている写真（4 つの角。左上・右上・右下・左下）、BOX：まっすぐな写真（x0, y0, x1, y1）
QUAD = {0: [(96, 46), (382, 48), (372, 478), (60, 474)], 2: [(682, 46), (970, 48), (990, 474), (684, 478)],
        3: [(48, 480), (366, 480), (358, 970), (26, 970)], 4: [(366, 483), (682, 483), (682, 966), (360, 966)],
        5: [(682, 480), (990, 480), (1020, 970), (690, 970)]}
BOX = {6: (36, 32, 362, 536), 11: (716, 558, 1039, 1058), 18: (30, 30, 360, 532), 22: (374, 552, 702, 1066), 23: (718, 550, 1048, 1062),
       31: (445, 145, 655, 455), 32: (717, 142, 932, 453), 33: (177, 517, 397, 864), 34: (450, 518, 669, 862), 35: (722, 515, 947, 862),
       36: (78, 102, 358, 542), 38: (702, 66, 1006, 534), 39: (78, 564, 366, 1022), 40: (400, 570, 698, 1042), 41: (720, 560, 1026, 1034),
       42: (123, 88, 386, 477), 43: (397, 81, 668, 456), 44: (691, 81, 962, 454), 45: (123, 479, 386, 906), 47: (691, 462, 985, 893),
       50: (718, 6, 1030, 458), 52: (392, 494, 682, 960), 53: (738, 480, 1062, 960),
       61: (419, 113, 697, 524), 63: (116, 521, 404, 988), 64: (416, 532, 711, 996)}


def crops():
    out = json.load(open(OUTJ, encoding="utf-8"))
    res = []
    for n, o in enumerate(out):
        if n in NG or (o["box"][3] - o["box"][1]) < 1.15 * o["old_h"]:
            continue
        im = Image.open(D + o["photo"]).convert("RGB")
        if n in QUAD:
            from albums_x_1022 import warp
            res.append((n, o, warp(im, QUAD[n], H=440, inset=0.01), True))
        else:
            res.append((n, o, im.crop(BOX[n]), True))
    return res


def apply():
    j = Job(JOB)
    for n, o, img, ok in crops():
        c, m, src, ver = o["key"]
        j.add(c, m.split("/"), src, ver, img, "メルカリの出品写真")
    j.save()


if __name__ == "__main__":
    {"find": find, "apply": apply}[sys.argv[1]]()
