"""cards.csv・collections.csv に、枠・コレクションごとの固定の ID（id 列）を足す（2026-10-03、本人了承。アプリの改善 44.【1】）
名前・番号を直しても「同じ枠」とわかるようにするための ID。いまの行にまだ ID がないものにだけ、重ならない 8 文字の ID を付ける（一度付けたら変えない）。
merge.py は id 列を引き継ぎ、新しい枠には新しい ID を付ける。名前を直すときは、行ごと直す（ID の列は触らない）"""
import csv, io, os, sys, uuid

SEED = os.path.dirname(os.path.abspath(__file__)) + "/../../public/seed/"
sys.stdout.reconfigure(encoding="utf-8")


def q(s):
    return '"' + s.replace('"', '""') + '"' if any(c in s for c in ',"') else s


def run(name):
    path = SEED + name
    rows = list(csv.reader(io.StringIO(open(path, encoding="utf-8").read())))
    header, body = rows[0], rows[1:]
    if "id" not in header:
        header.append("id")
        body = [r + [""] for r in body]
    i = header.index("id")
    used = {r[i] for r in body if r[i]}
    n = 0
    for r in body:
        if not r[i]:
            while True:
                x = uuid.uuid4().hex[:8]
                if x not in used:
                    break
            r[i] = x
            used.add(x)
            n += 1
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(",".join(header) + "\n")
        for r in body:
            f.write(",".join(q(x) for x in r) + "\n")
    print(name, len(body), "行、新しく ID を付けた", n)


if __name__ == "__main__":
    run("collections.csv")
    run("cards.csv")
