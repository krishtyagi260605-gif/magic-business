import colorsys

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert hex string (e.g., #FF0000 or FF0000) to RGB tuple (0-255)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        return (37, 99, 235)  # Default Magic Blue
    try:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return (37, 99, 235)

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple (0-255) to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def get_brightness(hex_str: str) -> float:
    """Calculate relative brightness (luminance) of a hex color (0.0 to 1.0)."""
    r, g, b = hex_to_rgb(hex_str)
    # Standard formula for relative luminance
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

def get_text_color_for_background(bg_hex: str) -> str:
    """Return #FFFFFF or #000000 depending on background luminance to ensure high contrast."""
    return "#FFFFFF" if get_brightness(bg_hex) < 0.6 else "#000000"

def generate_secondary_color(primary_hex: str) -> str:
    """
    Generate a harmonious secondary color based on the primary color.
    Uses HSL rotation (complimentary/triadic shift).
    """
    r, g, b = hex_to_rgb(primary_hex)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    
    # Shift hue by 180 degrees (complementary) or shift slightly if color is desaturated
    new_h = (h + 0.5) % 1.0
    
    # Make adjustments to saturation and lightness for harmony
    new_s = max(0.4, min(s, 0.9))
    new_l = max(0.3, min(l, 0.7))
    
    new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, new_s)
    return rgb_to_hex((int(new_r * 255), int(new_g * 255), int(new_b * 255)))

def get_reportlab_color(hex_str: str):
    """Return ReportLab Color object from hex string."""
    from reportlab.lib.colors import HexColor
    # Ensure it starts with #
    if not hex_str.startswith('#'):
        hex_str = '#' + hex_str
    return HexColor(hex_str)
