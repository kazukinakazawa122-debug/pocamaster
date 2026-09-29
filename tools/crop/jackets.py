"""コレクションの表紙（アルバムのジャケットなど）の ZIP を作る

1. 本人が pocamaster-images/_jackets/ にジャケット画像を入れる。
   ファイル名はコレクション名（「コレクション名の一覧.txt」からコピー）。大文字小文字・空白・記号の違いは気にしない
2. このファイルを実行 → pocamaster-images/pocamaster-jackets.zip ができる
3. アプリの「設定 → 画像をまとめて取り込む（ZIP）」で読み込むと、表紙が置き換わる
"""
import csv, io, json, os, re, sys, unicodedata, zipfile
from PIL import Image, ImageOps

ROOT = "C:/Users/kazuk/OneDrive/pocamaster-images/"
# 試すとき用：python jackets.py <入力フォルダ> <出力 ZIP>
DIR = sys.argv[1] if len(sys.argv) > 1 else ROOT + "_jackets/"
OUT = sys.argv[2] if len(sys.argv) > 2 else ROOT + "pocamaster-jackets.zip"
SEED = os.path.dirname(os.path.abspath(__file__)) + "/../../public/seed/collections.csv"
EXT = (".jpg", ".jpeg", ".png", ".webp")


def norm(s: str) -> str:
    """大文字小文字・全角半角・空白・記号の違いをなくす"""
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[^0-9a-z\u3040-\u30ff\u4e00-\u9fff]", "", s)


names = [r["name"] for r in csv.DictReader(io.StringIO(open(SEED, encoding="utf-8").read()))]
os.makedirs(DIR, exist_ok=True)
with open(DIR + "コレクション名の一覧.txt", "w", encoding="utf-8") as f:
    f.write("ジャケット画像のファイル名を、下のコレクション名にしてください（例：ELEVEN.jpg）\n\n")
    f.write("\n".join(names) + "\n")

by_norm = {norm(n): n for n in names}
entries, unknown = [], []
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_STORED) as z:
    for fn in sorted(os.listdir(DIR)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in EXT:
            continue
        name = by_norm.get(norm(stem))
        if not name:
            unknown.append(fn)
            continue
        im = ImageOps.exif_transpose(Image.open(DIR + fn)).convert("RGB")
        # 一覧の四角に合わせて、真ん中を正方形に切る
        s = min(im.size)
        im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2))
        k = len(entries)
        for path, size, q in [(f"jackets/{k:03d}.jpg", 800, 88), (f"jackets/{k:03d}_t.jpg", 300, 85)]:
            b = io.BytesIO()
            im.resize((min(size, s), min(size, s)), Image.LANCZOS).save(b, "JPEG", quality=q)
            z.writestr(path, b.getvalue())
        entries.append({"collection": name, "members": [], "source": "", "version": "", "cover": True,
                        "file": f"jackets/{k:03d}.jpg", "thumb": f"jackets/{k:03d}_t.jpg"})
    z.writestr("manifest.json", json.dumps(entries, ensure_ascii=False))

sys.stdout.reconfigure(encoding="utf-8")
print("表紙", len(entries), "枚 →", OUT)
missing = [n for n in names if n not in {e["collection"] for e in entries}]
if unknown:
    print("コレクション名と合わないファイル：", *unknown, sep="\n  ")
print(f"まだジャケットがないコレクション {len(missing)} 件：", *missing, sep="\n  ")
