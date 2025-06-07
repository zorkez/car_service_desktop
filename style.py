##
# @file style.py
# @brief Файл для настройки стилей интерфейса.
# 
# Этот файл отвечает за стилизацию элементов интерфейса с использованием библиотеки PyQt6.
# Он задает внешний вид элементов интерфейса, таких как кнопки, поля ввода и таблицы.
#
# @author Гаврилов Николай Срегеевич
# @version 1.0
# @date 2025-05-30
#
"""
Модуль оформления программы.

Автор: Гаврилов Николай Сергеевич
Дата: 2025-05-30
"""
from PyQt6.QtGui import QFont

def setup_style(app):
    """
    Устанавливает стиль для приложения.

    Параметры:
        app (QApplication): Приложение, к которому применяется стиль.
    """
    font = QFont("Comic Sans MS", 10)
    app.setFont(font)
    
    style = """
    QWidget {
        background-color: #FFFFFF;  
        color: #000000; 
    }
    
    QTabWidget::pane {
        border: 1px solid #ED760E;  
        background: #FFFFFF;  
    }
    
    QTabBar::tab {
        background: #ED760E; 
        color: white;  
        padding: 8px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
    }
    
    QTabBar::tab:selected {
        background: #FF8C00; 
        color: white;  
    }
    
    QPushButton {
        background-color: #ED760E;  
        color: white;  
        border: 1px solid #D85F0C;  
        border-radius: 5px;
        padding: 5px 10px;
    }
    
    QPushButton:hover {
        background-color: #FF8C00;  
    }
    
    QPushButton:pressed {
        background-color: #D85F0C;  
    }
    
    QPushButton:disabled {
        background-color: #FFD3A0;  
        color: #BC8F8F;
    }

    /* Стиль для кнопки Изменить */
    QPushButton#edit_button {
        background-color: #20ca8c;  
        color: white;
        border: 1px solid #A3A19E;  
        border-radius: 5px;
        padding: 5px 10px;
    }

    QPushButton#edit_button:hover {
        background-color: #1e9f76;
    }

    QPushButton#edit_button:pressed {
        background-color: #1a8b64;
    }

    /* Стиль для кнопки Удалить */
    QPushButton#delete_button {
        background-color: #e8493c;  
        color: white;
        border: 1px solid #A3A19E;  
        border-radius: 5px;
        padding: 5px 10px;
    }

    QPushButton#delete_button:hover {
        background-color: #d63f31;
    }

    QPushButton#delete_button:pressed {
        background-color: #b6362a;
    }

    QLineEdit, QComboBox, QDateEdit {
        background-color: #FFF5E1; 
        border: 1px solid #ED760E;  
        border-radius: 3px;
        padding: 3px;
    }
    
    QTableWidget {
        background-color: #FFFFFF;  
        alternate-background-color: #F5F5F5;  
        gridline-color: #A3A19E;  
    }
    
    QHeaderView::section {
        background-color: #A3A19E;  
        color: white;  
        padding: 5px;
    }
    
    QMessageBox {
        background-color: #FFFFFF;  
    }

    QTableWidget::item:selected {
        background-color: #0066FF;
        color: white;
    }
    
    QTableWidget QTableCornerButton::section {
        background-color: #A3A19E;
    }
    """
    app.setStyleSheet(style)
