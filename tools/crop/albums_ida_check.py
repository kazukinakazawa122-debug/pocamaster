"""本人が確認ページで「ない」とした @idalshiro の表のカード（メンバー別）を、ラベルに合わせて入れる（2026-09-30〜）

- 確認ページ：public/_review/<メンバー>.html（Git には入れない）。「ない」の番号は review_<メンバー>.json に書く
- 番号 → (コレクション, 入手元, バージョン, 扱い) はラベル（表の見出しのアルバム名・カードの下の文字）を目で読んで決めた
  - "have"：アプリに同じ枠がある。そのメンバーの枠に画像がなければ、この画像を入れる
  - "new"：アプリにない種類。6 人分の枠を足し、画像はそのメンバーの分だけ
  - "skip"：入れない（ユニットのカードで相手がわからない・すでにユニットの枠がある など）
- @idalshiro の 3 ページ目（日本盤）は作者が全部に「BOYCOTT!」の印を押しているので、画像は使わない（枠だけ）
- StarRiver は店の透かしがあるので画像は使わない（今までと同じ）
- ラベルの略語：SW=Soundwave、WM=withmuu、LD=ラキドロ、MKS=Makestar、SR=StarRiver、APPMU=Apple Music、YZY=Yizhiyu、
  KMS=KMStation、SSQ=Starship Square。グループのラベル（例「SOUNDWAVE LD 3」が 5 枚）は、表の左から 1, 2, 3… と番号をつけた
"""
import csv, glob, io, json, os
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/"
MEMBERS = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
SW, WM, SWL, WML = "Soundwave", "withmuu", "Soundwave ラキドロ", "withmuu ラキドロ"
H, N, X = "have", "new", "skip"

