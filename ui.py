##
# @file ui.py
# @brief Файл с интерфейсами и окнами приложения.
# 
# Этот файл содержит описание окон и интерфейсов приложения, включая главный экран, окна для авторизации и регистрации.
#
# @author Гаврилов Николай Срегеевич
# @version 1.0
# @date 2025-05-30
#
"""
Модуль интерфейса программы.

Автор: Гаврилов Николай Сергеевич
Дата: 2025-05-30
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLineEdit, QFormLayout, QDialog, QDateEdit, QMessageBox, QHBoxLayout, QAbstractItemView, QApplication, QLabel
from PyQt6.QtCore import Qt, QDate
from abc import abstractmethod
from utils import CenteredWindow, FilterComboBox, ForecastWindow, SearchWindow
from models import Client, Employee, Admin
import sqlite3

##
# @class MainWindow
# @brief Главное окно приложения для отображения заказов, клиентов и сотрудников.
# 
# Этот класс отвечает за отображение основного интерфейса приложения, включая вкладки для работы с заказами, клиентами и сотрудниками.
# Класс предоставляет функционал для добавления, редактирования, удаления записей и поиска данных.
#
class MainWindow(QWidget, CenteredWindow):
    """
    Главное окно приложения для отображения заказов, клиентов и сотрудников.
    
    Атрибуты:
        user (User): Текущий пользователь.
        permissions (dict): Права доступа пользователя.
        orders_table (QTableWidget): Таблица для отображения заказов.
        clients_table (QTableWidget): Таблица для отображения клиентов.
        employees_table (QTableWidget): Таблица для отображения сотрудников.
    """
    def __init__(self, user):
        """
        Инициализация главного окна.

        Параметры:
            user (User): Текущий пользователь системы.
        """
        super().__init__()
        self.setWindowTitle("Программа для учета заявок")
        self.setGeometry(100, 100, 1210, 700)
        self.user = user
        self.center_window()

        self.layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        self.permissions = user.get_permissions()

        self.orders_table = QTableWidget()
        self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.orders_table.setColumnCount(11) 
        self.orders_table.setHorizontalHeaderLabels(["ID", "Тип", "Статус", "Цена", "ФИО клиента", "ФИО мастера", "Номер авто", "Дата открытия", "Дата закрытия", "Изменить", "Удалить"])
        self.tab_widget.addTab(self.orders_table, "Заказы")
        self.populate_orders_table()

        if self.permissions["clients"]:
            self.clients_table = QTableWidget()
            self.clients_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.clients_table.setColumnCount(7)
            self.clients_table.setHorizontalHeaderLabels(["ID", "Логин", "ФИО клиента", "Телефон", "Почта", "Изменить", "Удалить"])
            self.tab_widget.addTab(self.clients_table, "Клиенты")
            self.populate_clients_table()

        if self.permissions["employees"]:
            self.employees_table = QTableWidget()
            self.employees_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.employees_table.setColumnCount(7)
            self.employees_table.setHorizontalHeaderLabels(["ID", "Логин", "ФИО сотрудника", "Телефон", "Почта", "Изменить", "Удалить"])
            self.tab_widget.addTab(self.employees_table, "Сотрудники")
            self.populate_employees_table()


        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_entry)
        self.layout.addWidget(self.add_button)

        self.is_filtered = False
        self.search_button = QPushButton("Поиск", self)
        self.search_button.clicked.connect(self.toggle_search)
        self.layout.addWidget(self.search_button)

        if self.permissions.get("can_view_forecast_button", False):
            self.forecast_button = QPushButton("Прогнозирование заказов", self)
            self.forecast_button.clicked.connect(self.show_forecast_window)
            self.layout.insertWidget(2, self.forecast_button)

        self.exit_button = QPushButton("Выход", self)
        self.exit_button.clicked.connect(self.logout)
        self.layout.addWidget(self.exit_button)

        self.orders_table.cellClicked.connect(self.on_cell_clicked)

        self.setLayout(self.layout)

    def logout(self):
        app = QApplication.instance()
        app.auth_window = LoginWindow() 
        app.auth_window.show()
        self.close()

    def toggle_search(self):
        if self.is_filtered:
            self.reset_filter()
        else:
            self.open_search_window()

    def reset_filter(self):
        current_tab_index = self.tab_widget.currentIndex()
        
        if current_tab_index == 0:  
            self.populate_orders_table()
        elif current_tab_index == 1:  
            self.populate_clients_table()
        elif current_tab_index == 2: 
            self.populate_employees_table()
        
        self.is_filtered = False
        self.search_button.setText("Поиск")

    def open_search_window(self):
        current_tab_index = self.tab_widget.currentIndex()
        
        if current_tab_index == 0:  
            self.search_window = SearchWindow(self, table_type="orders", user=self.user)
        elif current_tab_index == 1:  
            self.search_window = SearchWindow(self, table_type="clients", user=self.user)
        elif current_tab_index == 2:  
            self.search_window = SearchWindow(self, table_type="employees", user=self.user)
        
        self.search_window.search_completed.connect(self.on_search_completed)
        self.search_window.exec()

    def on_search_completed(self):
        self.is_filtered = True
        self.search_button.setText("Отменить фильтр")
        
    def on_cell_clicked(self, row, column):
        if column == 4: 
            client_name = self.orders_table.item(row, column).text()
            self.show_client_in_table(client_name)
        elif column == 5:
            master_name = self.orders_table.item(row, column).text()
            self.show_employee_in_table(master_name)

    def show_forecast_window(self):
        self.forecast_window = ForecastWindow(self)
        self.forecast_window.exec()

    def show_client_in_table(self, client_name):
        if not self.permissions["clients"]:
            return
            
        self.tab_widget.setCurrentIndex(1) 
        
        for row in range(self.clients_table.rowCount()):
            if self.clients_table.item(row, 2).text() == client_name: 
                self.clients_table.selectRow(row)
                self.clients_table.scrollToItem(self.clients_table.item(row, 0))
                break

    def show_employee_in_table(self, employee_name):
        if not self.permissions["employees"]:
            return
            
        self.tab_widget.setCurrentIndex(2) 
        
        for row in range(self.employees_table.rowCount()):
            if self.employees_table.item(row, 2).text() == employee_name: 
                self.employees_table.selectRow(row)
                self.employees_table.scrollToItem(self.employees_table.item(row, 0))
                break

    def populate_orders_table(self, data=None):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        if data is None:
            if isinstance(self.user, Client):
                cursor.execute('SELECT * FROM requests WHERE client_name=?', (self.user.full_name,))
            else:
                cursor.execute('SELECT * FROM requests')
            data = cursor.fetchall()
        
        self.orders_table.setRowCount(len(data))
        
        for i, order in enumerate(data):
            self.orders_table.setItem(i, 0, QTableWidgetItem(str(order[0])))
            self.orders_table.setItem(i, 1, QTableWidgetItem(order[1]))
            self.orders_table.setItem(i, 2, QTableWidgetItem(order[2]))
            self.orders_table.setItem(i, 3, QTableWidgetItem(str(order[3])))
            self.orders_table.setItem(i, 4, QTableWidgetItem(order[4]))
            self.orders_table.setItem(i, 5, QTableWidgetItem(order[5]))
            self.orders_table.setItem(i, 6, QTableWidgetItem(order[6]))
            self.orders_table.setItem(i, 7, QTableWidgetItem(order[7]))
            self.orders_table.setItem(i, 8, QTableWidgetItem(order[8]))

            edit_button = QPushButton("Изменить")
            delete_button = QPushButton("Удалить")
            edit_button.setObjectName("edit_button")
            delete_button.setObjectName("delete_button")
            self.orders_table.setCellWidget(i, 9, edit_button)
            self.orders_table.setCellWidget(i, 10, delete_button)

            edit_button.clicked.connect(lambda ch, row=i, id=order[0]: self.edit_order(row, id))
            delete_button.clicked.connect(lambda ch, row=i, order_id=order[0]: self.delete_order(row, order_id))
        
        conn.close()
        self.orders_table.resizeColumnsToContents()

    def populate_clients_table(self, data=None):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        if data is None:
            cursor.execute('SELECT * FROM clients')
            data = cursor.fetchall()
        
        self.clients_table.setRowCount(len(data))
        
        for i, client in enumerate(data):
            self.clients_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.clients_table.setItem(i, 1, QTableWidgetItem(client[0]))
            self.clients_table.setItem(i, 2, QTableWidgetItem(client[1]))
            self.clients_table.setItem(i, 3, QTableWidgetItem(client[3]))
            self.clients_table.setItem(i, 4, QTableWidgetItem(client[2]))

            edit_button = QPushButton("Изменить")
            edit_button.setObjectName("edit_button")
            self.clients_table.setCellWidget(i, 5, edit_button)
            edit_button.clicked.connect(lambda ch, row=i, username=client[0]: self.edit_client(row, username))

            delete_button = QPushButton("Удалить")
            delete_button.setObjectName("delete_button")
            self.clients_table.setCellWidget(i, 6, delete_button)
            delete_button.clicked.connect(lambda ch, row=i, username=client[0]: self.delete_client(row, username))
        
        conn.close()
        self.clients_table.resizeColumnsToContents()

    def populate_employees_table(self, data=None):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        if data is None:
            cursor.execute('SELECT * FROM employees')
            data = cursor.fetchall()
        
        self.employees_table.setRowCount(len(data))
        
        for i, employee in enumerate(data):
            self.employees_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.employees_table.setItem(i, 1, QTableWidgetItem(employee[0]))
            self.employees_table.setItem(i, 2, QTableWidgetItem(employee[1]))
            self.employees_table.setItem(i, 3, QTableWidgetItem(employee[3]))
            self.employees_table.setItem(i, 4, QTableWidgetItem(employee[2]))

            edit_button = QPushButton("Изменить")
            delete_button = QPushButton("Удалить")
            edit_button.setObjectName("edit_button")
            delete_button.setObjectName("delete_button")
            self.employees_table.setCellWidget(i, 5, edit_button)
            self.employees_table.setCellWidget(i, 6, delete_button)

            edit_button.clicked.connect(lambda ch, row=i, username=employee[0]: self.edit_employee(row, username))
            delete_button.clicked.connect(lambda ch, row=i, username=employee[0]: self.delete_employee(row, username))
        
        conn.close()
        self.employees_table.resizeColumnsToContents()

    def add_entry(self):
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0: 
            self.show_add_order_window()
        elif current_tab == 1:  
            self.show_add_client_window()
        elif current_tab == 2:  
            self.show_add_employee_window()

    def show_add_order_window(self):
        self.add_order_window = AddOrderWindow(self)
        self.add_order_window.exec()

    def show_add_client_window(self):
        self.add_client_window = AddClientWindow(self)
        self.add_client_window.exec()

    def show_add_employee_window(self):
        self.add_employee_window = AddEmployeeWindow(self)
        self.add_employee_window.exec()

    def edit_order(self, row, order_id):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM requests WHERE id=?', (order_id,))
        status = cursor.fetchone()[0]
        conn.close()
        
        if isinstance(self.user, Client) and status != "новый":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Вы не можете редактировать заказы со статусом 'в работе' или 'завершён'")
            msg.setWindowTitle("Ограничение прав")
            msg.exec()
            return
        
        self.edit_order_window = EditOrderWindow(self, order_id)
        self.edit_order_window.exec()

    def edit_client(self, row, username):
        self.edit_client_window = EditClientWindow(self, username)
        self.edit_client_window.exec()

    def edit_employee(self, row, username):
        self.edit_employee_window = EditEmployeeWindow(self, username)
        self.edit_employee_window.exec()

    def delete_order(self, row, order_id):  
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM requests WHERE id=?', (order_id,))
        status = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if isinstance(self.user, Client) and status == "в работе":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Вы не можете удалиять заказы со статусом 'в работе'")
            msg.setWindowTitle("Ограничение прав")
            msg.exec()
            return
        
        self.populate_orders_table()

    def delete_client(self, row, username):  
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients WHERE username=?', (username,))
        conn.commit()
        conn.close()
        self.populate_clients_table()
        
    def delete_employee(self, row, username):  
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM employees WHERE username=?', (username,))
        conn.commit()
        conn.close()
        self.populate_employees_table()

##
# @class RegisterWindow
# @brief Окно для регистрации нового пользователя.
# 
# Этот класс представляет собой окно регистрации нового пользователя в системе. 
# Включает в себя форму для ввода логина, ФИО, почты, телефона и пароля.
# Также содержит логику для проверки данных, их сохранения в базе данных и отображения ошибок.
#
class RegisterWindow(QDialog, CenteredWindow):  
    """
    Окно для регистрации нового пользователя.

    Атрибуты:
        layout (QVBoxLayout): Основной компоновщик для размещения виджетов.
        form_layout (QFormLayout): Компоновщик для формы регистрации.
        username_input (QLineEdit): Поле для ввода логина пользователя.
        full_name_input (QLineEdit): Поле для ввода полного имени.
        email_input (QLineEdit): Поле для ввода электронной почты.
        phone_input (QLineEdit): Поле для ввода телефона.
        password_input (QLineEdit): Поле для ввода пароля.
        show_hide_password_button (QPushButton): Кнопка для показа или скрытия пароля.
        confirm_password_input (QLineEdit): Поле для подтверждения пароля.
        register_button (QPushButton): Кнопка для отправки формы регистрации.
    """
    def __init__(self, parent):
        """
        Инициализация окна регистрации.

        Параметры:
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)  
        self.setWindowTitle("Регистрация")
        self.setGeometry(100, 100, 400, 300)
        self.center_window()

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        self.form_layout.addRow("Логин:", self.username_input)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setPlaceholderText("Введите ФИО")
        self.form_layout.addRow("ФИО:", self.full_name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Введите почту")
        self.form_layout.addRow("Почта:", self.email_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("Введите телефон")
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        
        self.show_hide_password_button = QPushButton("🕶️", self)
        self.show_hide_password_button.clicked.connect(self.toggle_password_visibility)
        self.show_hide_password_button.setFixedWidth(40)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_hide_password_button)
        self.form_layout.addRow("Пароль:", password_layout)

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Подтвердите пароль")
        self.form_layout.addRow("Подтверждение пароля:", self.confirm_password_input)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.clicked.connect(self.register)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def toggle_password_visibility(self):
        """
        Переключает видимость пароля в поле ввода.
        Показывает или скрывает введенный пароль.
        """
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide_password_button.setText("👀")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide_password_button.setText("🕶️")

    def register(self):
        """
        Обрабатывает регистрацию нового пользователя.

        Проверяет, совпадают ли пароли, и сохраняет данные пользователя в базу данных.
        Если регистрация успешна, окно закрывается.
        """
        username = self.username_input.text()
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if password != confirm_password:
            self.show_error("Пароли не совпадают!")
            return

        if not all([username, full_name, email, phone, password]):
            self.show_error("Все поля должны быть заполнены!")
            return

        self.save_client_to_db(username, full_name, email, phone, password)
        self.close()

    def show_error(self, message):
        """
        Отображает окно с сообщением об ошибке.

        Параметры:
            message (str): Сообщение об ошибке, которое нужно отобразить.
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()

    def show_success(self, message):
        """
        Отображает окно с сообщением об успешной регистрации.

        Параметры:
            message (str): Сообщение об успешной операции.
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)   
        msg.setText(message)
        msg.setWindowTitle("Успех")
        msg.exec()

    def save_client_to_db(self, username, full_name, email, phone, password):
        """
        Сохраняет данные клиента в базу данных.

        Параметры:
            username (str): Логин клиента.
            full_name (str): Полное имя клиента.
            email (str): Электронная почта клиента.
            phone (str): Телефон клиента.
            password (str): Пароль клиента.
        """
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM clients WHERE username=? UNION SELECT username FROM employees WHERE username=?', 
                    (username, username))
        existing_user = cursor.fetchone()
        
        if existing_user:
            self.show_error("Логин уже занят!")
            conn.close()
            return
        
        if username == "zorkez":
            self.show_error("Этот логин зарезервирован!")
            conn.close()
            return
        
        self.show_success("Регистрация прошла успешно!")
        cursor.execute('INSERT INTO clients (username, full_name, email, phone, password) VALUES (?, ?, ?, ?, ?)', 
                    (username, full_name, email, phone, password))
        conn.commit()
        conn.close()

