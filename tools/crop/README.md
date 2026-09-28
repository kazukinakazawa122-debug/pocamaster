# カード画像の切り出しツール

ファンが作ったフォトカード一覧表（`C:\Users\kazuk\OneDrive\pocamaster-images\`、Git には入れない）から
カードを 1 枚ずつ切り出し、アプリに取り込む ZIP を作る。

## 流れ
1. `albums_*.py` を実行 → `pocamaster-images/_cards/<名前>/` に画像、`out/<名前>.json` に枠と画像の対応
2. `merge.py` を実行 → `public/seed/cards.csv`（枠）を更新し、`pocamaster-images/pocamaster-images.zip` を作る
3. アプリの「設定 → 画像をまとめて取り込む（ZIP）」で読み込む

## ファイル
| ファイル | 内容 |
|---|---|
| grid.py | カードの位置を見つける基本処理 |
| build2.py | 切り出し方（全体表・6 人分の表・名前の札・型を使う） |
| memlist.py | メンバー別リストのカードを読む順に並べる |
| albums_*.py | コレクションごとの設定（どの表のどの位置がどのカードか） |
| merge.py | すべてをまとめて cards.csv と ZIP を作る |
| check.py / check2.py | 切り出し結果の確認用シート |
| inventory.py | 手元の資料の一覧と大きさを `out/sources.csv` に書き出す（画質のよい資料を探す用） |
| cardsize.py | 資料ごとにカード 1 枚の横幅を調べて `out/cardsizes.csv` に、いまの切り出し画像の横幅を `out/cropsizes.csv` に書き出す |

## 既知の問題
- グッズ・ステッカーの切り出しがずれているものがある（未修正）。今は `merge.py` の `GOODS = False` で cards.csv と ZIP から外している

必要なもの：Python 3、Pillow、numpy、scipy
