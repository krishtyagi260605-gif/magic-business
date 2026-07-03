import os
from PIL import Image, ImageDraw
from utils.fonts import get_pil_font
from utils.colors import hex_to_rgb, get_text_color_for_background

def draw_soft_background(img: Image.Image, brand_color_hex: str):
    """Draw a solid brand color background with subtle lighter/darker lighting circles for premium depth."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    brand_rgb = hex_to_rgb(brand_color_hex)
    
    # Base fill
    draw.rectangle([0, 0, w, h], fill=brand_rgb)
    
    # Create translucent overlay circles for depth
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw_o = ImageDraw.Draw(overlay)
    
    # Lighter circle in top-left
    r1 = int(min(w, h) * 0.6)
    draw_o.ellipse([-r1//2, -r1//2, r1//2, r1//2], fill=(255, 255, 255, 40))
    
    # Darker circle in bottom-right
    r2 = int(min(w, h) * 0.7)
    draw_o.ellipse([w - r2//2, h - r2//2, w + r2//2, h + r2//2], fill=(0, 0, 0, 45))
    
    img.alpha_composite(overlay)

def generate_social_kit(
    business_name: str,
    tagline: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    services: list[str] = None,
    brand_color_hex: str = "#2563EB",
    logo_path: str = None,
    output_dir: str = ""
) -> dict:
    """
    Generate Instagram post, Facebook cover, and WhatsApp profile PNGs.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    # Determine text contrast colors
    text_color_hex = get_text_color_for_background(brand_color_hex)
    text_color_rgb = (255, 255, 255, 255) if text_color_hex == "#FFFFFF" else (0, 0, 0, 255)
    subtext_color_rgb = (226, 232, 240, 255) if text_color_hex == "#FFFFFF" else (71, 85, 105, 255)
    
    # Load logo
    logo = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
        except Exception as e:
            print(f"Error loading logo for social kit: {e}")
            
    # ---------------- A. INSTAGRAM POST (1080x1080) ----------------
    ig_w, ig_h = 1080, 1080
    ig = Image.new("RGBA", (ig_w, ig_h))
    draw_soft_background(ig, brand_color_hex)
    draw_ig = ImageDraw.Draw(ig)
    
    # Draw a thin double border line inside
    draw_ig.rectangle([40, 40, ig_w - 40, ig_h - 40], outline=text_color_rgb, width=2)
    draw_ig.rectangle([50, 50, ig_w - 50, ig_h - 50], outline=subtext_color_rgb, width=1)
    
    # Logo centered at top
    logo_y = 120
    if logo:
        logo_temp = logo.copy()
        logo_temp.thumbnail((180, 180), Image.Resampling.LANCZOS)
        lw, lh = logo_temp.size
        ig.alpha_composite(logo_temp, ((ig_w - lw)//2, logo_y))
        logo_y += lh + 40
    else:
        # Drawing a geometric text icon
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        font_init = get_pil_font('montserrat_bold', 56)
        
        draw_ig.ellipse([ig_w//2 - 70, logo_y, ig_w//2 + 70, logo_y + 140], fill=text_color_rgb)
        
        ibox = draw_ig.textbbox((0, 0), initials, font=font_init)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        
        # Color inside letters is brand color
        draw_ig.text(
            (ig_w//2 - iw//2 - ibox[0], logo_y + 70 - ih//2 - ibox[1]),
            initials,
            fill=hex_to_rgb(brand_color_hex) + (255,),
            font=font_init
        )
        logo_y += 180
        
    # Business name large
    font_biz = get_pil_font('montserrat_bold', 64)
    bbox_biz = draw_ig.textbbox((0, 0), business_name, font=font_biz)
    bw = bbox_biz[2] - bbox_biz[0]
    draw_ig.text(((ig_w - bw)//2 - bbox_biz[0], logo_y), business_name, fill=text_color_rgb, font=font_biz)
    logo_y += 85
    
    # Tagline
    if tagline:
        font_tag = get_pil_font('inter_regular', 28)
        bbox_tag = draw_ig.textbbox((0, 0), tagline, font=font_tag)
        tw = bbox_tag[2] - bbox_tag[0]
        draw_ig.text(((ig_w - tw)//2 - bbox_tag[0], logo_y), tagline, fill=subtext_color_rgb, font=font_tag)
        logo_y += 80
        
    # "Now Open / Serving You" Badge
    badge_y = logo_y + 30
    draw_ig.rounded_rectangle(
        [ig_w//2 - 180, badge_y, ig_w//2 + 180, badge_y + 65],
        radius=30,
        fill=text_color_rgb
    )
    font_badge = get_pil_font('montserrat_bold', 22)
    badge_text = "WE ARE OPEN"
    bbox_b = draw_ig.textbbox((0, 0), badge_text, font=font_badge)
    bgw = bbox_b[2] - bbox_b[0]
    bgh = bbox_b[3] - bbox_b[1]
    
    draw_ig.text(
        (ig_w//2 - bgw//2 - bbox_b[0], badge_y + 32 - bgh//2 - bbox_b[1]),
        badge_text,
        fill=hex_to_rgb(brand_color_hex) + (255,),
        font=font_badge
    )
    
    # Contact Strip at bottom
    contact_parts = []
    if phone:
        contact_parts.append(phone)
    if website:
        contact_parts.append(website)
    elif email:
        contact_parts.append(email)
        
    contact_str = "   •   ".join(contact_parts)
    font_c = get_pil_font('inter_bold', 24)
    bbox_c = draw_ig.textbbox((0, 0), contact_str, font=font_c)
    cw = bbox_c[2] - bbox_c[0]
    draw_ig.text(((ig_w - cw)//2 - bbox_c[0], ig_h - 110), contact_str, fill=text_color_rgb, font=font_c)
    
    ig_path = os.path.join(output_dir, "social_instagram.png")
    ig.convert("RGB").save(ig_path, "PNG")
    generated_files["social_instagram"] = "social_instagram.png"
    
    # ---------------- B. FACEBOOK COVER (851x315) ----------------
    fb_w, fb_h = 851, 315
    fb = Image.new("RGBA", (fb_w, fb_h))
    draw_soft_background(fb, brand_color_hex)
    draw_fb = ImageDraw.Draw(fb)
    
    # Divider/border box inside
    draw_fb.rectangle([15, 15, fb_w - 15, fb_h - 15], outline=text_color_rgb, width=1)
    
    # Logo on the left
    logo_x = 50
    if logo:
        logo_temp = logo.copy()
        logo_temp.thumbnail((120, 120), Image.Resampling.LANCZOS)
        lw, lh = logo_temp.size
        fb.alpha_composite(logo_temp, (logo_x, (fb_h - lh)//2))
        logo_x += lw + 40
    else:
        # Mock text icon
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        draw_fb.ellipse([logo_x, (fb_h - 100)//2, logo_x + 100, (fb_h + 100)//2], fill=text_color_rgb)
        
        font_init_fb = get_pil_font('montserrat_bold', 40)
        ibox = draw_fb.textbbox((0, 0), initials, font=font_init_fb)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        draw_fb.text(
            (logo_x + 50 - iw//2 - ibox[0], fb_h//2 - ih//2 - ibox[1]),
            initials,
            fill=hex_to_rgb(brand_color_hex) + (255,),
            font=font_init_fb
        )
        logo_x += 140
        
    # Business name & details on the right
    font_biz_fb = get_pil_font('montserrat_bold', 44)
    draw_fb.text((logo_x, 50), business_name, fill=text_color_rgb, font=font_biz_fb)
    
    offset_y = 110
    if tagline:
        font_tag_fb = get_pil_font('inter_regular', 20)
        draw_fb.text((logo_x, offset_y), tagline, fill=subtext_color_rgb, font=font_tag_fb)
        offset_y += 35
        
    # List top 3 services horizontally
    if services:
        top_s = [s.strip() for s in services[:3]]
        s_text = " | ".join(top_s)
        if len(s_text) > 55:
            s_text = s_text[:52] + "..."
        font_s = get_pil_font('inter_bold', 16)
        draw_fb.text((logo_x, offset_y), s_text, fill=text_color_rgb, font=font_s)
        offset_y += 30
        
    # Contact info at the bottom-right corner area
    contact_parts_fb = []
    if phone:
        contact_parts_fb.append(f"Call: {phone}")
    if website:
        contact_parts_fb.append(website)
    contact_str_fb = "   •   ".join(contact_parts_fb)
    
    font_cfb = get_pil_font('inter_regular', 14)
    draw_fb.text((logo_x, fb_h - 55), contact_str_fb, fill=subtext_color_rgb, font=font_cfb)
    
    fb_path = os.path.join(output_dir, "social_facebook.png")
    fb.convert("RGB").save(fb_path, "PNG")
    generated_files["social_facebook"] = "social_facebook.png"
    
    # ---------------- C. WHATSAPP PROFILE IMAGE (500x500) ----------------
    wa_w, wa_h = 500, 500
    wa = Image.new("RGBA", (wa_w, wa_h))
    draw_soft_background(wa, brand_color_hex)
    draw_wa = ImageDraw.Draw(wa)
    
    # Circle Crop Guideline (highly aesthetic, dashed or solid outer circle)
    # Circle crop safe zone is typically 450x450px centered
    draw_wa.ellipse([25, 25, wa_w - 25, wa_h - 25], outline=subtext_color_rgb, width=2)
    
    # Logo centered in the circle
    if logo:
        logo_temp = logo.copy()
        logo_temp.thumbnail((200, 200), Image.Resampling.LANCZOS)
        lw, lh = logo_temp.size
        wa.alpha_composite(logo_temp, ((wa_w - lw)//2, (wa_h - lh)//2 - 20))
    else:
        # Text initials centered
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        font_init_wa = get_pil_font('montserrat_bold', 72)
        
        draw_wa.ellipse([wa_w//2 - 100, wa_h//2 - 120, wa_w//2 + 100, wa_h//2 + 80], fill=text_color_rgb)
        
        ibox = draw_wa.textbbox((0, 0), initials, font=font_init_wa)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        draw_wa.text(
            (wa_w//2 - iw//2 - ibox[0], wa_h//2 - 20 - ih//2 - ibox[1]),
            initials,
            fill=hex_to_rgb(brand_color_hex) + (255,),
            font=font_init_wa
        )
        
    # Small business name at the bottom of the profile circle
    font_biz_wa = get_pil_font('montserrat_bold', 28)
    bbox_wa = draw_wa.textbbox((0, 0), business_name, font=font_biz_wa)
    baw = bbox_wa[2] - bbox_wa[0]
    draw_wa.text(((wa_w - baw)//2 - bbox_wa[0], wa_h - 90), business_name, fill=text_color_rgb, font=font_biz_wa)
    
    wa_path = os.path.join(output_dir, "social_whatsapp.png")
    wa.convert("RGB").save(wa_path, "PNG")
    generated_files["social_whatsapp"] = "social_whatsapp.png"
    
    return generated_files
