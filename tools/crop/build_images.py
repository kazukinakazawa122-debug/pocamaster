"""一覧表からカード画像を切り出し、アプリに取り込むための manifest を作る

出力：pocamaster/images/_cards/<コレクション>/<番号>.jpg と manifest.json
"""
import json, os, sys
from PIL import Image

PROJ = r"C:/Users/kazuk/pocamaster/"
ENG = "C:/Users/kazuk/OneDrive/pocamaster-images/IVE English ver. - photocard list-20260927T144026Z-1-001/IVE English ver. - photocard list/"
OUT = "C:/Users/kazuk/OneDrive/pocamaster-images/_cards/"
M = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]  # reina831wy の表の並び順

entries = []
if os.path.exists(OUT + "manifest.json"):
    entries = json.load(open(OUT + "manifest.json", encoding="utf-8"))


def save(collection, members, source, version, img, credit):
    d = OUT + collection.replace("'", "").replace("|", "_").replace("｜", "_") + "/"
    os.makedirs(d, exist_ok=True)
    fn = f"{len([f for f in os.listdir(d) if not f.endswith('_t.jpg')]):04d}"
    img = img.convert("RGB")
    # 画質を上げる方針（本人、2026-10-02）：上限 800→1600px・画質 88→92、一覧用 400→600px・82→88（build2.py と同じ）
    img.thumbnail((1600, 1600))
    img.save(d + fn + ".jpg", quality=92)
    t = img.copy(); t.thumbnail((600, 600)); t.save(d + fn + "_t.jpg", quality=88)
    rel = os.path.relpath(d + fn + ".jpg", OUT).replace("\\", "/")
    # 同じカードの古い画像は置き換える
    key = (collection, tuple(sorted(members)), source, version)
    global entries
    entries = [e for e in entries if (e["collection"], tuple(sorted(e["members"])), e["source"], e["version"]) != key]
    entries.append({"collection": collection, "members": members, "source": source, "version": version, "file": rel, "thumb": rel[:-4] + "_t.jpg", "credit": credit})


def grid(path, collection, credit, sides):
    """sides: [{cols:[x...], rows:[(y, w, h, source, version) ...]}]。列は M の順"""
    im = Image.open(path)
    n = 0
    for side in sides:
        for (y, w, h, source, version) in side["rows"]:
            if source is None:
                continue
            for x, mem in zip(side["cols"], M):
                box = (int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2))
                save(collection, [mem], source, version, im.crop(box), credit)
                n += 1
    print(collection, n)


def after_like():
    p = ENG + "03 - after like/07-all.JPG"
    W, H = 172, 262
    L = [(612, W, H, "本体封入", "ver.1"), (907, W, H, "本体封入", "ver.2"), (1202, W, H, "本体封入", "ver.3"),
         (1497, W, H, "グッズ｜本体封入", "Postcard"), (1749, 175, 175, "POB", "Circle Card"),
         (2060, W, 235, "グッズ｜本体封入", "Jewel ver. Photobook"), (2307, W, H, "本体封入", "Jewel ver."),
         (2637, 180, 300, "グッズ｜本体封入", "Jewel ver. Mini Folded Poster"),
         (2970, W, H, "Fansign", "ATL ver."), (3263, W, H, "Daum Cafe", ""), (3560, W, H, "Broadcast", "After ver."),
         (3854, W, H, "Broadcast", "Like ver."), (4147, W, H, "Jewel ver. POB", "6set"), (4439, W, H, "Jewel ver. POB", "6+3set"),
         (4736, W, H, "Starship Square", "CHU~♥ 1"), (5029, W, H, "Starship Square", "CHU~♥ 2"), (5326, W, H, "Ktown4U", ""),
         (5621, W, H, "Bandina", ""), (5913, W, H, "mymusictaste", ""), (6208, W, H, "withmuu", "1.0")]
    R = [(611, W, H, "Soundwave", "1.0"), (907, W, H, "Naver Shopping Live", ""),
         (1202, W, H, "Soundwave ラキドロ", "2.0-1"), (1497, W, H, "Soundwave ラキドロ", "2.0-2"), (1791, W, H, "Soundwave ラキドロ", "2.0-3"),
         (2086, W, H, "withmuu ラキドロ", "2.0-1"), (2381, W, H, "withmuu ラキドロ", "2.0-2"), (2665, W, H, "withmuu ラキドロ", "2.0-3"),
         (2968, W, H, "Tower Records", "1"), (3253, W, H, "Tower Records", "2"), (3557, W, H, "Beatroad", ""),
         (3854, W, H, "Apple Music", ""), (4147, W, H, "Namil Music", ""), (4442, W, H, "MokketShop", ""), (4736, W, H, "TOU", "1.0"),
         (5031, W, H, "Music Korea", ""), (5326, W, H, "Soundwave", "3.0"), (5618, W, H, "StarRiver", ""),
         (5913, W, H, "withmuu", "3.0"), (6208, W, H, "Soundwave", "4.0")]
    grid(p, "After LIKE", "@reina831wy", [
        {"cols": [693, 907, 1120, 1333, 1547, 1758], "rows": L},
        {"cols": [2364, 2577, 2790, 3004, 3215, 3429], "rows": R},
    ])


if __name__ == "__main__":
    import shutil, zipfile
    args = sys.argv[1:]
    if args and args[0] == "--fresh":
        # 作り直すときは、前に切り出した画像を消してから始める
        shutil.rmtree(OUT, ignore_errors=True)
        entries = []
        args = args[1:]
    for name in args:
        globals()[name]()
    os.makedirs(OUT, exist_ok=True)
    json.dump(entries, open(OUT + "manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("manifest", len(entries))
    zp = "C:/Users/kazuk/OneDrive/pocamaster-images/pocamaster-images.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for e in entries:
            z.write(OUT + e["file"], e["file"])
            z.write(OUT + e["thumb"], e["thumb"])
        z.write(OUT + "manifest.json", "manifest.json")
    print("zip", os.path.getsize(zp) // 1024, "KB")
