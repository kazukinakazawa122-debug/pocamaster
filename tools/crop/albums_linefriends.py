"""MINIVE × LINE FRIENDS（イベント）：@idalshiro の表の「MINIVE X LINE FRIENDS」（ノンアルバムのページ。6 人とも同じ位置）

- 本人（2026-10-01）：IVE SWITCH の LINE FRIENDS の枠は SWITCH ではなくイベントに入れる → コラボ・イベントの「MINIVE × LINE FRIENDS」にする
- 表の 6 枚（左から）：トレカ pink・white・black・purple、HOLDER、50K KRW（列 x=3105+211.4×i・y=2638・幅 194・高さ約 296）
  旧 SWITCH の「LINE FRIENDS トレカ 1＝purple・2＝white」（アプリの画像と同じ写真。ユジン 0.74/0.91・ガウル 0.97/0.82・レイ 0.94/0.88）
- 旧「LINE FRIENDS キーリング」「特典 1〜3」は表にない。移すだけ（画像は今まで通り。なければ画像なし）。merge.py の DROP_SLOT で IVE SWITCH 側は消える
- 画像は表（カード 194px と小さい）から。旧画像のほうが大きいときは旧画像を使う
"""
import csv, glob, json, os
from PIL import Image
import grid
from build2 import *

Image.MAX_IMAGE_PIXELS = None
D = ROOT + "_nonalbum/idalshiro/"
COLL = "Collab & Event｜コラボ・イベント"
SRC = "MINIVE × LINE FRIENDS"
KEYS = [("yujin", "ユジン"), ("gaeul", "ガウル"), ("rei", "レイ"), ("wonyoung", "ウォニョン"), ("liz", "リズ"), ("leeseo", "イソ")]
NEW = ["トレカ pink", "トレカ white", "トレカ black", "トレカ purple", "HOLDER", "50K KRW"]
OLD_MAP = {("LINE FRIENDS トレカ", "1"): "トレカ purple", ("LINE FRIENDS トレカ", "2"): "トレカ white"}
CARRY = [("LINE FRIENDS キーリング", ""), ("LINE FRIENDS 特典", "1"), ("LINE FRIENDS 特典", "2"), ("LINE FRIENDS 特典", "3")]
if __name__ == "__main__":
    old = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "zzzzzzzzzzz_linefriends.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["collection"] == "IVE SWITCH" and e["source"].startswith("LINE FRIENDS") and len(e["members"]) == 1:
                old[(e["members"][0], e["source"], e["version"])] = e
    j = Job("zzzzzzzzzzz_linefriends")
    for key, name in KEYS:
        im = grid.load(D + f"{key}_na.jpg")
        for i, v in enumerate(NEW):
            x = int(3105 + 211.4 * i)
            crop = im.crop(inset_frame(im, (x, 2638, x + 194, 2638 + 296)))  # 表のメンバー色の枠を除く
            # 旧画像のほうが大きいとき（トレカ white・purple）はそちらを使う
            src_old = [k for k, vv in OLD_MAP.items() if vv == v]
            if src_old and (name,) + src_old[0] in old:
                o = old[(name,) + src_old[0]]; oi = Image.open(CARDS + o["file"])
                if min(oi.size) >= min(crop.size):
                    j.add(COLL, [name], SRC, v, oi, o["credit"]); continue
            j.add(COLL, [name], SRC, v, crop, "@idalshiro")
        for s, v in CARRY:
            o = old.get((name, s, v))
            j.add(COLL, [name], SRC, (s.replace("LINE FRIENDS ", "") + (" " + v if v else "")).strip(), Image.open(CARDS + o["file"]) if o else None, o["credit"] if o else "")
    j.save()