##
# @class LoginWindow
# @brief Окно для авторизации пользователя.
# 
# Этот класс представляет собой окно авторизации, где пользователь вводит логин и пароль для входа в систему.
# Также предоставляет возможность перейти к окну регистрации нового пользователя.
#
class LoginWindow(QWidget, CenteredWindow):
    """
    Окно для авторизации пользователя.

    Атрибуты:
        layout (QVBoxLayout): Основной компоновщик для размещения виджетов.
        username_input (QLineEdit): Поле для ввода логина пользователя.
        password_input (QLineEdit): Поле для ввода пароля.
        show_hide_password_button (QPushButton): Кнопка для отображения или скрытия пароля.
        login_button (QPushButton): Кнопка для авторизации.
        register_button (QPushButton): Кнопка для открытия окна регистрации.
    """
    def __init__(self):
        """
        Инициализация окна авторизации.

        Параметры:
            parent (QWidget): Родительский виджет.
        """
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.center_window()

        self.layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите имя пользователя")
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)
        
        self.show_hide_password_button = QPushButton("🕶️", self)
        self.show_hide_password_button.clicked.connect(self.toggle_password_visibility)
        self.show_hide_password_button.setFixedWidth(40)

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_hide_password_button)
        self.layout.addLayout(password_layout)

        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.clicked.connect(self.open_register_window)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def toggle_password_visibility(self):
        """
        Переключает видимость пароля в поле ввода.

        Это позволяет пользователю отображать или скрывать введенный пароль.
        """
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide_password_button.setText("👀")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide_password_button.setText("🕶️")

    def login(self):
        """
        Обрабатывает процесс авторизации.

        Проверяет введенные логин и пароль, и если они правильные, переходит в главное окно.
        Если данные неверны, показывается сообщение об ошибке.
        """
        username = self.username_input.text()
        password = self.password_input.text()
        user = self.check_credentials(username, password)
        if user:
            self.open_main_window(user)
            self.close()
        else:
            self.show_error("Неверные данные для входа")

    def check_credentials(self, username, password):
        """
        Проверяет правильность логина и пароля.

        Параметры:
            username (str): Логин пользователя.
            password (str): Пароль пользователя.

        Возвращает:
            User: Объект пользователя (если данные правильные) или None (если данные неверные).
        """
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clients WHERE username=? AND password=?', (username, password))
        result = cursor.fetchone()
        if result:
            conn.close()
            return Client(result[0], result[1], result[2], result[3], result[4])

        cursor.execute('SELECT * FROM employees WHERE username=? AND password=?', (username, password))
        result = cursor.fetchone()
        if result:
            conn.close()
            return Employee(result[0], result[1], result[2], result[3], result[4])

        if username == "zorkez" and password == "123qwe123":
            conn.close()
            return Admin(username, "Zorkez Admin", "admin@admin.com", "1234567890", password)

        conn.close()
        return None

    def open_main_window(self, user):
        """
        Открывает главное окно приложения после успешной авторизации.

        Параметры:
            user (User): Объект авторизованного пользователя.
        """
        print(f"Добро пожаловать, {user.username}")
        self.main_window = MainWindow(user)
        self.main_window.show()

    def open_register_window(self):
        """
        Открывает окно регистрации нового пользователя.
        """
        self.register_window = RegisterWindow(self)
        self.register_window.exec()

    def show_error(self, message):
        """
        Отображает окно с сообщением об ошибке.

        Параметры:
            message (str): Сообщение об ошибке.
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()

##
# @class AddWindow
# @brief Базовый класс для окон добавления записей.
# 
# Этот класс является базовым для всех окон, связанных с добавлением данных в систему. Он включает методы для обработки ошибок и отображения сообщений.
# Классы-наследники должны реализовать метод `add_window` для обработки добавления данных.
#
class AddWindow(QDialog, CenteredWindow):
    def __init__(self, parent):
        """Инициализация данных"""
        super().__init__(parent)
        pass

    def add_window(self):
        """Метод добавления"""
        pass

    @abstractmethod
    def show_error(self, message):
        """Окно ошибки"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()

