import os
import datetime
from PIL import Image, ImageDraw
from utils.fonts import get_pil_font, register_fonts_for_reportlab
from utils.colors import hex_to_rgb, get_reportlab_color
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5

def get_current_dates() -> tuple[str, str, str]:
    """Return (today_str, due_str, doc_num_suffix)."""
    now = datetime.datetime.now()
    today = now.strftime("%d/%m/%Y")
    due = (now + datetime.timedelta(days=15)).strftime("%d/%m/%Y")
    suffix = now.strftime("%Y%m%d")
    return today, due, suffix

def parse_service_to_item(s: str, fallback_rate: int = 1500) -> tuple[str, str, int, float]:
    """Parse service line to (Name, Qty, Rate, Amount)."""
    s = s.strip()
    if not s:
        return "", 0, 0.0, 0.0
        
    parts = []
    for sep in ['|', '-', ':']:
        if sep in s:
            parts = [p.strip() for p in s.split(sep)]
            break
            
    if not parts:
        return s[:25], 1, float(fallback_rate), float(fallback_rate)
        
    name = parts[0][:25]
    p_str = parts[-1]
    
    # Extract numeric price
    digits = "".join(c for c in p_str if c.isdigit())
    if digits:
        try:
            rate = float(digits)
            return name, 1, rate, rate
        except ValueError:
            pass
            
    return name, 1, float(fallback_rate), float(fallback_rate)

def draw_preview_grid_lines(draw: ImageDraw.ImageDraw, start_y: int, end_y: int, step: int, w: int, margin: int):
    """Draw thin ruled lines for mockup preview pages."""
    for y in range(start_y, end_y, step):
        draw.line([margin, y, w - margin, y], fill=(235, 235, 235))

