"""generator.py — генерация надёжных паролей и грубая оценка их силы."""

import secrets
import string


def generate_password(length=16, use_upper=True, use_digits=True, use_symbols=True) -> str:
    alphabet = list(string.ascii_lowercase)
    if use_upper:
        alphabet += list(string.ascii_uppercase)
    if use_digits:
        alphabet += list(string.digits)
    if use_symbols:
        alphabet += list("!@#$%^&*()-_=+[]{}")

    # secrets.choice — криптографически стойкий генератор случайных чисел,
    # в отличие от обычного random, который для паролей использовать нельзя.
    return "".join(secrets.choice(alphabet) for _ in range(length))


def password_strength(password: str) -> str:
    """Очень простая эвристика силы пароля для индикатора в UI."""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{}" for c in password):
        score += 1

    if score <= 1:
        return "Слабый"
    elif score <= 3:
        return "Средний"
    else:
        return "Сильный"
