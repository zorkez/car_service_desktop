##
# @file models.py
# @brief Файл с моделями пользователей системы.
# 
# Этот файл содержит определения классов для пользователей системы, таких как клиент, сотрудник и администратор.
# Классы включают методы для работы с данными пользователей, а также их правами доступа.
#
# @author Гаврилов Николай Срегеевич
# @version 1.0
# @date 2025-05-30
#
"""
Модуль представляющий пользователей.

Автор: Гаврилов Николай Сергеевич
Дата: 2025-05-30
"""
from abc import ABC, abstractmethod

##
# @class User
# @brief Абстрактный класс, представляющий пользователя системы.
# 
# Этот класс является базовым для всех типов пользователей системы (клиенты, сотрудники, администраторы).
# Классы-наследники должны реализовать метод `get_permissions` для получения прав доступа пользователя.
class User(ABC):
    """
    Класс, представляющий пользователя системы.
    Наследуется от класса ABC (abstract base class).

    Атрибуты:
        username (str): Логин пользователя.
        full_name (str): Полное имя пользователя.
        email (str): Электронная почта пользователя.
        phone (str): Телефон пользователя.
        password (str): Пароль пользователя.
    """
    def __init__(self, username, full_name, email, phone, password):
        """
        Инициализация нового пользователя.

        Параметры:
            username (str): Логин пользователя.
            full_name (str): Полное имя пользователя.
            email (str): Электронная почта.
            phone (str): Телефон пользователя.
            password (str): Пароль пользователя.
        """
        self.username = username
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.password = password

    @abstractmethod
    def get_permissions(self):
        """
        Метод, который должен быть реализован в дочерних классах для определения прав доступа пользователя.

        Возвращает:
            dict: Словарь с правами пользователя.
        """
        pass

##
# @class Client
# @brief Класс, представляющий клиента системы.
# 
# Этот класс наследуется от `User` и представляет клиента, который может создавать заказы.
# Права доступа клиента ограничены.
class Client(User):
    """
    Класс, представляющий клиента системы. Наследуется от класса User.

    Права клиента ограничены в системе.

    Атрибуты:
        username (str): Логин клиента.
        full_name (str): Полное имя клиента.
        email (str): Электронная почта клиента.
        phone (str): Телефон клиента.
        password (str): Пароль клиента.
    """
    def __init__(self, username, full_name, email, phone, password):
        """
        Класс, представляющий клиента системы. Наследуется от класса User.

        Права клиента ограничены в системе.

        Атрибуты:
            username (str): Логин клиента.
            full_name (str): Полное имя клиента.
            email (str): Электронная почта клиента.
            phone (str): Телефон клиента.
            password (str): Пароль клиента.
        """
        super().__init__(username, full_name, email, phone, password)

    def get_permissions(self):
        """
        Возвращает права доступа для клиента.

        Возвращает:
            dict: Словарь с правами клиента.
        """
        return {
            "orders": True,
            "clients": False,
            "employees": False,
            "can_edit_status": False,
            "can_edit_client_name": False,
            "can_edit_close_date": False,
            "can_view_forecast_button": False
        }

##
# @class Employee
# @brief Класс, представляющий сотрудника системы.
# 
# Этот класс наследуется от `User` и представляет сотрудника, который может управлять заказами.
# Сотрудник имеет больше прав, чем клиент.
class Employee(User):
    """
    Класс, представляющий сотрудника системы. Наследуется от класса User.

    Атрибуты:
        username (str): Логин сотрудника.
        full_name (str): Полное имя сотрудника.
        email (str): Электронная почта сотрудника.
        phone (str): Телефон сотрудника.
        password (str): Пароль сотрудника.
    """
    def __init__(self, username, full_name, email, phone, password):
        """
        Инициализация сотрудника.

        Параметры:
            username (str): Логин сотрудника.
            full_name (str): Полное имя сотрудника.
            email (str): Электронная почта сотрудника.
            phone (str): Телефон сотрудника.
            password (str): Пароль сотрудника.
        """
        super().__init__(username, full_name, email, phone, password)

    def get_permissions(self):
        """
        Возвращает права доступа для сотрудника.

        Возвращает:
            dict: Словарь с правами сотрудника.
        """
        return {
            "orders": True,
            "clients": True,
            "employees": False,
            "can_edit_status": True,
            "can_edit_client_name": True,
            "can_edit_close_date": True,
            "can_view_forecast_button": True
        }

##
# @class Admin
# @brief Класс, представляющий администратора системы.
# 
# Этот класс наследуется от `User` и представляет администратора, который имеет полный доступ ко всем данным и функциям системы.
class Admin(User):
    """
    Класс, представляющий администратора системы. Наследуется от класса User.

    Атрибуты:
        username (str): Логин администратора.
        full_name (str): Полное имя администратора.
        email (str): Электронная почта администратора.
        phone (str): Телефон администратора.
        password (str): Пароль администратора.
    """
    def __init__(self, username, full_name, email, phone, password):
        """
        Инициализация администратора.

        Параметры:
            username (str): Логин администратора.
            full_name (str): Полное имя администратора.
            email (str): Электронная почта администратора.
            phone (str): Телефон администратора.
            password (str): Пароль администратора.
        """
        super().__init__(username, full_name, email, phone, password)

    def get_permissions(self):
        """
        Возвращает права доступа для администратора.

        Возвращает:
            dict: Словарь с правами администратора.
        """
        return {
            "orders": True,
            "clients": True,
            "employees": True,
            "can_edit_status": True,
            "can_edit_client_name": True,
            "can_edit_close_date": True,
            "can_view_forecast_button": True
        }
