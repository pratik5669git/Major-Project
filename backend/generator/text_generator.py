import random
import string


def generate_random_text(length: int = 6, chars: str = None) -> str:
    """
    Generates a random alphanumeric string of the specified length.
    Default character set includes uppercase letters, lowercase letters, and digits.
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def text_generator(length: int = 6, count: int = None):
    """
    Generator function that yields random alphanumeric strings.
    
    :param length: Length of each alphanumeric text (default 6).
    :param count: Total number of texts to generate. If None, yields indefinitely.
    """
    generated = 0
    while count is None or generated < count:
        yield generate_random_text(length=length)
        generated += 1


if __name__ == "__main__":
    # Simple demonstration
    captcha_text = generate_random_text()
    print(captcha_text)
