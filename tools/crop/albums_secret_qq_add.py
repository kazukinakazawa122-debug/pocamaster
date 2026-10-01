"""IVE SECRET の QQ Music（本人が 2026-10-01 にフォルダへ入れた。pocamaster-images/新しい資料 2026-10-01/IVE SECRET QQ Music 追加分/）

- Christmas_Yujin.jpg：ユジンの「QQ Music × Starship Square｜Christmas」（239×332px と小さいが唯一の資料）
- QQ1_A.png・QQ1_B.png・QQ1_C.png：「QQ Music 1」の足りないメンバー（レイ・リズ・イソ）の実物の写真の画面写真（1 枚ずつ）
  どれが誰かは写真に名前がない。入れた順（A→B→C）をレイ→リズ→イソ（メンバーの標準の並びの残り）と見なした → 本人に確認してもらう（_review/secret_qq.html）
  B は「星光卡 STARLIGHT CARD」の白い台紙に入っているので、台紙の中の写真だけを切った
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/IVE SECRET QQ Music 追加分/"
C = "IVE SECRET"
k = 1284 / 601
BOX = {"QQ1_A.png": (180, 462, 438, 860), "QQ1_B.png": (218, 522, 432, 852), "QQ1_C.png": (133, 366, 470, 880)}
WHO = {"QQ1_A.png": "レイ", "QQ1_B.png": "リズ", "QQ1_C.png": "イソ"}
if __name__ == "__main__":
    j = Job("zzzzzzzzzzzz_secret_qq")
    j.add(C, ["ユジン"], "QQ Music × Starship Square", "Christmas", Image.open(D + "Christmas_Yujin.jpg").convert("RGB"), "本人の写真")
    for f, b in BOX.items():
        im = Image.open(D + f).convert("RGB")
        j.add(C, [WHO[f]], "QQ Music", "1", im.crop(tuple(int(v * k) for v in b)), "本人の写真")
    j.save()
