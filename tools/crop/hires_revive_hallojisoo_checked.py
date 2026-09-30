"""REVIVE+：@hallojisoo のメンバー別の表（pocamaster-images/REVIVE+/hallojisoo/、本人が 2026-09-30 にもう一度追加したものと同じ版）で画質を上げる（目で確かめた分）

- hires_sheets.py（MIN_CARD=120）で自動に 32 枚差し替えた（out/zzz_hires_revive_hallojisoo.json）
- 同じ写真らしいが、切り方・色の違いで自動では外れた 105 枚を並べて目で見た（review/0930/revive_hallojisoo_checked.json、[枠, 表, 位置]）。
  別の写真・ぼかし・切り出しの失敗と見えたもの（SKIP）を除いて差し替える。カードに透かしはない
"""
import json
from PIL import Image
from build2 import *

SKIP = {2, 12, 28, 51, 60, 64, 65, 81, 90, 98, 99}

if __name__ == "__main__":
    items = json.load(open(SP + "review/0930/revive_hallojisoo_checked.json", encoding="utf-8"))
    j = Job("zzz_hires_revive_hallojisoo_2"); ims = {}
    for n, (k, fn, box) in enumerate(items):
        if n in SKIP:
            continue
        if fn not in ims:
            ims[fn] = Image.open(ROOT + "REVIVE+/hallojisoo/" + fn.split("\\")[-1]).convert("RGB")
        j.add("REVIVE+", [k[0]], k[1], k[2], ims[fn].crop(box), "@hallojisoo")
    j.save()
