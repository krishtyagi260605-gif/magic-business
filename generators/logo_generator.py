import os
import math
from PIL import Image, ImageDraw, ImageOps
from utils.fonts import get_pil_font
from utils.colors import hex_to_rgb, get_text_color_for_background

def make_transparent_variant(img: Image.Image, color_rgb: tuple[int, int, int]) -> Image.Image:
    """Creates a monochrome variant of a transparent PNG (all non-transparent pixels colored with color_rgb)."""
    rgba = img.convert("RGBA")
    datas = rgba.getdata()
    
    new_data = []
    for item in datas:
        # If not completely transparent, replace with target color keeping original alpha
        if item[3] > 0:
            new_data.append((color_rgb[0], color_rgb[1], color_rgb[2], item[3]))
        else:
            new_data.append(item)
            
    rgba.putdata(new_data)
    return rgba

def draw_hexagon(draw: ImageDraw.ImageDraw, center: tuple[float, float], radius: float, fill_color: tuple[int, int, int]):
    """Draw a regular flat-top hexagon centered at the given coordinates."""
    cx, cy = center
    points = []
    for i in range(6):
        # 30, 90, 150, 210, 270, 330 degrees in radians
        angle = math.radians(30 + 60 * i)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill_color)

def generate_text_logo_icon(shape_type: str, initials: str, brand_color_hex: str, size: int = 500) -> Image.Image:
    """Generate the geometric shape icon portion of the logo (circle, rounded_rect, or hexagon)."""
    icon = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    color_rgb = hex_to_rgb(brand_color_hex)
    text_color = get_text_color_for_background(brand_color_hex)
    
    margin = int(size * 0.05)
    shape_radius = (size - 2 * margin) // 2
    cx, cy = size // 2, size // 2
    
    # Draw shape background
    if shape_type == "circle":
        draw.ellipse([margin, margin, size - margin, size - margin], fill=color_rgb)
    elif shape_type == "rounded_square":
        # Draw rounded rectangle
        draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=int(size * 0.15), fill=color_rgb)
    elif shape_type == "hexagon":
        draw_hexagon(draw, (cx, cy), shape_radius, color_rgb)
    else:
        # Default to circle
        draw.ellipse([margin, margin, size - margin, size - margin], fill=color_rgb)
        
    # Draw text initials
    # Find font size that fits nicely (typically 40% of shape height)
    font_size = int(size * 0.4)
    font = get_pil_font('montserrat_bold', font_size)
    
    # Use textlength and textbbox to accurately center text
    # Pillow 10 syntax:
    text_bbox = draw.textbbox((0, 0), initials, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    tx = cx - text_w // 2 - text_bbox[0]
    # Small vertical correction since Montserrat capital letters are slightly offset
    ty = cy - text_h // 2 - text_bbox[1] - int(text_h * 0.05)
    
    draw.text((tx, ty), initials, fill=text_color, font=font)
    
    return icon

def generate_logo(
    business_name: str, 
    brand_color_hex: str, 
    output_dir: str,
    uploaded_file_path: str = None
) -> dict:
    """
    Generate or process logos.
    Returns a dictionary of generated filenames.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    generated_files = {}
    
    if uploaded_file_path and os.path.exists(uploaded_file_path):
        # Process uploaded logo
        try:
            primary_img = Image.open(uploaded_file_path)
            # Remove white background if applicable or just convert to RGBA
            primary_img = primary_img.convert("RGBA")
            
            # Resize fit in 1000x1000px max (maintaining aspect ratio)
            primary_img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
            
            # Save primary logo
            primary_path = os.path.join(output_dir, "logo_primary.png")
            primary_img.save(primary_path, "PNG")
            generated_files["logo_primary"] = "logo_primary.png"
            
            # Generate White and Black versions
            white_img = make_transparent_variant(primary_img, (255, 255, 255))
            white_path = os.path.join(output_dir, "logo_white.png")
            white_img.save(white_path, "PNG")
            generated_files["logo_white"] = "logo_white.png"
            
            black_img = make_transparent_variant(primary_img, (0, 0, 0))
            black_path = os.path.join(output_dir, "logo_black.png")
            black_img.save(black_path, "PNG")
            generated_files["logo_black"] = "logo_black.png"
            
            # Generate favicons
            for size in [32, 64]:
                fav_img = primary_img.copy()
                fav_img.thumbnail((size, size), Image.Resampling.LANCZOS)
                fav_path = os.path.join(output_dir, f"favicon_{size}x{size}.png")
                fav_img.save(fav_path, "PNG")
                generated_files[f"favicon_{size}"] = f"favicon_{size}x{size}.png"
                
            return generated_files
            
        except Exception as e:
            print(f"Error processing uploaded logo: {e}. Falling back to text-based generation.")
            
    # Text-based Logo Generation
    # Extract initials (max 3 characters)
    words = business_name.split()
    if len(words) >= 3:
        initials = "".join(w[0] for w in words[:3]).upper()
    elif len(words) == 2:
        initials = (words[0][0] + words[1][0]).upper()
    elif len(words) == 1:
        initials = business_name[:2].upper() if len(business_name) > 1 else business_name[0].upper()
    else:
        initials = "MB"
        
    shapes = ["circle", "rounded_square", "hexagon"]
    
    # We will generate three shapes. The Circle shape will be the "primary" logo,
    # and we will save variations forrounded_square and hexagon as alternate options.
    for shape in shapes:
        # Create a canvas of 1000x1000
        canvas = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 1. Draw shape icon (500x500px centered in top half of the canvas)
        icon_img = generate_text_logo_icon(shape, initials, brand_color_hex, size=500)
        canvas.alpha_composite(icon_img, (250, 120))  # Centered horizontally, offset vertically
        
        # 2. Draw business name text (centered below the shape)
        # Font size auto-scaled based on business name length
        font_size = int(max(40, min(80, 1000 // (len(business_name) * 0.75))))
        font = get_pil_font('montserrat_bold', font_size)
        
        text_bbox = draw.textbbox((0, 0), business_name, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        
        tx = 500 - text_w // 2 - text_bbox[0]
        ty = 680 - text_bbox[1]  # Placed below the icon
        
        # Draw business name text in dark grey/black
        # For transparent PNG, we can draw in white for dark mode or dark grey for general use.
        # Let's draw in solid black for the primary, and white for the white variant.
        draw.text((tx, ty), business_name, fill=(18, 18, 18, 255), font=font)
        
        # Save shape-specific primary logo
        filename = f"logo_{shape}.png"
        path = os.path.join(output_dir, filename)
        canvas.save(path, "PNG")
        generated_files[f"logo_{shape}"] = filename
        
    # Set Circle as the main "logo_primary.png"
    shutil_copy(os.path.join(output_dir, "logo_circle.png"), os.path.join(output_dir, "logo_primary.png"))
    generated_files["logo_primary"] = "logo_primary.png"
    
    # Generate White and Black variants for the primary (circle) logo
    # White variant: White icon + white text
    canvas_w = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0))
    draw_w = ImageDraw.Draw(canvas_w)
    icon_w = generate_text_logo_icon("circle", initials, "#FFFFFF", size=500)
    canvas_w.alpha_composite(icon_w, (250, 120))
    
    font = get_pil_font('montserrat_bold', font_size)
    text_bbox = draw_w.textbbox((0, 0), business_name, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    tx = 500 - text_w // 2 - text_bbox[0]
    ty = 680 - text_bbox[1]
    draw_w.text((tx, ty), business_name, fill=(255, 255, 255, 255), font=font)
    
    white_path = os.path.join(output_dir, "logo_white.png")
    canvas_w.save(white_path, "PNG")
    generated_files["logo_white"] = "logo_white.png"
    
    # Black variant: Black icon + black text
    canvas_b = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0))
    draw_b = ImageDraw.Draw(canvas_b)
    icon_b = generate_text_logo_icon("circle", initials, "#000000", size=500)
    canvas_b.alpha_composite(icon_b, (250, 120))
    draw_b.text((tx, ty), business_name, fill=(0, 0, 0, 255), font=font)
    
    black_path = os.path.join(output_dir, "logo_black.png")
    canvas_b.save(black_path, "PNG")
    generated_files["logo_black"] = "logo_black.png"
    
    # Generate Favicons
    primary_circle = Image.open(os.path.join(output_dir, "logo_primary.png"))
    for size in [32, 64]:
        fav_img = primary_circle.copy()
        fav_img.thumbnail((size, size), Image.Resampling.LANCZOS)
        fav_path = os.path.join(output_dir, f"favicon_{size}x{size}.png")
        fav_img.save(fav_path, "PNG")
        generated_files[f"favicon_{size}"] = f"favicon_{size}x{size}.png"
        
    return generated_files

def shutil_copy(src, dst):
    import shutil
    shutil.copy(src, dst)
