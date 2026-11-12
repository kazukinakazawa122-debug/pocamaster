"""メルカリの写真で差し替える作業を、まとめて回す道具（2026-11-13。16〜20 回目に毎回その場で書いていた手順をまとめた）
スキル .claude/skills/pocamaster-card-hires/SKILL.md の手順で使う。1 枚ずつの道具は mercari_hires.py。

<回> は日付の形の名前（例 20261114）。その回の名前は <回>a・<回>b… になる。
<組> は「フォルダ名 コレクション名」を並べた JSON（tools/crop/review/hires/<回>_組.json）。例：
  {"SECRET": "IVE SECRET", "STASHI": "2nd WORLD TOUR 'SHOW WHAT I AM'||2nd FANMEETING 'MAGAZINE IVE'"}
  「A||B」で複数のコレクションをまとめて照らし合わせる。フォルダが _A・_B に分かれていても、もとの名前で書く。

  python tools/crop/hires_batch.py filter   <回> <集めた番号.txt>   … 保存済みの出品番号を外して <回>a_候補.txt を作る（件数を出す）
  python tools/crop/hires_batch.py download <回>                   … 候補を「新しい資料 <回>/」に保存（本人の了承のあとだけ）。110 件を超える組は _A・_B に分ける
  python tools/crop/hires_batch.py find     <回>                   … 全部のフォルダを並べて照らし合わせる（裏で動かす。10 本ずつ）
  python tools/crop/hires_batch.py dedupe   <回>                   … 同じ枠が 2 つの名前にあるとき、前の名前の ok から外す（あとの名前が勝つため）
  python tools/crop/hires_batch.py apply    <回>                   … 全部の名前を apply（このあと merge.py → make_diff.py）
  python tools/crop/hires_batch.py page     <回> <出力フォルダ> <見出し> … 押して確かめるページ（HTML と img/）を作る。<見出し> は「20回目」など
  python tools/crop/hires_batch.py ng       <回> a-03 e-01 …       … 本人が「合っていない」にした組を ok から外す（そのあと apply → merge → make_diff）
  python tools/crop/hires_batch.py split    <差分ZIP>              … 28MB を超える差分 ZIP を、同じ番号のまま 1of2・2of2… に分ける（スマホに送れるのは 30MB まで）

集めた番号.txt・候補.txt の形：1 行に「組の名前 出品番号 出品番号 …」（番号は m があってもなくてもよい）
"""
import glob, json, os, re, string, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/"
REPO = os.path.dirname(os.path.dirname(HERE.rstrip("/"))).replace("\\", "/") + "/"
ROOT = "C:/Users/kazuk/OneDrive/pocamaster-images/"
CFG = HERE + "review/hires/"
PHOTO = "https://static.mercdn.net/item/detail/orig/photos/m%s_1.jpg"
SPLIT_OVER = 110  # 1 つのフォルダに入れる件数（多いと照らし合わせが長くなるので半分に分ける）
ZIP_LIMIT = 28 * 1024 * 1024


def names(run):
    """その回の名前（設定ファイルのあるもの）を名前の順に"""
    return sorted(os.path.basename(p)[:-10] for p in glob.glob(CFG + run + "*_find.json"))


def load(name):
    return json.load(open(CFG + name + ".json", encoding="utf-8"))


