"""何人かで写ったカードのメンバーを、@idalshiro のメンバー別の表どうしで同じ写真を探して決める（顔では決めない）。

あるメンバーの表のカードと同じ写真が、ほかのメンバーの表のどこにあるかを探し、見つかったメンバーをそのカードのメンバーとする。
結果は out/../review/groups_<メンバー>.json（番号 → メンバーの一覧と似ている度合い）
"""
import json, sys
import numpy as np
from PIL import Image
import grid
from build2 import *
from hires_ida import feat

D = ROOT + "_nonalbum/idalshiro/"
KEYS = [("yujin", "ユジン"), ("gaeul", "ガウル"), ("rei", "レイ"), ("wonyoung", "ウォニョン"), ("liz", "リズ"), ("leeseo", "イソ")]
TH = float(os.environ.get("GROUP_TH", "0.88"))


def sheet_feats(key):
    out = []
    for page in ("1", "2", "3", "na"):
        im = grid.load(D + f"{key}_{page}.jpg")
        for b in grid.card_boxes(im, min_w=0.03, max_w=0.08):
            out.append((page, [int(v) for v in b], feat(im.crop(inset_frame(im, b)))))
    return out


if __name__ == "__main__":
    key, ids = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
    name = dict(KEYS)[key]
    miss = json.load(open(SP + f"review/miss_{key}.json"))
    others = {k: sheet_feats(k) for k, _ in KEYS if k != key}
    res = {}
    for i in ids:
        page, b, _ = miss[i]
        im = grid.load(D + f"{key}_{page}.jpg")
        f = feat(im.crop(inset_frame(im, b)))
        found = []
        for k, n in KEYS:
            if k == key:
                continue
            F = np.array([x[2] for x in others[k]])
            s = F @ f
            j = int(s.argmax())
            if s[j] >= TH:
                found.append([n, round(float(s[j]), 3), others[k][j][0], others[k][j][1]])
        res[i] = found
        print(i, [(x[0], x[1]) for x in found])
    json.dump(res, open(SP + f"review/groups_{key}.json", "w", encoding="utf-8"), ensure_ascii=False)
