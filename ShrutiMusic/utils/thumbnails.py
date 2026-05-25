import os
import aiohttp
import aiofiles
import traceback
import random

from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont,
    ImageEnhance
)

from py_yt import VideosSearch

# =====================================
# CACHE
# =====================================

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# =====================================
# 4K SIZE
# =====================================

CANVAS_W = 3840
CANVAS_H = 2160

# =====================================
# FONTS
# =====================================

FONT_BOLD = "ShrutiMusic/assets/font3.ttf"
FONT_REGULAR = "ShrutiMusic/assets/font2.ttf"

BOT_NAME = "KATIL MUSIC"

# =====================================
# THUMB GENERATOR
# =====================================

async def gen_thumb(videoid: str, user_name="KATIL"):

    try:

        # =====================================
        # FETCH YOUTUBE DATA
        # =====================================

        url = f"https://www.youtube.com/watch?v={videoid}"

        results = VideosSearch(url, limit=1)

        result = (await results.next())["result"][0]

        duration = result.get(
            "duration",
            "3:20"
        )

        thumburl = result["thumbnails"][0]["url"].split("?")[0]

        # =====================================
        # DOWNLOAD THUMB
        # =====================================

        thumb_path = CACHE_DIR / f"{videoid}.jpg"

        async with aiohttp.ClientSession() as session:

            async with session.get(thumburl) as resp:

                if resp.status == 200:

                    async with aiofiles.open(
                        thumb_path,
                        "wb"
                    ) as f:

                        await f.write(
                            await resp.read()
                        )

        # =====================================
        # OPEN IMAGE
        # =====================================

        base = Image.open(
            thumb_path
        ).convert("RGB")

        # =====================================
        # BACKGROUND
        # =====================================

        bg = base.resize(
            (CANVAS_W, CANVAS_H)
        )

        bg = bg.filter(
            ImageFilter.GaussianBlur(40)
        )

        bg = ImageEnhance.Brightness(
            bg
        ).enhance(0.18)

        canvas = bg.convert("RGBA")

        # =====================================
        # RED OVERLAY
        # =====================================

        overlay = Image.new(
            "RGBA",
            (CANVAS_W, CANVAS_H),
            (25, 0, 0, 180)
        )

        canvas = Image.alpha_composite(
            canvas,
            overlay
        )

        draw = ImageDraw.Draw(canvas)

        # =====================================
        # PLAYER BOX
        # =====================================

        box_x = 180
        box_y = 100
        box_w = 3480
        box_h = 1180

        draw.rounded_rectangle(
            (
                box_x,
                box_y,
                box_x + box_w,
                box_y + box_h
            ),
            radius=20,
            fill=(255, 255, 255, 55),
            outline=(255, 255, 255),
            width=6
        )

        # =====================================
        # THUMB IMAGE
        # =====================================

        thumb = base.resize((1900, 980))

        thumb_x = 970
        thumb_y = 130

        canvas.paste(
            thumb,
            (thumb_x, thumb_y)
        )

        # =====================================
        # BLACK FADE
        # =====================================

        fade = Image.new(
            "RGBA",
            (box_w, 350),
            (0, 0, 0, 0)
        )

        fd = ImageDraw.Draw(fade)

        for y in range(350):

            alpha = int((y / 350) * 255)

            fd.line(
                [(0, y), (box_w, y)],
                fill=(0, 0, 0, alpha)
            )

        canvas.paste(
            fade,
            (box_x, box_y + 830),
            fade
        )

        # =====================================
        # CORNERS
        # =====================================

        c = (255, 255, 255)

        # TL
        draw.line([(180, 100), (300, 100)], fill=c, width=8)
        draw.line([(180, 100), (180, 220)], fill=c, width=8)

        # TR
        draw.line([(3660, 100), (3540, 100)], fill=c, width=8)
        draw.line([(3660, 100), (3660, 220)], fill=c, width=8)

        # BL
        draw.line([(180, 1280), (300, 1280)], fill=c, width=8)
        draw.line([(180, 1280), (180, 1160)], fill=c, width=8)

        # BR
        draw.line([(3660, 1280), (3540, 1280)], fill=c, width=8)
        draw.line([(3660, 1280), (3660, 1160)], fill=c, width=8)

        # =====================================
        # FONTS
        # =====================================

        title_font = ImageFont.truetype(
            FONT_BOLD,
            120
        )

        medium_font = ImageFont.truetype(
            FONT_BOLD,
            75
        )

        small_font = ImageFont.truetype(
            FONT_REGULAR,
            58
        )

        # =====================================
        # BOT NAME
        # =====================================

        bot_width = draw.textlength(
            BOT_NAME,
            font=medium_font
        )

        draw.text(
            (
                3200 - bot_width,
                1040
            ),
            BOT_NAME,
            font=medium_font,
            fill=(255, 0, 0)
        )

        # =====================================
        # WAVEFORM
        # =====================================

        wave_y = 1740

        for x in range(300, 3400, 20):

            h = random.randint(20, 120)

            draw.line(
                [
                    (x, wave_y - h // 2),
                    (x, wave_y + h // 2)
                ],
                fill=(255, 255, 255),
                width=8
            )

        # =====================================
        # PROGRESS BAR
        # =====================================

        line_y = 1890

        draw.line(
            [(300, line_y), (3450, line_y)],
            fill=(150, 150, 150),
            width=14
        )

        draw.line(
            [(300, line_y), (1300, line_y)],
            fill=(255, 255, 255),
            width=16
        )

        draw.ellipse(
            (
                1270,
                line_y - 24,
                1320,
                line_y + 24
            ),
            fill="white"
        )

        # =====================================
        # TIME
        # =====================================

        draw.text(
            (300, 1940),
            "00:00",
            font=small_font,
            fill="white"
        )

        draw.text(
            (3250, 1940),
            duration,
            font=small_font,
            fill="white"
        )

        # =====================================
        # CONTROLS
        # =====================================

        control_font = ImageFont.truetype(
            FONT_BOLD,
            130
        )

        draw.text(
            (1450, 1980),
            "⏮",
            font=control_font,
            fill="white"
        )

        draw.text(
            (1820, 1960),
            "⏸",
            font=control_font,
            fill="white"
        )

        draw.text(
            (2200, 1980),
            "⏭",
            font=control_font,
            fill="white"
        )

        # =====================================
        # REQUESTED BY
        # =====================================

        req_font = ImageFont.truetype(
            FONT_BOLD,
            70
        )

        req_text = f"Requested by : {user_name}"

        draw.text(
            (300, 1040),
            req_text,
            font=req_font,
            fill="white"
        )

        # =====================================
        # SAVE
        # =====================================

        output = CACHE_DIR / f"{videoid}_final.png"

        canvas.save(
            output,
            quality=100
        )

        # =====================================
        # DELETE TEMP
        # =====================================

        try:
            os.remove(thumb_path)
        except:
            pass

        return str(output)

    except Exception as e:

        print(f"[THUMB ERROR] {e}")

        traceback.print_exc()

        return None
