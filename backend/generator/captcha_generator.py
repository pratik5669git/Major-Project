import os
import sys
import random
from PIL import Image, ImageDraw, ImageFont

# Ensure imports work whether run as module or script
try:
    from .text_generator import generate_random_text
except ImportError:
    try:
        from generator.text_generator import generate_random_text
    except ImportError:
        from text_generator import generate_random_text

# Resolve paths relative to backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "dataset", "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "captchas")


def get_all_font_paths():
    """
    Scans the fonts directory and returns a list of all available .ttf and .otf font file paths.
    """
    if os.path.exists(FONTS_DIR):
        font_files = [
            f for f in os.listdir(FONTS_DIR)
            if f.lower().endswith(('.ttf', '.otf'))
        ]
        return [os.path.join(FONTS_DIR, f) for f in font_files]
    return []


def check_font_supports_char(font, char: str, font_size: int = 40) -> bool:
    """
    Checks if a character is supported by the given PIL ImageFont and is clearly visible.
    Returns False if the character renders as a missing glyph box (\uFFFF / \u0000), a blank mask,
    or is too tiny/faint to be readable.
    """
    try:
        notdef_mask_1 = font.getmask('\uFFFF')
        notdef_mask_2 = font.getmask('\u0000')
        char_mask = font.getmask(char)

        min_w = max(2, int(4 * (font_size / 40.0)))
        min_h = max(5, int(10 * (font_size / 40.0)))

        # 1. Empty or excessively small mask dimensions (invisible characters)
        if char_mask.size[0] < min_w or char_mask.size[1] < min_h:
            return False

        char_bytes = list(char_mask)
        # 2. Entirely transparent / blank character
        if not any(char_bytes):
            return False

        # 3. Matches .notdef missing glyph box masks
        if char_mask.size == notdef_mask_1.size and char_bytes == list(notdef_mask_1):
            return False
        if char_mask.size == notdef_mask_2.size and char_bytes == list(notdef_mask_2):
            return False

        return True
    except Exception:
        return False


def get_random_font_for_char(char: str, font_size: int, all_font_paths: list):
    """
    Randomly selects a font from available .ttf and .otf files that supports the given character.
    Discards any font that renders a missing glyph box or invisible character.
    """
    available = list(all_font_paths)
    random.shuffle(available)

    for font_path in available:
        try:
            font = ImageFont.truetype(font_path, font_size)
            if check_font_supports_char(font, char, font_size):
                return font, font_path
        except Exception:
            continue

    # Fallback to PIL default font if no custom font supports this character
    return ImageFont.load_default(), "default"


def generate_captcha(
    text: str = None,
    font_size: int = 48,
    width: int = 240,
    height: int = 80,
    scale_factor: int = 3,
    output_dir: str = OUTPUT_DIR
) -> str:
    """
    Generates a high-definition (HD) CAPTCHA image with super-sampled anti-aliased rendering.
    Each character is rendered in a DIFFERENT randomly selected .ttf/.otf font style.
    Ensures ultra-sharp clarity, smooth edges, clear small and capital letters, and baseline alignment.

    :param text: Text string for CAPTCHA. If None, generates a random 6-character text.
    :param font_size: Base font size for uppercase letters and digits (at 1x scale).
    :param width: Base width of the CAPTCHA image.
    :param height: Base height of the CAPTCHA image.
    :param scale_factor: Supersampling multiplier for high-resolution anti-aliasing.
    :param output_dir: Directory where the output CAPTCHA image will be saved.
    :return: Absolute file path to the saved CAPTCHA image.
    """
    if text is None:
        text = generate_random_text(length=6)

    # High-Resolution canvas dimensions for HD supersampling anti-aliasing
    render_width = width * scale_factor
    render_height = height * scale_factor

    image = Image.new("RGB", (render_width, render_height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Gather all available .ttf and .otf font paths
    all_font_paths = get_all_font_paths()

    # Scale font sizes for high-resolution rendering
    upper_font_size = font_size * scale_factor
    lower_font_size = max(28 * scale_factor, int(upper_font_size * 0.88))

    char_spacing = 6 * scale_factor
    char_data = []
    total_width = 0

    ref_upper_height = upper_font_size

    for char in text:
        target_size = lower_font_size if char.islower() else upper_font_size
        
        # Select a DIFFERENT random font style (.ttf/.otf) for each character
        char_font, font_path = get_random_font_for_char(char, target_size, all_font_paths)
        
        try:
            bbox = draw.textbbox((0, 0), char, font=char_font)
            w = max(1, bbox[2] - bbox[0])
            h = max(1, bbox[3] - bbox[1])
            y_offset = bbox[1]
        except AttributeError:
            w, h = draw.textsize(char, font=char_font)
            y_offset = 0

        char_data.append({
            'char': char,
            'font': char_font,
            'font_path': font_path,
            'width': w,
            'height': h,
            'y_offset': y_offset,
            'is_lower': char.islower()
        })
        total_width += w + char_spacing

    if char_data:
        total_width -= char_spacing

    # Calculate start position to center string horizontally & vertically
    start_x = (render_width - total_width) / 2
    baseline_y = (render_height + ref_upper_height) / 2

    current_x = start_x
    for item in char_data:
        # Align characters along baseline
        char_y = baseline_y - item['height'] - item['y_offset']
        draw.text((current_x, char_y), item['char'], fill=(0, 0, 0), font=item['font'])
        current_x += item['width'] + char_spacing

    # High-quality downsampling using LANCZOS filter for ultra-sharp anti-aliased output
    final_width = render_width // 2  # Crisp 360x120 HD resolution output
    final_height = render_height // 2
    
    lanczos = getattr(Image, 'Resampling', Image).LANCZOS
    final_image = image.resize((final_width, final_height), lanczos)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save high-quality lossless PNG image
    output_filename = f"captcha_{text}.png"
    output_filepath = os.path.join(output_dir, output_filename)
    final_image.save(output_filepath, format="PNG", optimize=True)

    return output_filepath


if __name__ == "__main__":
    # Generate random text from text_generator.py
    sample_text = generate_random_text(6)
    print(f"Generated text: {sample_text}")

    # Create CAPTCHA image
    saved_path = generate_captcha(text=sample_text)
    print(f"CAPTCHA image saved to: {saved_path}")
