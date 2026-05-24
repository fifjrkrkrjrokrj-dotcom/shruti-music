# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar
#
# All rights reserved.
#
# This code is the intellectual property of Nand Yaduwanshi.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: badboy809075@gmail.com
#
# ATLEAST GIVE CREDITS IF YOU STEALING :
# ELSE NO FURTHER PUBLIC THUMBNAIL UPDATES

import os
import random
import aiohttp
import aiofiles
import traceback
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from py_yt import VideosSearch
from ShrutiMusic import app
import math

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Helper Function: Time to Seconds (For dynamic playbar)
def time_to_sec(time_str):
    if not time_str or time_str == "LIVE":
        return 0
    parts = time_str.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 1 and parts[0].isdigit():
        return int(parts[0])
    return 0

# 🟢 Helper Function: Filled Mask
def get_filled_mask(size, coords, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(coords, radius=radius, fill=255)
    return mask

# 🟢 Helper Function: Border Mask (Safe for all Pillow versions)
def get_border_mask(size, coords, radius, width):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    x0, y0, x1, y1 = coords
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=255)
    draw.rounded_rectangle([x0+width, y0+width, x1-width, y1-width], radius=max(1, radius-width), fill=0)
    return mask

# Helper function: Crop image into a square
def crop_to_square(img):
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    return img.crop((left, top, right, bottom))

# Helper function: Fallback Image
def get_random_fallback_img():
    if YOUTUBE_IMG_URL:
        if isinstance(YOUTUBE_IMG_URL, list):
            return random.choice(YOUTUBE_IMG_URL)
        return YOUTUBE_IMG_URL
    return "https://telegra.ph/file/2e3d368e77c449c287430.jpg"

