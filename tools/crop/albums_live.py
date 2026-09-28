"""ファンコン The Prom Queens と 1st WORLD TOUR"""
from build2 import *

G = "グッズ｜"
P = 295.0

j = Job("fancon")
C = "1st FAN CONCERT 'The Prom Queens'"
path = ENG + "09 - fancon/07-all.JPG"
im = grid.load(path)
L = [435 + 213.2 * k for k in range(6)]
R = [1932 + 213.2 * k for k in range(6)]
print("fancon cols", [int(x) for x in L], [int(x) for x in R])
fixed_grid(j, path, C, L, [345 + P * i for i in range(10)], [
    ("MD", "Photocard Deco Set"), ("MD", "Photocard Binder"), ("MD", "PVC Card Holder"),
    ("Random Photocard Pack (KOREA)", "1"), ("Random Photocard Pack (KOREA)", "2"), ("Random Photocard Pack (KOREA)", "3"),
    ("Random Photocard Pack (KOREA)", "4"), ("Random Photocard Pack (KOREA)", "5"),
    ("Random Trading Card (JAPAN)", "1"), ("Random Trading Card (JAPAN)", "2")], 272)
fixed_grid(j, path, C, R, [345 + P * i for i in range(8)], [
    (G + "MD", "Postcard"), (G + "MD", "Ticket"), (G + "MD", "Poster"),
    ("1st DIVE FC Class DIVE", "1"), ("1st DIVE FC Class DIVE", "2"),
    ("SuperStar STARSHIP", "1"), ("SuperStar STARSHIP", "2"), ("SuperStar STARSHIP", "3")], 272)
j.save()

j = Job("tour1")
C = "1st WORLD TOUR 'SHOW WHAT I HAVE'"
path = ENG + "world tour/07-all.JPG"
im = grid.load(path)
L = [376 + 213.0 * k for k in range(6)]
R = [1874 + 213.0 * k for k in range(6)]
print("tour cols", [int(x) for x in L], [int(x) for x in R])
c0 = 442.0
fixed_grid(j, path, C, L, [c0 + P * i for i in range(13)], [
    ("MD", "Photo Kit"), ("MD", "Photocard Binder"), ("MD", "Photocard Holder"), ("MD", "Cross Bag"), ("MD", "Necklace"),
    ("Random Photocard", "1"), ("Random Photocard", "2"), ("Random Photocard", "3"), ("Random Photocard", "4"),
    ("Japan Random Photocard", "1"), ("Japan Random Photocard", "2"),
    ("2nd DIVE FC Class DIVE", "1"), ("2nd DIVE FC Class DIVE", "2")], 272)
fixed_grid(j, path, C, R, [c0 + P * i for i in range(13)], [
    (G + "MD", "Postcard"), (G + "MD", "ID Photo"), (G + "MD", "Mini Poster 1"), (G + "MD", "Mini Poster 2"), (G + "MD", "Sticker"),
    None, None, None, None,
    ("SuperStar STARSHIP", "1"), ("SuperStar STARSHIP", "2"), ("SuperStar STARSHIP", "3"), ("SuperStar STARSHIP", "4")], 272)
j.save()