##
# @class AddOrderWindow
# @brief Окно для добавления нового заказа.
# 
# Этот класс представляет собой окно для добавления нового заказа в систему. 
# Включает форму для ввода информации о заказе, такой как тип, статус, цена, данные клиента и мастера.
# Также содержит логику для проверки данных, их сохранения в базу данных и отображения ошибок.
#
class AddOrderWindow(AddWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить заказ")
        self.setGeometry(100, 100, 400, 400)
        self.center_window()
        
        self.user = parent.user  
        self.permissions = self.user.get_permissions()

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["ремонт", "техническое обслуживание"])
        self.type_combo.currentTextChanged.connect(self.update_price)
        self.form_layout.addRow("Тип заказа:", self.type_combo)

        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["новый"])
        self.status_combo.setCurrentText("новый")
        self.status_combo.setEnabled(False) 
        self.form_layout.addRow("Статус:", self.status_combo)

        self.price_input = QLineEdit(self)
        self.price_input.setReadOnly(True)
        self.price_input.setText("5000")  
        self.form_layout.addRow("Цена:", self.price_input)

        self.client_name_input = FilterComboBox(self)
        if isinstance(self.user, Client):
            self.client_name_input.addItem(self.user.full_name)
            self.client_name_input.setCurrentText(self.user.full_name)
            self.client_name_input.setEnabled(False)
        else:
            self.load_client_names()
        self.form_layout.addRow("ФИО клиента:", self.client_name_input)

        self.master_name_input = FilterComboBox(self)
        self.load_employee_names()
        self.form_layout.addRow("ФИО мастера:", self.master_name_input)

        self.car_number_input = QLineEdit(self)
        self.car_number_input.setPlaceholderText("А000АА00RUS")
        self.form_layout.addRow("Номер автомобиля:", self.car_number_input)

        self.open_date_edit = QDateEdit(self)
        self.open_date_edit.setCalendarPopup(True)
        self.open_date_edit.setDate(QDate.currentDate())
        self.form_layout.addRow("Дата открытия:", self.open_date_edit)

        if isinstance(self.user, Client):
            self.close_date_edit = QLineEdit(self)
            self.close_date_edit.setText("не указано")
            self.close_date_edit.setEnabled(False)
            self.form_layout.addRow("Дата закрытия:", self.close_date_edit)
        else:
            self.close_date_edit = QDateEdit(self)
            self.close_date_edit.setCalendarPopup(True)
            self.close_date_edit.setDate(QDate.currentDate())
            self.form_layout.addRow("Дата закрытия:", self.close_date_edit)

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_window)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def update_price(self):
        order_type = self.type_combo.currentText()
        if order_type == "ремонт":
            self.price_input.setText("5000")
        elif order_type == "техническое обслуживание":
            self.price_input.setText("2500")

    def add_window(self):
        type_ = self.type_combo.currentText()
        status = self.status_combo.currentText()
        price = self.price_input.text()
        client_name = self.client_name_input.currentText() 
        master_name = self.master_name_input.currentText()
        car_number = self.car_number_input.text()
        open_date = self.open_date_edit.date().toString("yyyy-MM-dd")

        if isinstance(self.user, Client):
            close_date = "не указано"
        else:
            close_date = self.close_date_edit.date().toString("yyyy-MM-dd")

        if not all([type_, status, price, client_name, master_name, car_number]):
            self.show_error("Все обязательные поля должны быть заполнены!")
            return

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO requests (type, status, price, client_name, master_name, car_number, open_date, close_date)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (type_, status, price, client_name, master_name, car_number, open_date, close_date))
        conn.commit()
        conn.close()

        self.parent().populate_orders_table()
        self.close()

    def load_client_names(self):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM clients')
        clients = cursor.fetchall()
        conn.close()
        
        self.client_name_input.clear()
        for client in clients:
            self.client_name_input.addItem(client[0])
    
    def load_employee_names(self):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM employees')
        employees = cursor.fetchall()
        conn.close()
        
        self.master_name_input.clear()
        for employee in employees:
            self.master_name_input.addItem(employee[0])

