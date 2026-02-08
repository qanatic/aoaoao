from tkinter import messagebox, ttk
import tkinter as tk

import license_manager


class LicenseApp:
    def __init__(self, root, process_callback, base_dir):
        self.root = root
        self.process_callback = process_callback
        self.base_dir = base_dir

        self.root.title("AutoOrders — Лицензирование")
        self.root.geometry("560x640")
        self.root.resizable(False, False)

        self.license_data = license_manager.get_license_data(self.base_dir)
        self.license_data, _ = license_manager.cleanup_expired_codes(self.license_data)
        license_manager.save_license_data(self.base_dir, self.license_data)

        self.code_var = tk.StringVar(value=license_manager.get_active_code(self.base_dir))
        self.duration_var = tk.StringVar(value="24")
        self.new_license_var = tk.StringVar()

        self.build_ui()
        self.refresh_status()
        self.refresh_temp_codes()
        self.refresh_license_list()

    def create_license_code(self):
        self.license_data = license_manager.get_license_data(self.base_dir)
        code = license_manager.generate_license_code(self.base_dir, self.license_data)
        self.refresh_license_list()
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("Ключ создан", f"Ключ: {code}\nСкопирован в буфер обмена.")

    def add_license_code(self):
        code = self.new_license_var.get()
        self.license_data = license_manager.get_license_data(self.base_dir)
        if license_manager.add_license_code(self.base_dir, self.license_data, code):
            self.new_license_var.set("")
            self.refresh_license_list()
            messagebox.showinfo("Ключ добавлен", "Ключ сохранен в список.")
        else:
            messagebox.showwarning("Ошибка", "Ключ пустой или уже существует.")

    def copy_selected_license(self):
        selection = self.license_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите ключ из списка.")
            return
        code = self.license_list.get(selection[0])
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("Скопировано", "Ключ скопирован в буфер обмена.")

    def remove_selected_license(self):
        selection = self.license_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите ключ для удаления.")
            return
        code = self.license_list.get(selection[0])
        self.license_data = license_manager.get_license_data(self.base_dir)
        if license_manager.remove_license_code(self.base_dir, self.license_data, code):
            if license_manager.normalize_code(code) == license_manager.get_active_code(self.base_dir):
                license_manager.set_active_code(self.base_dir, "")
                self.code_var.set("")
                self.refresh_status()
            self.refresh_license_list()
            messagebox.showinfo("Удалено", "Ключ удален.")
        else:
            messagebox.showwarning("Ошибка", "Не удалось удалить ключ.")

    def build_ui(self):
        padding = {"padx": 12, "pady": 8}

        title = ttk.Label(self.root, text="Управление лицензией", font=("Arial", 16, "bold"))
        title.pack(pady=12)

        code_frame = ttk.LabelFrame(self.root, text="Лицензионный ключ")
        code_frame.pack(fill="x", **padding)

        ttk.Label(code_frame, text="Ключ:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        code_entry = ttk.Entry(code_frame, textvariable=self.code_var, width=36)
        code_entry.grid(row=0, column=1, sticky="w", padx=8, pady=8)
        code_entry.focus_set()

        ttk.Button(code_frame, text="Активировать", command=self.activate_license).grid(
            row=0, column=2, sticky="w", padx=8, pady=8
        )

        self.status_label = ttk.Label(code_frame, text="Статус: неизвестно", foreground="gray")
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=8, pady=4)

        temp_frame = ttk.LabelFrame(self.root, text="Временные коды")
        temp_frame.pack(fill="x", **padding)

        ttk.Label(temp_frame, text="Срок (часы):").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ttk.Entry(temp_frame, textvariable=self.duration_var, width=8).grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ttk.Button(temp_frame, text="Сгенерировать", command=self.create_temp_code).grid(
            row=0, column=2, sticky="w", padx=8, pady=8
        )

        self.temp_codes_box = tk.Text(temp_frame, height=8, width=56, state="disabled")
        self.temp_codes_box.grid(row=1, column=0, columnspan=3, padx=8, pady=8)

        license_frame = ttk.LabelFrame(self.root, text="Продажные ключи")
        license_frame.pack(fill="x", **padding)

        ttk.Button(license_frame, text="Сгенерировать ключ", command=self.create_license_code).grid(
            row=0, column=0, sticky="w", padx=8, pady=8
        )
        ttk.Label(license_frame, text="Добавить ключ:").grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ttk.Entry(license_frame, textvariable=self.new_license_var, width=20).grid(
            row=0, column=2, sticky="w", padx=8, pady=8
        )
        ttk.Button(license_frame, text="Сохранить", command=self.add_license_code).grid(
            row=0, column=3, sticky="w", padx=8, pady=8
        )

        self.license_list = tk.Listbox(license_frame, height=6, width=56)
        self.license_list.grid(row=1, column=0, columnspan=4, padx=8, pady=8)

        license_actions = ttk.Frame(license_frame)
        license_actions.grid(row=2, column=0, columnspan=4, sticky="w", padx=8, pady=4)

        ttk.Button(license_actions, text="Скопировать", command=self.copy_selected_license).pack(
            side="left", padx=4
        )
        ttk.Button(license_actions, text="Удалить", command=self.remove_selected_license).pack(
            side="left", padx=4
        )

        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", **padding)

        self.start_button = ttk.Button(action_frame, text="Запустить авто-заказы", command=self.start_process)
        self.start_button.pack(side="left", padx=8)

        ttk.Button(action_frame, text="Обновить данные", command=self.refresh_all).pack(
            side="left", padx=8
        )

        ttk.Button(action_frame, text="Выход", command=self.root.destroy).pack(side="right", padx=8)

    def refresh_status(self):
        self.license_data, _ = license_manager.cleanup_expired_codes(
            license_manager.get_license_data(self.base_dir)
        )
        license_manager.save_license_data(self.base_dir, self.license_data)
        active = license_manager.normalize_code(
            self.code_var.get() or license_manager.get_active_code(self.base_dir)
        )
        valid = license_manager.is_code_valid(active, self.license_data)
        if valid:
            self.status_label.config(text="Статус: лицензия активна ✅", foreground="green")
        else:
            self.status_label.config(text="Статус: лицензия не активна ❌", foreground="red")
        return valid

    def refresh_all(self):
        self.refresh_status()
        self.refresh_temp_codes()
        self.refresh_license_list()

    def refresh_temp_codes(self):
        self.license_data, expired = license_manager.cleanup_expired_codes(
            license_manager.get_license_data(self.base_dir)
        )
        license_manager.save_license_data(self.base_dir, self.license_data)
        temp_codes = self.license_data.get("temporary_codes", {})

        self.temp_codes_box.config(state="normal")
        self.temp_codes_box.delete("1.0", tk.END)
        if not temp_codes:
            self.temp_codes_box.insert(tk.END, "Нет активных временных кодов.")
        else:
            for code, meta in temp_codes.items():
                expires = datetime.fromisoformat(meta["expires_at"]).strftime("%Y-%m-%d %H:%M UTC")
                self.temp_codes_box.insert(tk.END, f"{code} — до {expires}\n")
        self.temp_codes_box.config(state="disabled")

        if expired:
            messagebox.showinfo("Истекшие коды", "Удалены истекшие временные коды.")

    def refresh_license_list(self):
        self.license_data = license_manager.get_license_data(self.base_dir)
        licenses = sorted(self.license_data.get("licenses", []))
        self.license_list.delete(0, tk.END)
        for code in licenses:
            self.license_list.insert(tk.END, code)

    def activate_license(self):
        code = license_manager.normalize_code(self.code_var.get())
        if not code:
            messagebox.showwarning("Пустой ключ", "Введите лицензионный ключ.")
            return
        self.license_data = license_manager.get_license_data(self.base_dir)
        if license_manager.is_code_valid(code, self.license_data):
            license_manager.set_active_code(self.base_dir, code)
            self.code_var.set(code)
            messagebox.showinfo("Лицензия активирована", "Лицензия успешно активирована.")
        else:
            messagebox.showerror("Ошибка лицензии", "Ключ не найден или истек.")
        self.refresh_status()

    def create_temp_code(self):
        if not self.refresh_status():
            messagebox.showwarning("Нет лицензии", "Сначала активируйте основную лицензию.")
            return
        try:
            hours = int(self.duration_var.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Срок должен быть числом.")
            return
        if hours <= 0 or hours > 168:
            messagebox.showwarning("Ошибка", "Срок должен быть от 1 до 168 часов.")
            return
        self.license_data = license_manager.get_license_data(self.base_dir)
        code, expires_at = license_manager.generate_temp_code(self.base_dir, self.license_data, hours)
        messagebox.showinfo(
            "Временный код создан",
            f"Код: {code}\nДействует до: {expires_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        self.refresh_temp_codes()

    def start_process(self):
        if not self.refresh_status():
            messagebox.showerror("Лицензия не активна", "Нельзя запускать авто-заказы без лицензии.")
            return
        self.start_button.config(state="disabled")
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        try:
            self.process_callback()
        finally:
            self.start_button.config(state="normal")