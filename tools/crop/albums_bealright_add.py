"""Be Alright オフラインイベントの足りない画像（本人が 2026-10-01 にフォルダへ入れた実物の写真の画面写真。メンバー 6 枚・2 段×3 列）

- offline_9.23_TOKYO.png／offline_10.12_TOKYO.png（新しい資料 2026-10-01/Be Alright 追加分/）
- 並びは ユジン・ガウル・レイ／ウォニョン・リズ・イソ（アプリにすでにある画像と同じ写真で確かめた：9.23＝レイ・リズ・イソ、10.12＝ユジン・ガウル・レイ・ウォニョン・イソ。似ている度合い 0.8 以上）
- 足したもの：9.23 TOKYO のユジン・ガウル・ウォニョン、10.12 TOKYO のリズ
- 切り出し位置は画面写真を見て決めた（列・段）。スリーブの縁を 4px 除いた
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/Be Alright 追加分/"
C = "Be Alright"
G = {
    "offline_9.23_TOKYO.png": ([(62, 449), (462, 846), (858, 1244)], [(792, 1380), (1408, 1994)]),
    "offline_10.12_TOKYO.png": ([(48, 441), (455, 844), (857, 1243)], [(784, 1382), (1406, 2003)]),
}
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
NEED = [("offline_9.23_TOKYO.png", "9.23 TOKYO", ["ユジン", "ガウル", "ウォニョン"]), ("offline_10.12_TOKYO.png", "10.12 TOKYO", ["リズ"])]
if __name__ == "__main__":
    j = Job("bealright_add")
    for f, ver, who in NEED:
        cs, rs = G[f]; im = Image.open(D + f).convert("RGB")
        for n in who:
            i = M.index(n); (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]
            j.add(C, [n], "オフラインイベント", ver, im.crop((x0 + 4, y0 + 4, x1 - 4, y1 - 4)), "本人の写真")
    j.save()
