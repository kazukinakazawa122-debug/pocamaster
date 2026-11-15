"""2026-11-16：新しいアルバム LOOKS CAN KILL（IVE EP《SPIN-OFF》、2026-10-26 発売）の枠と画像

資料は pocamaster-images/新しい資料 2026-11-16/（@LILY_221019 の X の一覧表を元の大きさで保存。本人の了承ずみ）
- lily_v5_1.jpg：封入＆特典＆ラキドロ 全員 ver.5（2026-11-01）。53 種類 × 6 人 → 枠はすべてここから。画像も基本はここ（カード 63×96px）
- lily_v6_2.jpg：封入のみ ver.6（カード 約 100px）→ 本体封入・PLANET を差し替え
- lily_solo_1〜3.jpg：封入のみ メンバー別 ver.3（ウォニョン・リズ・イソ。カード 約 140px）→ 同じく差し替え
- lily_jp_1.jpg：日本の店舗特典 ver.2（カード 約 190px）→ タワレコ・HMV・ソニミュ・A!SMART を差し替え
- 使わない：lily_jp_2・jp_3（カードの上に「@LILY_221019」の透かし）
差し替えは、同じメンバーの列の中で v5 の小さい画像と見比べて（灰色 24×36 の相関）いちばん似ている枠に入れる。
QQ Music（無印）はカードの半分がピンクで隠れているので画像なし。ぼかしのカードは、ほかに画像がないので入れる。
"""
import numpy as np
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-11-16/"
COLL = "LOOKS CAN KILL"
LILY = "@LILY_221019"
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]  # 表の列の順
P = "PLANET トレーディングカード "

# v5 の 3 列 × 上から（入手元, 種類）。None の行は画像なし
LABELS = [
    # 左の列
    [("本体封入", "GIRL HERO"), ("本体封入", "HERO COMICS"), ("本体封入", "HERO ON SET"), ("本体封入", "LOVED IVE"),
     ("本体封入", "Digipack"), ("本体封入", "PETIT-IVE"),
     ("本体封入", P + "SSR HERO SPECIAL"), ("本体封入", P + "SR HERO RARE"),
     ("本体封入", P + "A HERO BASIC 1"), ("本体封入", P + "A HERO BASIC 2"), ("本体封入", P + "A HERO BASIC 3"),
     ("本体封入", "PLANET フォトカード 1"), ("本体封入", "PLANET フォトカード 2"),
     ("Starship Square", "3TYPE"), ("Starship Square", "LOVED IVE"), ("Starship Square", "Digipack"),
     ("US Exclusive", ""), ("KPOP NARA", "")],
    # まん中の列
    [("hello82", "オンライン"), ("hello82", "82EVENT オフライン"), ("withmuu", "1.0"), ("Apple Music", "1.0"),
     ("Makestar", "1.0"), ("Amazon", ""), ("Target", ""), ("B&N", ""),
     ("Tower Records", "1.0 A"), ("Tower Records", "1.0 渋谷"), ("HMV", "B"), ("Sony Music", "C"), ("A!SMART", "D"),
     ("OLIVE YOUNG", ""), ("GS25", ""), ("Apple Music", "2.0"), ("Makestar", "2.0"), ("MCD STATION", "")],
    # 右の列
    [("一直娱（withfans）", ""), ("Album Release Celebration ラキドロ", "PLANET"),
     ("Album Release Celebration ラキドロ", "4TYPE"), ("Broadcast", "1"), ("Broadcast", "2"),
     ("Soundwave ラキドロ", "1.0"), ("Soundwave ラキドロ", "1.0 POLA"), ("withmuu ラキドロ", "2.0"),
     ("withmuu ラキドロ", "2.0 POLA"), ("Ktown4U", "1.0"), ("MusicArt", "ARTBOX"), ("MusicArt", "永豊文庫"),
     ("MUSINSA", ""), ("QQ Music", None), ("QQ Music", "NFC"), ("Music Korea", "1.0"), ("QQ Music", "オフライン")],
]


def rows_of(bs):
    rows = []
    for b in sorted(bs, key=lambda b: (b[1] + b[3]) / 2):
        cy, h = (b[1] + b[3]) / 2, b[3] - b[1]
        if rows and abs(cy - rows[-1][0]) < h * 0.35:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    return [sorted(r, key=lambda b: b[0]) for _, r in rows]


def sig(img):
    a = np.asarray(img.convert("L").resize((24, 36), Image.BILINEAR), float).ravel()
    a -= a.mean()
    return a / (np.linalg.norm(a) + 1e-9)


