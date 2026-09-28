"""NON ALBUM・ファンクラブ・その他"""
from build2 import *

G = "グッズ｜"
L = (0.45, 0.9)
WY, LS = "ウォニョン", "イソ"
D = ENG

j = Job("pepsi")
C = "Pepsi × IVE 'BLUE & BLACK'"
for f, rnd, mem in [("07-r1 wonyoung", "Round 1", WY), ("08-r1 leeseo", "Round 1", LS), ("09-r2 wonyoung", "Round 2", WY), ("10-r2 leeseo", "Round 2", LS)]:
    sheet_items(j, D + f"11 - pepsi/{f}.JPG", C, [([mem], rnd, "A"), ([mem], rnd, "B")])
sheet_items(j, D + "11 - pepsi/05-r1.JPG", C, [([WY, LS], "Round 1", "GROUP")], ratio=L)
sheet_items(j, D + "11 - pepsi/06-r2.JPG", C, [([WY, LS], "Round 2", "GROUP")], ratio=L)
j.save()

j = Job("fanclub")
C = "DIVE Official Fanclub｜ファンクラブ"
sheet6(j, D + "10 - 1st fanclub/02-photocard.JPG", C, "DIVE 1期 会員キット", "")
sheet6(j, D + "10 - 1st fanclub/03-poster.JPG", C, G + "DIVE 1期 会員キット", "Mini Poster")
sheet6(j, D + "10 - 1st fanclub/10-jp fc.JPG", C, "IVE JAPAN FC 早期入会特典", "")
sheet_chips(j, D + "2nd fanclub/IMG_0584.JPG", C, [("DIVE 2期 'MAGAZINE IVE'", "")])
sheet_chips(j, D + "2nd fanclub/IMG_0596.JPG", C, [(G + "DIVE 2期 'MAGAZINE IVE'", "Postcard")])
sheet_chips(j, D + "2nd fanclub/IMG_0600.JPG", C, [(G + "DIVE 2期 'MAGAZINE IVE'", "Mini Poster")])
j.save()

j = Job("magazine")
C = "Magazine｜雑誌特典"
sheet6(j, D + "12 - scawaii/02-photocard.JPG", C, "S Cawaii! 主婦の友 特典B トレカ", "")
sheet6(j, D + "12 - scawaii/01-postcard.JPG", C, G + "S Cawaii!", "主婦の友 特典A ポストカード")
sheet6(j, D + "12 - scawaii/03-bromide.JPG", C, G + "S Cawaii!", "タワレコ 特典C ブロマイド")
sheet6(j, D + "13 - other/vivi.JPG", C, "ViVi セブンネット特典", "")
j.save()

j = Job("broadcast")
C = "Music Show & Broadcast｜音楽番組・公開放送"
sheet6(j, D + "13 - other/mbc open broadcast.JPG", C, "MBC 音楽中心 公開放送", "")
sheet6(j, D + "13 - other/sbs open broadcast.JPG", C, "SBS 歌謡大祭典 公開放送", "")
j.save()

j = Job("collab")
C = "Collab & Event｜コラボ・イベント"
sheet6(j, D + "13 - other/unikon.JPG", C, "UNI-KON", "")
V = "V Coloring イベント特典"
sheet_items(j, D + "13 - other/vcoloring.JPG", C, [([m], V, "") for m in ORDER] +
            [(["イソ", "ユジン"], V, "ユニット"), (["ウォニョン", "ガウル"], V, "ユニット"), (["リズ", "レイ"], V, "ユニット")])
j.save()

j = Job("misc_eleven")
sheet6(j, D + "13 - other/お見送り会.JPG", "ELEVEN -Japanese ver.-", "お見送り会 CD購入特典", "")
O = G + "Official MD"
sheet_items(j, D + "13 - other/postcard.JPG", "ELEVEN", [
    (["ガウル"], O, "スクエアポストカード"), (["ユジン"], O, "スクエアポストカード"), (["レイ"], O, "スクエアポストカード"), (["全員"], O, "スクエアポストカード 1"),
    (["ウォニョン"], O, "スクエアポストカード"), (["リズ"], O, "スクエアポストカード"), (["イソ"], O, "スクエアポストカード"), (["全員"], O, "スクエアポストカード 2")],
    ratio=(0.7, 1.3))
j.save()
