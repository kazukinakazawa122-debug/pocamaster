"""REVIVE+ の QQ Music の Membership・Member set 2 を、6 人の wishlist（@idalshiro）から入れ直す（2026-10-01）

- 表の「QQ MUSIC member set」は 4 段目の 2 枚：2 列目＝Membership、3 列目＝Member set 2（本人が目で確認）
  （列 x=56+405c・段 y=1338+702r・カード 326×506、11 列 × 9 段。r=3, c=1・2）
- 資料：新しい資料 2026-10-01/REVIVE+ 追加分/wishlist_<メンバー>_idalshiro.jpg（6 人。カードに ID なし。ユジンの「tjxxx」は QQ Music 2 の 5 枚目だけ）
"""
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/REVIVE+ 追加分/"
C = "REVIVE+"
# 表のカードを囲む青い枠（約 6px）を除くため、箱を 12px 内側にする（inset_frame では 3 列目の枠が残った）
box = lambda r, c: (56 + 405 * c + 12, 1338 + 702 * r + 12, 56 + 405 * c + 326 - 12, 1338 + 702 * r + 506 - 12)
EN = {"ユジン": "Yujin", "ガウル": "Gaeul", "レイ": "Rei", "ウォニョン": "Wonyoung", "リズ": "Liz", "イソ": "Leeseo"}
if __name__ == "__main__":
    j = Job("zzzzz_revive_qq")
    for n, en in EN.items():
        im = grid.load(D + f"wishlist_{en}_idalshiro.jpg")
        j.add(C, [n], "QQ Music", "Membership", im.crop(box(3, 1)), "@idalshiro")
        j.add(C, [n], "QQ Music", "Member set 2", im.crop(box(3, 2)), "@idalshiro")
    j.save()
