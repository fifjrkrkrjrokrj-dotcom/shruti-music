import os
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

FONT_BOLD = "ShrutiMusic/assets/font3.ttf"
FONT_REGULAR = "ShrutiMusic/assets/font2.ttf"

CANVAS_W = 1280
CANVAS_H = 720

async def gen_thumb(videoid, thumburl):

    thumb_path = f"{CACHE_DIR}/{videoid}.jpg"

    # ===== DOWNLOAD THUMB =====

    async with aiohttp.ClientSession() as session:
        async with session.get(thumburl) as resp:
            if resp.status == 200:
                async with aiofiles.open(thumb_path, "wb") as f:
                    await f.write(await resp.read())

    # ===== OPEN IMAGE =====

    base = Image.open(thumb_path).convert("RGB")

    # ===== BG =====

    bg = base.resize((CANVAS_W, CANVAS_H))
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)

    canvas = bg.convert("RGBA")

    # ===== GLASS CARD =====

    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    card_x = 260
    card_y = 120
    card_w = 760
    card_h = 480

    odraw.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=35,
        fill=(255, 255, 255, 180)
    )

    overlay = overlay.filter(ImageFilter.GaussianBlur(2))

    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # ===== THUMB =====

    thumb = base.resize((540, 240))

    mask = Image.new("L", thumb.size, 0)
    mdraw = ImageDraw.Draw(mask)

    mdraw.rounded_rectangle(
        (0, 0, thumb.size[0], thumb.size[1]),
        radius=22,
        fill=255
    )

    thumb_x = card_x + 110
    thumb_y = card_y + 40

    canvas.paste(thumb, (thumb_x, thumb_y), mask)

    # ===== FONTS =====

    title_font = ImageFont.truetype(FONT_BOLD, 34)
    small_font = ImageFont.truetype(FONT_REGULAR, 20)

    # ===== TEXT =====

    draw.text(
        (card_x + 120, card_y + 310),
        "Now Playing",
        font=title_font,
        fill="black"
    )

    draw.text(
        (card_x + 120, card_y + 360),
        "YouTube Music",
        font=small_font,
        fill=(30, 30, 30)
    )

    # ===== BAR =====

    line_y = card_y + 420

    draw.line(
        (card_x + 130, line_y, card_x + 610, line_y),
        fill=(120, 120, 120),
        width=5
    )

    draw.line(
        (card_x + 130, line_y, card_x + 410, line_y),
        fill="red",
        width=6
    )

    draw.ellipse(
        (
            card_x + 400,
            line_y - 10,
            card_x + 420,
            line_y + 10
        ),
        fill="red"
    )

    output = f"{CACHE_DIR}/{videoid}_final.png"

    canvas.save(output)

    return output
