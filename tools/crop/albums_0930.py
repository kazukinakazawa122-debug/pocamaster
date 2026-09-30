"""本人が 2026-09-30 に追加した資料（pocamaster-images/新しい資料 2026-09-30/）から、空いている枠を埋める・新しい種類を足す

- SHOW WHAT I HAVE の Random Photocard（@reina831wy）：UNIT の 15 枚と全員の 1 枚。組み合わせは、同じ作者のメンバー別一覧 6 枚のどこに
  同じ写真があるかで決めた（14 枚は 2 人の表と一致。29 はイソの表だけ一致し、残っている組み合わせがガウル・イソだけなのでそれにした）
- SHOW WHAT I HAVE Encore の Random Photocard Pack（@ri__chan94）：1 人 2 枚。リズのいまの画像と比べて、表の右が 1、左が 2
- IVE SCOUT の Random Photocard（@ri__chan94）：UNIT & GROUP の 16 枚。@idalshiro のメンバー別の表どうしで同じ写真を探し、
  表の並び（ユジン・ガウル → ユジン・レイ → … → リズ・イソ → 全員）と合うことを確かめた → 新しい枠
- IVE SCOUT の Special Photocard Camp Cook ver.（@ri__chan94）：1 人 1 枚 → 新しい枠
- DIVE JAPAN の会場限定 FC フォンタブ抽選トレカ（@reina831wy）：リズのいまの画像（無印の DIVE JAPAN Phone Tab）と同じ写真 → 無印の枠に 6 人分
- SuperStar STARSHIP の表（@reina831wy、列はガウル・ユジン・レイ・ウォニョン・リズ・イソ）：KCON in LA 2023・LONDON の段 → コラボの枠
- 位置：tools/crop/review/0930/（swih_units.json・scout_units.json・boxes.json・pt_boxes.json・ss_boxes.json）
- IVE SCOUT の Random Photocard Pack 1〜4 の画像は hires_0930.py で大きい方に入れ替える
"""
import json
from PIL import Image, ImageOps
from build2 import *

D = ROOT + "新しい資料 2026-09-30/"
R = SP + "review/0930/"
ORD6 = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
SWIH = "1st WORLD TOUR 'SHOW WHAT I HAVE'"
SCOUT = "3rd FAN CONCERT 'IVE SCOUT'"
SWIH_UNITS = {25: "ユジン/ガウル", 26: "ガウル/レイ", 27: "ガウル/ウォニョン", 28: "ガウル/リズ", 29: "ガウル/イソ", 30: "ユジン/レイ",
              31: "ユジン/ウォニョン", 32: "ユジン/リズ", 33: "ユジン/イソ", 34: "レイ/ウォニョン", 35: "レイ/リズ", 36: "レイ/イソ",
              37: "ウォニョン/リズ", 38: "ウォニョン/イソ", 39: "リズ/イソ"}
PAIRS = [(a, b) for i, a in enumerate(ORD6) for b in ORD6[i + 1:]]  # IVE SCOUT の表の並び


def load(fn):
    return ImageOps.exif_transpose(Image.open(D + fn)).convert("RGB")


if __name__ == "__main__":
    j = Job("zzz_0930")
    # SHOW WHAT I HAVE ユニット・全員（枠はもとからある）
    im = load("SWIH_Random Photocard_reina831wy.jpg")
    for n, box in json.load(open(R + "swih_units.json")):
        c = im.crop(inset_frame(im, box))
        if n == 40:
            j.add(SWIH, ["全員"], "Random Photocard", "GROUP", c, "@reina831wy")
        else:
            j.add(SWIH, SWIH_UNITS[n].split("/"), "Random Photocard", "ユニット", c, "@reina831wy")
    boxes = json.load(open(R + "boxes.json", encoding="utf-8"))
    # Encore ランダム（表の並び：ユジン・ガウル／レイ・ウォニョン／リズ・イソ、1 人 2 枚。右が 1、左が 2）
    im = load("SWIH Encore_Random Photocard Pack_ri__chan94.jpg")
    for k, m in enumerate(ORD6):
        left, right = sorted(boxes["enc"][2 * k:2 * k + 2], key=lambda b: b[0])
        j.add(SWIH, [m], "Encore（アンコール）", "Random Photocard 1", im.crop(inset_frame(im, right)), "@ri__chan94")
        j.add(SWIH, [m], "Encore（アンコール）", "Random Photocard 2", im.crop(inset_frame(im, left)), "@ri__chan94")
    # IVE SCOUT ユニット・全員（新しい枠）
    im = load("IVE SCOUT_Random Photocard_ri__chan94.jpg")
    for n, box in enumerate(json.load(open(R + "scout_units.json"))):
        c = im.crop(inset_frame(im, box))
        if n < 15:
            j.add(SCOUT, list(PAIRS[n]), "Random Photocard Pack", "ユニット", c, "@ri__chan94")
        else:
            j.add(SCOUT, ["全員"], "Random Photocard Pack", "グループ", c, "@ri__chan94")
    # IVE SCOUT Camp Cook ver.（新しい枠。表の並び：ユジン・ガウル・レイ／ウォニョン・リズ・イソ）
    im = load("IVE SCOUT_Special Photocard Camp Cook ver_ri__chan94.jpg")
    cc = [b for b in boxes["cc"] if (b[2] - b[0]) > 600]  # カードの中にできた小さな枠を除く
    cc = sorted(cc, key=lambda b: (round(b[1] / 300), b[0]))
    for m, b in zip(ORD6, cc):
        j.add(SCOUT, [m], "Special Photocard", "Camp Cook ver.", im.crop(inset_frame(im, b)), "@ri__chan94")
    # DIVE JAPAN フォンタブ抽選トレカ（表の並び：ガウル・ユジン・レイ／ウォニョン・リズ・イソ）
    im = load("DIVE JAPAN GOODS_会場限定FCフォンタブ抽選トレカ_reina831wy.jpg")
    pt = sorted(json.load(open(R + "pt_boxes.json")), key=lambda b: (round(b[1] / 200), b[0]))
    for m, b in zip(["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"], pt):
        j.add("DIVE Official Fanclub｜ファンクラブ", [m], "DIVE JAPAN Phone Tab", "", im.crop(inset_frame(im, b)), "@reina831wy")
    # SuperStar STARSHIP：KCON in LA 2023（42〜47）・LONDON（48〜53）
    im = load("SuperStar STARSHIP_reina831wy.jpg")
    ss = json.load(open(R + "ss_boxes.json"))
    SSM = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]
    for ver, start in (("KCON LA", 42), ("LONDON", 48)):
        for k, m in enumerate(SSM):
            j.add("Collab & Event｜コラボ・イベント", [m], "SuperStar STARSHIP", ver, im.crop(inset_frame(im, ss[start + k])), "@reina831wy")
    j.save()
