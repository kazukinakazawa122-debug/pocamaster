"""フリマの実物の写真で、本人がシリーズを教えてくれた写真（3・6・8・9・10）を、そのシリーズの 6 枚と重ねて決める（2026-10-02）
hires_real_1002.py の refine と同じ考え方：全カードからではなく、シリーズの中の 6 枚だけと比べる。顔では決めない（重なりの点数）。
python tools/crop/hires_real_1002b.py   → real_flea.json の該当の写真を更新して見比べページを作り直す"""
import io, itertools, json, sys, zipfile
import numpy as np
from PIL import Image
from build2 import *
from hires_real_0930 import locate
import hires_real_1002 as H

sys.stdout.reconfigure(encoding="utf-8")
SERIES = {3: ("IVE SECRET", "withmuu", "1.0"),
          6: ("IVE SWITCH", "Soundwave ファンサイン", "1.0"),
          8: ("I've MINE", "Hi-Touch", "18th・19th"),
          9: ("IVE SECRET", "Yetimall ラキドロ", "-1"),
          10: ("IVE SECRET", "Yetimall ラキドロ", "-2")}

out = json.load(open(H.OUTJ, encoding="utf-8"))
z = zipfile.ZipFile(H.ZIP)
entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
files = H.photos()
for pi, ser in SERIES.items():
    es = [e for e in entries if (e["collection"], e["source"], e["version"]) == ser]
    olds = [Image.open(io.BytesIO(z.read(e["file"]))).convert("RGB") for e in es]
    im = Image.open(files[pi]).convert("RGB")
    cells = [o for o in out if o["pi"] == pi]
    S = np.zeros((len(cells), len(es))); B = {}
    for i, o in enumerate(cells):
        for j, old in enumerate(olds):
            box, sc = locate(im, o["cell"], old, lo=0.6, hi=1.1)
            S[i, j] = sc if box else 0
            B[i, j] = box
    print("写真", pi, ser)
    print(np.round(S, 2))
    # 6 つのマスと 6 人を 1 対 1 で結ぶ（点数の合計が最大の組み合わせ）
    best = max(itertools.permutations(range(len(es))), key=lambda p: sum(S[i, p[i]] for i in range(len(cells))))
    for i, o in enumerate(cells):
        j = best[i]; e = es[j]
        print(" ", o["r"], o["c"], e["members"], round(S[i, j], 3), "2 位", round(sorted(S[i])[-2], 3))
        o.update(key=list(H.key(e)), score=round(float(S[i, j]), 3), box=B[i, j], old_h=olds[j].size[1], series=True)

# 写真 9・10 は「6枚セット」の文字が上の段のカードの下側と下の段のカードの上側にかかる（本人の選択：下の段の 6 枚だけ差し替える）。
# 下の段は文字を避けて、拡大した写真に目盛りを重ねてカードの角を読み取った箱（左・上・右・下。端から 6〜8px 内側、上は文字の下から）
MANUAL = {(9, 1, 0): [86, 1408, 438, 1930], (9, 1, 1): [476, 1410, 828, 1944], (9, 1, 2): [866, 1400, 1222, 1952],
          (10, 1, 0): [112, 1408, 446, 1928], (10, 1, 1): [479, 1408, 818, 1936], (10, 1, 2): [847, 1408, 1194, 1944]}
for o in out:
    if o["pi"] in (9, 10):
        if (o["pi"], o["r"], o["c"]) in MANUAL:
            o["box"] = MANUAL[o["pi"], o["r"], o["c"]]
            o["skip"] = False
        else:
            o["skip"] = True   # 上の段：文字がかかる
    elif o["pi"] in SERIES:
        o["skip"] = True       # 3・6・8：いまの画像のほうが大きい（500〜800px）ので差し替えない
json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# 見比べページには、今回差し替える下の段の 6 枚（9・10）だけを出す（ほかは前に本人が「同じ」と確認済み）
H.page([dict(o, score=0) if not (o["pi"] in (9, 10) and not o["skip"]) else o for o in out], z, entries)
