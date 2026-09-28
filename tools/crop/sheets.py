import sys, os
from PIL import Image, ImageDraw
BASE = r"C:/Users/kazuk/OneDrive/pocamaster-images/IVE English ver. - photocard list-20260927T144026Z-1-001/IVE English ver. - photocard list/"
def run(prefix, rels, cols=3, w=660, per=6):
    fs = []
    for r in rels:
        p = BASE + r
        if os.path.isdir(p):
            fs += [r + "/" + f for f in sorted(os.listdir(p)) if f.lower().endswith((".jpg", ".jpeg"))]
        else:
            fs.append(r)
    out = []
    for k in range(0, len(fs), per):
        chunk = fs[k:k + per]
        thumbs = []
        for f in chunk:
            im = Image.open(BASE + f).convert("RGB"); im.thumbnail((w, int(w * 1.6))); thumbs.append(im)
        h = max(t.height for t in thumbs) + 22
        rows = (len(chunk) + cols - 1) // cols
        S = Image.new("RGB", (cols * w, rows * h), "white"); d = ImageDraw.Draw(S)
        for i, (t, f) in enumerate(zip(thumbs, chunk)):
            x, y = (i % cols) * w, (i // cols) * h
            S.paste(t, (x, y + 20)); d.text((x + 4, y + 4), f"{k+i}: {f}", fill="red")
        name = f"{prefix}_{k // per}.jpg"; S.save(name, quality=85); out.append(name)
    print(prefix, len(fs), out)
if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2:])
