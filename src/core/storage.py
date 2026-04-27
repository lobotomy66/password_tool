import os
import json
import base64
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

# Путь к файлу хранилища
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_FILE = os.path.join(BASE_DIR, "vault.json")





# ------------------------
# Генерация ключа из мастер-пароля
# ------------------------
def derive_key(master_password: str, salt: bytes) -> bytes:
    """Генерация ключа на основе мастер-пароля и соли."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


# ------------------------
# Загрузка хранилища
# ------------------------
def load_vault():
    """Загрузка хранилища из файла."""
    if not os.path.exists(VAULT_FILE):
        return None

    with open(VAULT_FILE, "r") as f:
        return json.load(f)


# ------------------------
# Сохранение хранилища
# ------------------------
def save_vault(data):
    """Сохранение хранилища в файл."""
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f)


# ------------------------
# Создание нового хранилища
# ------------------------
def create_vault(master_password: str):
    """Создание нового хранилища с заданным мастер-паролем."""
    if os.path.exists(VAULT_FILE):
        raise ValueError("Хранилище уже существует")

    salt = os.urandom(16)
    key = derive_key(master_password, salt)
    fernet = Fernet(key)

    vault = {
        "salt": base64.b64encode(salt).decode(),
        "data": fernet.encrypt(json.dumps({}).encode()).decode()
    }

    save_vault(vault)
    return True


# ------------------------
# Получение шифратора
# ------------------------
def get_fernet(master_password: str, vault: dict):
    """Получение объекта Fernet для шифрования/расшифровки."""
    salt = base64.b64decode(vault["salt"])
    key = derive_key(master_password, salt)
    return Fernet(key)


# ------------------------
# Расшифровка данных
# ------------------------
def decrypt_vault(master_password: str):
    """Расшифровка данных из хранилища."""
    vault = load_vault()
    if not vault:
        raise ValueError("Хранилище не найдено")

    fernet = get_fernet(master_password, vault)
    decrypted = fernet.decrypt(vault["data"].encode())

    # Проверяем, что расшифрованные данные - это словарь
    data = json.loads(decrypted.decode())
    if not isinstance(data, dict):
        raise ValueError("Vault повреждён")

    

    return data


# ------------------------
# Шифрование и сохранение
# ------------------------
def encrypt_and_save(master_password: str, data: dict):
    """Шифрование данных и их сохранение в хранилище."""
    vault = load_vault()
    if not vault:
        raise ValueError("Хранилище не найдено")

    fernet = get_fernet(master_password, vault)
    encrypted = fernet.encrypt(json.dumps(data).encode()).decode()

    vault["data"] = encrypted
    save_vault(vault)


# ------------------------
# Добавить пароль
# ------------------------
def add_password(master_password: str, site: str, password: str):
    """Добавление нового пароля в хранилище."""
    data = decrypt_vault(master_password)
    data[site] = password
    encrypt_and_save(master_password, data)


# ------------------------
# Получить пароль
# ------------------------
def get_password(master_password: str, site: str):
    """Получение пароля для указанного сайта."""
    data = decrypt_vault(master_password)
    return data.get(site)


# ------------------------
# Показать все сайты
# ------------------------
def list_sites(master_password: str):
    """Получение списка всех сайтов из хранилища."""
    data = decrypt_vault(master_password)
    return list(data.keys())


# ------------------------
# Пример использования
# ------------------------
if __name__ == "__main__":
    print("1. Создать хранилище")
    print("2. Добавить пароль")
    print("3. Получить пароль")
    print("4. Список сайтов")

    choice = input("Выбор: ")

    master = input("Мастер-пароль: ")

    if choice == "1":
        create_vault(master)
        print("Хранилище создано")

    elif choice == "2":
        site = input("Сайт: ")
        pwd = input("Пароль: ")
        add_password(master, site, pwd)
        print("Сохранено")

    elif choice == "3":
        site = input("Сайт: ")
        print("Пароль:", get_password(master, site))

    elif choice == "4":
        print(list_sites(master))

