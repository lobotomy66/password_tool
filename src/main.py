
"""
main.py — точка входа в приложение.
 
Экраны:
  1. SetupScreen  — первый запуск, создание мастер-пароля
  2. LoginScreen  — вход по мастер-паролю (если хранилище уже создано)
  3. VaultScreen  — основной экран: список записей + панель деталей
"""
 
import os
 
import customtkinter as ctk
import pyperclip
 
import database as db
import security as sec
from generator import generate_password, password_strength
 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
 
APP_TITLE = "SafeBox — менеджер паролей"
 
 
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("420x520")
        self.minsize(380, 480)
 
        db.init_db()
 
        self.encryption_key = None  # появится после успешного входа
        self.current_frame = None
 
        if db.vault_exists():
            self.show_frame(LoginScreen)
        else:
            self.show_frame(SetupScreen)
 
    def show_frame(self, frame_class, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)
 
    def on_login_success(self, key: bytes):
        self.encryption_key = key
        self.geometry("820x560")
        self.minsize(700, 480)
        self.show_frame(VaultScreen)
 
 
# ----------------------------------------------------------------------
# Экран первого запуска — создание мастер-пароля
# ----------------------------------------------------------------------
class SetupScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master_app = master
 
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
 
        ctk.CTkLabel(wrapper, text="🔒", font=ctk.CTkFont(size=42)).pack(pady=(0, 6))
        ctk.CTkLabel(wrapper, text="Добро пожаловать в SafeBox",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 4))
        ctk.CTkLabel(wrapper, text="Придумайте мастер-пароль для нового хранилища",
                     text_color="gray70").pack(pady=(0, 18))
 
        self.pw1 = ctk.CTkEntry(wrapper, placeholder_text="Мастер-пароль", show="•", width=280)
        self.pw1.pack(pady=6)
        self.pw2 = ctk.CTkEntry(wrapper, placeholder_text="Повторите пароль", show="•", width=280)
        self.pw2.pack(pady=6)
 
        self.error_label = ctk.CTkLabel(wrapper, text="", text_color="#ff6b6b")
        self.error_label.pack(pady=(4, 0))
 
        ctk.CTkButton(wrapper, text="Создать хранилище", width=280,
                      command=self.create_vault).pack(pady=(18, 0))
 
        ctk.CTkLabel(
            wrapper,
            text="⚠ Если вы забудете этот пароль, восстановить\nданные будет невозможно.",
            text_color="gray50", font=ctk.CTkFont(size=11), justify="center"
        ).pack(pady=(14, 0))
 
    def create_vault(self):
        p1, p2 = self.pw1.get(), self.pw2.get()
        if len(p1) < 8:
            self.error_label.configure(text="Пароль должен быть не короче 8 символов")
            return
        if p1 != p2:
            self.error_label.configure(text="Пароли не совпадают")
            return
 
        salt = sec.generate_salt()
        key = sec.derive_key(p1, salt)
        check_token = sec.encrypt("check", key)
        master_hash = sec.hash_master_password(p1)
 
        db.create_vault(master_hash, salt, check_token)
        self.master_app.on_login_success(key)
 
 