# イソ（review_leeseo.json の番号 → ラベル）
LEESEO = {
    4: ("ELEVEN", "POB", "ID Card", H),
    9: ("ELEVEN", "Fansign Special", "", H),  # 前は LOVE DIVE にしていた（まちがい。表の「FANSIGN EXCL」は ELEVEN）
    10: ("ELEVEN", "Fansign Special", "2", N),
    13: ("LOVE DIVE", WML, "1.0-1", H),
    16: ("LOVE DIVE", "Fansign", "", N),
    17: ("LOVE DIVE", "Tower Records", "2 POLA", H),
    18: ("After LIKE", "本体封入", "ver.2", H),
    20: ("After LIKE", "Jewel ver. POB", "6+3set", H),
    23: ("After LIKE", WML, "2.0-2", H),
    24: ("After LIKE", SWL, "2.0-2", H),
    26: ("After LIKE", "Tower Records", "2", H),
    27: ("After LIKE", "TOU", "WINNER", N),
    30: ("After LIKE", "Broadcast", "After ver.", H),
    31: ("After LIKE", "Broadcast", "3", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    33: ("I've IVE", "Vinyl", "", N),
    34: ("I've IVE", "US Exclusive", "", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    37: ("I've IVE", "Naver Live", "", X),  # 何人かのカード → GROUPS
    38: ("I've IVE", "Naver Live", "2", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    43: ("I've MINE", "Broadcast", "Baddie", X),  # 何人かのカード → GROUPS
    45: ("I've MINE", "Starship Square", "PB LOVED IVE", H),
    46: ("I've MINE", "KMStation", "1.0", H),
    52: ("I've MINE", SWL, "3-2", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    53: ("I've MINE", SWL, "3-3", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    56: ("I've MINE", "withmuu", "4.0", H),
    57: ("I've MINE", "Soundwave ファンサイン", "Singapore", N),
    61: ("I've MINE", "Soundwave ファンサイン", "Malaysia", N),
    62: ("I've MINE", "Sony Music Japan", "2-1", N),
    63: ("I've MINE", "Sony Music Japan", "2-2", N),
    64: ("I've MINE", "Sony Music Japan", "2-4", N),
    65: ("I've MINE", "Sony Music Japan", "2-5", N),
    66: ("I've MINE", "A!SMART ファンサイン", "", N),
    69: ("I've MINE", "Yizhiyu", "3.0", N),
    68: ("IVE SWITCH", "本体封入", "SPIN-OFF", H),
    70: ("IVE SWITCH", "Tower Records", "2", N),
    72: ("IVE SWITCH", SWL, "2.0 POLA", H),  # 表の「SOUNDWAVE LD」3 枚目（ポラ）。表の LD 1〜5 のポラ ＝ アプリの 2.0・4.0・6.0・9.0・11.0 POLA
    73: ("IVE SWITCH", WML, "1.0-2", H),
    74: ("IVE SWITCH", WML, "1.0-3", N),
    76: ("IVE SWITCH", SWL, "4.0 POLA", H),  # 表の「SOUNDWAVE LD 2」3 枚目
    77: ("IVE SWITCH", WML, "3.0-3", N),
    79: ("IVE SWITCH", WML, "4.0-3", N),
    81: ("IVE SWITCH", "Makestar ラキドロ", "4.0 POLA", H),  # 表の「MAKESTAR LD」3 枚目
    83: ("IVE SWITCH", WML, "4.0（2 組目）-3", N),  # 表のラベルも「WITHMUU LD 4」（2 回目）
    84: ("IVE SWITCH", SWL, "3.0-1", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    85: ("IVE SWITCH", SWL, "3.0-2", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    86: ("IVE SWITCH", SWL, "3.0-3", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    87: ("IVE SWITCH", SWL, "3.0-4", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    88: ("IVE SWITCH", SWL, "6.0 POLA", H),  # 表の「SOUNDWAVE LD 3」の 1 人のポラ（2 人のカードはアプリの 6.0）
    90: ("IVE SWITCH", SWL, "9.0 POLA", H),  # 表の「SOUNDWAVE LD 4」3 枚目
    91: ("IVE SWITCH", "TOKYO DOME 限定", "9/4", X),  # 2 人のカード。ユニットの枠がある
    92: ("IVE SWITCH", "TOKYO DOME 限定", "9/5", X),
    93: ("IVE SWITCH", SWL, "11.0 POLA", H),  # 表の「SOUNDWAVE LD 5」3 枚目
    94: ("IVE SWITCH", "Yizhiyu ファンサイン", "2.0", H),
    96: ("IVE EMPATHY", "MD", "", H),
    97: ("IVE EMPATHY", "Starship Square", "3TYPE 1", H),
    106: ("IVE EMPATHY", "StarRiver", "1.0", H),
    111: ("IVE EMPATHY", "StarRiver", "2.0", H),
    112: ("IVE EMPATHY", "Makestar", "2.0", H),
    113: ("IVE EMPATHY", "withmuu", "2.0 Live Studio Choom", H),
    114: ("IVE EMPATHY", "Makestar", "3.0", H),
    121: ("IVE EMPATHY", SWL, "2.0-2", N),
    122: ("IVE EMPATHY", "オフラインイベント", "TOKYO 2", N),
    124: ("IVE EMPATHY", "StarRiver", "2.0（2 枚目）", N),
    125: ("IVE EMPATHY", "Soundwave", "4.0（2 枚目）", N),
    126: ("IVE EMPATHY", "K-MONSTAR", "Taiwan POLA", H),
    127: ("IVE EMPATHY", "Makestar", "4.0 Shanghai", H),
    128: ("IVE EMPATHY", "Makestar", "4.0 Shanghai 3", N),
    129: ("IVE SECRET", "MD", "", H),
    131: ("IVE SECRET", "Starship Square", "Digipack", H),
    134: ("IVE SECRET", "Apple Music", "1.0", H),
    136: ("IVE SECRET", "Tower Records", "Shibuya", H),
    137: ("IVE SECRET", "Sony Music", "B", H),
    138: ("IVE SECRET", "Mukor", "", N),
    139: ("IVE SECRET", "OLIVE YOUNG ラキドロ", "", H),
    144: ("IVE SECRET", "MusicArt", "", H),
    145: ("IVE SECRET", "Makestar", "3.0", H),
    146: ("IVE SECRET", "オフラインイベント", "9.23 TOKYO", H),
    147: ("IVE SECRET", "QQ Music", "1", H),
    148: ("IVE SECRET", "QQ Music", "2", H),
    149: ("IVE SECRET", "QQ Music", "3", H),
    150: ("IVE SECRET", "QQ Music", "4", H),
    152: ("IVE SECRET", WML, "2.0", H),
    153: ("IVE SECRET", WML, "2.0 POLA", H),
    157: ("IVE SECRET", "Shanghai", "WINNER", N),
    159: ("IVE SECRET", "KMONSTAR", "2.0", H),
    163: ("IVE SECRET", WML, "9.0-2", H),  # 前は新しい枠 5.0-2 にしていた（まちがい。表の「WITHMUU LD 5」はアプリの 9.0）
    164: ("IVE SECRET", "QQ Music × Starship Square", "Christmas", N),
    165: ("IVE SECRET", "IDOLSHOP", "", H),
    167: ("IVE SECRET", WML, "4.0-3", N),
    173: ("REVIVE+", "本体封入", "MINI MINI", H),
    175: ("REVIVE+", "Mukor", "", N),
    180: ("REVIVE+", "QQ Music", "Member set 2", N),
    181: ("REVIVE+", "QQ Music", "2.0 ランダム 1", N),
    182: ("REVIVE+", "QQ Music", "2.0 ランダム 2", N),
    183: ("REVIVE+", "QQ Music", "2.0 ランダム 3", N),
    184: ("REVIVE+", "QQ Music", "2.0 ランダム 4", N),
    185: ("REVIVE+", "QQ Music", "2.0 ランダム 5", N),
    186: ("REVIVE+", "QQ Music", "2.0 ランダム 6", N),
    189: ("REVIVE+", SWL, "2.0", H),
    190: ("REVIVE+", "MusicArt ラキドロ", "2.0 POLA", H),
    194: ("REVIVE+", "KMONSTAR", "1.0", H),
    # 3 ページ目（日本盤）：画像は使わない
    198: ("ALIVE", "A!SMART", "ユニット 1", X),  # 2 人のカード。相手を顔で決めることになるので入れない
    199: ("ALIVE", "A!SMART", "ユニット 2", X),
    201: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット 1", X),
    202: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット 2", X),
    203: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 1", X),
    204: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 2", X),
    205: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # ユニットの枠がある
    206: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),
    207: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),
    208: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),
    209: ("Be Alright", "Sony Music ラキドロ", "", H),
    211: ("Be Alright", "オフラインイベント", "9.23 TOKYO", H),
    212: ("Be Alright", "オフラインイベント", "9.24 OSAKA", H),
    213: ("Be Alright", "オフラインイベント", "10.12 TOKYO", H),
    214: ("Be Alright", "オフラインイベント", "10.13 OSAKA", H),
    216: ("LUCID DREAM", "本体封入", "期間生産限定盤", H),
    217: ("LUCID DREAM", "本体封入", "DIVE 盤", N),
    218: ("LUCID DREAM", "タワレコ", "B", H),
    220: ("LUCID DREAM", "SWIA OSAKA exclusive", "4.19", X),  # 2 人のカード。ユニットの枠がある
}

# リズ（review_liz.json の番号 → ラベル）。表の並びはイソと同じなので、同じ位置はイソと同じラベル
LIZ = {
    9: ("LOVE DIVE", "Makestar", "2.0", N),
    12: ("ELEVEN", "Fansign Special", "", H),
    13: ("ELEVEN", "Fansign Special", "2", N),
    23: ("LOVE DIVE", "Fansign", "", N),
    27: ("After LIKE", WML, "2.0-2", H),
    28: ("After LIKE", "本体封入", "ver.1", H),
    29: ("After LIKE", "Tower Records", "2", H),
    30: ("After LIKE", "TOU", "WINNER", N),
    31: ("After LIKE", "Broadcast", "After ver.", H),
    32: ("After LIKE", "Broadcast", "グループ 2", X),  # 何人かのカード（枠はある）
    35: ("I've IVE", "Vinyl", "", N),
    36: ("I've IVE", "US Exclusive", "", X),  # 何人かのカード（メンバーが確かめられない）
    37: ("I've IVE", "Namil Music", "", H),
    40: ("I've IVE", "Tower Records", "2", H),
    41: ("I've IVE", "Naver Live", "", X),  # ユジン・リズ＋もう 1 人（確かめられない）
    42: ("I've IVE", "Naver Live", "グループ 2", X),  # 枠はある
    44: ("I've IVE", "Fansign", "", N),
    46: ("I've MINE", "Broadcast", "グループ 1", X),  # 枠はある
    49: ("I've MINE", "Starship Square", "PB LOVED IVE", H),
    50: ("I've MINE", "Namil Music", "1.0", H),
    54: ("I've MINE", "Tower Records", "1.0", H),
    57: ("I've MINE", "KMStation", "2.0", H),
    63: ("I've MINE", SWL, "3 ユニット 1", X),  # 枠はある（リズ・イソ）
    64: ("I've MINE", SWL, "3 ユニット 2", X),  # 枠はある（リズ・イソ）
    72: ("I've MINE", "Soundwave ファンサイン", "Singapore", N),
    74: ("I've MINE", "Soundwave", "8.0 Daegu", H),
    76: ("I've MINE", "Soundwave ファンサイン", "Malaysia", N),
    77: ("I've MINE", "Sony Music Japan", "2-1", N),
    78: ("I've MINE", "Sony Music Japan", "2-2", N),
    79: ("I've MINE", "Sony Music Japan", "2-3", N),
    80: ("I've MINE", "Sony Music Japan", "2-4", N),
    81: ("I've MINE", "Sony Music Japan", "2-5", N),
    82: ("I've MINE", "A!SMART ファンサイン", "", N),
    83: ("I've MINE", "Taiwan", "2", N),  # 表に「TAIWAN（sw fansign）」が 2 か所ある。2 つ目
    92: ("I've MINE", "Yizhiyu", "3.0", N),
    84: ("IVE SWITCH", "本体封入", "Lenticular", H),
    95: ("IVE SWITCH", "Tower Records", "2", N),
    98: ("IVE SWITCH", SWL, "2.0 POLA", H),
    99: ("IVE SWITCH", WML, "1.0-1", H),
    101: ("IVE SWITCH", WML, "1.0-3", N),
    104: ("IVE SWITCH", SWL, "4.0 POLA", H),
    105: ("IVE SWITCH", WML, "3.0-3", N),
    111: ("IVE SWITCH", "Makestar ラキドロ", "4.0 POLA", H),
    112: ("IVE SWITCH", WML, "4.0-3", N),
    113: ("IVE SWITCH", WML, "4.0（2 組目）-3", N),
    114: ("IVE SWITCH", SWL, "6.0", X),  # 2 人のカード → GROUPS
    115: ("IVE SWITCH", SWL, "6.0", X),  # 2 人のカード → GROUPS
    116: ("IVE SWITCH", SWL, "6.0", X),  # 2 人のカード → GROUPS
    117: ("IVE SWITCH", SWL, "6.0", X),  # 枠はある（リズ・イソ）
    118: ("IVE SWITCH", SWL, "6.0 POLA", H),
    121: ("IVE SWITCH", SWL, "9.0 POLA", H),
    122: ("IVE SWITCH", "Japan ファンサイン", "Tokyo", H),  # 表の「TOKYO 19.08」
    123: ("IVE SWITCH", "TOKYO DOME 限定", "9/4", X),  # 2 人のカード → GROUPS
    124: ("IVE SWITCH", "TOKYO DOME 限定", "9/5", X),  # 2 人のカード → GROUPS
    129: ("IVE SWITCH", "StarRiver ファンサイン", "3.0", N),
    135: ("IVE EMPATHY", "StarRiver", "1.0", H),
    138: ("IVE EMPATHY", "StarRiver", "2.0", H),
    140: ("IVE EMPATHY", SWL, "2.0", H),
    148: ("IVE EMPATHY", WML, "5.0 POLA", H),
    149: ("IVE EMPATHY", SWL, "2.0-1", N),
    150: ("IVE EMPATHY", SWL, "2.0-2", N),
    153: ("IVE EMPATHY", "オフラインイベント", "TOKYO 2", N),
    155: ("IVE EMPATHY", "StarRiver", "2.0（2 枚目）", N),
    156: ("IVE EMPATHY", "Soundwave", "4.0（2 枚目）", N),
    159: ("IVE EMPATHY", "Makestar", "4.0 Shanghai カフェ店長 ver.", H),
    160: ("IVE EMPATHY", "Makestar", "4.0 Shanghai 3", N),
    161: ("IVE EMPATHY", "Broadcast", "1.0", H),
    162: ("IVE SECRET", "MD", "", H),
    170: ("IVE SECRET", "StarRiver", "", H),
    171: ("IVE SECRET", "hellolive", "1.0", H),
    174: ("IVE SECRET", "MusicArt", "", H),
    176: ("IVE SECRET", "QQ Music", "1", H),
    177: ("IVE SECRET", "QQ Music", "2", H),
    187: ("IVE SECRET", "QQ Music", "3", H),
    181: ("IVE SECRET", "QQ Music", "4", H),
    179: ("IVE SECRET", SWL, "2.0", H),  # 表の「SOUNDWAVE LD 2（show what i am）」1 枚目
    180: ("IVE SECRET", SWL, "6.0", H),  # 表の「SOUNDWAVE LD 3」1 枚目
    184: ("IVE SECRET", "Shanghai", "WINNER", N),
    185: ("IVE SECRET", "hellolive", "2.0", H),
    186: ("IVE SECRET", "KMONSTAR", "2.0", H),
    188: ("IVE SECRET", "Yetimall ラキドロ", "-1", H),
    189: ("IVE SECRET", "QQ Music × Starship Square", "Christmas", N),
    192: ("IVE SECRET", WML, "4.0-3", N),
    193: ("IVE SECRET", "Yetimall ラキドロ", "POLA", H),
    194: ("IVE SECRET", "Apple Music ラキドロ", "5.0 POLA", H),
    195: ("IVE SECRET", WML, "9.0-2", H),
    199: ("REVIVE+", "本体封入", "MINI MINI", H),
    207: ("REVIVE+", WML, "3.0", H),
    208: ("REVIVE+", "QQ Music", "Membership", H),
    209: ("REVIVE+", "QQ Music", "Member set 2", N),
    210: ("REVIVE+", "QQ Music", "2.0 ランダム 1", N),
    211: ("REVIVE+", "QQ Music", "2.0 ランダム 2", N),
    212: ("REVIVE+", "QQ Music", "2.0 ランダム 3", N),
    213: ("REVIVE+", "QQ Music", "2.0 ランダム 4", N),
    214: ("REVIVE+", "QQ Music", "2.0 ランダム 5", N),
    215: ("REVIVE+", "QQ Music", "2.0 ランダム 6", N),
    217: ("REVIVE+", "QQ Music", "POP-UP", H),
    223: ("REVIVE+", "KMStation", "2.0", H),
    226: ("REVIVE+", "KMONSTAR", "1.0", H),
    230: ("ALIVE", "A!SMART", "ユニット 1", X),  # 2 人のカード。相手がわからない
    231: ("ALIVE", "A!SMART", "ユニット 2", X),  # 2 人のカード。相手がわからない
    234: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット", X),  # 2 人のカード。相手がわからない
    235: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット", X),  # 2 人のカード。相手がわからない
    236: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 1", X),  # → GROUPS
    237: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 2", X),  # → GROUPS
    238: ("ALIVE", "本体封入", "会場限定盤", N),
    239: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # → GROUPS（枠はある）
    240: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # → GROUPS（枠はある）
    241: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),  # → GROUPS（枠はある）
    242: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),  # → GROUPS（枠はある）
    245: ("Be Alright", "Tower Records", "B", H),
    246: ("Be Alright", "Sony Music ラキドロ", "", H),
    247: ("Be Alright", "A!SMART", "A", H),
    249: ("Be Alright", "オフラインイベント", "9.23 TOKYO", H),
    250: ("Be Alright", "オフラインイベント", "9.24 OSAKA", H),
    251: ("LUCID DREAM", "A!SMART", "A", H),
    255: ("Be Alright", "オフラインイベント", "10.13 OSAKA", H),
}

# ウォニョン（review_wonyoung.json の番号 → ラベル）。表の並びはイソ・リズと同じなので、同じ位置のラベルを使った（# のあとは元の番号）。
# 残りはラベルを目で読み、イソ・リズの表の同じ位置のカードがアプリのどの枠かを画像で確かめた
WONYOUNG = {
    0: ("ELEVEN", "本体封入", "ver.2", H),
    3: ("ELEVEN", "Tower Records", "", H),
    4: ("ELEVEN", SW, "3.0", H),
    5: ("ELEVEN", SWL, "2.0 POLA", H),
    7: ("ELEVEN", "Yizhiyu", "1.0", H),
    8: ("ELEVEN", "Fansign Special", "", H),  # 表の「FANSIGN EXCL」は ELEVEN（LOVE DIVE の見出しより左、衣装も ELEVEN）
    11: ("ELEVEN", "Fansign Special", "2", N),
    14: ("LOVE DIVE", WML, "1.0 POLA", H),
    16: ("LOVE DIVE", "Fansign", "", N),  # leeseo 16
    17: ("LOVE DIVE", "Tower Records", "2 POLA", H),  # leeseo 17
    18: ("After LIKE", "Ktown4U", "", H),
    20: ("After LIKE", WML, "2.0-2", H),  # leeseo 23
    21: ("After LIKE", "TOU", "1.0", H),
    22: ("After LIKE", "Tower Records", "2", H),  # leeseo 26
    23: ("After LIKE", "Broadcast", "3", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    24: ("After LIKE", "TOU", "WINNER", N),  # leeseo 27
    25: ("I've IVE", "Vinyl", "", N),  # leeseo 33
    26: ("I've IVE", "US Exclusive", "", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    32: ("I've IVE", "Naver Live", "", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    33: ("I've IVE", "Naver Live", "2", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    34: ("I've MINE", "Broadcast", "Baddie", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    35: ("I've MINE", "Starship Square", "PB LOVED IVE", H),  # leeseo 45
    36: ("I've MINE", "Namil Music", "1.0", H),  # liz 50
    44: ("I've MINE", SWL, "3-2", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    45: ("I've MINE", SWL, "3-3", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    48: ("I've MINE", "Soundwave ファンサイン", "Singapore", N),  # leeseo 57
    49: ("I've MINE", SW, "8.0 Daegu", H),  # liz 74
    50: ("I've MINE", "mymusictaste", "3.0", H),
    51: ("I've MINE", "Soundwave ファンサイン", "Malaysia", N),  # leeseo 61
    52: ("I've MINE", "Sony Music Japan", "2-1", N),  # leeseo 62
    53: ("I've MINE", "Sony Music Japan", "2-2", N),  # leeseo 63
    54: ("I've MINE", "Sony Music Japan", "2-4", N),  # leeseo 64
    55: ("I've MINE", "Sony Music Japan", "2-5", N),  # leeseo 65
    56: ("I've MINE", "A!SMART ファンサイン", "", N),  # leeseo 66
    57: ("I've MINE", "Taiwan", "2", N),  # liz 83
    59: ("I've MINE", "Yizhiyu", "3.0", N),  # liz 92
    64: ("IVE SWITCH", "Apple Music", "", H),
    68: ("IVE SWITCH", "Tower Records", "2", N),  # leeseo 70
    69: ("IVE SWITCH", "StarRiver", "", H),
    71: ("IVE SWITCH", "Apple Music ファンサイン", "1.0", H),
    72: ("IVE SWITCH", SWL, "2.0 POLA", H),  # leeseo 72
    73: ("IVE SWITCH", WML, "1.0-3", N),  # leeseo 74
    74: ("IVE SWITCH", "Makestar ファンサイン", "2.0", H),
    75: ("IVE SWITCH", SWL, "4.0 POLA", H),  # leeseo 76
    76: ("IVE SWITCH", WML, "3.0-3", N),  # leeseo 77
    77: ("IVE SWITCH", "Apple Music ファンサイン", "2.0", H),
    78: ("IVE SWITCH", "Makestar ラキドロ", "4.0 POLA", H),  # leeseo 81
    79: ("IVE SWITCH", WML, "4.0（2 組目）-3", N),  # liz 113
    80: ("IVE SWITCH", SWL, "3.0-1", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    81: ("IVE SWITCH", SWL, "3.0-2", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    82: ("IVE SWITCH", SWL, "3.0-3", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    83: ("IVE SWITCH", SWL, "3.0-4", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    84: ("IVE SWITCH", SWL, "6.0 POLA", H),  # leeseo 88
    85: ("IVE SWITCH", SWL, "9.0 POLA", H),  # leeseo 90
    86: ("IVE SWITCH", "TOKYO DOME 限定", "9/4", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    87: ("IVE SWITCH", "TOKYO DOME 限定", "9/5", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    88: ("IVE SWITCH", SWL, "11.0 POLA", H),  # leeseo 93
    90: ("IVE SWITCH", "Broadcast", "2週目", H),
    92: ("IVE EMPATHY", "Starship Square", "LOVED IVE", H),
    93: ("IVE EMPATHY", "Starship Square", "4TYPE", H),
    96: ("IVE EMPATHY", "StarRiver", "1.0", H),  # leeseo 106
    98: ("IVE EMPATHY", WML, "3.0 POLA", H),
    100: ("IVE EMPATHY", "StarRiver", "2.0", H),  # leeseo 111
    101: ("IVE EMPATHY", WM, "2.0 Live Studio Choom", H),  # leeseo 113
    106: ("IVE EMPATHY", "Apple Music", "4.0", H),
    108: ("IVE EMPATHY", "オフラインイベント", "TOKYO 2", N),  # leeseo 122
    112: ("IVE EMPATHY", "IDOUSTAGE", "2.0", H),
    113: ("IVE EMPATHY", "Makestar", "4.0 Shanghai 3", N),  # leeseo 128
    115: ("IVE SECRET", "MD", "", H),  # leeseo 129
    124: ("IVE SECRET", "HOTTRACKS", "", H),
    128: ("IVE SECRET", "QQ Music", "5", H),
    129: ("IVE SECRET", "QQ Music", "1", H),  # liz 176
    130: ("IVE SECRET", "QQ Music", "2", H),  # liz 177
    131: ("IVE SECRET", SWL, "2.0 POLA", H),
    132: ("IVE SECRET", "QQ Music", "3", H),  # leeseo 149
    133: ("IVE SECRET", "QQ Music", "4", H),  # leeseo 150
    134: ("IVE SECRET", "Beatroad", "2.0", H),
    139: ("IVE SECRET", "Shanghai", "WINNER", N),  # leeseo 157
    143: ("IVE SECRET", WML, "9.0-2", H),  # 表の「WITHMUU LD 5」＝アプリの 9.0（左が 9.0-2、右が 9.0-1）
    144: ("IVE SECRET", "QQ Music × Starship Square", "Christmas", N),  # leeseo 164
    147: ("IVE SECRET", "Yetimall ラキドロ", "POLA", H),  # liz 193
    148: ("IVE SECRET", "Apple Music ラキドロ", "5.0 POLA", H),  # liz 194
    149: ("IVE SECRET", WML, "9.0-1", H),
    152: ("REVIVE+", "本体封入", "MINI MINI", H),  # leeseo 173
    155: ("REVIVE+", "QQ Music", "Member set 2", N),  # liz 209
    156: ("REVIVE+", "QQ Music", "2.0 ランダム 1", N),  # liz 210
    157: ("REVIVE+", "QQ Music", "2.0 ランダム 2", N),  # liz 211
    158: ("REVIVE+", "QQ Music", "2.0 ランダム 3", N),  # liz 212
    159: ("REVIVE+", "QQ Music", "2.0 ランダム 4", N),  # liz 213
    160: ("REVIVE+", "QQ Music", "2.0 ランダム 5", N),  # liz 214
    161: ("REVIVE+", WML, "3.0 POLA", H),
    162: ("REVIVE+", "QQ Music", "2.0 ランダム 6", N),  # liz 215
    165: ("REVIVE+", "MusicArt ラキドロ", "2.0 POLA", H),  # leeseo 190
    167: ("REVIVE+", WML, "9.0", H),
    168: ("REVIVE+", "KMONSTAR", "1.0", H),  # leeseo 194
    176: ("ALIVE", "A!SMART", "ユニット 1", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    177: ("ALIVE", "A!SMART", "ユニット 2", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    179: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    180: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    181: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 1", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    182: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 2", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    183: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    184: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    185: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    186: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),  # 何人かのカード → GROUPS（相手がわからないものは入れない）
    190: ("Be Alright", "オフラインイベント", "9.24 OSAKA", H),  # leeseo 212
    191: ("LUCID DREAM", "本体封入", "期間生産限定盤", H),  # leeseo 216
    193: ("LUCID DREAM", "Sony Music Shop", "1.0 clear pc", H),
    195: ("Be Alright", "オフラインイベント", "10.12 TOKYO", H),  # leeseo 213
    196: ("Be Alright", "オフラインイベント", "10.13 OSAKA", H),  # liz 255
    198: ("LUCID DREAM", "SWIA TOKYO exclusive", "6.24-1", H),
}

# レイ（review_rei.json の番号 → ラベル）。同じ位置のラベル（# のあとは元の番号）を使い、残りはラベルを目で読み、
# イソ・リズ・ウォニョンの表の同じ位置のカードがアプリのどの枠かを画像で確かめた
REI = {
    3: ("ELEVEN", "EVERLINE", "2.0", H),
    6: ("ELEVEN", "Fansign Special", "", H),  # leeseo 9
    7: ("ELEVEN", "Fansign Special", "2", N),  # leeseo 10
    8: ("LOVE DIVE", "Jewel ver. POB", "6set Heart", H),
    10: ("LOVE DIVE", "本体封入", "Jewel ver.", H),
    12: ("LOVE DIVE", WML, "1.0-1", H),  # leeseo 13
    17: ("LOVE DIVE", "Fansign", "", N),  # leeseo 16
    18: ("LOVE DIVE", "Tower Records", "2 POLA", H),  # leeseo 17
    20: ("After LIKE", "Naver Shopping Live", "", H),
    21: ("After LIKE", WML, "2.0-2", H),  # leeseo 23
    22: ("After LIKE", "Tower Records", "2", H),  # leeseo 26
    24: ("After LIKE", "TOU", "WINNER", N),  # leeseo 27
    26: ("After LIKE", "Broadcast", "3", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    27: ("I've IVE", "Vinyl", "", N),  # leeseo 33
    28: ("I've IVE", "US Exclusive", "", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    30: ("I've IVE", "Namil Music", "", H),  # liz 37
    38: ("I've MINE", "Broadcast", "Baddie", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    40: ("I've MINE", "本体封入", "PLVE ver.", H),
    41: ("I've MINE", "Starship Square", "PB LOVED IVE", H),  # leeseo 45
    43: ("I've MINE", "Namil Music", "1.0", H),  # liz 50
    45: ("I've MINE", "Tower Records", "1.0", H),  # liz 54
    56: ("I've MINE", SWL, "3-2", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    57: ("I've MINE", SWL, "3 ユニット 2", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    60: ("I've MINE", "Tower Records", "2.0", H),
    61: ("I've MINE", "Soundwave ファンサイン", "Singapore", N),  # leeseo 57
    64: ("I've MINE", "Sony Music Japan", "2-1", N),  # leeseo 62
    65: ("I've MINE", "Sony Music Japan", "2-2", N),  # leeseo 63
    66: ("I've MINE", "Sony Music Japan", "2-3", N),  # liz 79
    67: ("I've MINE", "Sony Music Japan", "2-4", N),  # leeseo 64
    68: ("I've MINE", "Sony Music Japan", "2-5", N),  # leeseo 65
    69: ("I've MINE", "A!SMART ファンサイン", "", N),  # leeseo 66
    71: ("IVE SWITCH", "Starship Square", "1", H),
    72: ("IVE SWITCH", WM, "", H),
    73: ("I've MINE", "Yizhiyu", "3.0", N),  # wonyoung 59
    75: ("IVE SWITCH", "Tower Records", "2", N),  # leeseo 70
    77: ("IVE SWITCH", "Makestar ファンサイン", "1.0", H),
    78: ("IVE SWITCH", SWL, "2.0 POLA", H),  # leeseo 72
    80: ("IVE SWITCH", WML, "1.0-3", N),  # leeseo 74
    81: ("IVE SWITCH", SWL, "4.0 POLA", H),  # leeseo 76
    82: ("IVE SWITCH", WML, "3.0-3", N),  # leeseo 77
    83: ("IVE SWITCH", WML, "4.0（2 組目）-3", N),  # leeseo 83
    84: ("IVE SWITCH", WML, "4.0-3", N),  # liz 112
    85: ("IVE SWITCH", "Makestar ラキドロ", "4.0 POLA", H),  # leeseo 81
    86: ("IVE SWITCH", SWL, "3.0-1", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    87: ("IVE SWITCH", SWL, "3.0-2", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    88: ("IVE SWITCH", SWL, "3.0-3", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    89: ("IVE SWITCH", SWL, "3.0-4", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    90: ("IVE SWITCH", SWL, "6.0 POLA", H),  # leeseo 88
    91: ("IVE SWITCH", SWL, "9.0 POLA", H),  # leeseo 90
    92: ("IVE SWITCH", "TOKYO DOME 限定", "9/4", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    93: ("IVE SWITCH", "TOKYO DOME 限定", "9/5", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    101: ("IVE EMPATHY", "本体封入", "PLVE", H),
    103: ("IVE EMPATHY", "Starship Square", "3TYPE 1", H),  # leeseo 97
    105: ("IVE EMPATHY", "Starship Square", "LOVED IVE", H),  # wonyoung 92
    108: ("IVE EMPATHY", "Apple Music", "1.0", H),
    111: ("IVE EMPATHY", "StarRiver", "1.0", H),  # leeseo 106
    115: ("IVE EMPATHY", "StarRiver", "2.0", H),  # leeseo 111
    123: ("IVE EMPATHY", SW, "5.0", H),
    126: ("IVE EMPATHY", "Apple Music", "4.0", H),  # wonyoung 106
    127: ("IVE EMPATHY", "オフラインイベント", "TOKYO 2", N),  # leeseo 122
    130: ("IVE EMPATHY", "StarRiver", "2.0（2 枚目）", N),  # leeseo 124
    131: ("IVE EMPATHY", "IDOUSTAGE", "2.0", H),  # wonyoung 112
    134: ("IVE SECRET", "MD", "", H),  # leeseo 129
    135: ("IVE EMPATHY", "Makestar", "4.0 Shanghai 3", N),  # leeseo 128
    143: ("IVE SECRET", WM, "3.0", H),
    144: ("IVE SECRET", "HOTTRACKS", "", H),  # wonyoung 124
    149: ("IVE SECRET", "QQ Music", "1", H),  # leeseo 147
    150: ("IVE SECRET", "QQ Music", "2", H),  # leeseo 148
    152: ("IVE SECRET", "QQ Music", "3", H),  # liz 187
    153: ("IVE SECRET", "QQ Music", "4", H),  # leeseo 150
    156: ("IVE SECRET", "Shanghai", "WINNER", N),  # leeseo 157
    161: ("IVE SECRET", WML, "9.0-2", H),  # wonyoung 143
    162: ("IVE SECRET", "Apple Music ラキドロ", "5.0 POLA", H),  # liz 194
    164: ("IVE SECRET", "QQ Music × Starship Square", "Christmas", N),  # leeseo 164
    169: ("REVIVE+", "本体封入", "MINI MINI", H),  # wonyoung 152
    172: ("REVIVE+", "HOTTRACKS", "", H),
    174: ("REVIVE+", "QQ Music", "Membership", H),  # liz 208
    175: ("REVIVE+", "QQ Music", "Member set 2", N),  # leeseo 180
    176: ("REVIVE+", "QQ Music", "2.0 ランダム 1", N),  # liz 210
    177: ("REVIVE+", "QQ Music", "2.0 ランダム 2", N),  # liz 211
    178: ("REVIVE+", "QQ Music", "2.0 ランダム 3", N),  # liz 212
    179: ("REVIVE+", "QQ Music", "2.0 ランダム 4", N),  # liz 213
    180: ("REVIVE+", "QQ Music", "2.0 ランダム 5", N),  # leeseo 185
    181: ("REVIVE+", "QQ Music", "2.0 ランダム 6", N),  # liz 215
    182: ("REVIVE+", WML, "3.0 POLA", H),  # wonyoung 161
    187: ("REVIVE+", WML, "6.0 POLA", H),
    190: ("REVIVE+", "KMONSTAR", "1.0", H),  # leeseo 194
    192: ("ELEVEN -Japanese ver.-", "タワレコ", "IDトレカ", H),
    194: ("ALIVE", "本体封入", "Album B（II ver.）", H),
    196: ("ALIVE", "A!SMART", "ユニット 1", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    197: ("ALIVE", "A!SMART", "ユニット 2", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    199: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    200: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    201: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 1", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    202: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 2", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    203: ("ALIVE", "本体封入", "会場限定盤", N),  # liz 238
    204: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    205: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    206: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    207: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),  # 何人かのカード → GROUPS（相手がわからないもの・すでに枠と画像があるものは入れない）
    211: ("Be Alright", "オフラインイベント", "9.23 TOKYO", H),  # liz 249
    212: ("Be Alright", "オフラインイベント", "9.24 OSAKA", H),  # liz 250
    217: ("Be Alright", "オフラインイベント", "10.12 TOKYO", H),  # wonyoung 195
    218: ("Be Alright", "オフラインイベント", "10.13 OSAKA", H),  # liz 255
    220: ("LUCID DREAM", "オフラインイベント", "4.29 TOKYO", H),
}

PAGE3 = set()  # 本人：BOYCOTT の印は使ってよい（2026-09-30）。3 ページ目の画像も使う
NO_IMAGE_SOURCES = {"StarRiver"}
# 表の画像に店の透かし（BOYCOTT・中国語の印）がある → 枠だけ
NO_IMAGE_NO = {("leeseo", 27), ("liz", 30), ("wonyoung", 24), ("rei", 24)}  # After LIKE TOU WINNER：中国語の店の印（「不吃香菜」）
TABLES = {"leeseo": ("イソ", LEESEO), "liz": ("リズ", LIZ), "wonyoung": ("ウォニョン", WONYOUNG), "rei": ("レイ", REI)}
# 見比べページ（_review/<メンバー>_have.html）で本人が「ちがう」とした番号：アプリの画像を表の画像に入れ替える。
# 「同じ」としたものは、大きい方（画質のよい方）を使う
DIFF = {"leeseo": {23, 56, 73, 113, 152, 153, 194, 209}, "liz": {27, 40, 140, 179, 180, 226, 246}, "wonyoung": {20, 90, 101, 168}, "rei": {21, 190}}
# 37（I've IVE Naver Live）・43（I've MINE Broadcast Baddie）は、表では何人かで写ったカードだった。
# アプリの 1 人ずつの枠（1 人のカード）はそのままにして、下の GROUPS で何人かのカードの枠を足す

# 何人かで写ったカード（本人の要望：枠の作り方を直す）。メンバーは顔ではなく、メンバー別の表どうしで同じ写真を探して決めた
# （tools/crop/group_ida.py、似ている度合い 0.88 以上。レイの表は並びがずれているので直接比べた）
# (コレクション, 入手元, バージョン, メンバー, 画像の場所 (表の持ち主, [番号の元のメンバー,] 確認ページの番号))
GROUPS = [
    ("After LIKE", "Broadcast", "グループ 1", ["ガウル", "ウォニョン", "イソ"], ("leeseo", 31)),
    ("After LIKE", "Broadcast", "グループ 2", ["ユジン", "レイ", "リズ"], ("yujin", 31)),
    ("I've IVE", "Naver Live", "グループ 1", ["ガウル", "ウォニョン", "イソ"], ("leeseo", 37)),
    ("I've IVE", "Naver Live", "グループ 2", ["ガウル", "リズ", "イソ"], ("leeseo", 38)),
    ("I've IVE", "Naver Live", "ユニット 1", ["ユジン", "ウォニョン"], ("yujin", 37)),
    # ユジンの表の同じ位置のカードは 3 人の写真だが、3 人目が表どうしで確かめられない（レイの表は並びがずれている）→ まだ作らない
    ("I've MINE", "Broadcast", "グループ 1", ["ユジン", "リズ", "イソ"], ("leeseo", 43)),
    ("I've MINE", "Broadcast", "グループ 2", ["ガウル", "レイ", "ウォニョン"], ("gaeul", 43)),
    ("I've MINE", SWL, "3 ユニット 1", ["リズ", "イソ"], ("leeseo", 52)),
    ("I've MINE", SWL, "3 ユニット 2", ["リズ", "イソ"], ("leeseo", 53)),
    ("IVE SWITCH", SWL, "6.0", ["ユジン", "イソ"], ("leeseo", 84)),
    ("IVE SWITCH", SWL, "6.0", ["ガウル", "イソ"], ("leeseo", 85)),
    ("IVE SWITCH", SWL, "6.0", ["レイ", "イソ"], ("leeseo", 86)),
    ("IVE SWITCH", SWL, "6.0", ["リズ", "イソ"], ("leeseo", 87)),
    ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット 1", ["ユジン", "イソ"], ("leeseo", 201)),
    ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット 2", ["ユジン", "イソ"], ("leeseo", 202)),
    # リズ
    ("IVE SWITCH", SWL, "6.0", ["ガウル", "リズ"], ("liz", "liz", 114)),
    ("IVE SWITCH", SWL, "6.0", ["レイ", "リズ"], ("liz", "liz", 115)),
    ("IVE SWITCH", SWL, "6.0", ["リズ", "ウォニョン"], ("liz", "liz", 116)),
    ("IVE SWITCH", "TOKYO DOME 限定", "9/4", ["レイ", "リズ"], ("liz", "liz", 123)),
    ("IVE SWITCH", "TOKYO DOME 限定", "9/5", ["リズ", "イソ"], ("liz", "liz", 124)),
    ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 1", ["レイ", "リズ"], ("liz", "liz", 236)),
    ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 2", ["レイ", "リズ"], ("liz", "liz", 237)),
    ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", ["ガウル", "リズ"], ("liz", "liz", 239)),
    # 10/13・10/14 の 2 枚目は、ガウルの表にない方（アプリの枠のもう 1 組のレイ・リズ）
    ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", ["レイ", "リズ"], ("liz", "liz", 240)),
    ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", ["ガウル", "リズ"], ("liz", "liz", 241)),
    ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", ["レイ", "リズ"], ("liz", "liz", 242)),
    # ウォニョン（似ている度合い 0.94 以上のものだけ。ALIVE 9/4・9/5 TOKYO、10/13 TOKYO の 1 枚目、TOKYO DOME 9/4 は相手がはっきりしないので入れない）
    ("I've MINE", SWL, "3 ユニット 1", ["ガウル", "ウォニョン"], ("wonyoung", "wonyoung", 44)),
    ("I've MINE", SWL, "3 ユニット 2", ["ガウル", "ウォニョン"], ("wonyoung", "wonyoung", 45)),
    ("IVE SWITCH", SWL, "6.0", ["ユジン", "ウォニョン"], ("wonyoung", "wonyoung", 80)),
    ("IVE SWITCH", SWL, "6.0", ["ガウル", "ウォニョン"], ("wonyoung", "wonyoung", 81)),
    ("IVE SWITCH", SWL, "6.0", ["レイ", "ウォニョン"], ("wonyoung", "wonyoung", 82)),
    ("IVE SWITCH", "TOKYO DOME 限定", "9/5", ["ガウル", "ウォニョン"], ("wonyoung", "wonyoung", 87)),
    ("ALIVE", "A!SMART", "ユニット 1", ["ガウル", "ウォニョン"], ("wonyoung", "wonyoung", 176)),
    ("ALIVE", "A!SMART", "ユニット 2", ["ガウル", "ウォニョン"], ("wonyoung", "wonyoung", 177)),
    ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", ["ユジン", "ウォニョン"], ("wonyoung", "wonyoung", 184)),
    ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", ["ユジン", "ウォニョン"], ("wonyoung", "wonyoung", 185)),
    ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", ["レイ", "ウォニョン"], ("wonyoung", "wonyoung", 186)),
    # レイ（似ている度合い 0.94 以上で、まだ画像のない組み合わせだけ。I've MINE ラキドロ 3 の 2 枚目（0.79）、ALIVE 10/13 の 2 枚目（ユジンとウォニョンで迷う）などは入れない）
    ("I've MINE", SWL, "3 ユニット 1", ["ユジン", "レイ"], ("rei", "rei", 56)),
    ("IVE SWITCH", SWL, "6.0", ["ユジン", "レイ"], ("rei", "rei", 86)),
    ("IVE SWITCH", "TOKYO DOME 限定", "9/5", ["ユジン", "レイ"], ("rei", "rei", 93)),
]
GAIN = 1.1

if __name__ == "__main__":
    S = SP + "review/"
    seed = list(csv.reader(io.StringIO(open(PROJ + "public/seed/cards.csv", encoding="utf-8").read())))[1:]
    have = {(r[0], r[1], r[2], r[3]) for r in seed}
    # いまの画像がある枠
    imaged = {}  # 画像がある枠 → その画像の短い辺の長さ
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "zzzz_ida_check.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["credit"] not in ("@powerofablink",):
                imaged[(e["collection"], "/".join(e["members"]), e["source"], e["version"])] = e["file"]
    imaged = {k: min(Image.open(CARDS + f).size) for k, f in imaged.items()}
    j = Job("zzzz_ida_check")
    report = []
    for key, (name, table) in TABLES.items():
        no = json.load(open(S + f"review_{key}.json"))
        miss = json.load(open(S + f"miss_{key}.json"))
        pages = {}
        for i in no:
            coll, src, ver, kind = table[i]
            page, b, _ = miss[i]
            if page not in pages:
                pages[page] = grid.load(D + f"{key}_{page}.jpg")
            im = pages[page]
            use_img = coll not in PAGE3 and src not in NO_IMAGE_SOURCES and (key, i) not in NO_IMAGE_NO
            img = im.crop(inset_frame(im, b)) if use_img else None
            if kind == X:
                report.append([name, i, coll, src, ver, "入れない"])
                continue
            if kind == H:
                if (coll, name, src, ver) not in have:
                    print("枠が見つからない", i, coll, src, ver)
                    report.append([name, i, coll, src, ver, "枠が見つからない"])
                    continue
                k4 = (coll, name, src, ver)
                if img is None:
                    report.append([name, i, coll, src, ver, "枠あり（表の画像は使えないのでそのまま）"])
                elif k4 not in imaged:
                    j.add(coll, [name], src, ver, img, "@idalshiro")
                    report.append([name, i, coll, src, ver, "画像を入れた"])
                elif i in DIFF.get(key, set()):
                    j.add(coll, [name], src, ver, img, "@idalshiro")
                    report.append([name, i, coll, src, ver, "ちがう画像だったので入れ替えた"])
                elif min(img.size) >= imaged[k4] * GAIN:
                    j.add(coll, [name], src, ver, img, "@idalshiro")
                    report.append([name, i, coll, src, ver, "同じ写真で大きい方に入れ替えた"])
                else:
                    report.append([name, i, coll, src, ver, "同じ写真（アプリの方が大きいのでそのまま）"])
                continue
            for m in MEMBERS:
                j.add(coll, [m], src, ver, img if m == name else None, "@idalshiro")
            report.append([name, i, coll, src, ver, "新しい枠（6 人）" + ("" if img is not None else "・画像なし")])
    # 何人かで写ったカード
    for coll, src, ver, members, where in GROUPS:
        owner, ref, i = where if len(where) == 3 else (where[0], "leeseo", where[1])
        miss = json.load(open(S + f"miss_{ref}.json"))
        page, b, _ = miss[i]
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        im = grid.load(D + f"{owner}_{page}.jpg")
        # 表は 6 人とも同じ並び：持ち主の表の同じ位置のカード
        bs = grid.card_boxes(im, min_w=0.03, max_w=0.08)
        bx = min(bs, key=lambda x: abs((x[0] + x[2]) / 2 - cx) + abs((x[1] + x[3]) / 2 - cy))
        j.add(coll, members, src, ver, im.crop(inset_frame(im, bx)), "@idalshiro")
        report.append(["/".join(members), i, coll, src, ver, "何人かのカードの枠"])
    j.save()
    with open(SP + "out/ida_check_report.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["member", "no", "collection", "source", "version", "result"])
        w.writerows(report)
    from collections import Counter
    print(Counter(r[-1] for r in report))