def save(name, c):
    json.dump(c, open(CFG + name + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def read_groups(path):
    out = []
    for line in open(path, encoding="utf-8"):
        p = line.split()
        if len(p) >= 1:
            out.append((p[0], [x.lstrip("m") for x in p[1:]]))
    return out


def cmd_filter(run, raw):
    saved = set()
    for d in glob.glob(ROOT + "新しい資料*"):
        for _, _, fs in os.walk(d):
            for f in fs:
                saved |= set(re.findall(r"m(\d{9,})", f))
    seen, lines, total = set(), [], 0
    for tag, ids in read_groups(raw):
        new = [i for i in dict.fromkeys(ids) if i not in saved and i not in seen]
        seen |= set(new)
        total += len(new)
        print(f"{tag}：{len(ids)} 件 → 新しい {len(new)} 件")
        lines.append(tag + " " + " ".join("m" + i for i in new))
    out = CFG + run + "a_候補.txt"
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"合計 {total} 件 → {out}（保存済み {len(saved)} 件は外した）")


def folders(run):
    """候補の組 → [(フォルダ名, 組の名前, 番号…)]"""
    out = []
    for tag, ids in read_groups(CFG + run + "a_候補.txt"):
        if not ids:
            continue
        if len(ids) > SPLIT_OVER:
            h = (len(ids) + 1) // 2
            out += [(tag + "_A", tag, ids[:h]), (tag + "_B", tag, ids[h:])]
        else:
            out.append((tag, tag, ids))
    return out


def cmd_download(run):
    base = ROOT + f"新しい資料 {run}/"
    jobs = []
    for folder, tag, ids in folders(run):
        os.makedirs(base + folder, exist_ok=True)
        jobs += [(base + f"{folder}/{tag}_m{i}.jpg", PHOTO % i) for i in ids]

    def get(j):
        path, url = j
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return True
        r = subprocess.run(["curl", "-s", "-f", "-m", "30", "-o", path, url])
        return r.returncode == 0

    with ThreadPoolExecutor(8) as ex:
        ok = list(ex.map(get, jobs))
    size = sum(os.path.getsize(p) for p, _ in jobs if os.path.exists(p))
    print(f"保存 {sum(ok)} / {len(jobs)} 件・{size // 1024 // 1024}MB → {base}")
    for (p, _), good in zip(jobs, ok):
        if not good:
            print("取れなかった：", os.path.basename(p))


def cmd_find(run):
    groups = json.load(open(CFG + run + "_組.json", encoding="utf-8"))
    fs = sorted(f for f, _, _ in folders(run))
    jobs = [(run + string.ascii_lowercase[i], f) for i, f in enumerate(fs)]
    if len(jobs) > 26:
        sys.exit("フォルダが 26 を超えています。回を分けてください")
    tag_of = {f: t for f, t, _ in folders(run)}
    missing = sorted({tag_of[f] for _, f in jobs} - set(groups))
    if missing:
        sys.exit(f"{run}_組.json にコレクションがありません：{missing}")
    # まとめて照らし合わせる組（コレクションが多い＝長い）を先に始める
    jobs.sort(key=lambda j: -groups[tag_of[j[1]]].count("||"))

    def run_one(j):
        name, folder = j
        r = subprocess.run(
            [sys.executable, HERE + "mercari_hires.py", "find", name, f"新しい資料 {run}/{folder}", groups[tag_of[folder]]],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        print(name, folder, "OK" if r.returncode == 0 else "失敗 " + r.stderr[-300:], flush=True)

    with ThreadPoolExecutor(10) as ex:
        list(ex.map(run_one, jobs))
    print("照らし合わせ 終わり。次：それぞれ mercari_hires.py sheet <名前>")


def _crops(name):
    sys.path.insert(0, HERE)
    os.chdir(HERE)
    import mercari_hires as M
    return M, list(M.crops(name))


def cmd_dedupe(run):
    keys = {}
    for name in names(run):
        _, cs = _crops(name)
        for n, o, _ in cs:
            keys.setdefault(tuple(o["key"]), []).append((name, n))
    drop = {}
    for v in keys.values():
        for name, n in v[:-1]:
            drop.setdefault(name, []).append(n)
    for name, ns in drop.items():
        c = load(name)
        c["ok"] = [i for i in c["ok"] if i not in ns]
        c["note"] = c.get("note", "") + f" あとの名前と同じ枠なので外した：{ns}。"
        save(name, c)
        print(name, "から外した", ns)
    print("残り", sum(len(load(n).get("ok", [])) for n in names(run)), "組")


def cmd_apply(run):
    for name in names(run):
        r = subprocess.run([sys.executable, HERE + "mercari_hires.py", "apply", name], cwd=REPO, capture_output=True)
        print(name, "OK" if r.returncode == 0 else "失敗")
    print("次：python tools/crop/merge.py → python tools/crop/make_diff.py → python tools/crop/review_todo.py")


def cmd_page(run, out, label):
    """左＝新しい写真、右＝前の画像を並べ、「合っている／合っていない」を押すページを作る。
    公開は Artifact（root=<出力フォルダ>、files=img/*.jpg、capabilities {"db": {}}）。画像が 255 枚を超えたら 2 回に分けて公開する。
    結果は db の "checks"（id は a-01 など、v が "ng" のものが合っていない）"""
    from PIL import Image
    os.makedirs(out + "/img", exist_ok=True)
    out = os.path.abspath(out).replace("\\", "/")
    # merge.py の付け替え（RELABEL・MOVE）をかけた名前でも前の job を探す（ファンクラブなど、枠の名前が変わるコレクションがある）
    src = open(HERE + "merge.py", encoding="utf-8").read().splitlines()
    i = [n for n, l in enumerate(src) if l.startswith("RELABEL = ")][0]
    j = [n for n, l in enumerate(src) if l.startswith("_paths")][0]
    ns = {}
    os.chdir(HERE)
    sys.path.insert(0, HERE)
    exec("\n".join(src[i:j]), ns)
    relabel, MOVE = ns["relabel"], ns["MOVE"]
    groups = json.load(open(CFG + run + "_組.json", encoding="utf-8"))
    title = groups.get("_見出し", {})
    items = []
    for name in names(run):
        M, cs = _crops(name)
        if not cs:
            continue
        L = name[len(run):]
        folder = os.path.basename(load(name).get("folder", L))
        me, prev = "zzzzzzzzzzzzzzzzzzzzz_zz_" + name, {}
        for p in sorted(glob.glob(M.SP + "out/*.json")):
            if os.path.basename(p)[:-5] >= me:
                continue
            for e in json.load(open(p, encoding="utf-8")).get("images", []):
                m = "/".join(sorted(e["members"]))
                v = relabel(e["collection"], e["source"], e["version"])
                prev[(e["collection"], m, e["source"], e["version"])] = e
                prev[(e["collection"], m) + tuple(MOVE.get((e["collection"], e["source"], v), (e["source"], v)))] = e
        for no, (n, o, img) in enumerate(cs, 1):
            k = tuple(o["key"])
            old = Image.open(M.CARDS + prev[k]["file"]).convert("RGB")
            H = 600
            a = img.resize((round(img.width * H / img.height), H))
            b = old.resize((round(old.width * H / old.height), H))
            c = Image.new("RGB", (a.width + b.width + 16, H), (255, 255, 255))
            c.paste(a, (0, 0))
            c.paste(b, (a.width + 16, 0))
            iid = f"{L}-{no:02d}"
            c.save(f"{out}/img/{iid}.jpg", quality=82)
            items.append({"id": iid, "round": label, "group": title.get(folder, folder), "sheet": L, "no": no, "member": k[1], "source": k[2], "version": k[3],
                          "img": f"img/{iid}.jpg", "flag": n in load(name).get("flag", [])})
    html = open(HERE + "hires_review_template.html", encoding="utf-8").read()
    html = html.replace("7回目・8回目", label).replace("__ITEMS__", json.dumps(items, ensure_ascii=False))
    open(f"{out}/mikurabe_{run}.html", "w", encoding="utf-8").write(html)
    json.dump([{"path": x["img"]} for x in items], open(f"{out}/files.json", "w"))
    print(f"{len(items)} 組 → {out}/mikurabe_{run}.html（公開する画像の一覧は files.json）")


def cmd_ng(run, ids):
    by = {}
    for x in ids:
        L, no = x.split("-")
        by.setdefault(L, []).append(int(no))
    for L, nos in by.items():
        name = run + L
        c = load(name)
        # ページの番号は、公開したときの ok の順（小さい順）の何番目か
        ok = sorted(c["ok"])
        rm = [ok[n - 1] for n in nos]
        c["ok"] = [i for i in c["ok"] if i not in rm]
        c["note"] = c.get("note", "") + f" 本人の確認で {rm} はちがう（外した）。"
        save(name, c)
        subprocess.run([sys.executable, HERE + "mercari_hires.py", "apply", name], cwd=REPO, capture_output=True)
        print(name, "から外した", rm, "（apply 済み）")
    print("次：python tools/crop/merge.py → python tools/crop/make_diff.py")


def cmd_split(path):
    size = os.path.getsize(path)
    if size <= ZIP_LIMIT:
        return print(f"{size // 1024 // 1024}MB：分けなくてよい")
    z = zipfile.ZipFile(path)
    m = json.loads(z.read("manifest.json"))
    info = json.loads(z.read("info.json"))
    parts = -(-size // ZIP_LIMIT)
    step = -(-len(m) // parts)
    for i in range(parts):
        part = m[i * step:(i + 1) * step]
        out = path.replace(f"No{info['seq']}-", f"No{info['seq']}-{i + 1}of{parts}-")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as o:
            o.writestr("manifest.json", json.dumps(part, ensure_ascii=False))
            o.writestr("info.json", json.dumps(dict(info, count=len(part))))
            for e in part:
                for k in ("file", "thumb"):
                    if e.get(k):
                        o.writestr(e[k], z.read(e[k]))
        bad = zipfile.ZipFile(out).testzip()
        print(out, len(part), "枚", os.path.getsize(out) // 1024 // 1024, "MB", "壊れ：" + bad if bad else "検査 OK")
    print("2 つめからは「取り込み済み」と出るが、OK で取り込める（同じ番号のため）")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmds = {"filter": cmd_filter, "download": cmd_download, "find": cmd_find, "dedupe": cmd_dedupe, "apply": cmd_apply, "page": cmd_page, "split": cmd_split}
    if a[0] == "ng":
        cmd_ng(a[1], a[2:])
    elif a[0] in cmds:
        cmds[a[0]](*a[1:])
    else:
        sys.exit(__doc__)
