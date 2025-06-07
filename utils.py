##
# @file utils.py
# @brief Файл с утилитами и вспомогательными классами для работы с интерфейсом.
# 
# Этот файл содержит вспомогательные классы и методы для работы с элементами интерфейса, такие как централизованные окна и фильтрация данных.
#
# @author Гаврилов Николай Срегеевич
# @version 1.0
# @date 2025-05-30
#
"""
Модуль вспомогательных функций и утилит.

Автор: Гаврилов Николай Сергеевич
Дата: 2025-05-30
"""
from PyQt6.QtCore import Qt, QStringListModel, pyqtSignal, QDate
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QGroupBox, QFormLayout, QComboBox, QSpinBox, QTextEdit, QApplication, QCompleter, QDateEdit, QLineEdit, QWidget, QHBoxLayout, QLabel
from statistics import mean
from datetime import datetime
from models import Client
import sqlite3

##
# @class CenteredWindow
# @brief Класс для центрирования окна на экране.
# 
# Этот класс предоставляет метод для того, чтобы окно приложения было отображено по центру экрана.
# Он может быть использован для улучшения пользовательского интерфейса, обеспечивая удобное расположение окон.
#
class CenteredWindow():
    """
    Класс для центрирования окна на экране.
    """
    def center_window(self):
        """
        Центрирует окно на экране.
        """
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

