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
    ("ELEVEN", "グッズ｜Official MD"),
    ("LOVE DIVE", "Jewel ver. 9set POB"),
    ("LOVE DIVE", "グッズ｜POB"),
}
KEEP3 = {("IVE SWITCH", "Soundwave ラキドロ", "6.0"), ("IVE SWITCH", "TOKYO DOME 限定", "9/4"), ("IVE SWITCH", "TOKYO DOME 限定", "9/5")}
KEEP_VERSION = {("LOVE DIVE", "グッズ｜POB", "Sticker")}  # 表から作り直すので古い方は消す
ID_CREDITS = {"@powerofablink"}  # 画像に作者の ID（透かし）が写っている資料。画像は使わない（本人のルール、2026-09-29）
GOODS = False  # トレカ以外のグッズ（入手元が「グッズ｜」で始まる）を入れるか。今は入れない（本人決定、2026-09-28）


def DROP_SLOT(c, s, v):
    """本人が「この枠は消す」と決めた枠（作り直しの資料の job が再び作っても入れない）"""
    return (c == "IVE SWITCH" and s.startswith("LINE FRIENDS")) or (c == "IVE SECRET" and s == "Krispy Kreme Donuts") or (s == "MINIVE × LINE FRIENDS" and v in ("キーリング", "特典 3")) or (c == "IVE SECRET" and s == "withmuu ラキドロ" and v == "4.0-3") or (c == "IVE SECRET" and s == "the stage ラキドロ") or (c == "IVE SWITCH" and ((s == "Music Korea ラキドロ" and v == "2.0 POLA") or (s == "withmuu ラキドロ" and v in ("5.0 POLA", "6.0 POLA"))))  # 2026-10-01：LINE FRIENDS はイベントへ移す、Krispy Kreme はトレカではない


def q(s):
    return '"' + s.replace('"', '""') + '"' if any(c in s for c in ',"') else s


def key(r):
    return (r[0], "/".join(sorted(r[1].split("/"))), r[2], r[3])


rows = list(csv.reader(io.StringIO(open(SEED, encoding="utf-8").read())))
header, body = rows[0], rows[1:]

# 番号のつけちがいを直す（本人、2026-10-01）：IVE SECRET の QQ Music は、いまの 1→2・2→3・3→4・4→5・5→1 が正しい番号
RELABEL = {("IVE SECRET", "QQ Music"): {"1": "2", "2": "3", "3": "4", "4": "5", "5": "1"},
           # IVE SWITCH の Soundwave ラキドロ POLA（本人、2026-10-01）：いまの 2.0 の画像は実際は 1.0、4.0 は 2.0、6.0 は 3.0、9.0 は 4.0。6.0・9.0 の POLA は存在しない
           ("IVE SWITCH", "Soundwave ラキドロ"): {"2.0 POLA": "1.0 POLA", "4.0 POLA": "2.0 POLA", "6.0 POLA": "3.0 POLA", "9.0 POLA": "4.0 POLA", "11.0 POLA": "5.0 POLA"},  # 11.0 POLA は実際は 5.0 POLA（本人）
           # IVE SWITCH の「withmuu ラキドロ 4.0-3」の画像は実際は「withmuu ラキドロ 2.0 POLA」（本人、2026-10-01）
           ("IVE SWITCH", "withmuu ラキドロ"): {"4.0-3": "2.0 POLA"},
           # IVE SWITCH の「Tower Records 2」の実際の名前は「Tower Records 1.0 POLA」（本人、2026-10-01）
           ("IVE SWITCH", "Tower Records"): {"2": "1.0 POLA"}}


def relabel(c, s, v):
    return RELABEL.get((c, s), {}).get(v, v)


# 入手元ごと付け替える枠（本人、2026-10-01）：IVE SWITCH の「withmuu ラキドロ 3.0-3」の画像は実際は「Music Korea ラキドロ 1.0 POLA」
MOVE = {("IVE SWITCH", "withmuu ラキドロ", "3.0-3"): ("Music Korea ラキドロ", "1.0 POLA")}


