# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>

import os
import aiohttp
import aiofiles
import traceback
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from py_yt import VideosSearch
from ShrutiMusic import app

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

CANVAS_W, CANVAS_H = 1320, 760

FONT_REGULAR_PATH = "ShrutiMusic/assets/font2.ttf"
FONT_BOLD_PATH = "ShrutiMusic/assets/font3.ttf"
DEFAULT_THUMB = "ShrutiMusic/assets/ShrutiBots.jpg"


async def gen_thumb(videoid: str):

    url = f"https://www.youtube.com/watch?v={videoid}"
    thumb_path = None

    try:
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]

        title = result.get("title", "Unknown Title")
        duration = result.get("duration", "3:49")
        thumburl = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "38.4M")
        channel = result.get("channel", {}).get("name", "Sonu Nigam")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumburl) as resp:
                    if resp.status == 200:
                        thumb_path = CACHE_DIR / f"thumb{videoid}.png"

                        async with aiofiles.open(thumb_path, "wb") as f:
                            await f.write(await resp.read())

        except:
            pass

        if thumb_path and thumb_path.exists():
            base_img = Image.open(thumb_path).convert("RGBA")
        else:
            base_img = Image.open(DEFAULT_THUMB).convert("RGBA")

    except Exception as e:
        print(f"[Thumbnail Error] {e}")

        try:
            base_img = Image.open(DEFAULT_THUMB).convert("RGBA")

            title = "Dil Dooba"
            duration = "3:49"
            views = "38.4M"
            channel = "Sonu Nigam"

        except:
            traceback.print_exc()
            return None

    try:

        # ===== MAIN CANVAS =====

        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 255))

        # ===== BLURRED BACKGROUND =====

        bg = base_img.resize((CANVAS_W, CANVAS_H))
        bg = bg.filter(ImageFilter.GaussianBlur(25))
        bg = ImageEnhance.Brightness(bg).enhance(0.35)

        canvas.paste(bg, (0, 0))

        overlay = Image.new(
            "RGBA",
            (CANVAS_W, CANVAS_H),
            (40, 0, 0, 120)
        )

        canvas = Image.alpha_composite(canvas, overlay)

        draw = ImageDraw.Draw(canvas)

        # ===== PLAYER CARD =====

        card_x = 70
        card_y = 40
        card_w = 1180
        card_h = 520

        draw.rounded_rectangle(
            [
                card_x,
                card_y,
                card_x + card_w,
                card_y + card_h
            ],
            radius=18,
            fill=(20, 0, 0, 170),
            outline=(255, 200, 200, 120),
            width=3
        )

        # ===== THUMBNAIL =====

        thumb = base_img.resize((650, 360))

        thumb_x = card_x + 265
        thumb_y = card_y + 20

        canvas.paste(thumb, (thumb_x, thumb_y))

        # ===== BLACK FADE =====

        fade = Image.new("RGBA", (card_w, 180), (0, 0, 0, 0))
        fdraw = ImageDraw.Draw(fade)

        for y in range(180):
            alpha = int((y / 180) * 230)

            fdraw.line(
                [(0, y), (card_w, y)],
                fill=(0, 0, 0, alpha)
            )

        canvas.paste(
            fade,
            (card_x, card_y + card_h - 180),
            fade
        )

        # ===== FONTS =====

        title_font = ImageFont.truetype(FONT_BOLD_PATH, 52)
        meta_font = ImageFont.truetype(FONT_BOLD_PATH, 34)
        small_font = ImageFont.truetype(FONT_REGULAR_PATH, 28)

        # ===== SONG TITLE =====

        song_y = card_y + card_h + 35

        draw.text(
            (CANVAS_W // 2 - 140, song_y),
            title[:25],
            font=title_font,
            fill=(20, 0, 0)
        )

        # ===== ARTIST =====

        draw.text(
            (110, card_y + 430),
            "Artist",
            font=small_font,
            fill=(200, 200, 200)
        )

        draw.text(
            (110, card_y + 470),
            channel[:20],
            font=meta_font,
            fill=(255, 255, 255)
        )

        # ===== VIEWS =====

        draw.text(
            (600, card_y + 430),
            "Views",
            font=small_font,
            fill=(200, 200, 200)
        )

        draw.text(
            (600, card_y + 470),
            views,
            font=meta_font,
            fill=(255, 255, 255)
        )

        # ===== BRANDING =====

        draw.text(
            (1020, card_y + 450),
            f"{app.username}",
            font=small_font,
            fill=(255, 220, 220)
        )

        # ===== CORNER LINES =====

        line_color = (255, 200, 200)

        # top left
        draw.line([(70, 40), (110, 40)], fill=line_color, width=3)
        draw.line([(70, 40), (70, 80)], fill=line_color, width=3)

        # top right
        draw.line([(1240, 40), (1200, 40)], fill=line_color, width=3)
        draw.line([(1240, 40), (1240, 80)], fill=line_color, width=3)

        # bottom left
        draw.line([(70, 560), (110, 560)], fill=line_color, width=3)
        draw.line([(70, 560), (70, 520)], fill=line_color, width=3)

        # bottom right
        draw.line([(1240, 560), (1200, 560)], fill=line_color, width=3)
        draw.line([(1240, 560), (1240, 520)], fill=line_color, width=3)

        # ===== WAVEFORM =====

        wave_y = song_y + 70

        start_x = 120
        end_x = 1100

        import random

        for x in range(start_x, end_x, 8):

            bar_height = random.randint(10, 45)

            draw.line(
                [
                    (x, wave_y - bar_height // 2),
                    (x, wave_y + bar_height // 2)
                ],
                fill=(120, 0, 0),
                width=4
            )

        # ===== PROGRESS BAR =====

        bar_y = wave_y + 40

        draw.line(
            [(120, bar_y), (1200, bar_y)],
            fill=(60, 20, 20),
            width=8
        )

        draw.line(
            [(120, bar_y), (450, bar_y)],
            fill=(120, 0, 0),
            width=8
        )

        draw.ellipse(
            [440, bar_y - 10, 460, bar_y + 10],
            fill=(0, 0, 0)
        )

        # ===== TIME =====

        draw.text(
            (110, bar_y + 15),
            "00:00",
            font=small_font,
            fill="black"
        )

        draw.text(
            (1150, bar_y + 15),
            duration,
            font=small_font,
            fill="black"
        )

        # ===== CONTROL BUTTONS =====

        controls_y = bar_y + 65

        draw.text(
            (CANVAS_W // 2 - 80, controls_y),
            "◀",
            font=title_font,
            fill="black"
        )

        draw.text(
            (CANVAS_W // 2 - 20, controls_y),
            "⏸",
            font=title_font,
            fill=(120, 0, 0)
        )

        draw.text(
            (CANVAS_W // 2 + 50, controls_y),
            "▶",
            font=title_font,
            fill="black"
        )

        # ===== REQUESTED BY =====

        draw.text(
            (CANVAS_W // 2 - 120, controls_y + 65),
            "Requested by : KATIL",
            font=small_font,
            fill=(0, 0, 0)
        )

        # ===== SAVE =====

        out = CACHE_DIR / f"{videoid}_final.png"

        canvas.save(
            out,
            quality=95,
            optimize=True
        )

        # delete temp thumb
        if thumb_path and thumb_path.exists():
            try:
                os.remove(thumb_path)
            except:
                pass

        return str(out)

    except Exception as e:
        print(f"[Processing Error] {e}")
        traceback.print_exc()
        return None
