import os
import sys
import time
import tkinter as tk

import pyautogui

from license_ui import LicenseApp

# Определяем папку, где лежит exe или py
if getattr(sys, 'frozen', False):  
    BASE_DIR = os.path.dirname(sys.executable)  
else:  
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(filename):
    """Возвращает полный путь к файлу рядом с exe или py"""
    return os.path.join(BASE_DIR, filename)

# === Список предметов ===
def load_items_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            items = [line.strip() for line in f if line.strip()]
            return items
    except FileNotFoundError:
        print(f"❌ Файл {filepath} не найден.")
        return []

item_names = load_items_from_file(resource_path("items.txt"))


# === Клик по изображению на экране ===
@@ -65,31 +69,31 @@ def process_all_items():
        if not click_image(resource_path("search_field.png"), "Поле поиска"):
            continue

        # 2. Ввод названия предмета
        type_item_name(name)

        # 3. Клик по кнопке "Купить"
        if not click_image(resource_path("buy_button.png"), "Купить"):
            continue

        # 4. Клик по кнопке "+"
        if not click_image(resource_path("plus_button.png"), "Кнопка '+'"):
            continue

        # 5. Клик по кнопке "Подтвердить"
        if not click_image(resource_path("confirm_button.png"), "Подтвердить"):
            continue

        # 5. Клик по кнопке "Подтвердить"
        if not click_image(resource_path("da.png"), "Подтвердить"):
            continue

        print(f"✅ Готово: {name}")
        time.sleep(1)


# === Старт ===
if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseApp(root, process_all_items, BASE_DIR)
    root.mainloop()