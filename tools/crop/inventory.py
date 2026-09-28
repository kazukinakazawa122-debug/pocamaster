"""手元の資料（pocamaster-images の中の画像、_cards は除く）の一覧と大きさを out/sources.csv に書き出す

どの資料がいちばん大きいか（切り出したときに画質がよいか）を比べるために使う。
"""
import csv, os
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
ROOT = "C:/Users/kazuk/OneDrive/pocamaster-images/"
EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".jfif", ".heic")

rows = []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x != "_cards"]
    for f in files:
        if not f.lower().endswith(EXT):
            continue
        p = os.path.join(d, f)
        try:
            with Image.open(p) as im:
                w, h = im.size
        except Exception:
            w = h = 0
        rows.append((os.path.relpath(d, ROOT).replace("\\", "/"), f, w, h, os.path.getsize(p) // 1024))

rows.sort()
os.makedirs(SP + "out", exist_ok=True)
with open(SP + "out/sources.csv", "w", encoding="utf-8", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(["folder", "file", "width", "height", "kb"])
    wr.writerows(rows)

print("資料", len(rows), "枚 → out/sources.csv")
by = {}
for r in rows:
    by.setdefault(r[0], []).append(r[2])
for k, ws in sorted(by.items()):
    ws.sort()
    print(f"{len(ws):4d} 枚  横 {ws[0]}〜{ws[-1]}  {k}")
