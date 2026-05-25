from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import os

CANVAS_W = 1280
CANVAS_H = 720

FONT_BOLD = "ShrutiMusic/assets/font3.ttf"
FONT_REGULAR = "ShrutiMusic/assets/font2.ttf"

async def gen_thumb(videoid: str):

    thumb_path = f"cache/{videoid}.png"

    base = Image.open(thumb_path).convert("RGB")

    # ===== BACKGROUND =====

    bg = base.resize((CANVAS_W, CANVAS_H))
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)

    canvas = bg.convert("RGBA")

    # ===== GLASS CARD =====

    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    card_x = 260
    card_y = 120
    card_w = 760
    card_h = 480

    draw_overlay.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=35,
        fill=(255, 255, 255, 180)
    )

    overlay = overlay.filter(ImageFilter.GaussianBlur(2))

    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # ===== THUMB IMAGE =====

    thumb = base.resize((540, 240))

    thumb_x = card_x + 110
    thumb_y = card_y + 40

    mask = Image.new("L", thumb.size, 0)
    mask_draw = ImageDraw.Draw(mask)

    mask_draw.rounded_rectangle(
        (0, 0, thumb.size[0], thumb.size[1]),
        radius=22,
        fill=255
    )

    canvas.paste(thumb, (thumb_x, thumb_y), mask)

    # ===== FONTS =====

    title_font = ImageFont.truetype(FONT_BOLD, 34)
    small_font = ImageFont.truetype(FONT_BOLD, 20)
    tiny_font = ImageFont.truetype(FONT_REGULAR, 18)

    # ===== TITLE =====

    draw.text(
        (card_x + 120, card_y + 310),
        "Bairan Banjaare Lyrics Video",
        font=title_font,
        fill="black"
    )

    # ===== META =====

    draw.text(
        (card_x + 120, card_y + 365),
        "YouTube | 60K views",
        font=small_font,
        fill=(20, 20, 20)
    )

    # ===== PROGRESS BAR =====

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

    # ===== TIMESTAMP =====

    draw.text(
        (card_x + 120, card_y + 445),
        "00:00",
        font=small_font,
        fill="black"
    )

    draw.text(
        (card_x + 550, card_y + 445),
        "2:30",
        font=small_font,
        fill="black"
    )

    # ===== SAVE =====

    output = f"cache/{videoid}_final.png"

    canvas.save(output)

    return output