def base():
    """v5 から {(列, 行, メンバー番号): 画像}"""
    im = grid.load(D + "lily_v5_1.jpg")
    bs = grid.card_boxes(im, ratio=(1.2, 1.8), min_w=0.03, max_w=0.1)
    W = im.size[0]
    cols = [[], [], []]
    for b in bs:
        cx = (b[0] + b[2]) / 2
        cols[0 if cx < W * 0.37 else 1 if cx < W * 0.65 else 2].append(b)
    out = {}
    for c in range(3):
        rows = rows_of(cols[c])
        assert len(rows) == len(LABELS[c]), (c, len(rows))
        full = [row for row in rows if len(row) == 6]
        xs = np.median([[(b[0] + b[2]) / 2 for b in row] for row in full], 0)
        w = np.median([b[2] - b[0] for row in full for b in row])
        for r, row in enumerate(rows):
            if LABELS[c][r][1] is None:
                continue
            if len(row) < 6:
                # 白っぽいカードを見落とした所は、ほかの行の位置で補う
                y0, y1 = np.median([b[1] for b in row]), np.median([b[3] for b in row])
                got = {int(np.argmin(abs(xs - (b[0] + b[2]) / 2))): b for b in row}
                row = [got.get(k, (xs[k] - w / 2, y0, xs[k] + w / 2, y1)) for k in range(6)]
                print("補った行", c, r, sorted(set(range(6)) - set(got)))
            # 暗いポラなどで箱が小さく取れたものは、同じ行のほかのカードの大きさにそろえる
            y0, y1 = np.median([b[1] for b in row]), np.median([b[3] for b in row])
            bw = np.median([b[2] - b[0] for b in row])
            row = [b if abs((b[3] - b[1]) - (y1 - y0)) < (y1 - y0) * 0.06 else
                   ((b[0] + b[2]) / 2 - bw / 2, y0, (b[0] + b[2]) / 2 + bw / 2, y1) for b in row]
            for k, b in enumerate(row):
                out[(c, r, k)] = im.crop(tuple(int(v) for v in b))
    return out


def better(cards, files, members=None):
    """大きい資料のカードを、同じメンバーの v5 のカードと見比べて差し替える。members：資料ごとのメンバー番号（メンバー別の表）"""
    sigs = {key: sig(img) for key, img in cards.items()}
    log = []
    for i, f in enumerate(files):
        im = grid.load(D + f)
        bs = grid.card_boxes(im, ratio=(1.2, 1.8), min_w=0.04, max_w=0.2)
        cand = []
        for b in bs:
            crop = im.crop(tuple(int(v) for v in b))
            s = sig(crop)
            if members is not None:
                pool = [key for key in sigs if key[2] == members[i]]
            else:
                # 全員の表：列の位置でメンバーを決めず、全部と比べる
                pool = list(sigs)
            sc = sorted(((float(s @ sigs[key]), key) for key in pool), reverse=True)
            if sc and sc[0][0] >= 0.85 and (len(sc) < 2 or sc[0][0] - sc[1][0] >= 0.04):
                cand.append((sc[0][0], sc[0][1], crop))
        used = {}
        for score, key, crop in sorted(cand, key=lambda t: -t[0]):
            if key in used:
                continue
            if crop.size[0] > cards[key].size[0] * 1.15:
                used[key] = (score, crop)
        for key, (score, crop) in used.items():
            cards[key] = crop
            log.append((f, key, round(score, 3), crop.size))
    return log


if __name__ == "__main__":
    cards = base()
    log = better(cards, ["lily_v6_2.jpg"])
    log += better(cards, ["lily_solo_1.jpg", "lily_solo_2.jpg", "lily_solo_3.jpg"], members=[3, 4, 5])
    log += better(cards, ["lily_jp_1.jpg"])
    import collections
    print("差し替え", len(log), collections.Counter(l[0] for l in log))
    open("C:/Users/kazuk/AppData/Local/Temp/claude/ebec4f3e385bac35/ab8ee283-d126-40bd-85c1-6ccb066da3c8/scratchpad/lck_log.txt", "w", encoding="utf-8").write(
        "\n".join(f"{f}\t{LABELS[k[0]][k[1]]}\t{M[k[2]]}\t{s}\t{sz}" for f, k, s, sz in log))
    j = Job("lck")
    for c in range(3):
        for r, (src, ver) in enumerate(LABELS[c]):
            for k, m in enumerate(M):
                j.add(COLL, [m], src, ver or "", cards.get((c, r, k)), LILY)
    j.save()
