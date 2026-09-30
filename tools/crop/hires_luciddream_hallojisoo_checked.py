"""LUCID DREAM：@hallojisoo のメンバー別の表（新しい資料 2026-09-30/LUCID DREAM_hallojisoo/、カード約 197px）で画質を上げる（目で確かめた分）

- hires_sheets.py（MIN_CARD=150）で自動に 9 枚（下の一覧にも入っている）差し替えた（out/zzz_hires_revive_hallojisoo.json）
- 同じ写真らしいが、切り方・色の違いで自動では外れた 105 枚を並べて目で見た（review/0930/luciddream_hallojisoo_checked.json、[枠, 表, 位置]）。
  別の写真・ぼかし・切り出しの失敗と見えたもの（SKIP）を除いて差し替える。カードに透かしはない
"""
import json
from PIL import Image
from build2 import *

SKIP = {8, 10, 11, 13, 21, 27, 29, 33, 34, 39, 40, 44, 45, 46, 53, 63, 64, 65, 67, 70, 71, 73, 74, 76}  # ぼかし・別の写真

if __name__ == "__main__":
    items = json.load(open(SP + "review/0930/luciddream_hallojisoo_checked.json", encoding="utf-8"))
    j = Job("zzz_hires_luciddream_hallojisoo_2"); ims = {}
    for n, (k, fn, box) in enumerate(items):
        if n in SKIP:
            continue
        if fn not in ims:
            ims[fn] = Image.open(ROOT + "新しい資料 2026-09-30/LUCID DREAM_hallojisoo/" + fn.split("\\")[-1]).convert("RGB")
        j.add("LUCID DREAM", [k[0]], k[1], k[2], ims[fn].crop(box), "@hallojisoo")
    j.save()
