"""Make 1000x1500 Pinterest pins from shop photos.

Usage: python make_pins.py            -> writes pins/*.jpg and batch.json
Each pin: headline band on top, product photo, footer with sub-line + Etsy pill.
"""
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SHOP = HERE.parent
OUT = HERE / "pins"
OUT.mkdir(exist_ok=True)

CREAM = (246, 239, 228)
TERRA = (181, 96, 59)
GREEN = (62, 92, 74)
INK = (52, 38, 30)
FONTS = Path("C:/Windows/Fonts")
F_HEAD = str(FONTS / "georgiab.ttf")
F_BODY = str(FONTS / "segoeui.ttf")
F_BOLD = str(FONTS / "segoeuib.ttf")

W, H = 1000, 1500
HEAD_H, FOOT_H = 300, 200
PHOTO_H = H - HEAD_H - FOOT_H  # 1000

ETSY = "https://www.etsy.com/listing/{}"

# file, listing id, board, kicker, headline, footer line, pin title, description
PINS = [
    dict(src="cards/mock-main.jpg", listing=4619719883, board="Custom Christmas Cards",
         kicker="PERSONALIZED CHRISTMAS CARDS", head="Your Family Photo on Christmas Cards",
         foot="Pack of 10 · Your own text inside",
         title="Custom Photo Christmas Cards with Your Family Photo – Pack of 10",
         desc="Send this year's Christmas greetings with your own family photo. Personalized folded 5x7 holiday cards, pack of 10 with envelopes, your names and message printed inside. Easy order: upload your photo and text. Perfect for family Christmas card ideas, holiday photo cards and festive greetings."),
    dict(src="05_Etsy_Photos/coloring_book/src/family_spread.jpg", listing=4620382703, board="Personalized Photo Gifts",
         kicker="PERSONALIZED GIFT", head="Your Family Photos as a Coloring Book",
         foot="10 of your own moments, drawn as coloring pages",
         title="Personalized Coloring Book from Your Family Photos – Unique Christmas Gift",
         desc="We turn your favorite family photos into hand-drawn coloring pages – a one-of-a-kind book with your family's name on the cover. A cozy Christmas activity for kids, parents and grandparents, and a meaningful personalized gift idea for the whole family."),
    dict(src="05_Etsy_Photos/coloring_book/src/grandma_girl_coloring.jpg", listing=4620382703, board="Christmas Gift Ideas",
         kicker="GIFT IDEA FOR GRANDMA", head="Color Your Own Memories Together",
         foot="Custom coloring book made from your photos",
         title="Custom Coloring Book from Photos – Christmas Gift for Grandma and Grandkids",
         desc="A Christmas gift grandma will treasure: a coloring book made from your own family photos. Color your memories together by the tree. Personalized family coloring pages, a thoughtful gift for grandparents, kids and families."),
    dict(src="05_Etsy_Photos/metal_print/out/01_hero_your_photo.jpg", listing=4620957314, board="Wall Art & Metal Prints",
         kicker="CUSTOM WALL ART", head="Your Photo on Brushed Metal",
         foot="Made to order from the photo you send",
         title="Custom Photo Print on Brushed Aluminum – Personalized Metal Wall Art",
         desc="Turn your favorite family photo into modern metal wall art. Printed on brushed aluminum, ready to hang, in several sizes. A personalized Christmas gift for mom, an anniversary gift or a stylish photo display for your home decor."),
    dict(src="05_Etsy_Photos/metal_print/out/02_how_it_works.jpg", listing=4620957314, board="Personalized Photo Gifts",
         kicker="HOW IT WORKS", head="From Your Photo to Metal Wall Art",
         foot="Choose size · Upload photo · We print & ship",
         title="Personalized Metal Photo Print – From Your Photo to Wall Art in 3 Steps",
         desc="Choose the size, upload your photo, and we print it on brushed aluminum for you. A modern personalized photo gift for parents, couples and families – great for Christmas, anniversaries and housewarming."),
    dict(src="05_Etsy_Photos/rock_santa_tee_v2/01_hero_rock_santa.jpg", listing=4615547527, board="Christmas Gift Ideas",
         kicker="FUNNY CHRISTMAS TEE", head="Rock 'n' Roll Santa Shirt",
         foot="Gift for musicians · 9 colors · S–5XL",
         title="Rock N Roll Santa Shirt – Funny Christmas Guitar Tee, Gift for Musician",
         desc="Santa shredding a Christmas tree guitar! A funny holiday t-shirt for guitar players, rock fans and anyone who loves an ugly-sweater-party alternative. Unisex, 9 colors, sizes S–5XL. A fun Christmas gift for him, for her or for the musician in your family."),
    dict(src="05_Etsy_Photos/rock_santa_tee_v2/05_model_garnet.jpg", listing=4615547527, board="Christmas Gift Ideas",
         kicker="CHRISTMAS GIFT FOR HIM", head="Sleigh the Stage This Christmas",
         foot="Rock 'n' Roll Santa tee · unisex",
         title="Funny Christmas T-Shirt for Men – Rock Santa Guitar Tee, Holiday Party Outfit",
         desc="Holiday party outfit idea: a rock 'n' roll Santa playing a Christmas tree guitar. Funny Christmas shirt for men and women, perfect gift for musicians, dads, brothers and rock music lovers."),
    dict(src="санта крейзи/ad_01_hero_all_designs.jpg", listing=4615510325, board="Christmas Gift Ideas",
         kicker="FUNNY CHRISTMAS HOODIE", head="Santa Breaks Through!",
         foot="6 designs · organic cotton · unisex",
         title="Funny Santa Hoodie – Ripped 3D Christmas Sweatshirt, Gift for Him",
         desc="Santa bursting out of your hoodie! Funny 3D ripped-effect Christmas sweatshirt in organic cotton, 6 designs and 3 colors. A unique alternative to the ugly Christmas sweater and a great Christmas gift for him, for her or for teens."),
    dict(src="05_Etsy_Photos/beanie/out/01_hero_custom_text.jpg", listing=4620995380, board="Cozy Winter Beanies",
         kicker="CUSTOM EMBROIDERED BEANIE", head="Your Name or Text, Embroidered",
         foot="3 beanie colors × 6 thread colors",
         title="Custom Embroidered Beanie with Name – Personalized Winter Hat, Christmas Gift",
         desc="A cozy ribbed cuffed beanie embroidered with any name, nickname or short phrase. Choose from 3 beanie colors and 6 thread colors. Personalized winter hat for men, women and teens – a perfect stocking stuffer and Christmas gift."),
    dict(src="05_Etsy_Photos/beanie/out/02_all_colors.jpg", listing=4620995380, board="Cozy Winter Beanies",
         kicker="PICK YOUR COLORS", head="18 Ways to Make It Yours",
         foot="Personalized ribbed beanie · made to order",
         title="Personalized Beanie Color Options – Custom Name Embroidered Winter Hat",
         desc="Mustard, charcoal grey or burgundy beanie with maroon, green, white, grey, navy or gold embroidery – 18 combinations for your custom text. Personalized winter beanie, matching family hats and cozy Christmas gift ideas."),
    dict(src="мерч чашки/Gemini_Generated_Image_72vhvs72vhvs72vh.jpg", listing=4612794146, board="Christmas Gift Ideas", cover=0.45,
         kicker="MAGIC COLOR CHANGING MUG", head="Pour Hot Tea, Watch Your Message Appear",
         foot="Personalized heat reveal mug · 11 oz",
         title="Personalized Magic Christmas Mug – Color Changing Mug with Custom Text",
         desc="Pour in hot tea or cocoa and watch your secret Christmas message appear! Personalized heat reveal color changing mug, 11 oz ceramic. A magical Christmas gift for grandma, mom, kids or a fun way to announce big news."),
    dict(src="чехол тел/case-models.jpg", listing=4612819148, board="Personalized Photo Gifts",
         kicker="CUSTOM PHOTO PHONE CASE", head="Your Favorite Photo on Your iPhone",
         foot="27 models · iPhone X to 16 Pro Max",
         title="Custom Photo Phone Case for iPhone 16, 15, 14 – Personalized Picture Tough Case",
         desc="Put your favorite photo of family, partner or pet on a protective tough phone case. Available for 27 iPhone models from iPhone X to iPhone 16 Pro Max. A personalized gift for her, for him or for yourself."),
    dict(src="мишки граффити/01_all_bears_order_names.jpg", listing=4613377512, board="Christmas Gift Ideas",
         kicker="STREETWEAR HOODIE", head="Choose Your Graffiti Bear",
         foot="7 designs · front + back print · S–3XL",
         title="Graffiti Teddy Bear Hoodie – Urban Streetwear Sweatshirt, Gift for Him or Her",
         desc="Bold graffiti teddy bear hoodies in 7 designs with front and back print. Urban hip hop streetwear in 8 colors, unisex sizes S–3XL. A cool Christmas gift for teens, him or her."),
    dict(src="calendar_eu_promo/05_gift.jpg", listing=4611879729, board="Christmas Gift Ideas",
         kicker="2027 WALL CALENDAR", head="The Funniest Calendar for Animal Lovers",
         foot="Animal Zodiac · slim hanging calendar",
         title="Funny Animal Zodiac Calendar 2027 – Slim Wall Calendar, Gift for Animal Lovers",
         desc="12 hilarious party animals, one for every zodiac sign. Slim hanging wall calendar 2027 with US & Canadian holidays – a fun Christmas gift, Secret Santa idea or stocking stuffer for animal lovers and astrology fans."),
    # Retro Sunset cap — never name the game/brand it is styled after (trademarks)
    dict(src="05_Etsy_Photos/retro_cap/src/04.jpg", listing=4613453689, board="Christmas Gift Ideas",
         kicker="RETRO 80s EMBROIDERED CAP", head="Neon Sunset Vibes, Stitched on a Cap",
         foot="3 retro designs · 11 cap colors",
         title="Retro Sunset Embroidered Dad Hat – 80s Synthwave Palm Tree Cap, Gift for Gamers",
         desc="Neon sunsets, palm trees and 80s night-drive vibes, embroidered with real thread on a low profile dad hat. Choose Stay Golden, Neon Coast or Flamingo Sunset in 11 cap colors. A cool gift for gamers, retro wave fans and anyone who loves synthwave, Miami-style summer nights and vintage 80s aesthetic."),
    dict(src="free_shipping_badge/originals/4608931952.jpg", listing=4608931952, board="Christmas Gift Ideas", cover=0.5,
         kicker="COLORING BOOK FOR ADULTS", head="Cozy Moments to Color and Relax",
         foot="49 cozy home & garden scenes · 8.5 × 11 in",
         title="Cozy Moments Coloring Book for Adults – 49 Easy Cozy Home & Garden Scenes",
         desc="Slow down with 49 cozy home and garden scenes: snug reading corners, warm kitchens, knitted hats and blooming gardens. Easy bold line designs, one per page on thick paper – perfect for colored pencils. A relaxing Christmas gift for her, mom, grandma or any coloring lover, and a calm self-care activity for winter evenings."),
    # 17–19 = Kawaii pins made outside this script; pet ornament starts at 20 (num= keeps file names stable)
    # Pet photos in these pins are AI-generated examples -> schedule with isAiGenerated
    dict(num=20, src="pet_ornament/mockups/dog_golden_mockup.jpg", listing=4623800039, board="Personalized Photo Gifts",
         kicker="CUSTOM PET ORNAMENT", head="Your Pet's Photo on a Glass Ornament",
         foot="Name + year · clear glass · 3 in",
         title="Custom Pet Photo Ornament – Personalized Dog or Cat Christmas Ornament with Name",
         desc="Hang your best friend on the tree! Your dog's or cat's photo printed on a clear glass Christmas ornament with their name and the year. Upload your photo when you order. A sweet keepsake and Christmas gift for dog moms, cat dads and every pet lover. Free shipping to the USA and Canada."),
    dict(num=21, src="pet_ornament/mockups/dog_cat_duo_mockup.jpg", listing=4623800039, board="Christmas Gift Ideas",
         kicker="FOR DOG & CAT FAMILIES", head="Two Best Friends, One Ornament",
         foot="Two pets on one personalized ornament",
         title="Personalized Ornament with Two Pets – Custom Dog and Cat Photo Christmas Gift",
         desc="Dog and cat together on one ornament! Send a photo of your two pets and their names – we print them on a clear glass Christmas ornament. A cozy gift idea for pet families, dog and cat lovers, and a keepsake for the first Christmas in a new home."),
    dict(num=22, src="pet_ornament/mockups/dog_memorial_mockup.jpg", listing=4623800039, board="Christmas Gift Ideas",
         kicker="PET MEMORIAL GIFT", head="Forever in Our Hearts",
         foot="A gentle keepsake for a beloved pet",
         title="Pet Memorial Ornament with Photo – Dog or Cat Loss Keepsake, Sympathy Gift",
         desc="Remember a beloved dog or cat every Christmas. Their photo and name on a clear glass ornament with a short line like Forever in our hearts. A thoughtful pet loss sympathy gift for a friend, or a keepsake for your own tree. Free shipping to the USA and Canada."),
    dict(num=23, src="pet_ornament/mockups/cat_orange_mockup.jpg", listing=4623800039, board="Personalized Photo Gifts",
         kicker="GIFT FOR CAT LOVERS", head="Your Cat, Hanging on the Tree",
         foot="Upload photo · add name · we print & ship",
         title="Custom Cat Photo Ornament – Personalized Cat Christmas Ornament, Gift for Cat Mom",
         desc="Pick your favorite photo of your cat, add their name and a short line, and we print it on a 3 inch clear glass ornament. An easy personalized Christmas gift for cat moms, cat dads and every cat lover – ready to hang with a red ribbon. Free shipping to the USA and Canada."),
    # ---- Batch 2 (29.11–08.12, 12:00 + 20:30). Photos = the shop's own Etsy listing images (src_etsy/).
    # Order = schedule order: products with early Christmas cut-offs (portrait ornament 5.12, books/poster 8.12) go first.
    dict(num=24, src="pinterest_pins/src_etsy/4612596949_3.jpg", listing=4612596949, board="Personalized Photo Gifts",
         kicker="CUSTOM PORTRAIT ORNAMENT", head="Your Photo, Painted as an Ornament",
         foot="We paint the portrait · names + year",
         title="Custom Portrait Christmas Ornament from Photo – Personalized Couple Keepsake",
         desc="Send us your favorite photo and we turn it into a soft painted portrait on a clear glass Christmas ornament, with your names and the year. A romantic gift for couples, a first Christmas keepsake or a gift for parents and grandparents. Up to 4 people or pets. Free shipping to the USA and Canada."),
    dict(num=25, src="pinterest_pins/src_etsy/4619413538_2.jpg", listing=4619413538, board="Christmas Gift Ideas",
         kicker="ACTIVITY BOOK FOR KIDS 3–5", head="50 Christmas Activities for Little Ones",
         foot="Coloring · mazes · tracing · counting",
         title="Christmas Activity Book for Kids Ages 3-5 – 50 Coloring, Maze and Tracing Pages",
         desc="Keep little hands busy all December! 50 Christmas activities for preschoolers: coloring pages, mazes, tracing, counting, matching and dot-to-dot with Santa, reindeer and snowmen. Printed workbook in 3 sizes. A sweet stocking stuffer and Christmas Eve box idea for kids ages 3 to 5."),
    dict(num=26, src="pinterest_pins/src_etsy/4620971144_4.jpg", listing=4620971144, board="Personalized Photo Gifts",
         kicker="PERSONALIZED PHOTO CALENDAR", head="12 Months of Your Family Memories",
         foot="Your photos · your dates · 2027",
         title="Personalized Family Photo Calendar 2027 – Custom Wall Calendar with Your Photos",
         desc="Turn this year's best family photos into a 2027 wall calendar. One photo for every month, your own captions, birthdays and special dates printed in. A heartfelt Christmas gift for grandma, grandpa and mom that they will look at all year long. Free shipping to the USA and Canada."),
    dict(num=27, src="pinterest_pins/src_etsy/4611405820_2.jpg", listing=4611405820, board="Christmas Gift Ideas",
         kicker="COLORING BOOK FOR ADULTS", head="52 Cozy Scenes to Slow Down With",
         foot="Easy bold lines · 8.5 × 11 in paperback",
         title="Cozy Coloring Book for Adults – 52 Easy Home and Garden Scenes, Relaxing Gift",
         desc="Warm kitchens, reading nooks, knitted hats and little gardens: 52 cozy coloring pages with easy bold lines, one large design per page. A relaxing printed coloring book for winter evenings and a lovely Christmas gift for her, mom, grandma or any coloring lover."),
    dict(num=28, src="pinterest_pins/src_etsy/4613955482_2.jpg", listing=4613955482, board="Wall Art & Metal Prints",
         kicker="CUSTOM FRAMED PHOTO POSTER", head="Your Photo, Beautifully Framed",
         foot="With your names and special date",
         title="Custom Framed Photo Poster with Names and Date – Personalized Family Wall Art",
         desc="Your favorite photo printed as a framed poster with your family name and a special date. A meaningful gift for couples, anniversaries, weddings and family Christmas. Send your photo, add names and date, and we print and frame it for you."),
    dict(num=29, src="pinterest_pins/src_etsy/4612755942_2.jpg", listing=4612755942, board="Christmas Gift Ideas",
         kicker="FIRST CHRISTMAS MARRIED", head="Our First Christmas as Mr & Mrs",
         foot="Glass heart ornament · your names + year",
         title="Our First Christmas as Mr and Mrs Ornament 2026 – Personalized Newlywed Gift",
         desc="Celebrate your first Christmas as husband and wife! A clear glass heart ornament with gold details, your names and the year. A keepsake gift for newlyweds, a wedding gift for the couple, or a sweet surprise for your spouse. Free shipping to the USA and Canada."),
    dict(num=30, src="pinterest_pins/src_etsy/4612596949_6.jpg", listing=4612596949, board="Christmas Gift Ideas",
         kicker="GIFT FOR COUPLES", head="Your Love Story on the Tree",
         foot="Painted portrait from your photo",
         title="Personalized Couple Portrait Ornament – Custom Christmas Gift for Him or Her",
         desc="A painted portrait of the two of you, made from your own photo and printed on a glass Christmas ornament with your names. A romantic Christmas gift for your boyfriend, girlfriend, husband or wife, and a keepsake you will hang every year."),
    dict(num=31, src="pinterest_pins/src_etsy/4608931952_2.jpg", listing=4608931952, board="Christmas Gift Ideas",
         kicker="EASY COLORING FOR ADULTS", head="One Big Cozy Design per Page",
         foot="49 scenes · thick paper · 8.5 × 11 in",
         title="Easy Coloring Book for Adults and Seniors – Cozy Moments, Large Simple Designs",
         desc="Big, simple, cozy designs that are easy to finish in one evening: armchairs, plants, mugs, knitted hats and more. 49 pages, one design per page, printed on thick paper. A calming gift for beginners, seniors, moms and grandmas who love to color."),
    dict(num=32, src="pinterest_pins/src_etsy/4613295284_7.jpg", listing=4613295284, board="Christmas Gift Ideas",
         kicker="MATCHING FAMILY MUGS", head="A Mug with Every Initial",
         foot="Your letter + name · gold or red plaid",
         title="Personalized Christmas Mug with Initial and Name – Matching Family Mugs",
         desc="Pick an initial and a name for every family member and make a set of matching Christmas mugs. Gold or red plaid style, 11 oz white ceramic mug. A cozy stocking stuffer, gift for teachers and coworkers, and a cute Christmas morning tradition."),
    dict(num=33, src="pinterest_pins/src_etsy/4619413538_3.jpg", listing=4619413538, board="Christmas Gift Ideas",
         kicker="SCREEN-FREE HOLIDAY FUN", head="Mazes, Tracing and Coloring for Christmas",
         foot="50 activities · ages 3 to 5",
         title="Preschool Christmas Workbook – Coloring, Tracing and Counting Activities for Kids",
         desc="Screen-free fun for the holidays: a Christmas workbook for kids ages 3 to 5 with coloring, letter and number tracing, counting, mazes and matching games. Great for Christmas break, long car rides and the Christmas Eve box."),
    dict(num=34, src="pinterest_pins/src_etsy/4619719883_3.jpg", listing=4619719883, board="Custom Christmas Cards",
         kicker="PHOTO CHRISTMAS CARDS", head="Any Photo You Love, on Your Cards",
         foot="Family · couples · pets · kids",
         title="Personalized Photo Christmas Cards – Family, Couple or Pet Photo, Pack of 10",
         desc="Family, couple, kids or your pet: send any photo you love and we print it on folded 5x7 Christmas cards with your own greeting inside. Pack of 10 with envelopes. Easy custom holiday cards and New Year greetings for family and friends."),
    dict(num=35, src="pinterest_pins/src_etsy/4613955482_5.jpg", listing=4613955482, board="Personalized Photo Gifts",
         kicker="PERSONALIZED GIFT IDEA", head="The Perfect Personal Gift",
         foot="For family · anniversary · couples",
         title="Personalized Family Photo Poster in a Frame – Christmas, Wedding or Anniversary Gift",
         desc="One photo, endless meaning: a framed poster with your photo, names and date. For family Christmas, a wedding or an anniversary gift for your partner or parents. We print it from the photo you send and ship it ready to hang."),
    dict(num=36, src="pinterest_pins/src_etsy/4611960140_6.jpg", listing=4611960140, board="Christmas Gift Ideas",
         kicker="NAME ORNAMENTS 2026", head="One for Every Family Member",
         foot="Initial + name + year · acrylic",
         title="Personalized Name Ornament 2026 – Initial Christmas Ornament for the Whole Family",
         desc="A bright acrylic Christmas ornament with a gold initial in a little Santa hat, a name and the year. Make one for every family member, for baby's first Christmas or as a stocking stuffer. Free shipping to the USA and Canada."),
    dict(num=37, src="pinterest_pins/src_etsy/4612755942_5.jpg", listing=4612755942, board="Christmas Gift Ideas",
         kicker="WEDDING KEEPSAKE", head="A Keepsake for Your First Christmas Together",
         foot="Personalized Mr & Mrs heart ornament",
         title="Mr and Mrs Christmas Ornament – First Christmas Married Keepsake with Names",
         desc="A clear glass heart ornament for your first Christmas married, with your names and the year in gold. A beautiful keepsake for newlyweds and a thoughtful wedding or engagement gift for the happy couple."),
    dict(num=38, src="pinterest_pins/src_etsy/4613191071_6.jpg", listing=4613191071, board="Personalized Photo Gifts",
         kicker="CUSTOM LATTE MUG 17 OZ", head="Your Own Words on a Christmas Mug",
         foot="Tall latte mug · holly wreath design",
         title="Personalized Christmas Latte Mug 17oz – Custom Text Holly Wreath Mug, Cozy Gift",
         desc="A tall 17 oz latte mug with a holly Christmas wreath and your own text: a name, a greeting or a family wish. A cozy gift for coffee and cocoa lovers, mom, grandma or a coworker, and a sweet stocking stuffer."),
    dict(num=39, src="pinterest_pins/src_etsy/4611879729_6.jpg", listing=4611879729, board="Christmas Gift Ideas",
         kicker="WHITE ELEPHANT GIFT IDEA", head="A Funny Wish for Every Month of 2027",
         foot="12 zodiac party animals · slim calendar",
         title="Funny Wall Calendar 2027 – Zodiac Party Animals, White Elephant Gift Idea",
         desc="Goofy party animals for every zodiac sign and a funny wish every month: this slim hanging 2027 calendar makes everyone smile. With US and Canadian holidays. A great Secret Santa, white elephant or office gift for animal lovers."),
    dict(num=40, src="pinterest_pins/src_etsy/4620971144_3.jpg", listing=4620971144, board="Personalized Photo Gifts",
         kicker="HOW IT WORKS", head="Order Your Family Calendar in 3 Steps",
         foot="Personalize · send 13 photos · approve",
         title="Custom Family Photo Calendar 2027 – Easy to Order, Gift for Grandparents",
         desc="Order and personalize, send us 13 photos, approve your free digital proof – and we print your 2027 family photo calendar. An easy, meaningful Christmas gift for grandparents, parents and the whole family."),
    dict(num=41, src="pinterest_pins/src_etsy/4613295284_4.jpg", listing=4613295284, board="Christmas Gift Ideas",
         kicker="PERSONALIZED INITIAL MUG", head="Your Letter and Name in Gold",
         foot="Printed on both sides · 11 oz",
         title="Gold Initial Christmas Mug with Name – Personalized Gift for Her, Stocking Stuffer",
         desc="A gold initial with festive greenery and the name of your choice, printed on both sides of an 11 oz ceramic mug. A personalized Christmas gift for her, a teacher gift or a cute stocking stuffer."),
    dict(num=42, src="pinterest_pins/src_etsy/4619719883_4.jpg", listing=4619719883, board="Custom Christmas Cards",
         kicker="WHAT'S IN YOUR PACK", head="10 Photo Cards + 10 Envelopes",
         foot="One photo · your text inside",
         title="Custom Christmas Photo Cards Pack of 10 with Envelopes – Personalized Holiday Cards",
         desc="Everything you need for this year's Christmas greetings: 10 identical folded photo cards with your picture and your own message inside, plus 10 envelopes. Personalized holiday cards for family and friends, shipped to your door."),
    dict(num=43, src="pinterest_pins/src_etsy/4611960140_2.jpg", listing=4611960140, board="Christmas Gift Ideas",
         kicker="STOCKING STUFFER IDEA", head="A Little Ornament with Their Name",
         foot="Personalized initial ornament · 2026",
         title="Personalized Initial Ornament with Name 2026 – Kids Christmas Ornament, Stocking Stuffer",
         desc="A cheerful name ornament with a gold initial wearing a red Santa hat, plus the name and year 2026. A small personalized gift for kids, grandkids, friends and coworkers – perfect for stockings and gift toppers."),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(draw, text, path, max_w, max_lines, start, min_size):
    size = start
    while size >= min_size:
        f = font(path, size)
        avg = draw.textlength("abcdefghijklmnopqrstuvwxyz", font=f) / 26
        lines = textwrap.wrap(text, width=max(8, int(max_w / avg)))
        if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= 2
    return font(path, min_size), textwrap.wrap(text, 30)[:max_lines]


def place_photo(canvas, src, cover=None):
    im = Image.open(src).convert("RGB")
    box_w, box_h = W, PHOTO_H
    r = im.width / im.height
    if cover is not None and r > 1:  # wide photo: crop a square, cover = horizontal center (0..1)
        side = im.height
        x = int(min(max(cover * im.width - side / 2, 0), im.width - side))
        im = im.crop((x, 0, x + side, side))
        r = 1
    if abs(r - box_w / box_h) < 0.05:  # square: cover
        im = im.resize((box_w, box_h), Image.LANCZOS)
        canvas.paste(im, (0, HEAD_H))
        return
    # contain on cream, centered
    scale = min(box_w / im.width, box_h / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    canvas.paste(im, ((box_w - im.width) // 2, HEAD_H + (box_h - im.height) // 2))


def make(pin, idx):
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    # header
    fk = font(F_BOLD, 26)
    k = pin["kicker"]
    d.text(((W - d.textlength(k, font=fk)) / 2, 38), k, font=fk, fill=TERRA)
    fh, lines = fit_text(d, pin["head"], F_HEAD, W - 110, 2, 74, 50)
    lh = fh.size * 1.18
    y0 = 82 + (HEAD_H - 82 - 20 - lh * len(lines)) / 2
    for i, l in enumerate(lines):
        d.text(((W - d.textlength(l, font=fh)) / 2, y0 + i * lh), l, font=fh, fill=INK)
    place_photo(c, SHOP / pin["src"], pin.get("cover"))
    # footer
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
    name = f"{idx:02d}_{pin['listing']}.jpg"
    c.save(OUT / name, quality=86, optimize=True, progressive=True)
    return name


def main():
    batch = []
    for i, p in enumerate(PINS, 1):
        name = make(p, p.get("num", i))
        batch.append(dict(file=name, board=p["board"], title=p["title"], description=p["desc"],
                          link=ETSY.format(p["listing"]),
                          image_url=f"https://raw.githubusercontent.com/vitalijgudim-gif/tetavita-pins/main/pins/{name}"))
        assert len(p["title"]) <= 100 and len(p["desc"]) <= 500, name
    (HERE / "batch.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(batch), "pins")


if __name__ == "__main__":
    main()
