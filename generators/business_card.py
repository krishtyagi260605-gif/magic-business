import os
import qrcode
from PIL import Image, ImageDraw, ImageOps
from utils.fonts import get_pil_font
from utils.colors import hex_to_rgb, get_text_color_for_background
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch

def generate_qr_code(data: str, size: int = 150) -> Image.Image:
    """Generate a clean QR code PNG image."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    return qr_img

def draw_icon(draw: ImageDraw.ImageDraw, icon_type: str, xy: tuple[float, float], size: float, color: tuple[int, int, int]):
    """Draw a vector-like icon using PIL primitives."""
    x, y = xy
    if icon_type == "phone":
        # Draw a stylized phone handset
        draw.rounded_rectangle([x + size*0.3, y + size*0.1, x + size*0.7, y + size*0.9], radius=size*0.1, outline=color, width=2)
        draw.ellipse([x + size*0.45, y + size*0.7, x + size*0.55, y + size*0.8], fill=color)
    elif icon_type == "email":
        # Draw a stylized envelope
        draw.rectangle([x + size*0.1, y + size*0.2, x + size*0.9, y + size*0.8], outline=color, width=2)
        draw.line([x + size*0.1, y + size*0.2, x + size*0.5, y + size*0.55], fill=color, width=2)
        draw.line([x + size*0.9, y + size*0.2, x + size*0.5, y + size*0.55], fill=color, width=2)
    elif icon_type == "website":
        # Draw a stylized globe/web circle
        draw.ellipse([x + size*0.1, y + size*0.1, x + size*0.9, y + size*0.9], outline=color, width=2)
        draw.ellipse([x + size*0.3, y + size*0.1, x + size*0.7, y + size*0.9], outline=color, width=1)
        draw.line([x + size*0.1, y + size*0.5, x + size*0.9, y + size*0.5], fill=color, width=1)
    elif icon_type == "address":
        # Draw a stylized map pin
        draw.ellipse([x + size*0.2, y + size*0.1, x + size*0.8, y + size*0.7], fill=color)
        draw.polygon([x + size*0.2, y + size*0.5, x + size*0.8, y + size*0.5, x + size*0.5, y + size*0.95], fill=color)
        draw.ellipse([x + size*0.4, y + size*0.3, x + size*0.6, y + size*0.5], fill=(255, 255, 255))

def generate_business_card(
    business_name: str,
    owner_name: str,
    phone: str,
    email: str,
    website: str = "",
    address: str = "",
    tagline: str = "",
    services: list[str] = None,
    brand_color_hex: str = "#2563EB",
    logo_path: str = None,
    output_dir: str = ""
) -> dict:
    """
    Generate Front PNG, Back PNG, Digital card, and combined print PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    # 300 DPI business card sizes: 3.5" x 2" -> 1050 x 600 px
    w, h = 1050, 600
    brand_rgb = hex_to_rgb(brand_color_hex)
    
    # Load Logo
    logo = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
        except Exception as e:
            print(f"Error loading logo for card: {e}")
            
    # ---------------- FRONT SIDE ----------------
    front = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw_f = ImageDraw.Draw(front)
    
    # Left accent bar (brand color)
    draw_f.rectangle([0, 0, 30, h], fill=brand_rgb)
    
    # Render Logo (if exists) or business name initials icon
    logo_size = 120
    if logo:
        # Resize logo to fit
        logo_temp = logo.copy()
        logo_temp.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        front.alpha_composite(logo_temp, (80, 80))
    else:
        # Draw a fallback text icon
        draw_f.rounded_rectangle([80, 80, 200, 200], radius=15, fill=brand_rgb)
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        font_init = get_pil_font('montserrat_bold', 48)
        ibox = draw_f.textbbox((0, 0), initials, font=font_init)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        draw_f.text((140 - iw//2 - ibox[0], 140 - ih//2 - ibox[1]), initials, fill=(255, 255, 255), font=font_init)
        
    # Business Name
    font_biz = get_pil_font('montserrat_bold', 52)
    draw_f.text((240, 80), business_name, fill=(18, 18, 18), font=font_biz)
    
    # Tagline (if any)
    if tagline:
        font_tag = get_pil_font('inter_regular', 24)
        draw_f.text((240, 145), tagline, fill=(100, 100, 100), font=font_tag)
        
    # Owner Name & Title
    font_owner = get_pil_font('montserrat_bold', 38)
    draw_f.text((80, h - 280), owner_name, fill=(18, 18, 18), font=font_owner)
    
    font_title = get_pil_font('inter_regular', 22)
    draw_f.text((80, h - 235), "Owner / Founder", fill=brand_rgb, font=font_title)
    
    # Contact Details on the right side
    dx, dy = 600, h - 280
    details_font = get_pil_font('inter_regular', 24)
    
    contact_items = []
    if phone:
        contact_items.append(("phone", phone))
    if email:
        contact_items.append(("email", email))
    if website:
        contact_items.append(("website", website))
    if address:
        # Truncate address if too long
        cleaned_addr = address.replace('\n', ', ')
        if len(cleaned_addr) > 30:
            cleaned_addr = cleaned_addr[:27] + "..."
        contact_items.append(("address", cleaned_addr))
        
    for icon_name, val in contact_items:
        draw_icon(draw_f, icon_name, (dx, dy + 5), 32, brand_rgb)
        draw_f.text((dx + 50, dy + 5), val, fill=(50, 50, 50), font=details_font)
        dy += 55
        
    # Bottom brand accent bar
    draw_f.rectangle([0, h - 15, w, h], fill=brand_rgb)
    
    front_path = os.path.join(output_dir, "card_front.png")
    front.convert("RGB").save(front_path, "PNG", dpi=(300, 300))
    generated_files["card_front"] = "card_front.png"
    
    # ---------------- BACK SIDE ----------------
    back = Image.new("RGBA", (w, h), brand_rgb)
    draw_b = ImageDraw.Draw(back)
    
    # Determine what details to include: tagline or services
    text_color_b = get_text_color_for_background(brand_color_hex)
    text_color_b_tuple = (255, 255, 255) if text_color_b == "#FFFFFF" else (0, 0, 0)
    
    # Sub-box border
    draw_b.rectangle([40, 40, w - 40, h - 40], outline=text_color_b_tuple, width=2)
    
    # Center QR Code
    qr_data = website if website else (email if email else f"tel:{phone}")
    qr_img = generate_qr_code(qr_data, size=180)
    back.alpha_composite(qr_img, (w - 260, 210))
    
    # Draw "Scan to Connect" label
    font_scan = get_pil_font('inter_regular', 18)
    sbox = draw_b.textbbox((0, 0), "Scan to Connect", font=font_scan)
    sw = sbox[2] - sbox[0]
    draw_b.text((w - 170 - sw//2 - sbox[0], 410), "Scan to Connect", fill=text_color_b_tuple, font=font_scan)
    
    # Business name on back
    font_biz_b = get_pil_font('montserrat_bold', 48)
    draw_b.text((80, 80), business_name, fill=text_color_b_tuple, font=font_biz_b)
    
    # If services are provided, list top 3, else tagline
    if services and len(services) > 0:
        font_serv_head = get_pil_font('montserrat_bold', 26)
        draw_b.text((80, 180), "Our Services", fill=text_color_b_tuple, font=font_serv_head)
        
        font_serv_item = get_pil_font('inter_regular', 24)
        sy = 230
        for s in services[:4]:
            draw_b.ellipse([80, sy + 10, 88, sy + 18], fill=text_color_b_tuple)
            # Truncate service if too long
            cleaned_s = s.strip()
            if len(cleaned_s) > 30:
                cleaned_s = cleaned_s[:27] + "..."
            draw_b.text((105, sy), cleaned_s, fill=text_color_b_tuple, font=font_serv_item)
            sy += 45
    elif tagline:
        font_tag_b = get_pil_font('inter_regular', 32)
        # Wrap tagline if it's too long
        words = tagline.split()
        lines = []
        curr = []
        for word in words:
            if len(" ".join(curr + [word])) > 30:
                lines.append(" ".join(curr))
                curr = [word]
            else:
                curr.append(word)
        if curr:
            lines.append(" ".join(curr))
            
        ty = 220
        for line in lines[:3]:
            draw_b.text((80, ty), line, fill=text_color_b_tuple, font=font_tag_b)
            ty += 50
            
    # Small credit
    font_credit = get_pil_font('inter_regular', 14)
    draw_b.text((80, h - 80), "Powered by Magic Business", fill=text_color_b_tuple, font=font_credit)
    
    back_path = os.path.join(output_dir, "card_back.png")
    back.convert("RGB").save(back_path, "PNG", dpi=(300, 300))
    generated_files["card_back"] = "card_back.png"
    
    # ---------------- DIGITAL CARD (WHATSAPP OPTIMIZED) ----------------
    # 600 x 340px (aspect ratio fits whatsapp screen previews cleanly)
    dig_w, dig_h = 600, 340
    digital = Image.new("RGBA", (dig_w, dig_h), (255, 255, 255, 255))
    draw_d = ImageDraw.Draw(digital)
    
    # Left accent bar
    draw_d.rectangle([0, 0, 15, dig_h], fill=brand_rgb)
    
    # Logo
    if logo:
        logo_temp = logo.copy()
        logo_temp.thumbnail((70, 70), Image.Resampling.LANCZOS)
        digital.alpha_composite(logo_temp, (40, 40))
    else:
        draw_d.rounded_rectangle([40, 40, 110, 110], radius=8, fill=brand_rgb)
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        font_init = get_pil_font('montserrat_bold', 28)
        ibox = draw_d.textbbox((0, 0), initials, font=font_init)
        digital.alpha_composite(generate_text_logo_icon("circle", initials, brand_color_hex, 70), (40, 40))
        
    # Business name
    font_biz_d = get_pil_font('montserrat_bold', 32)
    draw_d.text((130, 40), business_name, fill=(18, 18, 18), font=font_biz_d)
    
    if tagline:
        font_tag_d = get_pil_font('inter_regular', 16)
        draw_d.text((130, 80), tagline[:35] + ("..." if len(tagline) > 35 else ""), fill=(120, 120, 120), font=font_tag_d)
        
    # Owner & Contact Details
    font_owner_d = get_pil_font('montserrat_bold', 22)
    draw_d.text((40, dig_h - 150), owner_name, fill=(18, 18, 18), font=font_owner_d)
    
    font_title_d = get_pil_font('inter_regular', 14)
    draw_d.text((40, dig_h - 120), "Founder / Owner", fill=brand_rgb, font=font_title_d)
    
    dy = dig_h - 150
    details_font_d = get_pil_font('inter_regular', 16)
    
    # Add QR code inside digital card
    qr_img_d = generate_qr_code(qr_data, size=90)
    digital.alpha_composite(qr_img_d, (dig_w - 130, dig_h - 150))
    draw_d.text((dig_w - 135, dig_h - 55), "Save Contact", fill=(100, 100, 100), font=get_pil_font('inter_regular', 12))
    
    for icon_name, val in contact_items[:3]:
        draw_icon(draw_d, icon_name, (340, dy + 2), 20, brand_rgb)
        draw_d.text((370, dy + 2), val[:22] + ("..." if len(val) > 22 else ""), fill=(60, 60, 60), font=details_font_d)
        dy += 35
        
    # Bottom brand accent bar
    draw_d.rectangle([0, dig_h - 8, dig_w, dig_h], fill=brand_rgb)
    
    digital_path = os.path.join(output_dir, "card_digital.png")
    digital.convert("RGB").save(digital_path, "PNG")
    generated_files["card_digital"] = "card_digital.png"
    
    # ---------------- PRINT READY COMBINED PDF ----------------
    # Bleed page size: 3.75" x 2.25" (includes 0.125" bleed all around)
    pdf_path = os.path.join(output_dir, "business_card.pdf")
    
    # 3.75" x 2.25" is 270 x 162 points
    c = canvas.Canvas(pdf_path, pagesize=(270, 162))
    
    # First Page: Front
    # Draw front image stretched over the bleed canvas (it has same aspect ratio)
    c.drawImage(front_path, 0, 0, width=270, height=162)
    # Draw simple visual bleed/crop guides (outside safe zone of 3.5" x 2" centered)
    # Safe zone: center 252 x 144 points (9 pt margin on all sides)
    c.setStrokeColor(get_reportlab_color(brand_color_hex))
    c.setLineWidth(0.5)
    c.rect(9, 9, 252, 144)
    c.showPage()
    
    # Second Page: Back
    c.drawImage(back_path, 0, 0, width=270, height=162)
    c.rect(9, 9, 252, 144)
    c.showPage()
    
    c.save()
    generated_files["card_pdf"] = "business_card.pdf"
    
    return generated_files

def get_reportlab_color(hex_str: str):
    from reportlab.lib.colors import HexColor
    if not hex_str.startswith('#'):
        hex_str = '#' + hex_str
    return HexColor(hex_str)
