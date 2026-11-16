#!/usr/bin/env python3
"""
Лаунчер графического интерфейса Typha Bio-Meteo.
Открывает typha_map_app.html в браузере по умолчанию.
"""

import webbrowser
import os
import sys

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "typha_map_app.html")
    
    if not os.path.exists(html_path):
        print(f"Ошибка: файл {html_path} не найден!")
        sys.exit(1)
        
    print("=" * 60)
    print(" Запуск графического интерфейса Typha Bio-Meteo...")
    print(f" Файл интерфейса: {html_path}")
    print("=" * 60)
    
    # Открываем в браузере по умолчанию
    webbrowser.open(f"file:///{html_path.replace(os.sep, '/')}")
    print("\nИнтерфейс успешно открыт в вашем браузере!")
    print("Вы можете кликнуть в любую точку на карте мира, выбрать год (1950–2026)")
    print("и нажать 'Рассчитать вероятность'.")

if __name__ == "__main__":
    main()
