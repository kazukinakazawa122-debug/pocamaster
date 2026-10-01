"""IVE SECRET の IDOLSHOP POLA（ぼかし。IDOLSTORE の「未公開 拍立得型小卡 預覧」の見本。本人が 2026-10-01 に入れた）

- 下の段の「未公开拍立得型小卡预览」の 6 枚（上 3 枚＋下 3 枚）。メンバーの順は本人の指定：ユジン・ガウル・レイ／ウォニョン・リズ・イソ
- 上の段（自拍小卡）は IDOLSHOP（POLA なし）の見本。画像はすでにあるので使わない
- ぼかしだが、ほかに画像がないので入れる（本人決定 2026-09-29）。表示 533 幅の座標 × 1.2
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/IVE SECRET IDOLSHOP POLA（ぼかし）/"
k = 640 / 533
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
BOX = [(123, 677, 207, 775), (225, 677, 309, 775), (327, 677, 411, 775), (73, 813, 157, 910), (175, 813, 259, 910), (277, 813, 361, 910)]
if __name__ == "__main__":
    im = Image.open(D + "IDOLSTORE_未公開_見本.jpg").convert("RGB")
    j = Job("zzzzzzzzzzzzzzz_secret_idolshop_pola")
    for m, b in zip(M, BOX):
        j.add("IVE SECRET", [m], "IDOLSHOP", "POLA", im.crop(tuple(int(v * k) for v in b)), "店の告知（IDOLSTORE）")
    j.save()