##
# @class AddClientWindow
# @brief Окно для добавления нового клиента.
# 
# Этот класс представляет собой окно для добавления нового клиента в систему. 
# Включает форму для ввода данных клиента, таких как логин, ФИО, почта, телефон и пароль.
# Также содержит логику для проверки данных, их сохранения в базу данных и отображения ошибок.
#
class AddClientWindow(AddWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить клиента")
        self.setGeometry(100, 100, 400, 300)
        self.center_window()

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        self.form_layout.addRow("Логин:", self.username_input)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setPlaceholderText("Введите ФИО")
        self.form_layout.addRow("ФИО:", self.full_name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Введите почту")
        self.form_layout.addRow("Почта:", self.email_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("Введите телефон")
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow("Пароль:", self.password_input)

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_window)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_window(self):
        username = self.username_input.text()
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        password = self.password_input.text()

        if not all([username, full_name, email, phone, password]):
            self.show_error("Все поля должны быть заполнены!")
            return

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM clients WHERE username=? UNION SELECT username FROM employees WHERE username=?', 
                      (username, username))
        existing_user = cursor.fetchone()
        
        if existing_user:
            self.show_error("Логин уже занят!")
            conn.close()
            return
        
        if username == "zorkez":
            self.show_error("Этот логин зарезервирован!")
            conn.close()
            return
        
        try:
            cursor.execute('''INSERT INTO clients (username, full_name, email, phone, password)
                            VALUES (?, ?, ?, ?, ?)''',
                         (username, full_name, email, phone, password))
            conn.commit()
            self.parent().populate_clients_table()
            self.close()
        except sqlite3.IntegrityError:
            self.show_error("Клиент с таким логином уже существует!")
        finally:
            conn.close()

##
# @class AddEmployeeWindow
# @brief Окно для добавления нового сотрудника.
# 
# Этот класс представляет собой окно для добавления нового сотрудника в систему. 
# Включает форму для ввода данных сотрудника, таких как логин, ФИО, почта, телефон и пароль.
# Также содержит логику для проверки данных, их сохранения в базу данных и отображения ошибок.
#
class AddEmployeeWindow(AddWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Добавить сотрудника")
        self.setGeometry(100, 100, 400, 300)
        self.center_window()

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        self.form_layout.addRow("Логин:", self.username_input)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setPlaceholderText("Введите ФИО")
        self.form_layout.addRow("ФИО:", self.full_name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Введите почту")
        self.form_layout.addRow("Почта:", self.email_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("Введите телефон")
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow("Пароль:", self.password_input)

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_window)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_window(self):
        username = self.username_input.text()
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        password = self.password_input.text()

        if not all([username, full_name, email, phone, password]):
            self.show_error("Все поля должны быть заполнены!")
            return

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM clients WHERE username=? UNION SELECT username FROM employees WHERE username=?', 
                      (username, username))
        existing_user = cursor.fetchone()
        
        if existing_user:
            self.show_error("Логин уже занят!")
            conn.close()
            return
        
        if username == "zorkez":
            self.show_error("Этот логин зарезервирован!")
            conn.close()
            return
        
        try:
            cursor.execute('''INSERT INTO employees (username, full_name, email, phone, password)
                            VALUES (?, ?, ?, ?, ?)''',
                         (username, full_name, email, phone, password))
            conn.commit()
            self.parent().populate_employees_table()
            self.close()
        except sqlite3.IntegrityError:
            self.show_error("Сотрудник с таким логином уже существует!")
        finally:
            conn.close()

##
# @class EditWindow
# @brief Базовый класс для окон редактирования записей.
# 
# Этот класс является базовым для всех окон редактирования данных в системе. Он включает в себя методы для обработки ошибок и отображения сообщений.
# Классы-наследники должны реализовать метод `edit_window` для обработки редактирования данных.
#
class EditWindow(QDialog, CenteredWindow):
    def __init__(self, parent):
        """Инициализация данных"""
        super().__init__(parent)
        pass

    def edit_window(self):
        """Метод изменения"""
        pass

    @abstractmethod
    def show_error(self, message):
        """Окно ошибки"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()

##
# @class EditOrderWindow
# @brief Окно для редактирования информации о заказе.
# 
# Этот класс представляет собой окно для редактирования информации о заказе. 
# Включает форму для изменения данных заказа, таких как тип, статус, цена, данные клиента и мастера.
# Также содержит логику для проверки данных, их обновления в базе данных и отображения ошибок.
#
class EditOrderWindow(EditWindow):
    def __init__(self, parent, order_id):
        super().__init__(parent)
        self.setWindowTitle("Редактировать заказ")
        self.setGeometry(100, 100, 400, 400)
        self.center_window()
        self.order_id = order_id
        self.user = parent.user  
        self.permissions = self.user.get_permissions()

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests WHERE id=?', (order_id,))
        order = cursor.fetchone()
        conn.close()

        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["ремонт", "техническое обслуживание"])
        self.type_combo.setCurrentText(order[1])
        self.type_combo.currentTextChanged.connect(self.update_price)
        self.form_layout.addRow("Тип заказа:", self.type_combo)

        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["новый", "в работе", "завершён"])
        
        if isinstance(self.user, Client) and order[2] != "новый":
            self.layout = QVBoxLayout()
            label = QLabel("Вы не можете редактировать заказы\nсо статусом 'в работе' или 'завершён'")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(label)
            
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(self.close)
            self.layout.addWidget(ok_button)
            
            self.setLayout(self.layout)
            return
        else:
            self.status_combo.setCurrentText(order[2])
            if not self.permissions["can_edit_status"]:
                self.status_combo.setEnabled(False)
        
        self.form_layout.addRow("Статус:", self.status_combo)

        self.price_input = QLineEdit(self)
        self.price_input.setReadOnly(True)
        self.price_input.setText(str(order[3]))
        self.form_layout.addRow("Цена:", self.price_input)

        self.client_name_input = FilterComboBox(self)
        self.load_client_names()
        self.client_name_input.setCurrentText(order[4])
        if not self.permissions["can_edit_client_name"]:
            self.client_name_input.setEnabled(False)
        self.form_layout.addRow("ФИО клиента:", self.client_name_input)

        self.master_name_input = FilterComboBox(self)
        self.load_employee_names()
        self.master_name_input.setCurrentText(order[5])
        self.form_layout.addRow("ФИО мастера:", self.master_name_input)

        self.car_number_input = QLineEdit(self)
        self.car_number_input.setText(order[6]) 
        self.form_layout.addRow("Номер автомобиля:", self.car_number_input)

        self.open_date_edit = QDateEdit(self)
        self.open_date_edit.setCalendarPopup(True)
        open_date = QDate.fromString(order[7], "yyyy-MM-dd")
        self.open_date_edit.setDate(open_date)
        self.form_layout.addRow("Дата открытия:", self.open_date_edit)

        if not self.permissions["can_edit_close_date"]:
            self.close_date_edit = QLineEdit(self)
            self.close_date_edit.setText("не указано")
            self.close_date_edit.setEnabled(False)
            self.form_layout.addRow("Дата закрытия:", self.close_date_edit)
        else:
            self.close_date_edit = QDateEdit(self)
            self.close_date_edit.setCalendarPopup(True)
            if order[8] and order[8] != "не указано":  
                close_date = QDate.fromString(order[8], "yyyy-MM-dd")
                self.close_date_edit.setDate(close_date)
            else:
                self.close_date_edit.setDate(QDate.currentDate())
            self.form_layout.addRow("Дата закрытия:", self.close_date_edit)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.edit_window)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def update_price(self):
        order_type = self.type_combo.currentText()
        if order_type == "ремонт":
            self.price_input.setText("5000")
        elif order_type == "техническое обслуживание":
            self.price_input.setText("2500")

    def edit_window(self):
        type_ = self.type_combo.currentText()
        status = self.status_combo.currentText()
        price = self.price_input.text()
        client_name = self.client_name_input.currentText()
        master_name = self.master_name_input.currentText()
        car_number = self.car_number_input.text()
        open_date = self.open_date_edit.date().toString("yyyy-MM-dd")
        if isinstance(self.user, Client):
            close_date = "не указано"
        else:
            close_date = self.close_date_edit.date().toString("yyyy-MM-dd")

        if not all([type_, status, price, client_name, master_name, car_number]):
            self.show_error("Все обязательные поля должны быть заполнены!")
            return

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('''UPDATE requests SET 
                          type=?, status=?, price=?, client_name=?, master_name=?, car_number=?, open_date=?, close_date=?
                          WHERE id=?''',
                       (type_, status, price, client_name, master_name, car_number, open_date, close_date, self.order_id))
        conn.commit()
        conn.close()

        self.parent().populate_orders_table()
        self.close()

    def load_client_names(self):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM clients')
        clients = cursor.fetchall()
        conn.close()
        
        self.client_name_input.clear()
        for client in clients:
            self.client_name_input.addItem(client[0])
    
    def load_employee_names(self):
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM employees')
        employees = cursor.fetchall()
        conn.close()
        
        self.master_name_input.clear()
        for employee in employees:
            self.master_name_input.addItem(employee[0])

##
# @class EditClientWindow
# @brief Окно для редактирования информации о клиенте.
# 
# Этот класс представляет собой окно для редактирования информации о клиенте. 
# Включает форму для изменения данных клиента, таких как логин, ФИО, почта, телефон и пароль.
# Также содержит логику для проверки данных, их обновления в базе данных и отображения ошибок.
#
class EditClientWindow(EditWindow):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.setWindowTitle("Редактировать клиента")
        self.setGeometry(100, 100, 400, 300)
        self.center_window()
        self.username = username

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE username=?', (username,))
        client = cursor.fetchone()
        conn.close()

        self.username_input = QLineEdit(self)
        self.username_input.setText(client[0])
        self.username_input.setReadOnly(True)  
        self.form_layout.addRow("Логин:", self.username_input)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setText(client[1])
        self.form_layout.addRow("ФИО:", self.full_name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setText(client[2])
        self.form_layout.addRow("Почта:", self.email_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setText(client[3])
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Оставьте пустым, чтобы не менять")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow("Новый пароль:", self.password_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.edit_window)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def edit_window(self):
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        password = self.password_input.text()

        if not all([full_name, email, phone]):
            self.show_error("Все обязательные поля должны быть заполнены!")
            return

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        if password:  
            cursor.execute('''UPDATE clients SET 
                              full_name=?, email=?, phone=?, password=?
                              WHERE username=?''',
                           (full_name, email, phone, password, self.username))
        else:  
            cursor.execute('''UPDATE clients SET 
                              full_name=?, email=?, phone=?
                              WHERE username=?''',
                           (full_name, email, phone, self.username))
        
        conn.commit()
        conn.close()

        self.parent().populate_clients_table()
        self.close()

##
# @class EditEmployeeWindow
# @brief Окно для редактирования информации о сотруднике.
# 
# Этот класс представляет собой окно для редактирования информации о сотруднике. 
# Включает форму для изменения данных сотрудника, таких как логин, ФИО, почта, телефон и пароль.
# Также содержит логику для проверки данных, их обновления в базе данных и отображения ошибок.
#
class EditEmployeeWindow(EditWindow):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.setWindowTitle("Редактировать сотрудника")
        self.setGeometry(100, 100, 400, 300)
        self.center_window()
        self.username = username

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE username=?', (username,))
        employee = cursor.fetchone()
        conn.close()

        self.username_input = QLineEdit(self)
        self.username_input.setText(employee[0])
        self.username_input.setReadOnly(True)  
        self.form_layout.addRow("Логин:", self.username_input)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setText(employee[1])
        self.form_layout.addRow("ФИО:", self.full_name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setText(employee[2])
        self.form_layout.addRow("Почта:", self.email_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setText(employee[3])
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Оставьте пустым, чтобы не менять")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form_layout.addRow("Новый пароль:", self.password_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.edit_window)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def edit_window(self):
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        password = self.password_input.text()

        if not all([full_name, email, phone]):
            self.show_error("Все обязательные поля должны быть заполнены!")
            return

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        
        if password:  
            cursor.execute('''UPDATE employees SET 
                              full_name=?, email=?, phone=?, password=?
                              WHERE username=?''',
                           (full_name, email, phone, password, self.username))
        else:  
            cursor.execute('''UPDATE employees SET 
                              full_name=?, email=?, phone=?
                              WHERE username=?''',
                           (full_name, email, phone, self.username))
        
        conn.commit()
        conn.close()

        self.parent().populate_employees_table()
        self.close()
