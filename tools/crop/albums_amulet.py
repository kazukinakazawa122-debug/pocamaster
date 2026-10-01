"""お守りカード（Amulet Card）：IVE EMPATHY と Be Alright（本人が 2026-10-01 に入れた実物の写真の画面写真。pocamaster-images/新しい資料 2026-10-01/お守りカード/）

- EMPATHY_amulet.png（クリーム色の衣装）：アプリの「オフラインイベント TOKYO 2」の画像と同じ写真（0.91・0.91・0.75・0.68 でメンバーの並びと一致）→ IVE EMPATHY の「Amulet Card (Tokyo 3/29)」6 人
- BeAlright_amulet.png（茶色・ギターの衣装）：Be Alright の新しい枠「Amulet Card (お守りカード)」6 人（枠を新しく足す。本人の指示）
- 2 枚とも 2 段×3 列で、並びは ユジン・ガウル・レイ／ウォニョン・リズ・イソ（EMPATHY の方は既存の画像で確認。Be Alright の方は同じ並びと見なした）
- 画面写真の位置は画面を見て決めた（元の画面は 1284×2778、表示 650 幅の座標 × 1.975）
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/お守りカード/"
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
k = 1284 / 650
CFG = {
    "BeAlright_amulet.png": ([(84, 244), (251, 412), (420, 580)], [(447, 688), (697, 950)]),
    "EMPATHY_amulet.png": ([(58, 205), (246, 386), (438, 584)], [(473, 663), (707, 932)]),
}
if __name__ == "__main__":
    j = Job("zzzzzzzzz_amulet")
    for f, coll, src, ver in (("EMPATHY_amulet.png", "IVE EMPATHY", "Amulet Card (Tokyo 3/29)", ""), ("BeAlright_amulet.png", "Be Alright", "Amulet Card (お守りカード)", "")):
        cs, rs = CFG[f]; im = Image.open(D + f).convert("RGB")
        for i, m in enumerate(M):
            (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]
            j.add(coll, [m], src, ver, im.crop((int(x0 * k) + 3, int(y0 * k) + 3, int(x1 * k) - 3, int(y1 * k) - 3)), "本人の写真")
    j.save()