def generate_documents(
    business_name: str,
    owner_name: str,
    phone: str,
    email: str,
    website: str = "",
    address: str = "",
    gst_number: str = "",
    services: list[str] = None,
    brand_color_hex: str = "#2563EB",
    logo_path: str = None,
    output_dir: str = ""
) -> dict:
    """
    Generate print-ready PDFs for Quotation, Invoice, Receipt and previews.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    register_fonts_for_reportlab()
    brand_rgb = hex_to_rgb(brand_color_hex)
    today_str, due_str, suffix = get_current_dates()
    
    # Pre-parse items
    items = []
    if services:
        fallback = 1200
        for s in services[:4]:  # Limit to 4 items
            name, qty, rate, amt = parse_service_to_item(s, fallback)
            if name:
                items.append((name, qty, rate, amt))
                fallback += 800
                
    if not items:
        items = [
            ("Standard Branding Setup", 1, 4500.0, 4500.0),
            ("Document Templates Pack", 1, 2500.0, 2500.0),
            ("Consulting Advisory", 2, 1200.0, 2400.0)
        ]
        
    subtotal = sum(i[3] for i in items)
    gst_rate = 0.18 if gst_number else 0.0
    gst_amount = subtotal * gst_rate
    total = subtotal + gst_amount
    
    # A4 point dimensions: 595 x 842
    w_a4, h_a4 = 595, 842
    margin = 56
    
    # ---------------- 1. QUOTATION ----------------
    qt_num = f"QT-{suffix}-01"
    pdf_qt_path = os.path.join(output_dir, "quotation.pdf")
    c_qt = canvas.Canvas(pdf_qt_path, pagesize=A4)
    
    def draw_doc_header(c, title):
        # Top brand banner
        c.setFillColor(get_reportlab_color(brand_color_hex))
        c.rect(0, h_a4 - 20, w_a4, 20, fill=1, stroke=0)
        
        # Logo or placeholder circle
        logo_drawn = False
        if logo_path and os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, margin, h_a4 - 100, width=60, height=60, mask='auto')
                logo_drawn = True
            except Exception:
                pass
        if not logo_drawn:
            c.setFillColor(get_reportlab_color(brand_color_hex))
            c.circle(margin + 30, h_a4 - 70, 30, fill=1, stroke=0)
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Montserrat-Bold", 22)
            initials = "".join(w[0] for w in business_name.split()[:2]).upper()
            c.drawCentredString(margin + 30, h_a4 - 78, initials)
            
        # Business Details
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.setFont("Montserrat-Bold", 20)
        c.drawString(margin + 75, h_a4 - 65, business_name)
        
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Inter-Regular", 9)
        contact_str = f"Call: {phone}  |  Email: {email}"
        if website:
            contact_str += f"  |  Web: {website}"
        c.drawString(margin + 75, h_a4 - 82, contact_str)
        if address:
            c.drawString(margin + 75, h_a4 - 96, address.replace('\n', ', '))
            
        # Document Title
        c.setFillColor(get_reportlab_color(brand_color_hex))
        c.setFont("Montserrat-Bold", 28)
        c.drawRightString(w_a4 - margin, h_a4 - 80, title)
        
        c.setStrokeColorRGB(0.85, 0.85, 0.85)
        c.setLineWidth(1)
        c.line(margin, h_a4 - 120, w_a4 - margin, h_a4 - 120)
        
    # Draw header on Quotation
    draw_doc_header(c_qt, "QUOTATION")
    
    # Metadata Block
    y = h_a4 - 150
    c_qt.setFillColorRGB(0.1, 0.1, 0.1)
    c_qt.setFont("Montserrat-Bold", 10.5)
    c_qt.drawString(margin, y, "QUOTATION TO:")
    c_qt.drawRightString(w_a4 - margin, y, "DETAILS:")
    
    c_qt.setFont("Inter-Regular", 9.5)
    c_qt.drawString(margin, y - 20, "Client Name / Organization")
    c_qt.drawString(margin, y - 35, "Representative Address Field")
    c_qt.drawString(margin, y - 50, "Client Contact Phone & Email")
    
    c_qt.drawRightString(w_a4 - margin, y - 20, f"Quote No: {qt_num}")
    c_qt.drawRightString(w_a4 - margin, y - 35, f"Date: {today_str}")
    if gst_number:
        c_qt.drawRightString(w_a4 - margin, y - 50, f"GSTIN: {gst_number}")
        
    # Item Table Headings
    y = h_a4 - 230
    c_qt.setFillColor(get_reportlab_color(brand_color_hex))
    c_qt.rect(margin, y, w_a4 - 2*margin, 22, fill=1, stroke=0)
    
    c_qt.setFillColorRGB(1, 1, 1)
    c_qt.setFont("Montserrat-Bold", 9.5)
    c_qt.drawString(margin + 10, y + 6, "ITEM DESCRIPTION")
    c_qt.drawCentredString(margin + 260, y + 6, "QTY")
    c_qt.drawRightString(margin + 360, y + 6, "RATE")
    c_qt.drawRightString(w_a4 - margin - 10, y + 6, "AMOUNT")
    
    # Draw items
    y -= 25
    c_qt.setFillColorRGB(0.1, 0.1, 0.1)
    c_qt.setFont("Inter-Regular", 9.5)
    
    for i, (name, qty, rate, amt) in enumerate(items):
        # Alternating background
        if i % 2 == 0:
            c_qt.setFillColorRGB(0.97, 0.98, 0.99)
            c_qt.rect(margin, y - 5, w_a4 - 2*margin, 22, fill=1, stroke=0)
            
        c_qt.setFillColorRGB(0.1, 0.1, 0.1)
        c_qt.drawString(margin + 10, y, name)
        c_qt.drawCentredString(margin + 260, y, str(qty))
        c_qt.drawRightString(margin + 360, y, f"₹{rate:,.2f}")
        c_qt.drawRightString(w_a4 - margin - 10, y, f"₹{amt:,.2f}")
        y -= 24
        
    # Table border line
    c_qt.setStrokeColorRGB(0.8, 0.8, 0.8)
    c_qt.line(margin, y + 15, w_a4 - margin, y + 15)
    
    # Financial breakdown
    y -= 15
    c_qt.setFont("Inter-Regular", 9.5)
    c_qt.drawString(margin, y, "TERMS & CONDITIONS:")
    
    c_qt.drawRightString(w_a4 - margin - 130, y, "Subtotal:")
    c_qt.drawRightString(w_a4 - margin - 10, y, f"₹{subtotal:,.2f}")
    
    if gst_number:
        y -= 18
        c_qt.drawRightString(w_a4 - margin - 130, y, "GST (18%):")
        c_qt.drawRightString(w_a4 - margin - 10, y, f"₹{gst_amount:,.2f}")
        
    y -= 22
    c_qt.setFont("Montserrat-Bold", 11)
    c_qt.setFillColor(get_reportlab_color(brand_color_hex))
    c_qt.drawRightString(w_a4 - margin - 130, y, "TOTAL:")
    c_qt.drawRightString(w_a4 - margin - 10, y, f"₹{total:,.2f}")
    
    # Quotation Terms Text
    y_terms = y + 22  # align back to terms column
    c_qt.setFillColorRGB(0.4, 0.4, 0.4)
    c_qt.setFont("Inter-Regular", 8)
    c_qt.drawString(margin, y_terms - 15, "1. Payment: 50% Advance & 50% upon delivery.")
    c_qt.drawString(margin, y_terms - 28, "2. Quote Validity: Valid for 30 calendar days.")
    c_qt.drawString(margin, y_terms - 41, "3. Estimated Turnaround: 7-10 working days.")
    
    # Signatures
    c_qt.setStrokeColorRGB(0.8, 0.8, 0.8)
    c_qt.line(w_a4 - margin - 150, 110, w_a4 - margin, 110)
    c_qt.drawCentredString(w_a4 - margin - 75, 95, "Authorized Signatory")
    
    # Footer brand
    c_qt.setFillColorRGB(0.6, 0.6, 0.6)
    c_qt.setFont("Inter-Regular", 8)
    c_qt.drawCentredString(w_a4 / 2, 40, "Generated by Magic Business  |  Krish Tyagi Platform")
    
    c_qt.showPage()
    c_qt.save()
    generated_files["quotation_pdf"] = "quotation.pdf"
    
    # ---------------- 2. INVOICE ----------------
    inv_num = f"INV-{suffix}-01"
    pdf_inv_path = os.path.join(output_dir, "invoice.pdf")
    c_inv = canvas.Canvas(pdf_inv_path, pagesize=A4)
    
    draw_doc_header(c_inv, "INVOICE")
    
    # Metadata Block
    y = h_a4 - 150
    c_inv.setFillColorRGB(0.1, 0.1, 0.1)
    c_inv.setFont("Montserrat-Bold", 10.5)
    c_inv.drawString(margin, y, "BILLED TO:")
    c_inv.drawRightString(w_a4 - margin, y, "DETAILS:")
    
    c_inv.setFont("Inter-Regular", 9.5)
    c_inv.drawString(margin, y - 20, "Client Name / Organization")
    c_inv.drawString(margin, y - 35, "Representative Address Field")
    c_inv.drawString(margin, y - 50, "Client Contact Phone & Email")
    
    c_inv.drawRightString(w_a4 - margin, y - 20, f"Invoice No: {inv_num}")
    c_inv.drawRightString(w_a4 - margin, y - 35, f"Date: {today_str}")
    c_inv.drawRightString(w_a4 - margin, y - 50, f"Due Date: {due_str}")
    
    # Item Table Headings
    y = h_a4 - 230
    c_inv.setFillColor(get_reportlab_color(brand_color_hex))
    c_inv.rect(margin, y, w_a4 - 2*margin, 22, fill=1, stroke=0)
    
    c_inv.setFillColorRGB(1, 1, 1)
    c_inv.setFont("Montserrat-Bold", 9.5)
    c_inv.drawString(margin + 10, y + 6, "ITEM DESCRIPTION")
    c_inv.drawCentredString(margin + 260, y + 6, "QTY")
    c_inv.drawRightString(margin + 360, y + 6, "RATE")
    c_inv.drawRightString(w_a4 - margin - 10, y + 6, "AMOUNT")
    
    # Draw items
    y -= 25
    c_inv.setFillColorRGB(0.1, 0.1, 0.1)
    c_inv.setFont("Inter-Regular", 9.5)
    
    for i, (name, qty, rate, amt) in enumerate(items):
        if i % 2 == 0:
            c_inv.setFillColorRGB(0.97, 0.98, 0.99)
            c_inv.rect(margin, y - 5, w_a4 - 2*margin, 22, fill=1, stroke=0)
            
        c_inv.setFillColorRGB(0.1, 0.1, 0.1)
        c_inv.drawString(margin + 10, y, name)
        c_inv.drawCentredString(margin + 260, y, str(qty))
        c_inv.drawRightString(margin + 360, y, f"₹{rate:,.2f}")
        c_inv.drawRightString(w_a4 - margin - 10, y, f"₹{amt:,.2f}")
        y -= 24
        
    c_inv.setStrokeColorRGB(0.8, 0.8, 0.8)
    c_inv.line(margin, y + 15, w_a4 - margin, y + 15)
    
    # Financial breakdown
    y -= 15
    c_inv.setFont("Inter-Regular", 9.5)
    c_inv.drawString(margin, y, "PAYMENT INFORMATION:")
    
    c_inv.drawRightString(w_a4 - margin - 130, y, "Subtotal:")
    c_inv.drawRightString(w_a4 - margin - 10, y, f"₹{subtotal:,.2f}")
    
    if gst_number:
        y -= 18
        c_inv.drawRightString(w_a4 - margin - 130, y, "GST (18%):")
        c_inv.drawRightString(w_a4 - margin - 10, y, f"₹{gst_amount:,.2f}")
        
    y -= 22
    c_inv.setFont("Montserrat-Bold", 11)
    c_inv.setFillColor(get_reportlab_color(brand_color_hex))
    c_inv.drawRightString(w_a4 - margin - 130, y, "TOTAL DUE:")
    c_inv.drawRightString(w_a4 - margin - 10, y, f"₹{total:,.2f}")
    
    # Bank details in terms column
    y_terms = y + 22
    c_inv.setFillColorRGB(0.4, 0.4, 0.4)
    c_inv.setFont("Inter-Regular", 8)
    c_inv.drawString(margin, y_terms - 15, "Bank Name: Mock National Bank")
    c_inv.drawString(margin, y_terms - 28, "Account No: 987654321098")
    c_inv.drawString(margin, y_terms - 41, "IFSC: MOCK0123456  |  Branch: Rajnagar")
    
    # Signatures
    c_inv.setStrokeColorRGB(0.8, 0.8, 0.8)
    c_inv.line(w_a4 - margin - 150, 110, w_a4 - margin, 110)
    c_inv.drawCentredString(w_a4 - margin - 75, 95, "Authorized Signatory")
    
    # Footer brand
    c_inv.setFillColorRGB(0.6, 0.6, 0.6)
    c_inv.setFont("Inter-Regular", 8)
    c_inv.drawCentredString(w_a4 / 2, 40, "Generated by Magic Business  |  Krish Tyagi Platform")
    
    c_inv.showPage()
    c_inv.save()
    generated_files["invoice_pdf"] = "invoice.pdf"
    
    # ---------------- 3. RECEIPT (A5 Portrait: 420 x 595 pt) ----------------
    rec_num = f"REC-{suffix}-01"
    pdf_rec_path = os.path.join(output_dir, "receipt.pdf")
    c_rec = canvas.Canvas(pdf_rec_path, pagesize=A5)
    
    w_a5, h_a5 = 420, 595
    margin_5 = 35
    
    # A5 Top Accent
    c_rec.setFillColor(get_reportlab_color(brand_color_hex))
    c_rec.rect(0, h_a5 - 15, w_a5, 15, fill=1, stroke=0)
    
    # Logo
    logo_drawn = False
    if logo_path and os.path.exists(logo_path):
        try:
            c_rec.drawImage(logo_path, margin_5, h_a5 - 75, width=45, height=45, mask='auto')
            logo_drawn = True
        except Exception:
            pass
    if not logo_drawn:
        c_rec.setFillColor(get_reportlab_color(brand_color_hex))
        c_rec.circle(margin_5 + 20, h_a5 - 50, 20, fill=1, stroke=0)
        c_rec.setFillColorRGB(1, 1, 1)
        c_rec.setFont("Montserrat-Bold", 15)
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        c_rec.drawCentredString(margin_5 + 20, h_a5 - 55, initials)
        
    c_rec.setFillColorRGB(0.1, 0.1, 0.1)
    c_rec.setFont("Montserrat-Bold", 16)
    c_rec.drawString(margin_5 + 50, h_a5 - 45, business_name)
    
    c_rec.setFillColor(get_reportlab_color(brand_color_hex))
    c_rec.setFont("Montserrat-Bold", 20)
    c_rec.drawRightString(w_a5 - margin_5, h_a5 - 50, "RECEIPT")
    
    c_rec.setStrokeColorRGB(0.85, 0.85, 0.85)
    c_rec.setLineWidth(1)
    c_rec.line(margin_5, h_a5 - 85, w_a5 - margin_5, h_a5 - 85)
    
    # Metadata fields
    y = h_a5 - 120
    c_rec.setFillColorRGB(0.3, 0.3, 0.3)
    c_rec.setFont("Inter-Regular", 9)
    c_rec.drawString(margin_5, y, f"Receipt No: {rec_num}")
    c_rec.drawRightString(w_a5 - margin_5, y, f"Date: {today_str}")
    
    # Receipt Core Box
    y -= 30
    c_rec.setFillColorRGB(0.97, 0.98, 0.99)
    c_rec.rect(margin_5, y - 200, w_a5 - 2*margin_5, 210, fill=1, stroke=1)
    
    c_rec.setFillColorRGB(0.2, 0.2, 0.2)
    c_rec.setFont("Inter-Regular", 10.5)
    c_rec.drawString(margin_5 + 15, y - 20, "Received From:")
    c_rec.drawString(margin_5 + 15, y - 55, "Amount (in words):")
    c_rec.drawString(margin_5 + 15, y - 90, "Payment Purpose:")
    c_rec.drawString(margin_5 + 15, y - 125, "Payment Method:")
    
    # Blanks / Lines
    c_rec.setStrokeColorRGB(0.8, 0.8, 0.8)
    c_rec.line(margin_5 + 115, y - 20, w_a5 - margin_5 - 15, y - 20)
    c_rec.line(margin_5 + 130, y - 55, w_a5 - margin_5 - 15, y - 55)
    c_rec.line(margin_5 + 125, y - 90, w_a5 - margin_5 - 15, y - 90)
    
    # Fill in details if available
    c_rec.setFillColorRGB(0.1, 0.1, 0.1)
    c_rec.setFont("Montserrat-Bold", 10.5)
    c_rec.drawString(margin_5 + 125, y - 18, "Representative Customer")
    c_rec.drawString(margin_5 + 135, y - 53, "Rupees One Lakh Only (Demo)")
    c_rec.drawString(margin_5 + 130, y - 88, f"{items[0][0]} Setup Delivery")
    c_rec.drawString(margin_5 + 125, y - 123, "Online Bank Transfer / UPI")
    
    # Amount block inside the receipt box
    c_rec.setFillColor(get_reportlab_color(brand_color_hex))
    c_rec.rect(margin_5 + 15, y - 185, 140, 35, fill=1, stroke=0)
    
    c_rec.setFillColorRGB(1, 1, 1)
    c_rec.setFont("Montserrat-Bold", 14)
    c_rec.drawCentredString(margin_5 + 85, y - 173, f"₹{total:,.2f}")
    
    # Signature
    c_rec.setFillColorRGB(0.3, 0.3, 0.3)
    c_rec.setFont("Inter-Regular", 9)
    c_rec.setStrokeColorRGB(0.8, 0.8, 0.8)
    c_rec.line(w_a5 - margin_5 - 120, y - 150, w_a5 - margin_5, y - 150)
    c_rec.drawCentredString(w_a5 - margin_5 - 60, y - 165, "Receiver's Signature")
    
    # A5 bottom bar
    c_rec.setFillColor(get_reportlab_color(brand_color_hex))
    c_rec.rect(0, 0, w_a5, 10, fill=1, stroke=0)
    
    c_rec.showPage()
    c_rec.save()
    generated_files["receipt_pdf"] = "receipt.pdf"
    
    # ---------------- PIL PREVIEWS (QUOTATION, INVOICE, RECEIPT) ----------------
    def generate_pil_mockup(filename, title, num_label, num_val, extra_label=None, extra_val=None):
        pw, ph = 595, 842
        img = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Header banner
        draw.rectangle([0, 0, pw, 20], fill=brand_rgb)
        
        # Mock logo circle
        draw.ellipse([margin, 40, margin + 40, 80], fill=brand_rgb)
        
        # Name
        font_b = get_pil_font('montserrat_bold', 20)
        draw.text((margin + 50, 45), business_name, fill=(30, 30, 30), font=font_b)
        
        # Title Right
        font_t = get_pil_font('montserrat_bold', 22)
        bbox = draw.textbbox((0, 0), title, font=font_t)
        t_w = bbox[2] - bbox[0]
        draw.text((pw - margin - t_w, 45), title, fill=brand_rgb, font=font_t)
        
        # Line
        draw.rectangle([margin, 100, pw - margin, 101], fill=(200, 200, 200))
        
        # Metadata block mockup
        font_m = get_pil_font('inter_regular', 10)
        draw.text((margin, 120), "TO: Representative Customer", fill=(100, 100, 100), font=font_m)
        draw.text((margin, 135), "Address Field, Rajnagar, Ghaziabad", fill=(120, 120, 120), font=font_m)
        
        # Right meta
        m1 = f"{num_label}: {num_val}"
        rbox1 = draw.textbbox((0, 0), m1, font=font_m)
        draw.text((pw - margin - (rbox1[2]-rbox1[0]), 120), m1, fill=(100, 100, 100), font=font_m)
        
        m2 = f"Date: {today_str}"
        rbox2 = draw.textbbox((0, 0), m2, font=font_m)
        draw.text((pw - margin - (rbox2[2]-rbox2[0]), 135), m2, fill=(100, 100, 100), font=font_m)
        
        if extra_label:
            m3 = f"{extra_label}: {extra_val}"
            rbox3 = draw.textbbox((0, 0), m3, font=font_m)
            draw.text((pw - margin - (rbox3[2]-rbox3[0]), 150), m3, fill=(100, 100, 100), font=font_m)
            
        # Items Box
        draw.rectangle([margin, 180, pw - margin, 200], fill=brand_rgb)
        
        # Rows Grid mockup
        font_i = get_pil_font('montserrat_bold', 10)
        draw_preview_grid_lines(draw, 220, 360, 30, pw, margin)
        
        # Draw top 2 parsed items mock
        draw.text((margin + 10, 210), items[0][0], fill=(50, 50, 50), font=font_i)
        draw.text((margin + 10, 240), items[1][0] if len(items) > 1 else "Standard Setup Option", fill=(50, 50, 50), font=font_i)
        
        # Draw subtotal and total
        draw.text((pw - margin - 150, 380), "Subtotal:", fill=(100, 100, 100), font=font_m)
        tot_str = f"₹{total:,.2f}"
        tbox = draw.textbbox((0, 0), tot_str, font=font_i)
        draw.text((pw - margin - (tbox[2]-tbox[0]), 410), tot_str, fill=brand_rgb, font=font_i)
        draw.text((pw - margin - 150, 410), "Total Due:", fill=(30, 30, 30), font=font_i)
        
        # Sign lines
        draw.line([pw - margin - 120, 500, pw - margin, 500], fill=(200, 200, 200))
        
        # Save preview
        img_path = os.path.join(output_dir, filename)
        img.convert("RGB").save(img_path, "PNG")
        
    generate_pil_mockup("quotation_preview.png", "QUOTATION", "Quote No", qt_num)
    generated_files["quotation_preview"] = "quotation_preview.png"
    
    generate_pil_mockup("invoice_preview.png", "INVOICE", "Invoice No", inv_num, "Due Date", due_str)
    generated_files["invoice_preview"] = "invoice_preview.png"
    
    # Generate receipt preview (smaller)
    pw_r, ph_r = 420, 595
    img_r = Image.new("RGBA", (pw_r, ph_r), (255, 255, 255, 255))
    draw_r = ImageDraw.Draw(img_r)
    
    # Top banner
    draw_r.rectangle([0, 0, pw_r, 15], fill=brand_rgb)
    
    # Receipt text
    font_rb = get_pil_font('montserrat_bold', 16)
    draw_r.text((30, 30), "PAYMENT RECEIPT", fill=brand_rgb, font=font_rb)
    
    # Business name
    font_ri = get_pil_font('inter_regular', 9)
    draw_r.text((30, 60), f"From: {business_name}", fill=(100, 100, 100), font=font_ri)
    
    # Center core receipt box mockup
    draw_r.rectangle([30, 90, pw_r - 30, 330], fill=(245, 248, 250), outline=(220, 220, 220))
    
    font_ritem = get_pil_font('inter_regular', 10)
    draw_r.text((45, 110), f"Received From: Representative Customer", fill=(50, 50, 50), font=font_ritem)
    draw_r.text((45, 145), f"Amount: ₹{total:,.2f}", fill=(50, 50, 50), font=font_ritem)
    draw_r.text((45, 180), f"Purpose: {items[0][0]} Setup", fill=(50, 50, 50), font=font_ritem)
    
    # Signature line A5
    draw_r.line([pw_r - 140, 260, pw_r - 45, 260], fill=(180, 180, 180))
    draw_r.text((pw_r - 135, 270), "Authorized Signee", fill=(120, 120, 120), font=get_pil_font('inter_regular', 8))
    
    rec_preview_path = os.path.join(output_dir, "receipt_preview.png")
    img_r.convert("RGB").save(rec_preview_path, "PNG")
    generated_files["receipt_preview"] = "receipt_preview.png"
    
    return generated_files
