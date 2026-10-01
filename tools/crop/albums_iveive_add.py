"""I've IVE の足りない画像（本人が 2026-10-01 にフォルダへ入れた @reina831wy の追加分）

- tower_record.jpg（PRE-ORDER BENEFITS tower record。大きい写真＝Tower Records 2、ポラ＝Tower Records 1）：ウォニョンの Tower Records 1（ポラ）
- naver_shoppinglive.jpg（Naver Shoppinglive。メンバー 6 枚＋ユニット 4 枚）：ガウル・リズの「Naver Live」（本人：枠名は Never Shopping Live＝Naver Live）
- withmuu_lucky_draw.jpg（withmuu 1.0 lucky draw。各メンバー 3 枚）：イソの「withmuu ラキドロ 3」はこの表のイソの 3 枚目（ポラ）（本人、2026-10-01）
- 画像が小さい（ポラ 189px・Naver 347px）ので、すでにある画像より小さくならないときだけ入れる
"""
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/I've IVE 追加分_reina831wy/"
C = "I've IVE"
if __name__ == "__main__":
    j = Job("iveive_add")
    tw = grid.load(D + "tower_record.jpg")
    j.add(C, ["ウォニョン"], "Tower Records", "1", tw.crop((1292, 934, 1481, 1189)), "@reina831wy")
    nv = grid.load(D + "naver_shoppinglive.jpg")
    j.add(C, ["ガウル"], "Naver Live", "", nv.crop((320, 462, 667, 999)), "@reina831wy")
    j.add(C, ["リズ"], "Naver Live", "", nv.crop((763, 1086, 1110, 1623)), "@reina831wy")
    wm = grid.load(D + "withmuu_lucky_draw.jpg")
    j.add(C, ["イソ"], "withmuu ラキドロ", "3", wm.crop((1514, 1367, 1683, 1593)), "@reina831wy")
    j.save()
