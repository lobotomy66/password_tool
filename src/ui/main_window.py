import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk  # Добавляем ttk для вкладок

class PasswordManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Password Manager")
        self.master.geometry("500x400")
        
        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(pady=10, fill="both", expand=True)

        # Вкладка 1: Хранилище
        self.vault_frame = tk.Frame(self.notebook)
        self.notebook.add(self.vault_frame, text="Хранилище")
        
        # Вкладка 2: Генерация паролей
        self.generate_frame = tk.Frame(self.notebook)
        self.notebook.add(self.generate_frame, text="Генерация паролей")

        # Вкладка 3: Проверка паролей
        self.check_frame = tk.Frame(self.notebook)
        self.notebook.add(self.check_frame, text="Проверка паролей")

        # Размещение элементов на вкладках
        self.create_vault_button = tk.Button(self.vault_frame, text="Создать хранилище", command=self.create_vault)
        self.create_vault_button.pack(pady=10)

        self.generate_password_button = tk.Button(self.generate_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_password_button.pack(pady=10)

        self.check_password_button = tk.Button(self.check_frame, text="Проверить пароль", command=self.check_password)
        self.check_password_button.pack(pady=10)

                # Изменение фона окна
        self.master.configure(bg="#f0f0f0")

        # Изменение стиля кнопок
        self.create_vault_button.configure(bg="#4CAF50", fg="white")  # Зеленая кнопка для создания хранилища
        self.generate_password_button.configure(bg="#2196F3", fg="white")  # Синяя кнопка для генерации пароля
        self.check_password_button.configure(bg="#FFC107", fg="white")  # Желтая кнопка для проверки пароля
        
                # Изменение шрифта кнопок
        self.create_vault_button.configure(font=("Arial", 12, "bold"))
        self.generate_password_button.configure(font=("Arial", 12, "bold"))
        self.check_password_button.configure(font=("Arial", 12, "bold"))
        
    def create_vault(self):
        """Функция для создания хранилища"""
        master_password = simpledialog.askstring("Мастер-пароль", "Введите мастер-пароль для хранилища:")
        if master_password:
            try:
                from core.storage import create_vault
                create_vault(master_password)
                messagebox.showinfo("Успех", "Хранилище успешно создано")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

    def generate_password(self):
        """Функция для генерации пароля"""
        from core.generator import generate_password
        length = simpledialog.askinteger("Длина пароля", "Введите длину пароля:")
        if length:
            password = generate_password(length)
            messagebox.showinfo("Сгенерированный пароль", f"Пароль: {password}")

    def check_password(self):
        """Функция для проверки пароля"""
        from core.password_checker import evaluate_password
        password = simpledialog.askstring("Проверка пароля", "Введите пароль для проверки:")
        if password:
            result = evaluate_password(password)
            messagebox.showinfo("Результаты проверки", f"Сложность: {result['level']}\nEntropy: {result['entropy']}\nScore: {result['score']}")
            if result['feedback']:
                feedback = "\n".join(result['feedback'])
                messagebox.showinfo("Рекомендации", feedback)



   