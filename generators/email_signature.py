import os
from PIL import Image, ImageDraw
from utils.fonts import get_pil_font
from utils.colors import hex_to_rgb

def draw_mini_icon(draw: ImageDraw.ImageDraw, icon_type: str, xy: tuple[float, float], size: float, color: tuple[int, int, int]):
    """Draw a tiny stylized icon on the email signature PNG."""
    x, y = xy
    if icon_type == "phone":
        draw.rectangle([x + 2, y + 2, x + size - 2, y + size - 2], outline=color, width=1)
        draw.ellipse([x + size//2 - 2, y + size - 5, x + size//2 + 2, y + size - 1], fill=color)
    elif icon_type == "email":
        draw.rectangle([x + 1, y + 3, x + size - 1, y + size - 3], outline=color, width=1)
        draw.line([x + 1, y + 3, x + size//2, y + size//2], fill=color, width=1)
        draw.line([x + size - 1, y + 3, x + size//2, y + size//2], fill=color, width=1)
    elif icon_type == "website":
        draw.ellipse([x + 1, y + 1, x + size - 1, y + size - 1], outline=color, width=1)
        draw.line([x + 1, y + size//2, x + size - 1, y + size//2], fill=color, width=1)

def generate_email_signature(
    business_name: str,
    owner_name: str,
    phone: str,
    email: str,
    website: str = "",
    tagline: str = "",
    brand_color_hex: str = "#2563EB",
    logo_path: str = None,
    output_dir: str = ""
) -> dict:
    """
    Generate inline-styled HTML signature file and a matching PNG image.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    brand_rgb = hex_to_rgb(brand_color_hex)
    
    html_path = os.path.join(output_dir, "email_signature.html")
    png_path = os.path.join(output_dir, "email_signature.png")
    
    # ---------------- 1. HTML SIGNATURE (INLINE STYLED TABLES) ----------------
    # We use table structure for high email client rendering compatibility
    logo_src = ""
    if logo_path and os.path.exists(logo_path):
        # We serve logo via API or base64. Let's use relative path logo_primary.png
        # In a real email, this would be hosted online, so we use a placeholder that the user can replace.
        logo_src = "logo_primary.png"
    else:
        logo_src = ""
        
    logo_td = ""
    if logo_src:
        logo_td = f"""
        <td style="vertical-align: middle; padding-right: 20px;">
            <img src="{logo_src}" alt="Logo" width="80" height="80" style="display: block; border-radius: 8px;" />
        </td>
        """
    else:
        # Initial letter icon circle
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        logo_td = f"""
        <td style="vertical-align: middle; padding-right: 20px;">
            <table cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                <tr>
                    <td align="center" style="width: 80px; height: 80px; background-color: {brand_color_hex}; border-radius: 50%; color: #FFFFFF; font-family: 'Montserrat', Arial, sans-serif; font-size: 28px; font-weight: bold; line-height: 80px; vertical-align: middle;">
                        {initials}
                    </td>
                </tr>
            </table>
        </td>
        """
        
    website_row = ""
    if website:
        website_row = f"""
        <tr style="font-family: Arial, sans-serif; font-size: 13px; color: #4B5563; line-height: 18px;">
            <td style="font-weight: bold; color: {brand_color_hex}; width: 18px;">W:</td>
            <td><a href="https://{website}" target="_blank" style="color: #4B5563; text-decoration: none;">{website}</a></td>
        </tr>
        """
        
    html_content = f"""<!-- Magic Business Email Signature Template -->
<table cellpadding="0" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif; text-align: left;">
    <tr>
        {logo_td}
        <!-- Vertical Accent Bar -->
        <td style="border-left: 2px solid {brand_color_hex}; padding-left: 20px; vertical-align: middle;">
            <table cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                <tr>
                    <td style="font-family: 'Montserrat', Arial, sans-serif; font-size: 18px; font-weight: bold; color: #111827; padding-bottom: 2px;">
                        {owner_name}
                    </td>
                </tr>
                <tr>
                    <td style="font-family: Arial, sans-serif; font-size: 13px; color: {brand_color_hex}; font-weight: bold; padding-bottom: 8px;">
                        Founder / Owner at {business_name}
                    </td>
                </tr>
                <tr>
                    <td>
                        <table cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                            <tr style="font-family: Arial, sans-serif; font-size: 13px; color: #4B5563; line-height: 18px;">
                                <td style="font-weight: bold; color: {brand_color_hex}; width: 18px;">P:</td>
                                <td style="padding-right: 15px;"><a href="tel:{phone}" style="color: #4B5563; text-decoration: none;">{phone}</a></td>
                            </tr>
                            <tr style="font-family: Arial, sans-serif; font-size: 13px; color: #4B5563; line-height: 18px;">
                                <td style="font-weight: bold; color: {brand_color_hex}; width: 18px;">E:</td>
                                <td><a href="mailto:{email}" style="color: #4B5563; text-decoration: none;">{email}</a></td>
                            </tr>
                            {website_row}
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td colspan="2" style="font-family: Arial, sans-serif; font-size: 10px; color: #9CA3AF; padding-top: 15px; border-top: 1px solid #E5E7EB; margin-top: 10px;">
            This email signature was generated by <b>Magic Business</b>. Join the branding ecosystem.
        </td>
    </tr>
</table>
"""
    with open(html_path, "w") as f:
        f.write(html_content)
    generated_files["email_signature_html"] = "email_signature.html"
    
    # ---------------- 2. PNG SIGNATURE (600x200 px) ----------------
    w, h = 600, 200
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Left logo placement
    logo_drawn = False
    if logo_path and os.path.exists(logo_path):
        try:
            p_logo = Image.open(logo_path).convert("RGBA")
            p_logo.thumbnail((80, 80), Image.Resampling.LANCZOS)
            lw, lh = p_logo.size
            img.alpha_composite(p_logo, (30, (h - lh - 25)//2))
            logo_drawn = True
        except Exception:
            pass
            
    if not logo_drawn:
        # Fallback geometric initials circle
        draw.ellipse([30, 40, 110, 120], fill=brand_rgb)
        initials = "".join(w[0] for w in business_name.split()[:2]).upper()
        font_init = get_pil_font('montserrat_bold', 28)
        ibox = draw.textbbox((0, 0), initials, font=font_init)
        iw = ibox[2] - ibox[0]
        ih = ibox[3] - ibox[1]
        draw.text((70 - iw//2 - ibox[0], 80 - ih//2 - ibox[1]), initials, fill=(255, 255, 255), font=font_init)
        
    # Vertical brand color accent bar
    draw.rectangle([130, 30, 132, 130], fill=brand_rgb)
    
    # Text details
    font_name = get_pil_font('montserrat_bold', 18)
    draw.text((150, 30), owner_name, fill=(18, 18, 18), font=font_name)
    
    font_title = get_pil_font('inter_bold', 12)
    draw.text((150, 55), f"Founder / Owner at {business_name}", fill=brand_rgb, font=font_title)
    
    # Details rows
    font_detail = get_pil_font('inter_regular', 11)
    
    # Row 1: Phone
    draw_mini_icon(draw, "phone", (150, 80), 12, brand_rgb)
    draw.text((170, 80), phone, fill=(80, 80, 80), font=font_detail)
    
    # Row 2: Email
    draw_mini_icon(draw, "email", (150, 100), 12, brand_rgb)
    draw.text((170, 100), email, fill=(80, 80, 80), font=font_detail)
    
    # Row 3: Website
    if website:
        draw_mini_icon(draw, "website", (150, 120), 12, brand_rgb)
        draw.text((170, 120), website, fill=(80, 80, 80), font=font_detail)
        
    # Divider for footer credit
    draw.line([30, 160, w - 30, 160], fill=(220, 220, 220))
    
    # Footer credit
    font_credit = get_pil_font('inter_regular', 9)
    draw.text((30, 172), "Email signature generated by Magic Business.", fill=(150, 150, 150), font=font_credit)
    
    img.convert("RGB").save(png_path, "PNG")
    generated_files["email_signature_png"] = "email_signature.png"
    
    return generated_files
