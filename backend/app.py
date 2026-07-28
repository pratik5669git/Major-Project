import os
import sys

# Add backend root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator.text_generator import generate_random_text
from generator.captcha_generator import generate_captcha


def main(num_captchas: int = 1):
    """
    Main runner script to generate CAPTCHA images.
    
    :param num_captchas: Number of CAPTCHA images to generate (default 1).
    """
    print("=" * 55)
    print("            CAPTCHA GENERATOR PIPELINE             ")
    print("=" * 55)

    for i in range(1, num_captchas + 1):
        # 1. Generate random text
        text = generate_random_text(length=6)
        
        # 2. Generate CAPTCHA image with random per-character .ttf/.otf fonts
        image_path = generate_captcha(text=text)
        
        print(f"[{i}/{num_captchas}] CAPTCHA Text: '{text}' -> Saved: {image_path}")

    print("=" * 55)
    print(f"Successfully completed generating {num_captchas} CAPTCHA image(s)!")


if __name__ == "__main__":
    # Optional count parameter from command line (e.g. `python app.py 5`)
    count = 1
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid count '{sys.argv[1]}', defaulting to 1.")

    main(num_captchas=count)