# ----------------------------------------------------------------------
# Модальное окно подтверждения сброса хранилища
# ----------------------------------------------------------------------
class ConfirmResetDialog(ctk.CTkToplevel):
    def __init__(self, master, on_confirm):
        super().__init__(master)
        self.title("Сброс хранилища")
        self.geometry("360x230")
        self.resizable(False, False)
        self.on_confirm = on_confirm
 
        self.grab_set()  # делает окно модальным
        self.transient(master)
 
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)
 
        ctk.CTkLabel(wrap, text="⚠ Это удалит ВСЕ записи безвозвратно",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#ff6b6b", justify="center", wraplength=300).pack(pady=(0, 10))
        ctk.CTkLabel(wrap, text='Чтобы подтвердить, введите слово УДАЛИТЬ:',
                     text_color="gray70", justify="center", wraplength=300).pack(pady=(0, 8))
 
        self.confirm_entry = ctk.CTkEntry(wrap, justify="center")
        self.confirm_entry.pack(fill="x", pady=(0, 6))
 
        self.error_label = ctk.CTkLabel(wrap, text="", text_color="#ff6b6b")
        self.error_label.pack()
 
        btn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(btn_row, text="Отмена", fg_color="transparent",
                      border_width=1, command=self.destroy).pack(side="left", expand=True, padx=(0, 6))
        ctk.CTkButton(btn_row, text="Удалить навсегда", fg_color="#b3261e",
                      hover_color="#8c1d17", command=self.confirm).pack(side="left", expand=True, padx=(6, 0))
 
        self.confirm_entry.focus()
 
    def confirm(self):
        if self.confirm_entry.get().strip().upper() != "УДАЛИТЬ":
            self.error_label.configure(text="Введите слово точно как указано")
            return
        self.destroy()
        self.on_confirm()
 
 
# ----------------------------------------------------------------------
# Экран входа
# ----------------------------------------------------------------------
class LoginScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master_app = master
 
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
 
        ctk.CTkLabel(wrapper, text="🔒", font=ctk.CTkFont(size=42)).pack(pady=(0, 6))
        ctk.CTkLabel(wrapper, text="SafeBox", font=ctk.CTkFont(size=22, weight="bold")).pack()
        ctk.CTkLabel(wrapper, text="Введите мастер-пароль", text_color="gray70").pack(pady=(0, 18))
 
        self.pw_entry = ctk.CTkEntry(wrapper, placeholder_text="Мастер-пароль", show="•", width=280)
        self.pw_entry.pack(pady=6)
        self.pw_entry.bind("<Return>", lambda e: self.try_login())
 
        self.error_label = ctk.CTkLabel(wrapper, text="", text_color="#ff6b6b")
        self.error_label.pack(pady=(4, 0))
 
        ctk.CTkButton(wrapper, text="Войти", width=280, command=self.try_login).pack(pady=(18, 0))
 
        ctk.CTkButton(wrapper, text="Сбросить хранилище", width=280,
                      fg_color="transparent", text_color="gray50",
                      hover_color=("gray85", "gray20"),
                      command=self.open_reset_dialog).pack(pady=(10, 0))
 
        self.pw_entry.focus()
 
    def open_reset_dialog(self):
        ConfirmResetDialog(self.master_app, on_confirm=self.reset_vault)
 
    def reset_vault(self):
        try:
            if os.path.exists(db.DB_PATH):
                os.remove(db.DB_PATH)
        except OSError:
            pass
        db.init_db()
        self.master_app.show_frame(SetupScreen)
 
    def try_login(self):
        password = self.pw_entry.get()
        meta = db.get_vault_meta()
 
        if not sec.verify_master_password(password, meta["master_hash"]):
            self.error_label.configure(text="Неверный мастер-пароль")
            return
 
        key = sec.derive_key(password, meta["salt"])
        if not sec.is_key_valid(key, meta["check_token"]):
            self.error_label.configure(text="Ошибка расшифровки. Попробуйте снова.")
            return
 
        self.master_app.on_login_success(key)
 
 
# ----------------------------------------------------------------------
# Основной экран — список записей + детали
# ----------------------------------------------------------------------
class VaultScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master_app = master
        self.key = master.encryption_key
        self.entries_cache = []
        self.selected_id = None
 
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
 
        # ---------- левая колонка: список ----------
        left = ctk.CTkFrame(self, width=280, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsw")
        left.grid_propagate(False)
 
        top_bar = ctk.CTkFrame(left, fg_color="transparent")
        top_bar.pack(fill="x", padx=14, pady=(14, 8))
        ctk.CTkLabel(top_bar, text="🔒 SafeBox", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(top_bar, text="+", width=32, height=32,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self.new_entry).pack(side="right")
 
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_list())
        search_entry = ctk.CTkEntry(left, placeholder_text="🔍 Поиск...", textvariable=self.search_var)
        search_entry.pack(fill="x", padx=14, pady=(0, 10))
 
        self.list_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 10))
 
        ctk.CTkButton(left, text="Выйти из хранилища", fg_color="transparent",
                      border_width=1, text_color="gray70",
                      command=self.lock_vault).pack(fill="x", padx=14, pady=(0, 14))
 
        # ---------- правая колонка: детали ----------
        self.right = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "gray13"))
        self.right.grid(row=0, column=1, sticky="nsew")
 
        self.show_placeholder()
        self.refresh_list()
 
    # ---------------- список ----------------
    def refresh_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()
 
        rows = db.get_all_entries()
        query = self.search_var.get().lower().strip()
        self.entries_cache = []
 
        for row in rows:
            try:
                title = row["title"]
            except Exception:
                title = "—"
            if query and query not in title.lower():
                continue
            self.entries_cache.append(row)
 
            btn = ctk.CTkButton(
                self.list_scroll, text=title, anchor="w",
                fg_color="transparent", hover_color=("gray85", "gray25"),
                text_color=("gray10", "gray90"),
                command=lambda r=row: self.open_entry(r["id"]),
            )
            btn.pack(fill="x", pady=2, padx=4)
 
        if not self.entries_cache:
            ctk.CTkLabel(self.list_scroll, text="Записей пока нет",
                         text_color="gray50").pack(pady=20)
 
    def show_placeholder(self):
        for w in self.right.winfo_children():
            w.destroy()
        wrap = ctk.CTkFrame(self.right, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(wrap, text="🗝️", font=ctk.CTkFont(size=40)).pack()
        ctk.CTkLabel(wrap, text="Выберите запись слева\nили создайте новую",
                     text_color="gray50", justify="center").pack(pady=(8, 0))
 
    # ---------------- детали записи ----------------
    def open_entry(self, entry_id):
        row = next((r for r in db.get_all_entries() if r["id"] == entry_id), None)
        if row is None:
            return
        self.render_detail(row)
 
    def new_entry(self):
        self.render_detail(None)
 
    def render_detail(self, row):
        for w in self.right.winfo_children():
            w.destroy()
 
        is_new = row is None
 
        def dec(field):
            if is_new:
                return ""
            try:
                return sec.decrypt(row[field], self.key)
            except Exception:
                return "⚠ ошибка расшифровки"
 
        container = ctk.CTkFrame(self.right, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=26)
 
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(header, text="Новая запись" if is_new else "Запись",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        if not is_new:
            ctk.CTkButton(header, text="Удалить", width=90, fg_color="#b3261e",
                          hover_color="#8c1d17",
                          command=lambda: self.delete_current(row["id"])).pack(side="right")
 
        title_entry = ctk.CTkEntry(container, placeholder_text="Название (например, GitHub)")
        title_entry.insert(0, row["title"] if not is_new else "")
        title_entry.pack(fill="x", pady=6)
 
        user_entry = ctk.CTkEntry(container, placeholder_text="Логин / email")
        user_entry.insert(0, dec("username"))
        user_entry.pack(fill="x", pady=6)
 
        pw_row = ctk.CTkFrame(container, fg_color="transparent")
        pw_row.pack(fill="x", pady=6)
        pw_entry = ctk.CTkEntry(pw_row, placeholder_text="Пароль", show="•")
        pw_entry.insert(0, dec("password"))
        pw_entry.pack(side="left", fill="x", expand=True)
 
        def toggle_show():
            pw_entry.configure(show="" if pw_entry.cget("show") == "•" else "•")
 
        ctk.CTkButton(pw_row, text="👁", width=36, command=toggle_show).pack(side="left", padx=(6, 0))
        ctk.CTkButton(pw_row, text="⧉", width=36,
                      command=lambda: self.copy_to_clipboard(pw_entry.get())).pack(side="left", padx=(6, 0))
 
        gen_row = ctk.CTkFrame(container, fg_color="transparent")
        gen_row.pack(fill="x", pady=(0, 6))
        strength_label = ctk.CTkLabel(gen_row, text="", text_color="gray60")
        strength_label.pack(side="left")
 
        def do_generate():
            new_pw = generate_password(16)
            pw_entry.delete(0, "end")
            pw_entry.insert(0, new_pw)
            update_strength()
 
        def update_strength(*_):
            s = password_strength(pw_entry.get())
            color = {"Слабый": "#ff6b6b", "Средний": "#ffd166", "Сильный": "#06d6a0"}[s]
            strength_label.configure(text=f"Сложность: {s}", text_color=color)
 
        pw_entry.bind("<KeyRelease>", update_strength)
        update_strength()
 
        ctk.CTkButton(gen_row, text="🎲 Сгенерировать пароль", width=200,
                      fg_color="transparent", border_width=1,
                      command=do_generate).pack(side="right")
 
        url_entry = ctk.CTkEntry(container, placeholder_text="URL сайта")
        url_entry.insert(0, dec("url"))
        url_entry.pack(fill="x", pady=6)
 
        notes_box = ctk.CTkTextbox(container, height=90)
        notes_box.insert("1.0", dec("notes"))
        notes_box.pack(fill="x", pady=6)
 
        def save():
            title = title_entry.get().strip()
            if not title:
                return
            u_enc = sec.encrypt(user_entry.get(), self.key)
            p_enc = sec.encrypt(pw_entry.get(), self.key)
            url_enc = sec.encrypt(url_entry.get(), self.key)
            notes_enc = sec.encrypt(notes_box.get("1.0", "end").strip(), self.key)
 
            if is_new:
                new_id = db.add_entry(title, u_enc, p_enc, url_enc, notes_enc)
                self.refresh_list()
                self.open_entry(new_id)
            else:
                db.update_entry(row["id"], title, u_enc, p_enc, url_enc, notes_enc)
                self.refresh_list()
 
        ctk.CTkButton(container, text="Сохранить", command=save).pack(fill="x", pady=(14, 0))
 
    def delete_current(self, entry_id):
        db.delete_entry(entry_id)
        self.refresh_list()
        self.show_placeholder()
 
    def copy_to_clipboard(self, text):
        if text:
            pyperclip.copy(text)
 
    def lock_vault(self):
        self.master_app.encryption_key = None
        self.master_app.geometry("420x520")
        self.master_app.show_frame(LoginScreen)
 
 
if __name__ == "__main__":
    app = App()
    app.mainloop()
 