async def get_thumb(videoid: str, player_username: str = None) -> str:
    path = os.path.join(CACHE_DIR, f"{videoid}_play.png")
    if os.path.exists(path):
        return path

    try:
        search_url = f"https://www.youtube.com/watch?v={videoid}"
        vs = VideosSearch(search_url, limit=1)
        result = await vs.next()
        data = result["result"][0]
        title = data.get("title", "Unknown Track")
        thumb_url = data["thumbnails"][0]["url"].split("?")[0]
        duration = data.get("duration", "LIVE")
        channel = data.get("channel", {}).get("name", "Unknown Artist")
    except Exception as e:
        title, duration, channel = "Unknown Track", "LIVE", "Unknown Artist"
        thumb_url = get_random_fallback_img()

    temp_img = os.path.join(CACHE_DIR, f"{videoid}_temp.png")
    downloaded = False

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(thumb_url) as r:
                if r.status == 200:
                    async with aiofiles.open(temp_img, "wb") as f:
                        await f.write(await r.read())
                    downloaded = True
    except Exception:
        pass

    if not downloaded:
        return get_random_fallback_img()

    try:
        original_img = Image.open(temp_img).convert("RGBA")
        
        # ==========================================
        # 🟢 STEP 1: BACKGROUND PREPARATION
        # ==========================================
        bg_out = original_img.resize((1280, 720))
        bg_out = bg_out.filter(ImageFilter.GaussianBlur(10)) 
        bg_out = ImageEnhance.Brightness(bg_out).enhance(1.0)
        
        bg_in = original_img.resize((1280, 720))
        bg_in = bg_in.filter(ImageFilter.GaussianBlur(20)) 
        bg_in = ImageEnhance.Brightness(bg_in).enhance(0.7) 

        card_coords = (220, 140, 1060, 580)
        card_radius = 35

        shadow_mask = get_filled_mask((1280, 720), [220+8, 140+8, 1060+8, 580+8], 35)
        shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(10))
        shadow_img = Image.new("RGBA", (1280, 720), (0, 0, 0, 100))
        shadow_img.putalpha(shadow_mask)
        bg_out.paste(shadow_img, (0, 0), shadow_img)

        mask_in = get_filled_mask((1280, 720), card_coords, card_radius)
        bg_final = Image.composite(bg_in, bg_out, mask_in)

        draw = ImageDraw.Draw(bg_final, "RGBA")

        # ==========================================
        # 🟢 STEP 2: MULTI-COLOR NEON GRADIENT BORDER
        # ==========================================
        grad = Image.new('RGBA', (1280, 720))
        draw_g = ImageDraw.Draw(grad)
        colors = [(0, 255, 255, 255), (255, 20, 147, 255), (57, 255, 20, 255), (255, 215, 0, 255), (138, 43, 226, 255), (0, 255, 255, 255)]
        step = 1280 / (len(colors) - 1)
        for i in range(len(colors) - 1):
            draw_g.rectangle([int(i*step), 0, int((i+1)*step), 720], fill=colors[i])
        grad = grad.filter(ImageFilter.GaussianBlur(150)) 

        mask_glow = get_border_mask((1280, 720), card_coords, card_radius, width=12).filter(ImageFilter.GaussianBlur(8))
        glow_grad = grad.copy()
        glow_grad.putalpha(mask_glow)
        bg_final.paste(glow_grad, (0, 0), glow_grad)

        mask_border = get_border_mask((1280, 720), card_coords, card_radius, width=4)
        sharp_grad = grad.copy()
        sharp_grad.putalpha(mask_border)
        bg_final.paste(sharp_grad, (0, 0), sharp_grad)

        # ==========================================
        # 🟢 STEP 3: SQUARE THUMBNAIL 
        # ==========================================
        thumb_coords = (260, 190, 600, 530)
        sq_img = crop_to_square(original_img).resize((340, 340))
        mask_thumb = Image.new("L", (340, 340), 0)
        ImageDraw.Draw(mask_thumb).rounded_rectangle((0, 0, 340, 340), radius=25, fill=255)
        sq_img.putalpha(mask_thumb)
        bg_final.paste(sq_img, (260, 190), sq_img)

        mask_thumb_glow = get_border_mask((1280, 720), thumb_coords, radius=25, width=10).filter(ImageFilter.GaussianBlur(6))
        thumb_glow_grad = grad.copy()
        thumb_glow_grad.putalpha(mask_thumb_glow)
        bg_final.paste(thumb_glow_grad, (0, 0), thumb_glow_grad)

        mask_thumb_border = get_border_mask((1280, 720), thumb_coords, radius=25, width=3)
        thumb_sharp_grad = grad.copy()
        thumb_sharp_grad.putalpha(mask_thumb_border)
        bg_final.paste(thumb_sharp_grad, (0, 0), thumb_sharp_grad)

        # ==========================================
        # 🟢 STEP 4: TEXT (SMALL FONT + BOUNDARY STRICT)
        # ==========================================
        try:
            title_font = ImageFont.truetype("PritiMusic/assets/font.ttf", 36)
            artist_font = ImageFont.truetype("PritiMusic/assets/font2.ttf", 24)
            time_font = ImageFont.truetype("PritiMusic/assets/font2.ttf", 20)
        except:
            title_font = artist_font = time_font = ImageFont.load_default()

        text_x = 640
        display_title = (title[:20] + "..." if len(title) > 20 else title).upper()
        display_channel = channel[:26] + "..." if len(channel) > 26 else channel

        draw.text((text_x, 235), display_title, font=title_font, fill="white")
        draw.text((text_x, 295), display_channel, font=artist_font, fill=(210, 210, 210, 255))

        # ==========================================
        # 🟢 STEP 5: MULTI-COLOR GRADIENT PLAYBAR & TIMESTAMPS
        # ==========================================
        bar_y = 400
        
        progress = random.uniform(0.10, 0.85)
        play_width = 380  
        end_x = int(text_x + (play_width * progress))

        if duration != "LIVE":
            total_sec = time_to_sec(duration)
            curr_sec = int(total_sec * progress)
            h, m, s = curr_sec // 3600, (curr_sec % 3600) // 60, curr_sec % 60
            current_time = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        else:
            current_time = "LIVE"
            end_x = 1020 

        end_x = max(text_x + 10, end_x) # Prevent glitch on 0 progress

        # 1. Background Track (Grey)
        draw.rounded_rectangle([(text_x, bar_y-3), (1020, bar_y+3)], radius=3, fill=(200, 200, 200, 150))
        
        # 2. 🟢 THE MAGIC: Gradient Colored Playbar
        mask_playbar = Image.new("L", (1280, 720), 0)
        ImageDraw.Draw(mask_playbar).rounded_rectangle([(text_x, bar_y-3), (end_x, bar_y+3)], radius=3, fill=255)
        playbar_grad = grad.copy()
        playbar_grad.putalpha(mask_playbar)
        bg_final.paste(playbar_grad, (0, 0), playbar_grad)

        # 3. Solid White Knob
        draw.ellipse([(end_x - 8, bar_y - 8), (end_x + 8, bar_y + 8)], fill="white") 

        # Timestamps
        draw.text((text_x, 420), current_time, font=time_font, fill=(240, 240, 240, 255))
        try:
            dur_w = time_font.getlength(duration)
        except:
            dur_w = 45
        draw.text((1020 - dur_w, 420), duration, font=time_font, fill=(240, 240, 240, 255))

        # ==========================================
        # 🟢 STEP 6: PLAYER CONTROLS (7 ICONS)
        # ==========================================
        icon_y = 500
        gap = 56 
        
        x = text_x
        draw.line([(x-12, icon_y-6), (x-4, icon_y-6), (x+4, icon_y+6), (x+12, icon_y+6)], fill=(50, 255, 150, 255), width=3)
        draw.line([(x-12, icon_y+6), (x-4, icon_y+6), (x+4, icon_y-6), (x+12, icon_y-6)], fill=(50, 255, 150, 255), width=3)
        draw.polygon([(x+12, icon_y+6), (x+6, icon_y+2), (x+14, icon_y-1)], fill=(50, 255, 150, 255)) 

        x = text_x + gap
        draw.arc([x-12, icon_y-10, x+12, icon_y+10], start=40, end=320, fill=(255, 200, 50, 255), width=3)
        draw.polygon([(x+8, icon_y-8), (x+16, icon_y-8), (x+12, icon_y-14)], fill=(255, 200, 50, 255))

        x = text_x + gap * 2
        draw.rectangle([(x-14, icon_y-10), (x-10, icon_y+10)], fill="white")
        draw.polygon([(x-10, icon_y), (x+2, icon_y-10), (x+2, icon_y+10)], fill="white")
        draw.polygon([(x+2, icon_y), (x+14, icon_y-10), (x+14, icon_y+10)], fill="white")

        x = text_x + gap * 3
        draw.rectangle([(x-8, icon_y-12), (x-2, icon_y+12)], fill="white")
        draw.rectangle([(x+2, icon_y-12), (x+8, icon_y+12)], fill="white")

        x = text_x + gap * 4
        draw.polygon([(x-14, icon_y-10), (x-14, icon_y+10), (x-2, icon_y)], fill="white")
        draw.polygon([(x-2, icon_y-10), (x-2, icon_y+10), (x+10, icon_y)], fill="white")
        draw.rectangle([(x+10, icon_y-10), (x+14, icon_y+10)], fill="white")

        x = text_x + gap * 5
        draw.polygon([(x-12, icon_y-2), (x+12, icon_y-2), (x, icon_y+14)], fill=(255, 60, 60, 255))
        draw.ellipse([(x-12, icon_y-12), (x, icon_y+2)], fill=(255, 60, 60, 255))
        draw.ellipse([(x, icon_y-12), (x+12, icon_y+2)], fill=(255, 60, 60, 255))

        x = text_x + gap * 6
        draw.arc([x-14, icon_y-14, x+14, icon_y+6], start=180, end=0, fill="white", width=3)
        draw.rounded_rectangle([x-16, icon_y-2, x-8, icon_y+10], radius=3, fill="white")
        draw.rounded_rectangle([x+8, icon_y-2, x+16, icon_y+10], radius=3, fill="white")

        # Save Final Image
        bg_final.convert("RGB").save(path)

    except Exception as e:
        print(f"Thumbnail UI Error: {e}")
        return thumb_url if isinstance(thumb_url, str) else get_random_fallback_img()
        
    finally:
        if os.path.exists(temp_img):
            os.remove(temp_img)
            
    return path
