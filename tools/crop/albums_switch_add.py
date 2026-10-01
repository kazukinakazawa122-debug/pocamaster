"""IVE SWITCH の足りない画像（本人が 2026-10-01 に入れた @ri__chan94 の表。pocamaster-images/新しい資料 2026-10-01/IVE SWITCH 追加分/）

- withmuu_LuckyDraw_2.0_ri__chan94.jpg：6 人の withmuu Lucky Draw 2.0（1 人 3 枚：カード 2 枚＋ポラ）。ウォニョンの 3 枚目（ポラ）→ 「withmuu ラキドロ 2.0 POLA」のウォニョン（画像なしだった。元画像が小さい＝約 87px）
- Liz_PhotocardList_ri__chan94.png：リズの全種類の表。「Soundwave Lucky Draw 5.0」の 3 枚目（ポラ）→ リズの「Soundwave ラキドロ 5.0 POLA」
- Rei_PhotocardList_ri__chan94.png：レイの全種類の表。「Soundwave Lucky Draw 5.0」はこの表に載っていない（レイの 5.0 POLA は資料なしのまま）
"""
from PIL import Image
from build2 import *

Image.MAX_IMAGE_PIXELS = None
D = ROOT + "新しい資料 2026-10-01/IVE SWITCH 追加分/"
if __name__ == "__main__":
    j = Job("zzzzzzzzzzzzzzzz_switch_add")
    a = Image.open(D + "withmuu_LuckyDraw_2.0_ri__chan94.jpg").convert("RGB")
    j.add("IVE SWITCH", ["ウォニョン"], "withmuu ラキドロ", "2.0 POLA", a.crop((775, 463, 862, 603)), "@ri__chan94")
    l = Image.open(D + "Liz_PhotocardList_ri__chan94.png").convert("RGB"); k = 3750 / 1400
    x0, y0, x1, y1 = (int(v * k) for v in (653, 1366, 740, 1497))
    j.add("IVE SWITCH", ["リズ"], "Soundwave ラキドロ", "5.0 POLA", l.crop((x0 + 16, y0 + 16, x1 - 8, y1 - 8)), "@ri__chan94")
    j.save()
