import os
import datetime

def generate_website_placeholder(
    business_name: str,
    tagline: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    address: str = "",
    services: list[str] = None,
    brand_color_hex: str = "#2563EB",
    output_dir: str = ""
) -> dict:
    """
    Generate a modern, responsive index.html placeholder webpage for the business.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    
    html_path = os.path.join(output_dir, "index.html")
    
    # Preprocess services list
    services_li = ""
    if services:
        for s in services[:6]:
            s_clean = s.strip()
            # If separator is present, split into title and detail
            title = s_clean
            desc = ""
            for sep in ['-', '|', ':']:
                if sep in s_clean:
                    parts = s_clean.split(sep, 1)
                    title = parts[0].strip()
                    desc = parts[1].strip()
                    break
            
            desc_p = f"<p class='service-desc'>{desc}</p>" if desc else ""
            services_li += f"""
            <div class="service-card">
                <div class="service-icon" style="background-color: {brand_color_hex}1A; color: {brand_color_hex};">
                    ✦
                </div>
                <h3 class="service-title">{title}</h3>
                {desc_p}
            </div>
            """
    else:
        services_li = f"""
        <div class="service-card">
            <div class="service-icon" style="background-color: {brand_color_hex}1A; color: {brand_color_hex};">✦</div>
            <h3 class="service-title">Quality Assurance</h3>
            <p class="service-desc">We deliver top-tier standards in every project scope.</p>
        </div>
        <div class="service-card">
            <div class="service-icon" style="background-color: {brand_color_hex}1A; color: {brand_color_hex};">✦</div>
            <h3 class="service-title">Consultancy</h3>
            <p class="service-desc">Professional guidelines customized to meet your timeline goals.</p>
        </div>
        """
        
    tagline_h2 = f"<h2 class='tagline'>{tagline}</h2>" if tagline else ""
    address_p = f"<p class='contact-detail'><strong>📍 Address:</strong> {address.replace('\n', ', ')}</p>" if address else ""
    website_p = f"<p class='contact-detail'><strong>🌐 Website:</strong> <a href='https://{website}' target='_blank'>{website}</a></p>" if website else ""
    
    # Auto-generate initials logo for header
    initials = "".join(w[0] for w in business_name.split()[:2]).upper()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_name} | Welcome</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {brand_color_hex};
            --primary-light: {brand_color_hex}1A;
            --bg-dark: #0A0F1D;
            --bg-card: #141B2D;
            --text-light: #F8FAFC;
            --text-gray: #94A3B8;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: var(--bg-dark);
            color: var(--text-light);
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            overflow-x: hidden;
        }}
        
        /* Navbar */
        nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 8%;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .logo-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .logo-circle {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background-color: var(--primary);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 16px;
        }}
        
        .logo-name {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 18px;
            letter-spacing: 0.5px;
        }}
        
        .badge-soon {{
            background-color: var(--primary-light);
            color: var(--primary);
            font-size: 11px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid var(--primary);
        }}
        
        /* Hero Section */
        header {{
            text-align: center;
            padding: 100px 5% 60px 5%;
            position: relative;
        }}
        
        header::after {{
            content: '';
            position: absolute;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
            top: 10%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0.15;
            z-index: -1;
            filter: blur(40px);
        }}
        
        .hero-title {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 48px;
            letter-spacing: -0.5px;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #FFFFFF 0%, var(--text-gray) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .tagline {{
            font-size: 20px;
            color: var(--text-gray);
            font-weight: 400;
            max-width: 600px;
            margin: 0 auto 30px auto;
        }}
        
        .btn-cta {{
            display: inline-block;
            background-color: var(--primary);
            color: #FFFFFF;
            font-weight: 600;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.05);
        }}
        
        .btn-cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            filter: brightness(1.1);
        }}
        
        /* Services Section */
        .services-section {{
            padding: 60px 8%;
            text-align: center;
        }}
        
        .section-heading {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 28px;
            margin-bottom: 40px;
            position: relative;
            display: inline-block;
        }}
        
        .section-heading::after {{
            content: '';
            position: absolute;
            width: 60px;
            height: 3px;
            background-color: var(--primary);
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }}
        
        .service-card {{
            background-color: var(--bg-card);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 30px;
            text-align: left;
            transition: all 0.3s ease;
        }}
        
        .service-card:hover {{
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .service-icon {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-bottom: 20px;
        }}
        
        .service-title {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        
        .service-desc {{
            color: var(--text-gray);
            font-size: 14px;
        }}
        
        /* Contact Section */
        .contact-section {{
            background-color: rgba(20, 27, 45, 0.5);
            padding: 80px 8%;
            text-align: center;
            border-top: 1px solid rgba(255, 255, 255, 0.03);
        }}
        
        .contact-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: var(--bg-card);
            padding: 40px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }}
        
        .contact-detail {{
            font-size: 15px;
            margin: 15px 0;
            color: var(--text-gray);
        }}
        
        .contact-detail a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .contact-detail a:hover {{
            text-decoration: underline;
        }}
        
        /* Footer */
        footer {{
            text-align: center;
            padding: 40px 0;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.2);
            border-top: 1px solid rgba(255, 255, 255, 0.02);
        }}
        
        footer a {{
            color: rgba(255, 255, 255, 0.3);
            text-decoration: none;
        }}
    </style>
</head>
<body>

    <nav>
        <div class="logo-container">
            <div class="logo-circle">{initials}</div>
            <span class="logo-name">{business_name}</span>
        </div>
        <span class="badge-soon">Full Website Coming Soon</span>
    </nav>

    <header>
        <h1 class="hero-title">{business_name}</h1>
        {tagline_h2}
        <a href="#contact" class="btn-cta">Get In Touch</a>
    </header>

    <section class="services-section">
        <h2 class="section-heading">Our Core Offerings</h2>
        <div class="services-grid">
            {services_li}
        </div>
    </section>

    <section id="contact" class="contact-section">
        <h2 class="section-heading">Contact Us</h2>
        <div class="contact-container">
            <p class="contact-detail" style="margin-bottom: 25px; font-size: 16px; font-weight: 500;">
                Reach out directly via phone or email, or drop by our location.
            </p>
            <p class="contact-detail"><strong>📞 Phone:</strong> <a href="tel:{phone}">{phone}</a></p>
            <p class="contact-detail"><strong>✉️ Email:</strong> <a href="mailto:{email}">{email}</a></p>
            {website_p}
            {address_p}
        </div>
    </section>

    <footer>
        <p>&copy; {datetime.datetime.now().year} {business_name}. All rights reserved.</p>
        <p style="margin-top: 5px;">Branding Ecosystem by <a href="#" target="_blank">Magic Business</a></p>
    </footer>

</body>
</html>
"""
    with open(html_path, "w") as f:
        f.write(html_content)
    generated_files["website_index"] = "index.html"
    
    return generated_files
