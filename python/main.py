from password_checker import evaluate_password
from generator import generate_password
from storage import (
    create_vault,
    add_password,
    get_password,
    list_sites,
    load_vault
)


def print_menu():
    print("\n====== PASSWORD MANAGER ======")
    print("1. Создать хранилище")
    print("2. Сгенерировать пароль")
    print("3. Проверить пароль")
    print("4. Сохранить пароль")
    print("5. Получить пароль")
    print("6. Список сайтов")
    print("0. Выход")


def main():
    while True:
        print_menu()
        choice = input("\nВыбор: ")

        # ---------------- CREATE VAULT ----------------
        if choice == "1":
            master = input("Придумай мастер-пароль: ")
            create_vault(master)
            print("✅ Хранилище создано")

        # ---------------- GENERATE ----------------
        elif choice == "2":
            length = int(input("Длина пароля: "))
            pwd = generate_password(length=length)
            print("🔑 Пароль:", pwd)

        # ---------------- CHECK ----------------
        elif choice == "3":
            pwd = input("Пароль: ")
            result = evaluate_password(pwd)

            print("\n📊 Результат:")
            print("Уровень:", result["level"])
            print("Entropy:", result["entropy"])
            print("Score:", result["score"])

            if result["feedback"]:
                print("\n💡 Рекомендации:")
                for f in result["feedback"]:
                    print("-", f)

        # ---------------- SAVE ----------------
        elif choice == "4":
            master = input("Мастер-пароль: ")
            site = input("Сайт: ")
            pwd = input("Пароль: ")

            add_password(master, site, pwd)
            print("💾 Сохранено")

        # ---------------- GET ----------------
        elif choice == "5":
            master = input("Мастер-пароль: ")
            site = input("Сайт: ")

            pwd = get_password(master, site)
            print("🔓 Пароль:", pwd)

        # ---------------- LIST ----------------
        elif choice == "6":
            master = input("Мастер-пароль: ")
            sites = list_sites(master)

            print("\n📋 Сайты:")
            for s in sites:
                print("-", s)

        # ---------------- EXIT ----------------
        elif choice == "0":
            print("Выход...")
            break

        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    main()
