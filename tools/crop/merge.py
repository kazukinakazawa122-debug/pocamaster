"""out/*.json をまとめて、cards.csv（枠）と画像の ZIP を作り直す

- REPLACE に書いたコレクションは、cards.csv の古い枠を消して表から作った枠に置き換える
  （KEEP に書いた、別の資料から追加済みの枠は残す）
- ほかのコレクションは、まだない枠だけ追加する
"""
import csv, io, json, os, glob, zipfile

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
PROJ = r"C:/Users/kazuk/pocamaster/"
CARDS = "C:/Users/kazuk/OneDrive/pocamaster-images/_cards/"
SEED = PROJ + "public/seed/cards.csv"

REPLACE = {"ELEVEN", "LOVE DIVE", "IVE SWITCH", "IVE EMPATHY", "IVE SECRET"}
KEEP = {
    ("IVE EMPATHY", "Amulet Card (Tokyo 3/29)"),
    ("IVE EMPATHY", "'IVE SCOUT' Offline Event Kobe/Yokohama (4/25-26)/(4/29-30)"),
    ("IVE EMPATHY", "'IVE SCOUT' Offline Event Nagoya/Fukuoka (4/12-13)/(4/21-22)"),
    ("ELEVEN", "グッズ｜Official MD"),
    ("LOVE DIVE", "Jewel ver. 9set POB"),
    ("LOVE DIVE", "グッズ｜POB"),
}
KEEP3 = {("IVE SWITCH", "Soundwave ラキドロ", "6.0"), ("IVE SWITCH", "TOKYO DOME 限定", "9/4"), ("IVE SWITCH", "TOKYO DOME 限定", "9/5")}
KEEP_VERSION = {("LOVE DIVE", "グッズ｜POB", "Sticker")}  # 表から作り直すので古い方は消す
ID_CREDITS = {"@powerofablink"}  # 画像に作者の ID（透かし）が写っている資料。画像は使わない（本人のルール、2026-09-29）
GOODS = False  # トレカ以外のグッズ（入手元が「グッズ｜」で始まる）を入れるか。今は入れない（本人決定、2026-09-28）


def q(s):
    return '"' + s.replace('"', '""') + '"' if any(c in s for c in ',"') else s


def key(r):
    return (r[0], "/".join(sorted(r[1].split("/"))), r[2], r[3])


rows = list(csv.reader(io.StringIO(open(SEED, encoding="utf-8").read())))
header, body = rows[0], rows[1:]

jobs = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(SP + "out/*.json"))]
new_seed = [tuple(r) for j in jobs for r in j["seed"]]

kept = []
for r in body:
    if r[0] in REPLACE and (r[0], r[2]) not in KEEP and (r[0], r[2], r[3]) not in KEEP3:
        continue
    if (r[0], r[2], r[3]) in KEEP_VERSION:
        continue
    if not GOODS and r[2].startswith("グッズ｜"):
        continue
    kept.append(tuple(r))
have = {key(r) for r in kept}
added = 0
front = []  # 作り直したコレクションは、表から作った枠を先に並べる
for r in new_seed:
    if not GOODS and r[2].startswith("グッズ｜"):
        continue
    if key(r) not in have:
        (front if r[0] in REPLACE else kept).append(r)
        have.add(key(r))
        added += 1
kept = [r for r in kept if r[0] not in REPLACE] + front + [r for r in kept if r[0] in REPLACE]
with open(SEED, "w", encoding="utf-8", newline="\n") as f:
    f.write(",".join(header) + "\n")
    for r in kept:
        f.write(",".join(q(x) for x in r) + "\n")
print("cards.csv", len(body), "->", len(kept), f"(表から追加 {added})")

# 画像：After LIKE（build_images.py の manifest）＋ 各 job
entries = []
if os.path.exists(CARDS + "manifest.json"):
    entries = [e for e in json.load(open(CARDS + "manifest.json", encoding="utf-8")) if e["collection"] == "After LIKE"]
for j in jobs:
    entries += j["images"]
entries = [e for e in entries if e["credit"] not in ID_CREDITS]
# 本人の確認で「その枠のカードではない」とわかった画像（代わりの画像がないので外すだけ）
WRONG_IMAGES = {("Be Alright", ("イソ",), "Sony Music ラキドロ", "")}
entries = [e for e in entries if (e["collection"], tuple(sorted(e["members"])), e["source"], e["version"]) not in WRONG_IMAGES]
# 同じカードの画像が 2 つあれば、あとの方（新しい表）を使う
uniq = {}
for e in entries:
    uniq[(e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])] = e
entries = [e for e in uniq.values() if GOODS or not e["source"].startswith("グッズ｜")]
zp = "C:/Users/kazuk/OneDrive/pocamaster-images/pocamaster-images.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
    for e in entries:
        z.write(CARDS + e["file"], e["file"])
        z.write(CARDS + e["thumb"], e["thumb"])
    z.writestr("manifest.json", json.dumps(entries, ensure_ascii=False))
print("images", len(entries), "zip", os.path.getsize(zp) // 1024, "KB")
