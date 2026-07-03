import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import ImageFont
from config import FONTS_DIR

# Define font paths
MONTSERRAT_BOLD = os.path.join(FONTS_DIR, "Montserrat-Bold.ttf")
MONTSERRAT_REGULAR = os.path.join(FONTS_DIR, "Montserrat-Regular.ttf")
INTER_BOLD = os.path.join(FONTS_DIR, "Inter-Bold.ttf")
INTER_REGULAR = os.path.join(FONTS_DIR, "Inter-Regular.ttf")

# Flags to trace if fonts have been registered in ReportLab
_reportlab_fonts_registered = False

def register_fonts_for_reportlab():
    """Register downloaded Montserrat and Inter fonts with ReportLab pdfmetrics."""
    global _reportlab_fonts_registered
    if _reportlab_fonts_registered:
        return
        
    try:
        if os.path.exists(MONTSERRAT_BOLD):
            pdfmetrics.registerFont(TTFont('Montserrat-Bold', MONTSERRAT_BOLD))
        if os.path.exists(MONTSERRAT_REGULAR):
            pdfmetrics.registerFont(TTFont('Montserrat-Regular', MONTSERRAT_REGULAR))
        if os.path.exists(INTER_REGULAR):
            pdfmetrics.registerFont(TTFont('Inter-Regular', INTER_REGULAR))
        if os.path.exists(INTER_BOLD):
            pdfmetrics.registerFont(TTFont('Inter-Bold', INTER_BOLD))
        _reportlab_fonts_registered = True
        print("Registered fonts with ReportLab successfully.")
    except Exception as e:
        print(f"Error registering fonts with ReportLab: {e}")

def get_pil_font(font_type: str, size: int) -> ImageFont.ImageFont:
    """
    Load and return a PIL ImageFont.
    font_type: 'montserrat_bold', 'montserrat_regular', 'inter_bold', 'inter_regular'
    """
    font_map = {
        'montserrat_bold': MONTSERRAT_BOLD,
        'montserrat_regular': MONTSERRAT_REGULAR,
        'inter_bold': INTER_BOLD,
        'inter_regular': INTER_REGULAR
    }
    
    font_path = font_map.get(font_type.lower())
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Failed to load font {font_path}: {e}. Falling back to default.")
            
    # Fallback to default system or PIL load_default font
    try:
        return ImageFont.load_default()
    except Exception:
        raise RuntimeError("Could not load any font, including system default.")
