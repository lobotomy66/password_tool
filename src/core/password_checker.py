import re
import math

# Простейший список частых паролей (можешь расширить)
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "qwerty", "12345678",
    "111111", "123123", "abc123", "password1"
}

# ------------------------
# Проверка структуры
# ------------------------
def check_password_structure(password):
    checks = {
        "length_8": len(password) >= 8,
        "length_12": len(password) >= 12,
        "lowercase": bool(re.search(r"[a-z]", password)),
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "digits": bool(re.search(r"[0-9]", password)),
        "special": bool(re.search(r"[^A-Za-z0-9]", password)),
    }
    return checks


# ------------------------
# Подсчёт score
# ------------------------
def calculate_score(checks):
    score = sum(checks.values())
    return score


# ------------------------
# Проверка на слабые паттерны
# ------------------------
def has_repeated_chars(password):
    return bool(re.search(r"(.)\1{2,}", password))


def has_sequences(password):
    sequences = [
        "abcdefghijklmnopqrstuvwxyz",
        "0123456789"
    ]
    password_lower = password.lower()

    for seq in sequences:
        for i in range(len(seq) - 3):
            if seq[i:i+4] in password_lower:
                return True
    return False


def is_common_password(password):
    return password.lower() in COMMON_PASSWORDS


# ------------------------
# Энтропия
# ------------------------
def calculate_entropy(password):
    charset = 0

    if re.search(r"[a-z]", password):
        charset += 26
    if re.search(r"[A-Z]", password):
        charset += 26
    if re.search(r"[0-9]", password):
        charset += 10
    if re.search(r"[^A-Za-z0-9]", password):
        charset += 32

    if charset == 0:
        return 0

    return len(password) * math.log2(charset)


# ------------------------
# Уровень сложности
# ------------------------
def get_strength_level(entropy):
    if entropy < 28:
        return "Очень слабый"
    elif entropy < 36:
        return "Слабый"
    elif entropy < 60:
        return "Средний"
    else:
        return "Сильный"


# ------------------------
# Рекомендации
# ------------------------
def get_feedback(password, checks):
    feedback = []

    if not checks["length_12"]:
        feedback.append("Сделай пароль длиннее (12+ символов)")
    if not checks["uppercase"]:
        feedback.append("Добавь заглавные буквы")
    if not checks["lowercase"]:
        feedback.append("Добавь строчные буквы")
    if not checks["digits"]:
        feedback.append("Добавь цифры")
    if not checks["special"]:
        feedback.append("Добавь специальные символы")

    if has_repeated_chars(password):
        feedback.append("Избегай повторяющихся символов (aaa, 111)")

    if has_sequences(password):
        feedback.append("Избегай последовательностей (abcd, 1234)")

    if is_common_password(password):
        feedback.append("Этот пароль слишком распространён")

    return feedback


# ------------------------
# Основная функция
# ------------------------
def evaluate_password(password):
    checks = check_password_structure(password)
    score = calculate_score(checks)
    entropy = calculate_entropy(password)

    # Приоритет слабых случаев
    if is_common_password(password):
        level = "Очень слабый"
    else:
        level = get_strength_level(entropy)

    feedback = get_feedback(password, checks)

    return {
        "password": password,
        "score": score,
        "entropy": round(entropy, 2),
        "level": level,
        "checks": checks,
        "feedback": feedback
    }


# ------------------------
# Пример запуска
# ------------------------
if __name__ == "__main__":
    pwd = input("Введите пароль: ")
    result = evaluate_password(pwd)

    print("\n--- Результат ---")
    print(f"Сложность: {result['level']}")
    print(f"Score: {result['score']}")
    print(f"Entropy: {result['entropy']}")

    print("\nРекомендации:")
    for f in result["feedback"]:
        print("-", f)
