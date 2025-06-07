##
# @file db.py
# @brief Файл для работы с базой данных.
# 
# Этот файл содержит функции для работы с SQLite базой данных, включая выполнение запросов и инициализацию базы.
#
# @author Гаврилов Николай Срегеевич
# @version 1.0
# @date 2025-05-30
#
"""
Модуль базы данных.

Автор: Гаврилов Николай Сергеевич
Дата: 2025-05-30
"""
import sqlite3

def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect('service_requests.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetch:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def init_db():
    conn = sqlite3.connect('service_requests.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            status TEXT,
            price REAL,
            client_name TEXT,
            master_name TEXT,
            car_number TEXT,        
            open_date TEXT,
            close_date TEXT
        )''')

    conn.commit()
    conn.close()