##
# @class ForecastWindow
# @brief Окно для прогнозирования заказов.
# 
# Этот класс представляет собой диалоговое окно, которое позволяет пользователю прогнозировать количество заказов
# на основе данных о предыдущих заказах. Пользователь может выбрать месяц, год и размер окна для скользящей средней.
# Результаты прогноза отображаются в текстовом поле.
#
class ForecastWindow(QDialog, CenteredWindow):
    """
    Окно для прогнозирования заказов.

    Атрибуты:
        layout (QVBoxLayout): Основной компоновщик для размещения виджетов в окне.
        month_combo (QComboBox): Комбо-бокс для выбора месяца прогноза.
        year_spin (QSpinBox): Поле для выбора года прогноза.
        window_size_spin (QSpinBox): Поле для выбора размера окна для скользящей средней.
        calculate_btn (QPushButton): Кнопка для расчета прогноза.
        results_text (QTextEdit): Текстовое поле для отображения результатов.
    """
    def __init__(self, parent):
        """
        Инициализация окна прогнозирования заказов.

        Параметры:
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)
        self.setWindowTitle("Прогнозирование заказов")
        self.setGeometry(100, 100, 700, 500)
        self.center_window()
        
        self.layout = QVBoxLayout()
        
        params_group = QGroupBox("Параметры прогнозирования")
        params_layout = QFormLayout()
        
        self.month_combo = QComboBox()
        self.month_combo.addItems(["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                                 "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"])
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        params_layout.addRow("Месяц прогноза:", self.month_combo)
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(datetime.now().year)
        params_layout.addRow("Год прогноза:", self.year_spin)
        
        self.window_size_spin = QSpinBox()
        self.window_size_spin.setRange(2, 12)
        self.window_size_spin.setValue(3)
        params_layout.addRow("Размер окна для скользящей средней:", self.window_size_spin)
        
        params_group.setLayout(params_layout)
        self.layout.addWidget(params_group)
        
        self.calculate_btn = QPushButton("Рассчитать прогноз")
        self.calculate_btn.clicked.connect(self.calculate_forecast)
        self.layout.addWidget(self.calculate_btn)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.layout.addWidget(self.results_text)
        
        self.setLayout(self.layout)
    
    def calculate_forecast(self):
        """
        Выполняет расчет прогноза на основе данных о заказах.

        Прогноз строится с использованием скользящей средней за определенное количество месяцев.
        """
        selected_month = self.month_combo.currentIndex() + 1
        selected_year = self.year_spin.value()
        window_size = self.window_size_spin.value()
        
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT open_date FROM requests ORDER BY open_date')
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not dates:
            self.results_text.setPlainText("Нет данных для анализа")
            return
        
        monthly_counts = {}
        for date_str in dates:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                month_key = (date.year, date.month)
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            except ValueError:
                continue  
        
        sorted_months = sorted(monthly_counts.keys())
        counts = [monthly_counts[month] for month in sorted_months]
        
        if len(counts) < window_size:
            self.results_text.setPlainText(
                f"Недостаточно данных для расчета (нужно минимум {window_size} месяца, доступно {len(counts)})"
            )
            return
        
        moving_averages = []
        for i in range(window_size - 1, len(counts)):
            window = counts[i - window_size + 1 : i + 1]
            moving_averages.append(round(mean(window), 2))
        
        target_date = (selected_year, selected_month)
        
        if target_date in monthly_counts:
            target_index = sorted_months.index(target_date)
            
            if target_index >= window_size:
                forecast = moving_averages[target_index - window_size]
            else:
                forecast = round(mean(counts[:target_index]), 2) if target_index > 0 else 0
            
            actual = monthly_counts[target_date]
            deviation = (forecast - actual) / actual * 100 if actual != 0 else 0
        else:
            forecast = self.recursive_forecast(
                sorted_months, monthly_counts, target_date, window_size
            )
            actual = None
        
        report = "=== Исторические данные по месяцам ===\n"
        for (y, m), count in zip(sorted_months, counts):
            report += f"{m:02d}/{y}: {count} заказов\n"
        
        report += f"\n=== Прогноз на {self.month_combo.currentText()} {selected_year} ===\n"
        report += f"Прогнозируемое количество заказов: {max(forecast, 0)}\n"
        
        if actual is not None:
            report += f"Фактическое количество заказов: {actual}\n"
            report += f"Отклонение прогноза: {deviation:+.2f}%\n"
        
        self.results_text.setPlainText(report)
    
    def recursive_forecast(self, sorted_months, monthly_counts, target_date, window_size):
        """
        Рекурсивный метод для вычисления прогноза на основе предыдущих месяцев.

        Параметры:
            sorted_months (list): Сортированные месяцы.
            monthly_counts (dict): Словарь с количеством заказов по месяцам.
            target_date (tuple): Целевая дата для прогноза (год, месяц).
            window_size (int): Размер окна для скользящей средней.

        Возвращает:
            float: Прогнозируемое количество заказов.
        """
        target_year, target_month = target_date
        
        prev_months = []
        current_year, current_month = target_year, target_month
        for _ in range(window_size):
            current_month -= 1
            if current_month == 0:
                current_month = 12
                current_year -= 1
            
            prev_months.append((current_year, current_month))
        
        values = []
        for month in prev_months:
            if month in monthly_counts:
                values.append(monthly_counts[month])
            else:
                if month < sorted_months[0]:
                    values.append(0)
                else:
                    values.append(self.recursive_forecast(
                        sorted_months, monthly_counts, month, window_size
                    ))
        
        return round(mean(values), 2)

##
# @class FilterComboBox
# @brief Кастомный комбинированный список с фильтрацией.
# 
# Этот класс расширяет стандартный QComboBox и добавляет функциональность фильтрации элементов списка в реальном времени.
# Пользователь может вводить текст, и элементы списка будут автоматически фильтроваться в зависимости от ввода.
#
class FilterComboBox(QComboBox):
    """
    Кастомный комбинированный список с фильтрацией.

    Атрибуты:
        _completer (QCompleter): Комплект для автодополнения.
    """
    def __init__(self, parent=None):
        """
        Инициализация комбинированного списка с фильтрацией.

        Параметры:
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        self.setCompleter(None)
        
        self._completer = QCompleter(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(self._completer)
        
        self.lineEdit().textEdited.connect(self.updateCompleter)

    def updateCompleter(self):
        """
        Обновляет модель автодополнения на основе введенного текста.
        """
        current_text = self.lineEdit().text()
        
        model = QStringListModel([self.itemText(i) for i in range(self.count())])
        self._completer.setModel(model)
        
        self._completer.setCompletionPrefix(current_text)
        
        if current_text and self._completer.completionCount() > 0:
            self._completer.complete()
        else:
            self._completer.popup().hide()
    
    def updateFilter(self):
        """
        Обновляет фильтр для отображения только тех элементов, которые содержат введенный текст.
        """
        text = self.lineEdit().text().lower()
        model = QStringListModel()
        
        filtered_items = [
            self.itemText(i) 
            for i in range(self.count()) 
            if text in self.itemText(i).lower()
        ]
        
        model.setStringList(filtered_items)
        self.completer.setModel(model)
        
        if text and filtered_items:
            self.showPopup()
        else:
            self.hidePopup()

##
# @class SearchWindow
# @brief Окно для поиска данных в таблицах (заказы, клиенты, сотрудники).
# 
# Этот класс представляет собой окно для поиска данных в таблицах приложения. 
# Пользователь может выполнять поиск по различным параметрам (например, типу заказа, статусу, клиенту и т.д.).
# В зависимости от типа таблицы (заказы, клиенты, сотрудники) окно будет отображать соответствующие поля поиска.
#
class SearchWindow(QDialog, CenteredWindow):
    """
    Окно для поиска данных в таблицах (заказы, клиенты, сотрудники).

    Атрибуты:
        search_completed (pyqtSignal): Сигнал, который отправляется по завершению поиска.
        table_type (str): Тип таблицы для поиска (заказы, клиенты, сотрудники).
    """
    search_completed = pyqtSignal()
    def __init__(self, parent, table_type, user):
        """
        Инициализация окна поиска.

        Параметры:
            parent (QWidget): Родительский виджет.
            table_type (str): Тип таблицы для поиска.
            user (User): Текущий пользователь.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Поиск ({'Заказы' if table_type == 'orders' else 'Клиенты' if table_type == 'clients' else 'Сотрудники'})")
        self.setGeometry(100, 100, 400, 500)
        self.center_window()
        self.parent = parent
        self.table_type = table_type
        self.is_filtered = False
        self.user = user  

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        if table_type == "orders":
            self.setup_order_fields()
            self.info_label = QLabel()
            self.info_label.setWordWrap(True)
            self.info_label.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-size: 12px;
                    padding: 8px;
                    background-color: #f8f8f8;
                    border-radius: 5px;
                    margin-top: 10px;
                }
            """)
            self.info_label.setText(
                "Примечание: Если дата закрытия включена, но не изменена (осталась 01.01.2000), "
                "поиск будет выполнен только по заказам с 'не указано' в дате закрытия."
            )
            self.layout.addWidget(self.info_label)
        elif table_type == "clients":
            self.setup_client_fields()
        elif table_type == "employees":
            self.setup_employee_fields()    
        
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.toggle_search)
        self.layout.addWidget(self.search_button)

        self.setLayout(self.layout)

    def setup_order_fields(self):
        self.type_input = FilterComboBox()
        self.type_input.addItems(["", "ремонт", "техническое обслуживание"])
        self.form_layout.addRow("Тип заказа:", self.type_input)

        self.status_input = FilterComboBox()
        self.status_input.addItems(["", "новый", "в работе", "завершён"])
        self.form_layout.addRow("Статус:", self.status_input)

        self.client_input = FilterComboBox()
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM clients')
        clients = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.client_input.addItems([""] + clients)
        self.form_layout.addRow("ФИО клиента:", self.client_input)

        self.master_input = FilterComboBox()
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM employees')
        employees = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.master_input.addItems([""] + employees)
        self.form_layout.addRow("ФИО мастера:", self.master_input)

        self.open_date_from_widget = DateFilterWidget()
        self.form_layout.addRow("Дата открытия от:", self.open_date_from_widget)
        
        self.open_date_to_widget = DateFilterWidget()
        self.open_date_to_widget.toggle_button.setEnabled(False)  
        self.form_layout.addRow("Дата открытия до:", self.open_date_to_widget)
        
        self.close_date_from_widget = DateFilterWidget()
        self.form_layout.addRow("Дата закрытия от:", self.close_date_from_widget)
        
        self.close_date_to_widget = DateFilterWidget()
        self.close_date_to_widget.toggle_button.setEnabled(False)  
        self.form_layout.addRow("Дата закрытия до:", self.close_date_to_widget)
        
        def update_open_dates():
            from_enabled = self.open_date_from_widget.is_enabled()
            to_enabled = self.open_date_to_widget.is_enabled()
            
            if from_enabled and not to_enabled:
                self.open_date_to_widget.toggle_button.setEnabled(True)
            
            if not from_enabled:
                self.open_date_to_widget.toggle_button.setChecked(False)
                self.open_date_to_widget.toggle_button.setEnabled(False)
            
            if to_enabled:
                self.open_date_from_widget.toggle_button.setEnabled(False)
            else:
                self.open_date_from_widget.toggle_button.setEnabled(True)
        
        def update_close_dates():
            from_enabled = self.close_date_from_widget.is_enabled()
            to_enabled = self.close_date_to_widget.is_enabled()           
           
            if from_enabled and not to_enabled:
                self.close_date_to_widget.toggle_button.setEnabled(True)
            
            if not from_enabled:
                self.close_date_to_widget.toggle_button.setChecked(False)
                self.close_date_to_widget.toggle_button.setEnabled(False)
            
            if to_enabled:
                self.close_date_from_widget.toggle_button.setEnabled(False)
            else:
                self.close_date_from_widget.toggle_button.setEnabled(True)
        
        self.open_date_from_widget.toggle_button.toggled.connect(update_open_dates)
        self.open_date_to_widget.toggle_button.toggled.connect(update_open_dates)
        self.close_date_from_widget.toggle_button.toggled.connect(update_close_dates)
        self.close_date_to_widget.toggle_button.toggled.connect(update_close_dates)

    def setup_client_fields(self):
        self.login_input = FilterComboBox()
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM clients')
        logins = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.login_input.addItems([""] + logins)
        self.form_layout.addRow("Логин клиента:", self.login_input)

        self.name_input = FilterComboBox()
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM clients')
        clients = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.name_input.addItems([""] + clients)
        self.form_layout.addRow("ФИО клиента:", self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Часть номера")
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Часть email")
        self.form_layout.addRow("Email:", self.email_input)

    def setup_employee_fields(self):
        self.login_input = FilterComboBox()
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM employees')
        logins = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.login_input.addItems([""] + logins)
        self.form_layout.addRow("Логин сотрудника:", self.login_input)

        self.name_input = FilterComboBox()
        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM employees')
        employees = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.name_input.addItems([""] + employees)
        self.form_layout.addRow("ФИО сотрудника:", self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Часть номера")
        self.form_layout.addRow("Телефон:", self.phone_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Часть email")
        self.form_layout.addRow("Email:", self.email_input)

    def toggle_search(self):
        if self.is_filtered:
            self.reset_filter()
        else:
            self.perform_search()

    def perform_search(self):
        if self.table_type == "orders":
            self.search_orders()
        elif self.table_type == "clients":
            self.search_clients()
        elif self.table_type == "employees":
            self.search_employees()
        
        self.search_completed.emit()  
        self.close()

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

    def search_orders(self):
        query = "SELECT * FROM requests WHERE 1=1"
        params = []

        if isinstance(self.user, Client):  
            query += " AND client_name = ?"
            params.append(self.user.full_name)

        if self.type_input.currentText():
            query += " AND type LIKE ?"
            params.append(f"%{self.type_input.currentText()}%")

        if self.status_input.currentText():
            query += " AND status LIKE ?"
            params.append(f"%{self.status_input.currentText()}%")
        
        if self.client_input.currentText():
            query += " AND client_name LIKE ?"
            params.append(f"%{self.client_input.currentText()}%")
        
        if self.master_input.currentText():
            query += " AND master_name LIKE ?"
            params.append(f"%{self.master_input.currentText()}%")
        
        if self.open_date_from_widget.is_enabled():
            date_from = self.open_date_from_widget.date().toString("yyyy-MM-dd")
            if self.open_date_to_widget.is_enabled():
                date_to = self.open_date_to_widget.date().toString("yyyy-MM-dd")
                query += " AND open_date BETWEEN ? AND ?"
                params.extend([date_from, date_to])
            else:
                query += " AND open_date = ?"
                params.append(date_from)

        if self.close_date_from_widget.is_enabled():
            date_from = self.close_date_from_widget.date().toString("yyyy-MM-dd")
            if self.close_date_to_widget.is_enabled():
                date_to = self.close_date_to_widget.date().toString("yyyy-MM-dd")
                query += " AND (close_date = 'не указано' OR close_date BETWEEN ? AND ?)"
                params.extend([date_from, date_to])
            else:
                query += " AND (close_date = 'не указано' OR close_date = ?)"
                params.append(date_from)

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        self.parent.populate_orders_table(results)

    def search_clients(self):
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        if self.login_input.currentText():
            query += " AND username LIKE ?"
            params.append(f"%{self.login_input.currentText()}%")
        
        if self.name_input.currentText():
            query += " AND full_name LIKE ?"
            params.append(f"%{self.name_input.currentText()}%")
        
        if self.phone_input.text():
            query += " AND phone LIKE ?"
            params.append(f"%{self.phone_input.text()}%")
        
        if self.email_input.text():
            query += " AND email LIKE ?"
            params.append(f"%{self.email_input.text()}%")

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        self.parent.populate_clients_table(results)

    def search_employees(self):
        query = "SELECT * FROM employees WHERE 1=1"
        params = []

        if self.login_input.currentText():
            query += " AND username LIKE ?"
            params.append(f"%{self.login_input.currentText()}%")
        
        if self.name_input.currentText():
            query += " AND full_name LIKE ?"
            params.append(f"%{self.name_input.currentText()}%")
        
        if self.phone_input.text():
            query += " AND phone LIKE ?"
            params.append(f"%{self.phone_input.text()}%")
        
        if self.email_input.text():
            query += " AND email LIKE ?"
            params.append(f"%{self.email_input.text()}%")

        conn = sqlite3.connect('service_requests.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        self.parent.populate_employees_table(results)

##
# @class DateFilterWidget
# @brief Виджет для фильтрации по дате.
# 
# Этот класс представляет собой виджет, который позволяет пользователю выбрать дату из календаря и включить/выключить фильтрацию по этой дате.
# Виджет включает кнопку для включения и отключения фильтрации, а также поле для выбора даты.
#
class DateFilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setEnabled(False)
        
        self.toggle_button = QPushButton("Вкл")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedWidth(50)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #20ca8c;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #e8493c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.toggle_button.toggled.connect(self.toggle_date)
        
        self.layout.addWidget(self.date_edit)
        self.layout.addWidget(self.toggle_button)
        self.setLayout(self.layout)
    
    def toggle_date(self, checked):
        self.date_edit.setEnabled(checked)
        self.toggle_button.setText("Выкл" if checked else "Вкл")
    
    def is_enabled(self):
        return self.toggle_button.isChecked()
    
    def date(self):
        return self.date_edit.date() if self.is_enabled() else QDate()
    
    def set_date(self, date):
        self.date_edit.setDate(date)