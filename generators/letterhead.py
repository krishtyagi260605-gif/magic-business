import os
from PIL import Image, ImageDraw
from utils.fonts import get_pil_font, register_fonts_for_reportlab
from utils.colors import hex_to_rgb, get_reportlab_color
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def draw_preview_icon(draw: ImageDraw.ImageDraw, icon_type: str, xy: tuple[float, float], size: float, color: tuple[int, int, int]):
    """Draw simple preview shapes for the mockup image."""
    x, y = xy
    if icon_type == "logo":
        draw.ellipse([x, y, x + size, y + size], fill=color)
        draw.ellipse([x + size*0.25, y + size*0.25, x + size*0.75, y + size*0.75], fill=(255, 255, 255))

def generate_letterhead(
    business_name: str,
    phone: str,
    email: str,
    website: str = "",
    address: str = "",
    gst_number: str = "",
    brand_color_hex: str = "#2563EB",
    logo_path: str = None,
    output_dir: str = ""
) -> dict:
    """
    Generate A4 print-ready PDF and a preview PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    register_fonts_for_reportlab()
    brand_rgb = hex_to_rgb(brand_color_hex)
    
    pdf_path = os.path.join(output_dir, "letterhead.pdf")
    preview_path = os.path.join(output_dir, "letterhead_preview.png")
    
    # A4 dimensions in points: 595.27 x 841.89 (approx 595 x 842)
    pdf_w, pdf_h = 595, 842
    margin = 56  # 20mm
    
    # ---------------- REPORTLAB PDF GENERATION ----------------
    c = canvas.Canvas(pdf_path, pagesize=A4)
    
    # Draw Watermark in the center
    c.saveState()
    c.setFont("Montserrat-Bold", 45)
    c.setFillColorRGB(0.96, 0.96, 0.96)
    c.translate(pdf_w / 2, pdf_h / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, business_name.upper())
    c.restoreState()
    
    # Header Logo & Name
    logo_drawn = False
    if logo_path and os.path.exists(logo_path):
        try:
            # Draw logo image
            c.drawImage(logo_path, margin, pdf_h - margin - 50, width=50, height=50, mask='auto')
            logo_drawn = True
        except Exception as e:
            print(f"Error drawing logo on letterhead PDF: {e}")
            
    if not logo_drawn:
        # Fallback circle logo
        c.setFillColor(get_reportlab_color(brand_color_hex))
        c.circle(margin + 25, pdf_h - margin - 25, 25, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Montserrat-Bold", 18)
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        c.drawCentredString(margin + 25, pdf_h - margin - 31, initials)
        
    # Business Name (Right side of header)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Montserrat-Bold", 24)
    c.drawRightString(pdf_w - margin, pdf_h - margin - 35, business_name)
    
    # Brand thin divider line below header
    c.setStrokeColor(get_reportlab_color(brand_color_hex))
    c.setLineWidth(1.5)
    c.line(margin, pdf_h - margin - 65, pdf_w - margin, pdf_h - margin - 65)
    
    # Contact Strip below divider line
    contact_parts = [phone, email]
    if website:
        contact_parts.append(website)
    if address:
        contact_parts.append(address.replace('\n', ', '))
        
    contact_text = "  |  ".join(contact_parts)
    # Truncate contact text if too wide
    if len(contact_text) > 85:
        contact_text = contact_text[:82] + "..."
        
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Inter-Regular", 8.5)
    c.drawCentredString(pdf_w / 2, pdf_h - margin - 82, contact_text)
    
    # Footer Layout
    # Solid bottom strip
    c.setFillColor(get_reportlab_color(brand_color_hex))
    c.rect(0, 0, pdf_w, 15, fill=1, stroke=0)
    
    # Footer lines and texts
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.setLineWidth(0.5)
    c.line(margin, 55, pdf_w - margin, 55)
    
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Inter-Regular", 9)
    c.drawString(margin, 35, "Thank you for your business.")
    
    if gst_number:
        c.drawRightString(pdf_w - margin, 35, f"GSTIN: {gst_number}")
        
    c.showPage()
    c.save()
    generated_files["letterhead_pdf"] = "letterhead.pdf"
    
    # ---------------- PILLOW PREVIEW PNG GENERATION ----------------
    # A4 aspect ratio mockup, e.g. 595 x 842 pixels
    pw, ph = 595, 842
    preview = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
    draw_p = ImageDraw.Draw(preview)
    
    # Center watermark
    font_wm = get_pil_font('montserrat_bold', 40)
    # To draw rotated text in PIL, we can draw on a separate transparent image and rotate it
    wm_img = Image.new("RGBA", (pw, ph), (255, 255, 255, 0))
    draw_wm = ImageDraw.Draw(wm_img)
    wbox = draw_wm.textbbox((0, 0), business_name.upper(), font=font_wm)
    ww = wbox[2] - wbox[0]
    wh = wbox[3] - wbox[1]
    draw_wm.text(((pw - ww)//2 - wbox[0], (ph - wh)//2 - wbox[1]), business_name.upper(), fill=(240, 240, 240, 255), font=font_wm)
    rotated_wm = wm_img.rotate(45, resample=Image.Resampling.BICUBIC)
    preview.alpha_composite(rotated_wm)
    
    # Header logo preview
    logo_preview_drawn = False
    if logo_path and os.path.exists(logo_path):
        try:
            p_logo = Image.open(logo_path).convert("RGBA")
            p_logo.thumbnail((50, 50), Image.Resampling.LANCZOS)
            preview.alpha_composite(p_logo, (margin, margin))
            logo_preview_drawn = True
        except Exception:
            pass
            
    if not logo_preview_drawn:
        # Fallback circle icon
        draw_p.ellipse([margin, margin, margin + 50, margin + 50], fill=brand_rgb)
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        font_init = get_pil_font('montserrat_bold', 18)
        ibox = draw_p.textbbox((0, 0), initials, font=font_init)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        draw_p.text((margin + 25 - iw//2 - ibox[0], margin + 25 - ih//2 - ibox[1]), initials, fill=(255, 255, 255), font=font_init)
        
    # Business name text
    font_biz = get_pil_font('montserrat_bold', 24)
    bbox_biz = draw_p.textbbox((0, 0), business_name, font=font_biz)
    bw = bbox_biz[2] - bbox_biz[0]
    draw_p.text((pw - margin - bw, margin + 10), business_name, fill=(30, 30, 30), font=font_biz)
    
    # Accent line
    draw_p.rectangle([margin, margin + 65, pw - margin, margin + 67], fill=brand_rgb)
    
    # Contact strip text
    font_c = get_pil_font('inter_regular', 9)
    cbox = draw_p.textbbox((0, 0), contact_text, font=font_c)
    cw = cbox[2] - cbox[0]
    draw_p.text(((pw - cw)//2, margin + 78), contact_text, fill=(100, 100, 100), font=font_c)
    
    # Ruled body guidelines mockup (make it look like a letterhead sheet)
    draw_p.rectangle([margin, 200, pw - margin, 201], fill=(220, 220, 220))
    draw_p.rectangle([margin, 240, pw - margin, 241], fill=(240, 240, 240))
    draw_p.rectangle([margin, 280, pw - margin, 281], fill=(240, 240, 240))
    draw_p.rectangle([margin, 320, pw - margin, 321], fill=(240, 240, 240))
    
    # Footer bottom strip
    draw_p.rectangle([0, ph - 15, pw, ph], fill=brand_rgb)
    
    # Footer line
    draw_p.rectangle([margin, ph - 55, pw - margin, ph - 54], fill=(230, 230, 230))
    
    # Footer texts
    font_f = get_pil_font('inter_regular', 9)
    draw_p.text((margin, ph - 45), "Thank you for your business.", fill=(120, 120, 120), font=font_f)
    if gst_number:
        gst_str = f"GSTIN: {gst_number}"
        gbox = draw_p.textbbox((0, 0), gst_str, font=font_f)
        gw = gbox[2] - gbox[0]
        draw_p.text((pw - margin - gw, ph - 45), gst_str, fill=(120, 120, 120), font=font_f)
        
    preview.convert("RGB").save(preview_path, "PNG")
    generated_files["letterhead_preview"] = "letterhead_preview.png"
    
    return generated_files
