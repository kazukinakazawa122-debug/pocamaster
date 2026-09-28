"""シーズングリーティング 2022〜2024"""
from build2 import *

G = "グッズ｜"
TALL = (1.6, 2.6)

j = Job("ssgt2022")
C = "2022 SEASON'S GREETINGS [A RAY OF SUNSHINE]"
D = ENG + "07 - 2022ssgt/"
sheet6(j, D + "08-photocard.JPG", C, "本体封入", "")
sheet6(j, D + "12-starship square.JPG", C, "Starship Square", "")
sheet6(j, D + "13-synnara.JPG", C, "Synnara", "")
sheet6(j, D + "14-soundwave.JPG", C, "Soundwave", "")
sheet6(j, D + "15-soundcontents.JPG", C, "Sound Contents", "")
sheet(j, D + "09-polaroid.JPG", C, [(G + "本体封入", "Polaroid")], ratio=(0.9, 1.5))
sheet(j, D + "10-bookmark.JPG", C, [(G + "本体封入", "Bookmark")], ratio=TALL)
sheet6(j, D + "11-postcard.JPG", C, G + "本体封入", "Postcard")
j.save()

j = Job("ssgt2023")
C = "2023 SEASON'S GREETINGS [Ready, Get Set, IVE!]"
D = ENG + "08 - 2023ssgt/"
sheet6(j, D + "09-box photocard.JPG", C, "本体封入", "")
sheet6(j, D + "16-sw photocard.JPG", C, "Soundwave", "")
sheet6(j, D + "13-starship.JPG", C, "Starship Square", "", template=D + "15-synnara.JPG")
sheet6(j, D + "14-ktown4u.JPG", C, "Ktown4U", "", template=D + "15-synnara.JPG")
sheet6(j, D + "15-synnara.JPG", C, "Synnara", "")
sheet6(j, D + "10-id photo.JPG", C, G + "本体封入", "ID Photo")
sheet6(j, D + "11-club application.JPG", C, G + "本体封入", "Club Application")
sheet(j, D + "12-poster calendar.JPG", C, [(G + "本体封入", "Mini Poster Calendar 1"), (G + "本体封入", "Mini Poster Calendar 2")], ratio=(1.0, 1.6))
sheet6(j, D + "17-sw postcard.JPG", C, G + "Soundwave", "Postcard")
j.save()

j = Job("ssgt2024")
C = "2024 SEASON'S GREETINGS [A Fairy's Wish]"
D = ENG + "2024ssgt/"
sheet6(j, D + "IMG_4437.JPG", C, "本体封入", "フォトカードセット")
sheet6(j, D + "IMG_4439.JPG", C, "Soundwave", "", template=D + "IMG_4441.JPG")
sheet6(j, D + "IMG_4441.JPG", C, "Starship Square", "")
sheet6(j, D + "IMG_4443.JPG", C, "Ktown4U", "")
sheet6(j, D + "IMG_4445.JPG", C, "Apple Music", "", template=D + "IMG_4441.JPG")
sheet(j, D + "IMG_4447.JPG", C, [(G + "本体封入", "Postcard")],
      members=[["全員"], ["ガウル"], ["ユジン"], ["レイ"], ["ウォニョン"], ["リズ"], ["イソ"]])
sheet(j, D + "IMG_4449.JPG", C, [(G + "本体封入", "Fairy Wish Card")], ratio=TALL)
j.save()
