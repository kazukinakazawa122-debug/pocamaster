"""イソの MC Broadcast postcard（作者 _pipipup、2024。本人が 2026-09-30 に追加）

- 資料：pocamaster-images/新しい資料 2026-09-30/イソ_MC Broadcast postcard_pipipup.png。作者名は表の上下だけで、カードの上に透かしはない
- 14 枚を日付ごとの枠として「Leeseo Solo｜イソ個人」に足す（入手元 MC Broadcast postcard、バージョンは日付）
- 同じ作者の ELEVEN の表（同じフォルダの ELEVEN_pipipup…）は、カードの上に「made in 2025 by _pipipup」の透かしがあるので使わない
"""
from PIL import Image, ImageOps
import grid
from build2 import *

F = ROOT + "新しい資料 2026-09-30/イソ_MC Broadcast postcard_pipipup.png"
DATES = ["2024.04.28", "2024.05.06", "2024.07.14", "2024.09.01", "2024.09.27", "2024.09.29", "2024.10.06", "2024.10.27",
         "2024.11.03", "2024.11.10", "2024.11.17", "2024.11.24", "2024.12.01", "2024.12.15"]

if __name__ == "__main__":
    im = ImageOps.exif_transpose(Image.open(F)).convert("RGB")
    bs = sorted(grid.card_boxes(im, min_w=0.1, max_w=0.25), key=lambda b: (round(b[1] / 300), b[0]))
    assert len(bs) == len(DATES), len(bs)
    j = Job("zzz_mc_leeseo")
    for d, b in zip(DATES, bs):
        j.add("Leeseo Solo｜イソ個人", ["イソ"], "MC Broadcast postcard", d, im.crop(inset_frame(im, b)), "@_pipipup")
    j.save()
