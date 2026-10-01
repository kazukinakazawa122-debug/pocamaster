"""I've IVE の Broadcast（公開放送）の足りない 4 枠（本人が 2026-10-01 にフォルダへ入れた @reina831wy の表 3 枚）

- 表：「IVE ver.」「I ver.」「HAVE ver.」（各 6 人、331px）。アプリの Broadcast 1＝I ver.、2＝HAVE ver.、3＝IVE ver.
  （ほかのメンバーの既存の画像と同じ写真で確かめた。似ている度合い 1.0）
- 足したもの：ガウル 1・リズ 1（I ver.）、レイ 2（HAVE ver.）、リズ 3（IVE ver.）
- 表の位置は 3 枚とも同じ：左から ガウル・ユジン・レイ／ウォニョン・リズ・イソ
- ファイルは pocamaster-images/ の一番上にある日付名のもの（20220402_074217000_iOS 1 10.jpg = IVE、1 11 = I、2 2 = HAVE）。
  新しい資料 2026-10-01/I've IVE 追加分_reina831wy/ に移してから使うこと（memlist.py の番号がずれるため）
"""
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/I've IVE 追加分_reina831wy/"
C = "I've IVE"
FILES = {"IVE": "broadcast_IVE.jpg", "I": "broadcast_I.jpg", "HAVE": "broadcast_HAVE.jpg"}
ORDER = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]
NEED = [("ガウル", "I", "1"), ("リズ", "I", "1"), ("レイ", "HAVE", "2"), ("リズ", "IVE", "3")]
if __name__ == "__main__":
    j = Job("iveive_add2")
    for who, sheet, ver in NEED:
        im = grid.load(D + FILES[sheet])
        bs = sorted(grid.card_boxes(im, min_w=0.1, max_w=0.25, ratio=(1.3, 1.7)), key=lambda b: (round((b[1] + b[3]) / 2 / 400), b[0]))
        assert len(bs) == 6
        j.add(C, [who], "Broadcast", ver, im.crop(tuple(int(v) for v in bs[ORDER.index(who)])), "@reina831wy")
    j.save()
