import random
import string


def generate_pin_code(length: int = 6) -> str:
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))