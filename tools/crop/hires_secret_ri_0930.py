"""IVE SECRET：@ri__chan94 の種類ごとの表 7 枚（本人が 2026-09-30 に追加、新しい資料 2026-09-30/IVE SECRET_ri__chan94/）で画質を上げる

- カードに透かしなし（作者名は表の上だけ）。カードの横幅 約 500〜800px（いまの画像は約 378px）
- 表：Apple Music 1.0／SSQ 4set（＝4TYPE）／SSQ 9set（＝3+6、左が A・右が B）／SSQ Photobook（＝3TYPE 1・2）／SSQ LOVED IVE／withmuu 1.0／XOXZ Broadcast
- 枠は、いまのアプリの画像といちばん似ているもの。まちがって当たった 4 枚は表の位置から決めた（OV）。すべて並べて同じ写真だと目で確かめた
- 位置と枠：review/0930/secret_ri.json（[ファイル, 位置, [メンバー, 入手元, バージョン], 似ている度合い]）。48 番は切り出しの失敗なので使わない
"""
import json
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-09-30/IVE SECRET_ri__chan94/"
OV = {13: ["ユジン", "Starship Square", "3+6 (B)"], 28: ["レイ", "Starship Square", "3TYPE 1"],
      38: ["レイ", "Starship Square", "LOVED IVE"], 44: ["レイ", "withmuu", "1.0"]}
SKIP = {48}

if __name__ == "__main__":
    info = json.load(open(SP + "review/0930/secret_ri.json", encoding="utf-8"))
    j = Job("zzz_hires_secret_ri_0930"); ims = {}
    for i, (fn, box, key, _) in enumerate(info):
        if i in SKIP:
            continue
        m, src, ver = OV.get(i, key)
        if fn not in ims:
            ims[fn] = Image.open(D + fn).convert("RGB")
        j.add("IVE SECRET", [m], src, ver, ims[fn].crop(inset_frame(ims[fn], box)), "@ri__chan94")
    j.save()
