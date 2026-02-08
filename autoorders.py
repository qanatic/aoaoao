import pyautogui
import time
import sys
import os

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
def click_image(image_path, description="", delay=0.3, timeout=3):
    print(f"🔍 Ищем: {description}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
        if location:
            print(f"✅ Найдено: {description} — {location}")
            pyautogui.moveTo(location)
            pyautogui.click()
            time.sleep(delay)
            return True
        time.sleep(0.2)
    print(f"❌ Не найдено: {description}")
    return False

# === Ввод текста в поле ===
def type_item_name(name, delay=0.5):
    pyautogui.write(name, interval=0.01)
    time.sleep(delay)

# === Основной цикл ===
def process_all_items():
    for index, name in enumerate(item_names):
        print(f"\n🛒 Обработка предмета: {name}")

        if index == 0:
            # Первый предмет — открываем маркет
            if not click_image(resource_path("market_icon.png"), "Открыть маркет"):
                continue
        else:
            # Остальные — кликаем по кнопке новой покупки/поиска
            if not click_image(resource_path("reset.png"), "Очистить/новый поиск"):
                continue

        # 1. Клик по полю поиска
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
    print("⏳ Старт через 3 секунды...")
    time.sleep(3)
    process_all_items()
    print("🎉 Все предметы обработаны.")
