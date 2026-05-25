# =========================
# FIXED PREMIUM THUMBNAIL
# =========================

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

# =========================
# CACHE
# =========================

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# =========================
# SIZE
# =========================

CANVAS_W = 1280
CANVAS_H = 720

# =========================
# FONTS
# =========================

FONT_BOLD = "ShrutiMusic/assets/font3.ttf"
FONT_REGULAR = "ShrutiMusic/assets/font2.ttf"

# =========================
# THUMB GENERATOR
# =========================

async def gen_thumb(videoid: str):

    try:

        # =========================
        # FETCH YOUTUBE DATA
        # =========================

        url = f"https://www.youtube.com/watch?v={videoid}"

        results = VideosSearch(url, limit=1)

        result = (await results.next())["result"][0]

        title = result.get(
            "title",
            "Unknown Song"
        )[:28]

        duration = result.get(
            "duration",
            "2:30"
        )

        views = result.get(
            "viewCount",
            {}
        ).get(
            "short",
            "1M"
        )

        channel = result.get(
            "channel",
            {}
        ).get(
            "name",
            "YouTube"
        )

        thumburl = result["thumbnails"][0]["url"].split("?")[0]

        # =========================
        # DOWNLOAD THUMB
        # =========================

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

        # =========================
        # OPEN IMAGE
        # =========================

        base = Image.open(
            thumb_path
        ).convert("RGB")

        # =========================
        # BACKGROUND
        # =========================

        bg = base.resize(
            (CANVAS_W, CANVAS_H)
        )

        bg = bg.filter(
            ImageFilter.GaussianBlur(30)
        )

        bg = ImageEnhance.Brightness(
            bg
        ).enhance(0.22)

        canvas = bg.convert("RGBA")

        # =========================
        # RED DARK OVERLAY
        # =========================

        overlay = Image.new(
            "RGBA",
            (CANVAS_W, CANVAS_H),
            (25, 0, 0, 160)
        )

        canvas = Image.alpha_composite(
            canvas,
            overlay
        )

        draw = ImageDraw.Draw(canvas)

        # =========================
        # PLAYER BOX
        # =========================

        box_x = 70
        box_y = 40
        box_w = 1140
        box_h = 420

        draw.rounded_rectangle(
            (
                box_x,
                box_y,
                box_x + box_w,
                box_y + box_h
            ),
            radius=10,
            fill=(255, 255, 255, 70),
            outline=(255, 220, 220),
            width=3
        )

        # =========================
        # THUMB IMAGE
        # =========================

        thumb = base.resize((620, 360))

        thumb_x = 330
        thumb_y = 50

        canvas.paste(
            thumb,
            (thumb_x, thumb_y)
        )

        # =========================
        # BLACK FADE
        # =========================

        fade = Image.new(
            "RGBA",
            (box_w, 150),
            (0, 0, 0, 0)
        )

        fd = ImageDraw.Draw(fade)

        for y in range(150):

            alpha = int((y / 150) * 255)

            fd.line(
                [(0, y), (box_w, y)],
                fill=(0, 0, 0, alpha)
            )

        canvas.paste(
            fade,
            (box_x, box_y + 270),
            fade
        )

        # =========================
        # CORNERS
        # =========================

        c = (255, 220, 220)

        # top left
        draw.line([(70, 40), (110, 40)], fill=c, width=4)
        draw.line([(70, 40), (70, 80)], fill=c, width=4)

        # top right
        draw.line([(1210, 40), (1170, 40)], fill=c, width=4)
        draw.line([(1210, 40), (1210, 80)], fill=c, width=4)

        # bottom left
        draw.line([(70, 460), (110, 460)], fill=c, width=4)
        draw.line([(70, 460), (70, 420)], fill=c, width=4)

        # bottom right
        draw.line([(1210, 460), (1170, 460)], fill=c, width=4)
        draw.line([(1210, 460), (1210, 420)], fill=c, width=4)

        # =========================
        # FONTS
        # =========================

        title_font = ImageFont.truetype(
            FONT_BOLD,
            54
        )

        medium_font = ImageFont.truetype(
            FONT_BOLD,
            30
        )

        small_font = ImageFont.truetype(
            FONT_REGULAR,
            24
        )

        # =========================
        # BOTTOM INFO
        # =========================

        draw.text(
            (100, 365),
            "Artist",
            font=small_font,
            fill=(220, 220, 220)
        )

        draw.text(
            (100, 405),
            channel[:15],
            font=medium_font,
            fill="white"
        )

        draw.text(
            (560, 365),
            "Views",
            font=small_font,
            fill=(220, 220, 220)
        )

        draw.text(
            (560, 405),
            f"{views} views",
            font=medium_font,
            fill="white"
        )

        # =========================
        # YOUR BOT NAME
        # =========================

        draw.text(
            (930, 395),
            "𝐊𝐀𝐓𝐈𝐋 𝐌𝐔𝐒𝐈𝐂 🎧",
            font=medium_font,
            fill=(255, 220, 220)
        )

        # =========================
        # SONG TITLE
        # =========================

        title_width = draw.textlength(
            title,
            font=title_font
        )

        draw.text(
            (
                (CANVAS_W - title_width) / 2,
                500
            ),
            title,
            font=title_font,
            fill=(90, 0, 0)
        )

        # =========================
        # WAVEFORM
        # =========================

        wave_y = 575

        for x in range(100, 1130, 10):

            h = random.randint(8, 40)

            draw.line(
                [
                    (x, wave_y - h // 2),
                    (x, wave_y + h // 2)
                ],
                fill=(120, 0, 0),
                width=4
            )

        # =========================
        # PROGRESS BAR
        # =========================

        line_y = 630

        draw.line(
            [(100, line_y), (1150, line_y)],
            fill=(80, 30, 30),
            width=6
        )

        draw.line(
            [(100, line_y), (420, line_y)],
            fill=(255, 0, 0),
            width=7
        )

        draw.ellipse(
            (
                410,
                line_y - 10,
                430,
                line_y + 10
            ),
            fill=(255, 0, 0)
        )

        # =========================
        # TIME
        # =========================

        draw.text(
            (100, 650),
            "00:00",
            font=small_font,
            fill=(70, 0, 0)
        )

        draw.text(
            (1110, 650),
            duration,
            font=small_font,
            fill=(70, 0, 0)
        )

        # =========================
        # CONTROLS
        # =========================

        draw.text(
            (520, 675),
            "◀",
            font=title_font,
            fill=(60, 0, 0)
        )

        draw.text(
            (610, 665),
            "⏸",
            font=title_font,
            fill=(60, 0, 0)
        )

        draw.text(
            (720, 675),
            "▶",
            font=title_font,
            fill=(60, 0, 0)
        )

        # =========================
        # REQUESTED BY
        # =========================

        draw.text(
            (470, 730),
            "Requested by : KATIL",
            font=medium_font,
            fill=(60, 0, 0)
        )

        # =========================
        # SAVE
        # =========================

        output = CACHE_DIR / f"{videoid}_final.png"

        canvas.save(output)

        # =========================
        # DELETE TEMP
        # =========================

        try:
            os.remove(thumb_path)
        except:
            pass

        return str(output)

    except Exception as e:

        print(f"[THUMB ERROR] {e}")

        traceback.print_exc()

        return None
