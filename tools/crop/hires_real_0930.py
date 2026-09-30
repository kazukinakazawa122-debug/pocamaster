"""本人が持ってきた実物のカードの写真（新しい資料 2026-09-30/実物の写真（本人、LUCID DREAM・REVIVE+ など）/、2026-09-30）で画質を上げる

- 写真の中のカードは 1 枚 約 380px（いまの REVIVE+ 121px・LUCID DREAM 161px）。カードにお店・人の ID の透かしはない（公式のバーコード・SAMPLE はそのまま）
- カードどうしがくっついていて自動では見つからないので、写真をマス目（ふつう 3×2）に分け、マスの中のカードを探して切り出した
- どのマスもアプリのいちばん似ている画像と並べ、同じ写真だと目で確かめたもの（OK）だけ差し替える。位置：review/0930/real_photos.json
"""
import json
from PIL import Image
import grid
from build2 import *

D = ROOT + "新しい資料 2026-09-30/実物の写真（本人、LUCID DREAM・REVIVE+ など）/"
OK = {18, 19, 42, 48, 49, 50, 51, 52, 53, 60, 61, 62, 63, 64, 67, 70, 71, 72, 73, 74, 75, 76, 77, 90, 93, 94, 100, 102, 103, 105, 106,
      108, 110, 111, 112, 113, 115, 116, 117, 118, 119, 120, 121, 124, 126, 127, 128, 129, 130, 131, 133, 134, 136}


def card_in(cell):
    """マスの中のカードの範囲（見つからなければマスのまま）"""
    bs = [b for b in grid.card_boxes(cell, min_w=0.55, max_w=1.01) if (b[2] - b[0]) * (b[3] - b[1]) > cell.width * cell.height * 0.5]
    if not bs:
        return cell
    b = max(bs, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    return cell.crop(inset_frame(cell, b))


if __name__ == "__main__":
    res = json.load(open(SP + "review/0930/real_photos.json", encoding="utf-8"))
    j = Job("zzz_hires_real_0930"); ims = {}
    for n in sorted(OK):
        r = res[n]
        if r["new"] <= r["old"]:
            continue
        if r["file"] not in ims:
            ims[r["file"]] = Image.open(D + r["file"]).convert("RGB")
        coll, m, src, ver = r["cands"][0][0]
        j.add(coll, [m], src, ver, card_in(ims[r["file"]].crop(r["box"])), "本人の写真")
    j.save()
