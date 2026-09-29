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
EXT = (".jpg", ".jpeg", ".png", ".webp", ".avif")

# ファイル名がコレクション名と違うもの（2026-09-29 に本人が入れた分。画像を見て確認済み）
MAP = {
    "IVE - Eleven Album Cover": "ELEVEN",
    "IVE _ REVIVE+": "REVIVE+",
    "IVE 〈ELEVEN -Japanese ver_〉 ALBUM COVER": "ELEVEN -Japanese ver.-",
    "IVE 〈I'VE MINE〉 ALBUM COVER": "I've MINE",
    "IVE 〈I've IVE〉 ALBUM COVER": "I've IVE",
    "IVE 〈IVE EMPATHY〉 ALBUM COVER": "IVE EMPATHY",
    "IVE 〈WAVE〉 ALBUM COVER": "WAVE",
    "IVE_season_greeting_2024_cover": "2024 SEASON'S GREETINGS [A Fairy's Wish]",
    "Ive - Ive Switch Album": "IVE SWITCH",
    "ive-2026-seasons-greetings-atelier-ive": "2026 SEASON'S GREETINGS [ATELIER IVE]",
    "ive_afterlike_cover": "After LIKE",
    "ive_alive_cover": "ALIVE",
    "ive_bealright_cover": "Be Alright",
    "ive_dive_fanclub": "DIVE Official Fanclub｜ファンクラブ",
    "ive_dive_into_ive_cover": "4th FAN CONCERT 'DIVE into IVE'",
    "ive_lovedive_cover": "LOVE DIVE",
    "ive_lucid_dream_cover": "LUCID DREAM",
    "ive_magazine_ive_cover": "2nd FANMEETING 'MAGAZINE IVE'",
    "ive_pepsi_cover": "Pepsi × IVE 'BLUE & BLACK'",
    "ive_scount_jacket": "3rd FAN CONCERT 'IVE SCOUT'",
    "ive_season_greeting_2022_cover": "2022 SEASON'S GREETINGS [A RAY OF SUNSHINE]",
    "ive_season_greeting_2023_cover": "2023 SEASON'S GREETINGS [Ready, Get Set, IVE!]",
    "ive_season_greeting_2025_cover": "2025 SEASON'S GREETINGS [Colorful Days with IVE]",
    "ive_secret_cover": "IVE SECRET",
    "ive_show_ehat_i_have_cover": "1st WORLD TOUR 'SHOW WHAT I HAVE'",
    "ive_show_what_i_am_cover": "2nd WORLD TOUR 'SHOW WHAT I AM'",
    "ive_the_prom_queens_cover": "1st FAN CONCERT 'The Prom Queens'",
    "ive_wonyoung_album_cover": "Wonyoung Solo｜ウォニョン個人",
}


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
        name = MAP.get(stem) or by_norm.get(norm(stem))
        if not name:
            unknown.append(fn)
            continue
        im = ImageOps.exif_transpose(Image.open(DIR + fn)).convert("RGB")
        # 一覧の四角に合わせて正方形に切る。縦長のポスターはタイトルが上にあることが多いので、少し上寄りに切る
        s = min(im.size)
        x0 = (im.width - s) // 2
        y0 = (im.height - s) // 4
        im = im.crop((x0, y0, x0 + s, y0 + s))
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
