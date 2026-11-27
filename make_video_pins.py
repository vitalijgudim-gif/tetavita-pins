"""Video pins 1000x1500 from the square Etsy listing videos (05_Etsy_Photos/listing_videos/out/<id>.mp4).

Same layout as make_pins.py: headline band on top, the video in the photo area (its own title bar cropped off),
green footer with the Etsy pill.  Usage: python make_video_pins.py  -> pins/NN_<id>.mp4 + video_batch.json
"""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

from make_pins import (HERE, SHOP, OUT, W, H, HEAD_H, FOOT_H, PHOTO_H, CREAM, TERRA, GREEN, INK,
                       F_HEAD, F_BODY, F_BOLD, ETSY, font, fit_text)

FF = next((Path.home() / "AppData/Local/Programs/Python/Python312/Lib/site-packages/imageio_ffmpeg/binaries")
          .glob("ffmpeg*.exe"))
VIDEOS = SHOP / "05_Etsy_Photos/listing_videos/out"
BAR = 110  # title bar height of the 1080 square video, cropped off

# ai / ai_person -> Pinterest isAiGenerated / isAiGeneratedPerson
PINS = [
    dict(num=72, listing=4620957314, board="Wall Art & Metal Prints", ai=True, ai_person=True,
         kicker="CUSTOM WALL ART", head="Your Family Photo on Brushed Metal",
         foot="Made to order · ready to hang · many sizes",
         title="Custom Metal Photo Print – Your Family Photo on Brushed Aluminum, Christmas Gift",
         desc="See how your favorite family photo looks as modern metal wall art. We print the photo you send on brushed aluminum, ready to hang, in square, vertical and horizontal sizes. A personalized Christmas gift for mom and grandparents, an anniversary gift or a stylish photo display for your home. Free shipping to the USA and Canada."),
    dict(num=73, listing=4619719883, board="Custom Christmas Cards", ai=True, ai_person=True,
         kicker="PHOTO CHRISTMAS CARDS", head="Send Christmas Cards with Your Photo",
         foot="Pack of 10 · envelopes · your text inside",
         title="Custom Photo Christmas Cards – Pack of 10 Folded Cards with Your Family Photo",
         desc="Your family, couple or pet photo on folded 5x7 Christmas cards, with your own title, names and message inside. Pack of 10 identical cards with envelopes, printed and shipped to your door. Easy personalized holiday cards for family and friends. Free shipping to the USA and Canada."),
    dict(num=74, listing=4620995380, board="Cozy Winter Beanies", ai=True, ai_person=True,
         kicker="PERSONALIZED BEANIE", head="Any Name or Text, Embroidered",
         foot="3 beanie colors × 6 thread colors",
         title="Custom Embroidered Beanie with Name – Personalized Winter Hat, Stocking Stuffer",
         desc="A cozy ribbed cuffed beanie embroidered with any name, nickname or short phrase. Mustard, charcoal grey or burgundy with 6 thread colors. A personalized winter hat for men, women and teens, matching family hats and an easy Christmas stocking stuffer. Free shipping to the USA and Canada."),
    dict(num=75, listing=4623800039, board="Personalized Photo Gifts", ai=True, ai_person=False,
         kicker="CUSTOM PET ORNAMENT", head="Your Pet on the Christmas Tree",
         foot="Name + year · clear glass · 3 in",
         title="Custom Pet Photo Ornament – Dog or Cat Christmas Ornament with Name and Year",
         desc="Your dog's or cat's photo on a clear glass Christmas ornament with their name and the year. One pet, two pets or a memorial keepsake. Upload your photo when you order and we design and print it. A sweet gift for dog moms, cat dads and every pet lover. Pet photos shown are AI-generated examples. Free shipping to the USA and Canada."),
]


def frame(pin):
    """Header + footer on a transparent photo area."""
    c = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(c)
    fk = font(F_BOLD, 26)
    k = pin["kicker"]
    d.text(((W - d.textlength(k, font=fk)) / 2, 38), k, font=fk, fill=TERRA)
    fh, lines = fit_text(d, pin["head"], F_HEAD, W - 110, 2, 74, 50)
    lh = fh.size * 1.18
    y0 = 82 + (HEAD_H - 82 - 20 - lh * len(lines)) / 2
    for i, l in enumerate(lines):
        d.text(((W - d.textlength(l, font=fh)) / 2, y0 + i * lh), l, font=fh, fill=INK)
    d.rectangle([0, HEAD_H, W, HEAD_H + PHOTO_H - 1], fill=(0, 0, 0, 0))
    fy = HEAD_H + PHOTO_H
    d.rectangle([0, fy, W, H], fill=GREEN)
    ff, fl = fit_text(d, pin["foot"], F_BODY, W - 100, 1, 38, 28)
    d.text(((W - d.textlength(fl[0], font=ff)) / 2, fy + 34), fl[0], font=ff, fill=CREAM)
    fp = font(F_BOLD, 30)
    pill = "Shop on Etsy  ·  TetaVitaArtPress"
    pw = d.textlength(pill, font=fp) + 70
    px, py = (W - pw) / 2, fy + 108
    d.rounded_rectangle([px, py, px + pw, py + 60], radius=30, fill=TERRA)
    d.text((px + 35, py + 9), pill, font=fp, fill=(255, 255, 255))
    return c


def make(pin):
    png = OUT / f"_frame_{pin['num']}.png"
    frame(pin).save(png)
    vh = round((1080 - BAR) * W / 1080 / 2) * 2          # 898
    y = HEAD_H + (PHOTO_H - vh) // 2
    name = f"{pin['num']:02d}_{pin['listing']}.mp4"
    cream = "0x%02X%02X%02X" % CREAM
    flt = (f"color=c={cream}:s={W}x{H}:r=30[bg];"
           f"[0:v]crop=1080:{1080 - BAR}:0:{BAR},scale={W}:{vh}[v];"
           f"[bg][v]overlay=0:{y}:shortest=1[a];[a][1:v]overlay=0:0,format=yuv420p")
    subprocess.run([str(FF), "-y", "-loglevel", "error", "-i", str(VIDEOS / f"{pin['listing']}.mp4"),
                    "-i", str(png), "-filter_complex", flt, "-c:v", "libx264", "-crf", "20",
                    "-movflags", "+faststart", "-an", str(OUT / name)], check=True)
    png.unlink()
    return name


def main():
    batch = []
    for p in PINS:
        assert len(p["title"]) <= 100 and len(p["desc"]) <= 500, p["num"]
        batch.append(dict(file=make(p), board=p["board"], title=p["title"], description=p["desc"],
                          link=ETSY.format(p["listing"]), ai=p["ai"], ai_person=p["ai_person"]))
    (HERE / "video_batch.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1), encoding="utf-8")
    print(*[b["file"] for b in batch])


if __name__ == "__main__":
    main()
