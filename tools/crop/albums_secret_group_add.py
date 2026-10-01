"""IVE SECRET の全員のカード（ぼかし。店の告知画像の見本。本人が 2026-10-01 に入れた。pocamaster-images/新しい資料 2026-10-01/IVE SECRET 全員カード（ぼかし）/）

- MusicArt_告知_영풍문고.jpg（ピンクの告知）→「MusicArt｜全員」（本人の指定）。ぼかしだが、ほかに画像がないので入れる（ぼかしは画像がないときだけ使う、本人決定 2026-09-29）
- HOTTRACKS_교보문고.jpg（赤いカード 7 枚）→「HOTTRACKS ラキドロ｜全員」。右下の縦のカードが全員のカード
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/IVE SECRET 全員カード（ぼかし）/"
if __name__ == "__main__":
    j = Job("zzzzzzzzzzzzzz_secret_group")
    a = Image.open(D + "MusicArt_告知_영풍문고.jpg").convert("RGB").crop((598, 548, 764, 666))
    b = Image.open(D + "HOTTRACKS_교보문고.jpg").convert("RGB").crop((852, 518, 1038, 806))
    j.add("IVE SECRET", ["全員"], "MusicArt", "全員", a, "店の告知（영풍문고）")
    j.add("IVE SECRET", ["全員"], "HOTTRACKS ラキドロ", "全員", b, "店の告知（교보문고）")
    j.save()
