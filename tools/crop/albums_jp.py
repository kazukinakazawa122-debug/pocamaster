"""日本盤：ELEVEN -Japanese ver.- と WAVE"""
from build2 import *

G = "グッズ｜"
P = (1.2, 1.8)      # 縦長
L = (0.45, 0.85)    # 横長
S = (0.8, 1.2)      # 正方形

j = Job("jp_eleven")
C = "ELEVEN -Japanese ver.-"
D = ENG + "05 - japan eleven/"
for f, v in [("10-i盤.JPG", "I盤 type-A"), ("11-v盤.JPG", "V盤 type-B"), ("12-e盤.JPG", "E盤 type-C"), ("13-fc盤.JPG", "FC盤")]:
    sheet6(j, D + f, C, "本体封入", v)
sheet_chips(j, D + "14-id card-towerrecord.JPG", C, [("タワレコ", "IDトレカ")])
sheet_chips(j, D + "15-luckydraw-towerrecord.JPG", C, [("タワレコ", "ラキドロ")])
sheet6(j, D + "24-soundwave.JPG", C, "Soundwave", "")
sheet6(j, D + "16-flyer-towerrecord.JPG", C, G + "店舗特典", "タワレコ フライヤー")
sheet_chips(j, D + "17-hmv-bookmark.JPG", C, [(G + "店舗特典", "HMV しおり")])
sheet6(j, D + "18-tsutaya-postcard.JPG", C, G + "店舗特典", "TSUTAYA ポストカード")
sheet6(j, D + "19-rakuten-clear file.JPG", C, G + "店舗特典", "楽天 クリアファイル")
sheet6(j, D + "20-7net-sticker.JPG", C, G + "店舗特典", "7net ステッカー")
sheet(j, D + "21-amazon.JPG", C, [(G + "店舗特典", "Amazon メガジャケ")], ratio=S)
sheet6(j, D + "22-shibuya sticker.JPG", C, G + "渋谷 POP UP", "ICカードステッカー")
sheet_chips(j, D + "23-shibuya-clear coaster.JPG", C, [(G + "渋谷 POP UP", "クリアコースター")])
j.save()

j = Job("wave")
C = "WAVE"
D = ENG + "06 - japan wave/"
overview(j, D + "10-album photocard.JPG", C, [
    ((0, 99999), [("本体封入", "初回AB盤 photocard I"), ("本体封入", "初回C盤 photocard II"),
                  ("本体封入", "通常盤 photocard III"), ("本体封入", "DIVE盤 photocard IV")]),
], y_from=0.2)
sheet_chips(j, D + "15-sonymusic.JPG", C, [("Sony Music ラキドロ", "")])
sheet6(j, D + "16-全国cd特典.JPG", C, "全国CDショップ ラキドロ", "")
sheet6(j, D + "17-抽選会.JPG", C, "タワレコ", "抽選会特典")
sheet6(j, D + "18-soundwave.JPG", C, "Soundwave", "ランダム")
sheet_chips(j, D + "19-hitouch.JPG", C, [("ハイタッチ会", "A"), ("ハイタッチ会", "B")])
sheet6(j, D + "20-towerrecords.JPG", C, "タワレコ", "ランダム")
sheet6(j, D + "21-hmv.JPG", C, "HMV", "ランダム")
j.save()