_paths = sorted(glob.glob(SP + "out/*.json"))
jobs = [json.load(open(p, encoding="utf-8")) for p in _paths]
RELABELED_ALREADY = {"zzzzzzzzzzzz_secret_qq"}  # 新しい番号で作った job（付け替えない）
for _p, _j in zip(_paths, jobs):
    if os.path.splitext(os.path.basename(_p))[0] in RELABELED_ALREADY:
        continue
    _j["seed"] = [[r[0], r[1], r[2], relabel(r[0], r[2], r[3])] for r in _j["seed"]]
    for _e in _j["images"]:
        _e["version"] = relabel(_e["collection"], _e["source"], _e["version"])
    _j["seed"] = [[r[0], r[1]] + list(MOVE.get((r[0], r[2], r[3]), (r[2], r[3]))) for r in _j["seed"]]
    for _e in _j["images"]:
        _e["source"], _e["version"] = MOVE.get((_e["collection"], _e["source"], _e["version"]), (_e["source"], _e["version"]))
new_seed = [tuple(r) for j in jobs for r in j["seed"]]

kept = []
for r in body:
    if r[0] in REPLACE and (r[0], r[2]) not in KEEP and (r[0], r[2], r[3]) not in KEEP3:
        continue
    if (r[0], r[2], r[3]) in KEEP_VERSION:
        continue
    if not GOODS and r[2].startswith("グッズ｜"):
        continue
    if DROP_SLOT(r[0], r[2], r[3]):
        continue
    kept.append(tuple(r))
have = {key(r) for r in kept}
added = 0
front = []  # 作り直したコレクションは、表から作った枠を先に並べる
for r in new_seed:
    if not GOODS and r[2].startswith("グッズ｜"):
        continue
    if DROP_SLOT(r[0], r[2], r[3]):
        continue
    if key(r) not in have:
        (front if r[0] in REPLACE else kept).append(r)
        have.add(key(r))
        added += 1
kept = [r for r in kept if r[0] not in REPLACE] + front + [r for r in kept if r[0] in REPLACE]
# IVE SECRET の QQ Music は「1・2・3・4・5・Christmas」の順に並べる（本人、2026-10-01）。各メンバーの該当行の位置はそのままに、中身を並べ替える
_qq_order = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "Christmas": 5}
for _m in {r[1] for r in kept if r[0] == "IVE SECRET"}:
    _idx = [i for i, r in enumerate(kept) if r[0] == "IVE SECRET" and r[1] == _m and ((r[2] == "QQ Music" and r[3] in _qq_order) or (r[2] == "QQ Music × Starship Square" and r[3] == "Christmas"))]
    _rows = sorted((kept[i] for i in _idx), key=lambda r: _qq_order[r[3]])
    for i, r in zip(_idx, _rows):
        kept[i] = r
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
entries = [e for e in entries if e["credit"] not in ID_CREDITS and not DROP_SLOT(e["collection"], e["source"], e["version"])]
# 本人の確認で「その枠のカードではない」とわかった画像（代わりの画像がないので外すだけ）
WRONG_IMAGES = set()  # Be Alright のイソの Sony Music ラキドロは、BOYCOTT の印つきの表の画像に入れ替えた
entries = [e for e in entries if (e["collection"], tuple(sorted(e["members"])), e["source"], e["version"]) not in WRONG_IMAGES]
# 同じカードの画像が 2 つあれば、あとの方（新しい表）を使う
uniq = {}
for e in entries:
    uniq[(e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])] = e
entries = [e for e in uniq.values() if GOODS or not e["source"].startswith("グッズ｜")]
zp = "C:/Users/kazuk/OneDrive/pocamaster-images/pocamaster-images.zip"
# 明るさ補正（本人の要望、2026-10-01「REVIVE+ のカードが暗い」）：REVIVE+ の画像だけ、ZIP に入れるときに暗い部分を持ち上げる（ガンマ）。
# _cards の元の画像は変えない（補正をやめたいときは BRIGHT を空にして ZIP を作り直す）
BRIGHT = {"REVIVE+": 0.78}


def put(z, name, coll):
    g = BRIGHT.get(coll)
    if not g:
        z.write(CARDS + name, name); return
    from PIL import Image
    import numpy as np
    im = Image.open(CARDS + name).convert("RGB")
    a = 255.0 * (np.asarray(im).astype(np.float32) / 255.0) ** g
    buf = io.BytesIO(); Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(buf, "JPEG", quality=92)
    z.writestr(name, buf.getvalue())


with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
    for e in entries:
        put(z, e["file"], e["collection"])
        put(z, e["thumb"], e["collection"])
    z.writestr("manifest.json", json.dumps(entries, ensure_ascii=False))
print("images", len(entries), "zip", os.path.getsize(zp) // 1024, "KB")
