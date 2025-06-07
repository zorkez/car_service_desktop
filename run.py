##
# @file run.py
# @brief Главный файл для запуска приложения.
# 
# Этот файл инициализирует базу данных, применяет стили и запускает главное окно приложения.
# Он также обрабатывает процесс аутентификации пользователя.
#
# @author Гаврилов Николай Срегеевич
# @version 1.0
# @date 2025-05-30
#
"""
Модуль для запуска программы.

Автор: Гаврилов Николай Сергеевич
Дата: 2025-05-30
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui import LoginWindow
from db import init_db
from style import setup_style

def main():
    """
    Главная функция для запуска приложения.
    """
    init_db()  # Инициализация базы данных
    app = QApplication(sys.argv)  # Создание приложения
    setup_style(app)  # Применение стилей
    window = LoginWindow()  # Окно авторизации
    window.show()  # Отображение окна
    sys.exit(app.exec())  # Запуск основного цикла приложения

if __name__ == "__main__":
    main()