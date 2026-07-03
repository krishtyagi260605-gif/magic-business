import os
import datetime
from PIL import Image, ImageDraw
from utils.fonts import get_pil_font, register_fonts_for_reportlab
from utils.colors import hex_to_rgb, get_reportlab_color
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def parse_service_line(line: str) -> tuple[str, str, str]:
    """
    Parse a service line to extract Name, Description, and Price.
    Formats:
      Name - Description - Price
      Name - Price
      Name
    """
    line = line.strip()
    if not line:
        return "", "", ""
        
    parts = []
    # Try different separators
    for sep in ['|', '-', ':']:
        if sep in line:
            parts = [p.strip() for p in line.split(sep)]
            break
            
    if not parts:
        return line, "Standard high-quality offering", "On Request"
        
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        # Check if the second part is a price
        p2 = parts[1]
        is_price = any(char.isdigit() for char in p2) or "rs" in p2.lower() or "₹" in p2
        if is_price:
            return parts[0], "Standard high-quality offering", parts[1]
        else:
            return parts[0], parts[1], "On Request"
            
    return parts[0], "Standard high-quality offering", "On Request"

def get_validity_date() -> str:
    """Return 'Prices valid until [current month + 3 months]'."""
    now = datetime.datetime.now()
    # Add approx 90 days (3 months)
    validity = now + datetime.timedelta(days=90)
    return validity.strftime("%B %Y")

