"""Square 1000x1000 photo blocks for the 'last minute' digital pins (Kawaii, Cozy Moments, activity book).

    python make_digital_sources.py   -> src_digital/<name>.jpg, then used as src= in make_pins.py

Kinds: grid (4 pages 2x2), hero (one big page + one behind), fan (colour cover + 2 pages),
before/after (line page + coloured version, Kawaii only).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SHOP = HERE.parent
OUT = HERE / "src_digital"
OUT.mkdir(exist_ok=True)
S = 1000
F = "C:/Windows/Fonts/"

KAW = SHOP / "digital/kawaii"
COZY = SHOP / "cozy_moments"
ACT = SHOP / "раб.тетрать 1"
BG = {"kaw": (225, 236, 248), "cozy": (240, 232, 218), "act": (250, 236, 228)}
COVER = {"kaw": KAW / "final/Kawaii_Christmas_Animals_cover_A4.jpg",
         "cozy": COZY / "03_Etsy/Product_PDF/Cozy_Moments_cover_color.jpg",
         "act": ACT / "cover_split/front_cover_8.5x11_300dpi.png"}


def pg(kind, n):
    if kind == "kaw":
        return KAW / f"nuw/page_{n:02d}.png"
    if kind == "cozy":
        return COZY / f"01_Исходники/png/page_{n:02d}.png"
    return ACT / f"book_5.5x8.5/{n:02d}.png"


def load(path, h, kind=None):
    im = Image.open(path).convert("RGB")
    if kind == "act" and im.size == (1744, 2644):  # cut the book page's white margin
        im = im.crop((100, 260, 1644, 2400))
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline=(205, 200, 190), width=2)
    return im


def shadowed(base, img, xy, blur=12, off=(8, 10), alpha=70, angle=0):
    if angle:
        img = img.convert("RGBA").rotate(angle, expand=True, resample=Image.BICUBIC)
        mask = img.getchannel("A")
    else:
        mask = Image.new("L", img.size, 255)
    sh = Image.new("RGBA", (img.width + blur * 4, img.height + blur * 4), (0, 0, 0, 0))
    sh.paste((0, 0, 0, alpha), (blur * 2, blur * 2), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.paste(sh, (xy[0] - blur * 2 + off[0], xy[1] - blur * 2 + off[1]), sh)
    base.paste(img.convert("RGB"), xy, mask)


def grid(kind, pages, name):
    im = Image.new("RGB", (S, S), BG[kind])
    h, gap = 450, 34
    tiles = [load(pg(kind, n), h, kind) for n in pages]
    w = tiles[0].width
    x0, y0 = (S - 2 * w - gap) // 2, (S - 2 * h - gap) // 2
    for k, t in enumerate(tiles):
        shadowed(im, t, (x0 + (k % 2) * (w + gap), y0 + (k // 2) * (h + gap)))
    im.save(OUT / f"{name}.jpg", quality=92)


def hero(kind, front, back, name):
    im = Image.new("RGB", (S, S), BG[kind])
    b = load(pg(kind, back), 820, kind)
    f = load(pg(kind, front), 880, kind)
    shadowed(im, b, (S - b.width - 60, 50), angle=-5)
    shadowed(im, f, (80, 60), angle=3)
    im.save(OUT / f"{name}.jpg", quality=92)


def fan(kind, pages, name):
    im = Image.new("RGB", (S, S), BG[kind])
    a = load(pg(kind, pages[0]), 760, kind)
    b = load(pg(kind, pages[1]), 760, kind)
    shadowed(im, b, (S - b.width - 40, 70), angle=-8)
    shadowed(im, a, (S - a.width - 120, 150), angle=-3)
    cov = load(COVER[kind], 820)
    shadowed(im, cov, (50, 90), blur=16, off=(12, 14), alpha=90)
    im.save(OUT / f"{name}.jpg", quality=92)


def before_after(line, colour, name):
    im = Image.new("RGB", (S, S), BG["kaw"])
    d = ImageDraw.Draw(im)
    a = load(KAW / f"etsy/src/pages/{line}.png", 640)
    b = load(KAW / f"etsy/src/pages/{colour}.png", 640)
    shadowed(im, a, (40, 250), angle=4)
    shadowed(im, b, (S - b.width - 40, 230), angle=-4)
    f = ImageFont.truetype(F + "segoeuib.ttf", 54)
    for x, t in ((260, "PRINT IT"), (740, "COLOR IT!")):
        w = d.textlength(t, font=f)
        d.rounded_rectangle((x - w / 2 - 34, 80, x + w / 2 + 34, 170), 45, fill=(200, 35, 45))
        d.text((x - w / 2, 92), t, font=f, fill=(255, 255, 255))
    im.save(OUT / f"{name}.jpg", quality=92)


def main():
    # Kawaii
    before_after("dog", "dog_coloured", "kaw_ba_dog")
    before_after("goat_tree", "goat_tree_coloured", "kaw_ba_goat")
    before_after("panda_train", "panda_train_coloured", "kaw_ba_panda")
    grid("kaw", [9, 13, 26, 49], "kaw_grid1")
    grid("kaw", [3, 16, 17, 34], "kaw_grid2")
    hero("kaw", 11, 15, "kaw_hero1")
    fan("kaw", [45, 23], "kaw_fan")
    # Cozy Moments
    grid("cozy", [5, 26, 33, 46], "cozy_grid1")
    grid("cozy", [1, 6, 22, 28], "cozy_grid2")
    hero("cozy", 26, 35, "cozy_hero1")
    hero("cozy", 5, 22, "cozy_hero2")
    hero("cozy", 46, 43, "cozy_hero3")
    fan("cozy", [33, 1], "cozy_fan")
    # Activity book
    grid("act", [1, 16, 28, 38], "act_grid1")
    grid("act", [7, 13, 21, 47], "act_grid2")
    hero("act", 18, 19, "act_hero1")
    hero("act", 51, 2, "act_hero2")
    fan("act", [17, 36], "act_fan")
    print(len(list(OUT.glob("*.jpg"))), "sources")


if __name__ == "__main__":
    main()
