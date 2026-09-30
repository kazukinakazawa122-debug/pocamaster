"""MINIVE：@hallojisoo のメンバー別の表 6 枚（本人が 2026-09-30 に追加、新しい資料 2026-09-30/MINIVE_hallojisoo/）

- カードに透かしなし（作者名は右上だけ）。カード 260×390px
- 表の並び：MINIVE PARK 6（Mega Cushion・Face Cushion・Pouch・Binder・50K MINIVE VER・50K ANIMAL VER）／MINIVE CHRISTMAS 1／
  IVE x LINE 50K 2／MINIVE SCHOOL 5（30cm Plush・Hug Bag・70K・Shanghai・Taiwan）／EVERLAND 3（どれもぼかし → 使わない）
- 位置：ガウルの表の位置を型にして、表ごとに行の高さを合わせた（review/0930/minive_boxes.json）。6 人分を目で確かめた
- MINIVE VER ＝ 50K Benefit 1st week、ANIMAL VER ＝ 2nd week（リズのいまの画像と同じ写真）
- IVE x LINE の 2 枚 ＝ IVE SWITCH の LINE FRIENDS 特典 1・2（リズで確かめた）。いまの画像より大きいときだけ入れる
"""
import glob, json
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-09-30/MINIVE_hallojisoo/"
C = "Collab & Event｜コラボ・イベント"
PARK, SCHOOL = "MINIVE POP-UP 'MINIVE PARK'", "MINIVE POP-UP 'MINIVE SCHOOL'"
LABELS = [(C, PARK, "Mega Cushion"), (C, PARK, "Face Cushion"), (C, PARK, "Pouch"), (C, PARK, "Poca Binder"),
          (C, PARK, "50K Benefit 1st week"), (C, PARK, "50K Benefit 2nd week"), (C, "MINIVE Christmas", ""),
          ("IVE SWITCH", "LINE FRIENDS 特典", "1"), ("IVE SWITCH", "LINE FRIENDS 特典", "2"),
          (C, SCHOOL, "Fluffy Plush"), (C, SCHOOL, "Hug Bag"), (C, SCHOOL, "70K Benefit"), (C, SCHOOL, "Shanghai MD 特典"),
          (C, SCHOOL, "Taipei & Kaohsiung MD 特典")]
NAMES = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]

if __name__ == "__main__":
    boxes = json.load(open(SP + "review/0930/minive_boxes.json", encoding="utf-8"))["boxes"]
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if "minive_0930" in p:
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if len(e["members"]) == 1:
                cur[(e["collection"], e["members"][0], e["source"], e["version"])] = e["file"]
    j = Job("zzz_minive_0930")
    for f, n in zip(sorted(glob.glob(D + "*.png"))[:6], NAMES):
        im = Image.open(f).convert("RGB")
        for (coll, src, ver), box in zip(LABELS, boxes[n]):
            c = im.crop(box)
            old = cur.get((coll, n, src, ver))
            if coll == "IVE SWITCH" and old and min(Image.open(CARDS + old).size) >= min(c.size):
                continue
            j.add(coll, [n], src, ver, c, "@hallojisoo")
    j.save()