def generate_price_list(
    business_name: str,
    tagline: str,
    phone: str,
    email: str,
    website: str = "",
    services: list[str] = None,
    brand_color_hex: str = "#2563EB",
    output_dir: str = ""
) -> dict:
    """
    Generate price list A4 PDF and preview PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    register_fonts_for_reportlab()
    brand_rgb = hex_to_rgb(brand_color_hex)
    
    pdf_path = os.path.join(output_dir, "price_list.pdf")
    preview_path = os.path.join(output_dir, "price_list_preview.png")
    
    pdf_w, pdf_h = 595, 842
    margin = 56
    
    # Pre-parse service items
    parsed_items = []
    if services:
        for s in services:
            name, desc, price = parse_service_line(s)
            if name:
                parsed_items.append((name, desc, price))
    if not parsed_items:
        # Fallback items
        parsed_items = [
            ("Starter Package", "Ideal for small businesses or individuals starting out", "₹1,499"),
            ("Professional Tier", "Comprehensive support and standard capabilities", "₹2,999"),
            ("Elite Enterprise Setup", "Full ecosystem access, custom setups, and 24/7 priority support", "₹5,499"),
            ("Consulting Services", "Expert strategic review, planning, and dedicated advice", "₹999 / Hr")
        ]
        
    validity_month = get_validity_date()
    
    # ---------------- REPORTLAB PDF GENERATION ----------------
    c = canvas.Canvas(pdf_path, pagesize=A4)
    
    # Solid Top Accent Bar
    c.setFillColor(get_reportlab_color(brand_color_hex))
    c.rect(0, pdf_h - 120, pdf_w, 120, fill=1, stroke=0)
    
    # Business name in white
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Montserrat-Bold", 32)
    c.drawString(margin, pdf_h - 60, business_name)
    
    # Tagline in light grey/white
    if tagline:
        c.setFont("Inter-Regular", 14)
        c.drawString(margin, pdf_h - 90, tagline)
        
    # Title
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Montserrat-Bold", 24)
    c.drawString(margin, pdf_h - 170, "SERVICES & PRICING")
    
    # Accent indicator line below title
    c.setStrokeColor(get_reportlab_color(brand_color_hex))
    c.setLineWidth(2)
    c.line(margin, pdf_h - 180, margin + 150, pdf_h - 180)
    
    # Table Headings
    y = pdf_h - 220
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("Montserrat-Bold", 11)
    c.drawString(margin + 10, y, "SERVICE / DELIVERABLE")
    c.drawString(margin + 180, y, "DESCRIPTION")
    c.drawRightString(pdf_w - margin - 10, y, "PRICE")
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(1)
    c.line(margin, y - 8, pdf_w - margin, y - 8)
    
    y -= 35
    
    # Draw service rows
    for i, (name, desc, price) in enumerate(parsed_items):
        if y < 100:  # Page break safety (limit items on 1 page for standard display)
            break
            
        # Row Background Accent (alternating)
        if i % 2 == 0:
            c.setFillColorRGB(0.97, 0.98, 0.99)
            c.rect(margin, y - 12, pdf_w - 2 * margin, 36, fill=1, stroke=0)
            
        # Draw text
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Montserrat-Bold", 10.5)
        c.drawString(margin + 10, y, name)
        
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Inter-Regular", 9)
        # Truncate description if too long
        if len(desc) > 52:
            desc = desc[:49] + "..."
        c.drawString(margin + 180, y, desc)
        
        c.setFillColor(get_reportlab_color(brand_color_hex))
        c.setFont("Montserrat-Bold", 11)
        c.drawRightString(pdf_w - margin - 10, y, price)
        
        y -= 36
        
    # Footer Area
    c.setFillColor(get_reportlab_color(brand_color_hex))
    c.rect(0, 0, pdf_w, 15, fill=1, stroke=0)
    
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.setLineWidth(0.5)
    c.line(margin, 70, pdf_w - margin, 70)
    
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Inter-Regular", 9)
    # Contact Info Centered/Left
    contact_info = f"Phone: {phone}   |   Email: {email}"
    if website:
        contact_info += f"   |   Website: {website}"
    c.drawString(margin, 45, contact_info)
    c.drawRightString(pdf_w - margin, 45, f"Prices valid until {validity_month}")
    
    c.showPage()
    c.save()
    generated_files["price_list_pdf"] = "price_list.pdf"
    
    # ---------------- PILLOW PREVIEW PNG ----------------
    pw, ph = 595, 842
    preview = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
    draw_p = ImageDraw.Draw(preview)
    
    # Top header block in brand color
    draw_p.rectangle([0, 0, pw, 120], fill=brand_rgb)
    
    # Business name in header
    font_biz = get_pil_font('montserrat_bold', 28)
    draw_p.text((margin, 30), business_name, fill=(255, 255, 255), font=font_biz)
    
    if tagline:
        font_tag = get_pil_font('inter_regular', 12)
        draw_p.text((margin, 70), tagline, fill=(230, 230, 230), font=font_tag)
        
    # Title
    font_title = get_pil_font('montserrat_bold', 20)
    draw_p.text((margin, 150), "SERVICES & PRICING", fill=(30, 30, 30), font=font_title)
    
    # Underline
    draw_p.rectangle([margin, 180, margin + 120, 182], fill=brand_rgb)
    
    # Column headings
    font_head = get_pil_font('montserrat_bold', 10)
    draw_p.text((margin + 10, 210), "SERVICE", fill=(100, 100, 100), font=font_head)
    draw_p.text((margin + 180, 210), "DESCRIPTION", fill=(100, 100, 100), font=font_head)
    draw_p.text((pw - margin - 50, 210), "PRICE", fill=(100, 100, 100), font=font_head)
    
    # Divider
    draw_p.rectangle([margin, 225, pw - margin, 226], fill=(200, 200, 200))
    
    # Draw rows
    ry = 240
    font_item = get_pil_font('montserrat_bold', 10)
    font_desc = get_pil_font('inter_regular', 9)
    for i, (name, desc, price) in enumerate(parsed_items[:12]):
        if ry > ph - 100:
            break
            
        if i % 2 == 0:
            draw_p.rectangle([margin, ry - 5, pw - margin, ry + 25], fill=(245, 247, 250))
            
        draw_p.text((margin + 10, ry), name, fill=(30, 30, 30), font=font_item)
        draw_p.text((margin + 180, ry + 1), desc[:40] + ("..." if len(desc) > 40 else ""), fill=(100, 100, 100), font=font_desc)
        
        # Right align price
        p_bbox = draw_p.textbbox((0, 0), price, font=font_item)
        pw_t = p_bbox[2] - p_bbox[0]
        draw_p.text((pw - margin - 10 - pw_t, ry), price, fill=brand_rgb, font=font_item)
        
        ry += 32
        
    # Bottom Footer Strip
    draw_p.rectangle([0, ph - 15, pw, ph], fill=brand_rgb)
    draw_p.rectangle([margin, ph - 65, pw - margin, ph - 64], fill=(220, 220, 220))
    
    font_foot = get_pil_font('inter_regular', 8.5)
    draw_p.text((margin, ph - 45), contact_info[:65] + ("..." if len(contact_info) > 65 else ""), fill=(120, 120, 120), font=font_foot)
    
    validity_str = f"Valid until: {validity_month}"
    v_bbox = draw_p.textbbox((0, 0), validity_str, font=font_foot)
    vw_t = v_bbox[2] - v_bbox[0]
    draw_p.text((pw - margin - vw_t, ph - 45), validity_str, fill=(120, 120, 120), font=font_foot)
    
    preview.convert("RGB").save(preview_path, "PNG")
    generated_files["price_list_preview"] = "price_list_preview.png"
    
    return generated_files
