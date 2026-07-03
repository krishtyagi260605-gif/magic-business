import os
from PIL import Image, ImageDraw
from utils.fonts import get_pil_font
from utils.colors import hex_to_rgb, get_text_color_for_background

def draw_artistic_background(img: Image.Image, brand_color_hex: str):
    """Draw a rich artistic background for the poster."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    brand_rgb = hex_to_rgb(brand_color_hex)
    
    # Base fill
    draw.rectangle([0, 0, w, h], fill=brand_rgb)
    
    # Draw geometric accent layers
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw_o = ImageDraw.Draw(overlay)
    
    # Diagonal stripe shapes
    draw_o.polygon([(0, 0), (w * 0.4, 0), (0, h * 0.4)], fill=(255, 255, 255, 25))
    draw_o.polygon([(w, h), (w * 0.6, h), (w, h * 0.6)], fill=(0, 0, 0, 30))
    
    # Big glowing ring in center
    draw_o.ellipse([w//2 - 400, h//2 - 400, w//2 + 400, h//2 + 400], outline=(255, 255, 255, 20), width=4)
    draw_o.ellipse([w//2 - 420, h//2 - 420, w//2 + 420, h//2 + 420], outline=(255, 255, 255, 10), width=2)
    
    img.alpha_composite(overlay)

def generate_poster(
    business_name: str,
    address: str = "",
    brand_color_hex: str = "#2563EB",
    logo_path: str = None,
    output_dir: str = ""
) -> dict:
    """
    Generate 'WE'RE OPEN' poster in 1080x1080px PNG format.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    w, h = 1080, 1080
    poster = Image.new("RGBA", (w, h))
    draw_artistic_background(poster, brand_color_hex)
    draw = ImageDraw.Draw(poster)
    
    brand_rgb = hex_to_rgb(brand_color_hex)
    text_color_hex = get_text_color_for_background(brand_color_hex)
    text_color = (255, 255, 255, 255) if text_color_hex == "#FFFFFF" else (0, 0, 0, 255)
    accent_text_color = (254, 240, 138, 255) if text_color_hex == "#FFFFFF" else brand_rgb + (255,) # Yellow or brand color
    
    # Draw double inner frame border
    draw.rectangle([50, 50, w - 50, h - 50], outline=text_color, width=3)
    draw.rectangle([65, 65, w - 65, h - 65], outline=accent_text_color, width=1)
    
    # Logo placement at top
    y = 120
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((160, 160), Image.Resampling.LANCZOS)
            lw, lh = logo.size
            poster.alpha_composite(logo, ((w - lw)//2, y))
            y += lh + 50
        except Exception:
            pass
            
    # Announcement small heading
    font_sub = get_pil_font('inter_bold', 28)
    sub_text = "HELLO NEIGHBOR!"
    sbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sbox[2] - sbox[0]
    draw.text(((w - sw)//2 - sbox[0], y), sub_text, fill=accent_text_color, font=font_sub)
    
    # Giant WE'RE OPEN header
    y += 70
    font_giant = get_pil_font('montserrat_bold', 96)
    main_text = "WE'RE OPEN"
    gbox = draw.textbbox((0, 0), main_text, font=font_giant)
    gw = gbox[2] - gbox[0]
    draw.text(((w - gw)//2 - gbox[0], y), main_text, fill=text_color, font=font_giant)
    
    # Divider bar
    y += 150
    draw.rectangle([w//2 - 200, y, w//2 + 200, y + 6], fill=accent_text_color)
    
    # Business name
    y += 50
    font_biz = get_pil_font('montserrat_bold', 52)
    bbox_biz = draw.textbbox((0, 0), business_name, font=font_biz)
    bw = bbox_biz[2] - bbox_biz[0]
    draw.text(((w - bw)//2 - bbox_biz[0], y), business_name, fill=text_color, font=font_biz)
    
    # Hours default text
    y += 100
    font_hours = get_pil_font('inter_bold', 24)
    hours_text = "Timings: 09:00 AM - 09:00 PM  |  Open All 7 Days"
    hbox = draw.textbbox((0, 0), hours_text, font=font_hours)
    hw = hbox[2] - hbox[0]
    draw.text(((w - hw)//2 - hbox[0], y), hours_text, fill=accent_text_color, font=font_hours)
    
    # Address details at the bottom
    if address:
        y += 80
        font_addr = get_pil_font('inter_regular', 20)
        # Handle simple wrapping if too long
        cleaned_addr = address.replace('\n', ', ')
        if len(cleaned_addr) > 65:
            cleaned_addr = cleaned_addr[:62] + "..."
        abox = draw.textbbox((0, 0), cleaned_addr, font=font_addr)
        aw = abox[2] - abox[0]
        draw.text(((w - aw)//2 - abox[0], y), cleaned_addr, fill=text_color, font=font_addr)
        
    # Standard footer credit
    font_f = get_pil_font('inter_regular', 14)
    f_text = "Powered by Magic Business Platform"
    fbox = draw.textbbox((0, 0), f_text, font=font_f)
    fw = fbox[2] - fbox[0]
    draw.text(((w - fw)//2 - fbox[0], h - 110), f_text, fill=text_color, font=font_f)
    
    poster_path = os.path.join(output_dir, "poster_open.png")
    poster.convert("RGB").save(poster_path, "PNG")
    generated_files["poster_open"] = "poster_open.png"
    
    return generated_files
