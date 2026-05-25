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
# CANVAS SIZE
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
            "Bairan"
        )[:20]

        duration = result.get(
            "duration",
            "2:31"
        )

        views = result.get(
            "viewCount",
            {}
        ).get(
            "short",
            "60.2M"
        )

        channel = result.get(
            "channel",
            {}
        ).get(
            "name",
            "Banjaare"
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
            ImageFilter.GaussianBlur(25)
        )

        bg = ImageEnhance.Brightness(
            bg
        ).enhance(0.30)

        canvas = bg.convert("RGBA")

        # =========================
        # RED OVERLAY
        # =========================

        red = Image.new(
            "RGBA",
            (CANVAS_W, CANVAS_H),
            (35, 0, 0, 130)
        )

        canvas = Image.alpha_composite(
            canvas,
            red
        )

        draw = ImageDraw.Draw(canvas)

        # =========================
        # MAIN PLAYER BOX
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
            radius=8,
            fill=(20, 0, 0, 100),
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
            (box_w, 140),
            (0, 0, 0, 0)
        )

        fd = ImageDraw.Draw(fade)

        for y in range(140):

            alpha = int((y / 140) * 240)

            fd.line(
                [(0, y), (box_w, y)],
                fill=(0, 0, 0, alpha)
            )

        canvas.paste(
            fade,
            (box_x, box_y + 280),
            fade
        )

        # =========================
        # CORNER LINES
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
            50
        )

        medium_font = ImageFont.truetype(
            FONT_BOLD,
            28
        )

        small_font = ImageFont.truetype(
            FONT_REGULAR,
            22
        )

        # =========================
        # ARTIST
        # =========================

        draw.text(
            (100, 365),
            "Artist",
            font=small_font,
            fill=(210, 210, 210)
        )

        draw.text(
            (100, 400),
            channel[:15],
            font=medium_font,
            fill="white"
        )

        # =========================
        # VIEWS
        # =========================

        draw.text(
            (560, 365),
            "Views",
            font=small_font,
            fill=(210, 210, 210)
        )

        draw.text(
            (560, 400),
            views,
            font=medium_font,
            fill="white"
        )

        # =========================
        # BRAND
        # =========================

        draw.text(
            (1010, 390),
            "Void x Music",
            font=medium_font,
            fill=(255, 220, 220)
        )

        # =========================
        # SONG TITLE
        # =========================

        draw.text(
            (540, 500),
            title,
            font=title_font,
            fill=(40, 0, 0)
        )

        # =========================
        # WAVEFORM
        # =========================

        wave_y = 570

        for x in range(100, 1030, 10):

            h = random.randint(10, 45)

            draw.line(
                [
                    (x, wave_y - h // 2),
                    (x, wave_y + h // 2)
                ],
                fill=(80, 0, 0),
                width=4
            )

        # =========================
        # PROGRESS BAR
        # =========================

        line_y = 620

        draw.line(
            [(100, line_y), (1150, line_y)],
            fill=(80, 20, 20),
            width=6
        )

        draw.line(
            [(100, line_y), (420, line_y)],
            fill=(120, 0, 0),
            width=7
        )

        draw.ellipse(
            (
                410,
                line_y - 10,
                430,
                line_y + 10
            ),
            fill=(50, 0, 0)
        )

        # =========================
        # TIME
        # =========================

        draw.text(
            (100, 640),
            "00:00",
            font=small_font,
            fill=(40, 0, 0)
        )

        draw.text(
            (1110, 640),
            duration,
            font=small_font,
            fill=(40, 0, 0)
        )

        # =========================
        # CONTROLS
        # =========================

        draw.text(
            (500, 675),
            "◀",
            font=title_font,
            fill=(40, 0, 0)
        )

        draw.text(
            (610, 665),
            "⏸",
            font=title_font,
            fill=(40, 0, 0)
        )

        draw.text(
            (730, 675),
            "▶",
            font=title_font,
            fill=(40, 0, 0)
        )

        # =========================
        # REQUESTED BY
        # =========================

        draw.text(
            (500, 735),
            "Requested by : KATIL",
            font=medium_font,
            fill=(40, 0, 0)
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
