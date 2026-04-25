import secrets
import string


# ------------------------
# Наборы символов
# ------------------------
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SPECIAL = "!@#$%^&*()-_=+[]{};:,.<>?"


# ------------------------
# Генерация пароля
# ------------------------
def generate_password(
    length=12,
    use_lowercase=True,
    use_uppercase=True,
    use_digits=True,
    use_special=True
):
    if length < 4:
        raise ValueError("Длина пароля должна быть минимум 4")

    char_pool = ""
    password_chars = []

    # Гарантируем хотя бы 1 символ каждого выбранного типа
    if use_lowercase:
        char_pool += LOWERCASE
        password_chars.append(secrets.choice(LOWERCASE))

    if use_uppercase:
        char_pool += UPPERCASE
        password_chars.append(secrets.choice(UPPERCASE))

    if use_digits:
        char_pool += DIGITS
        password_chars.append(secrets.choice(DIGITS))

    if use_special:
        char_pool += SPECIAL
        password_chars.append(secrets.choice(SPECIAL))

    if not char_pool:
        raise ValueError("Нужно выбрать хотя бы один тип символов")

    # Добиваем оставшуюся длину
    remaining_length = length - len(password_chars)
    for _ in range(remaining_length):
        password_chars.append(secrets.choice(char_pool))

    # Перемешиваем (иначе первые символы предсказуемы)
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


# ------------------------
# Генерация нескольких паролей
# ------------------------
def generate_multiple(count=5, **kwargs):
    return [generate_password(**kwargs) for _ in range(count)]


# ------------------------
# Генерация "читаемых" паролей (опционально)
# ------------------------
def generate_passphrase(num_words=4, separator="-"):
    # Мини-словарь (можно заменить на большой файл)
    words = [
        "apple", "river", "stone", "cloud", "forest",
        "shadow", "light", "storm", "wolf", "fire"
    ]

    chosen = [secrets.choice(words) for _ in range(num_words)]
    return separator.join(chosen)


# ------------------------
# Пример запуска
# ------------------------
if __name__ == "__main__":
    print("1. Случайный пароль")
    print("2. Несколько паролей")
    print("3. Passphrase")

    choice = input("Выбор: ")

    if choice == "1":
        pwd = generate_password(length=16)
        print("Пароль:", pwd)

    elif choice == "2":
        pwds = generate_multiple(count=5, length=14)
        for p in pwds:
            print(p)

    elif choice == "3":
        phrase = generate_passphrase()
        print("Passphrase:", phrase)
