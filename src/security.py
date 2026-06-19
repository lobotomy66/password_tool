"""
security.py
Отвечает за всё, что связано с криптографией:

1. Мастер-пароль никогда не хранится в открытом виде.
   Для проверки входа используется Argon2 (современный, устойчивый
   к подбору алгоритм хеширования паролей — победитель Password
   Hashing Competition, рекомендован OWASP).

2. Для шифрования самих записей (логин/пароль/заметки) используется
   симметричное шифрование Fernet (AES-128 в режиме CBC + HMAC для
   проверки целостности) из библиотеки `cryptography`.

3. Ключ шифрования НЕ хранится на диске. Он каждый раз заново
   вычисляется из мастер-пароля пользователя с помощью PBKDF2HMAC
   и уникальной соли (salt), которая хранится в базе. Это значит:
   забыли мастер-пароль — расшифровать данные невозможно (как и в
   KeePassXC).
"""

import os
import base64

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ph = PasswordHasher()


def hash_master_password(master_password: str) -> str:
    """Возвращает хеш мастер-пароля для хранения в базе."""
    return ph.hash(master_password)


def verify_master_password(master_password: str, stored_hash: str) -> bool:
    """Проверяет, совпадает ли введённый мастер-пароль с хешем."""
    try:
        return ph.verify(stored_hash, master_password)
    except VerifyMismatchError:
        return False


def generate_salt() -> bytes:
    """Генерирует случайную соль (16 байт) для деривации ключа."""
    return os.urandom(16)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Превращает (мастер-пароль + соль) в 32-байтный ключ,
    пригодный для Fernet. 390_000 итераций — рекомендация
    OWASP на 2024+ год для PBKDF2-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390_000,
    )
    key_bytes = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(key_bytes)


def encrypt(data: str, key: bytes) -> str:
    """Шифрует строку и возвращает её в виде текста (для хранения в SQLite)."""
    f = Fernet(key)
    token = f.encrypt(data.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(token: str, key: bytes) -> str:
    """Расшифровывает строку. Если ключ неверный — выбрасывает InvalidToken."""
    f = Fernet(key)
    data = f.decrypt(token.encode("utf-8"))
    return data.decode("utf-8")


def is_key_valid(key: bytes, test_token: str) -> bool:
    """Проверяет, подходит ли ключ к зашифрованным данным."""
    try:
        decrypt(test_token, key)
        return True
    except InvalidToken:
        return False
