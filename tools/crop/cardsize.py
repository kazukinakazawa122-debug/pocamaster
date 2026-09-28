"""資料ごとに、カード 1 枚が何ピクセルで写っているかを調べる（画質のよい資料を探す用）

- out/cardsizes.csv：資料ごとのカードの数と、カードの横幅（中央値・元の画像のピクセル）
- out/cropsizes.csv：いま切り出してある画像（_cards）の横幅（フォルダごとの中央値）
"""
import csv, os, statistics
from PIL import Image
import grid
from build2 import ROOT, CARDS

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
EXT = (".jpg", ".jpeg", ".png", ".webp")

rows = []
root_files = sorted(f for f in os.listdir(ROOT) if f.lower().endswith(".jpg"))  # memlist.FILES と同じ並び
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x != "_cards"]
    for f in sorted(files):
        if not f.lower().endswith(EXT):
            continue
        p = os.path.join(d, f)
        folder = os.path.relpath(d, ROOT).replace("\\", "/")
        idx = root_files.index(f) if folder == "." and f in root_files else ""
        try:
            im = grid.load(p)
            bs = grid.card_boxes(im)
        except Exception as e:
            print("読めない", p, e)
            continue
        ws = [b[2] - b[0] for b in bs]
        med = round(statistics.median(ws)) if ws else 0
        rows.append((folder, f, idx, im.width, im.height, len(ws), med))
        print(f"{med:5d}px x{len(ws):3d}  {folder}/{f}")

os.makedirs(SP + "out", exist_ok=True)
with open(SP + "out/cardsizes.csv", "w", encoding="utf-8", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(["folder", "file", "memlist_index", "width", "height", "cards", "card_w"])
    wr.writerows(rows)

crop = []
for name in sorted(os.listdir(CARDS)):
    d = os.path.join(CARDS, name)
    if not os.path.isdir(d):
        continue
    ws = []
    for f in os.listdir(d):
        if f.lower().endswith(".jpg") and not f.endswith("_t.jpg"):
            with Image.open(os.path.join(d, f)) as im:
                ws.append(im.width)
    if ws:
        crop.append((name, len(ws), round(statistics.median(ws)), min(ws), max(ws)))
with open(SP + "out/cropsizes.csv", "w", encoding="utf-8", newline="") as fp:
    wr = csv.writer(fp)
    wr.writerow(["job", "images", "median_w", "min_w", "max_w"])
    wr.writerows(crop)
print("資料", len(rows), "枚 → out/cardsizes.csv、切り出し", len(crop), "フォルダ → out/cropsizes.csv")
