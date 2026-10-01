"""SHOW WHAT I AM のランダムトレカの全員のカード 4 枚（本人が 2026-10-01 にフォルダへ入れた Amazingk の「MD Benefit Photocard / Trading Card」の表）

- 表（1000×1000）：左の 1 列＝MD Benefit Photocard 6 枚、右＝Trading Card（6 人×6 枚＋右端の全員のカード 4 枚）。
  右端の縦 4 枚（上から）を「Random Photocard Pack Korea｜IVE 1〜4」（全員）にする。上から 1・2・3・4 と見なした（確認 _review/swia_group.html）
- 表は店（Amazingk）の模様が背景にあるだけで、カードには何も写っていない（個人の ID ではない）
- 小さい（約 80×127px）が唯一の資料
"""
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/SHOW WHAT I AM ランダムトレカ 全員カード/"
BOX = [(825, 134, 906, 261), (825, 265, 906, 392), (825, 397, 906, 524), (825, 528, 906, 655)]
if __name__ == "__main__":
    im = grid.load(D + "SWIA_MD_TradingCard_Amazingk.jpg")
    j = Job("zzzzzzzzzzzzzzzzzz_swia_group")
    for i, b in enumerate(BOX, start=1):
        j.add("2nd WORLD TOUR 'SHOW WHAT I AM'", ["全員"], "Random Photocard Pack Korea", f"IVE {i}", im.crop((b[0] + 2, b[1] + 2, b[2] - 2, b[3] - 2)), "店の表（Amazingk）")
    j.save()
