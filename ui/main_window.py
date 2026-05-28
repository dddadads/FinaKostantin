from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMenu, QMessageBox
)
from PyQt6.QtGui import QAction, QCursor
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.register_dialog import RegisterDialog
from logic.database import get_last_user_data


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FinaKostantin")
        self.resize(1300, 750)

        self.setStyleSheet("""
            QWidget { background-color: #0F172A; color: white; font-family: '.AppleSystemUIFont', 'Segoe UI'; }
            QPushButton { background-color: #1E293B; border: none; border-radius: 12px; padding: 10px 18px; color: white; font-size: 14px; }
            QPushButton:hover { background-color: #334155; }
        """)

        main_layout = QVBoxLayout()

        top_menu = QHBoxLayout()
        self.finance_btn = QPushButton("Финансы")
        self.debts_btn = QPushButton("Долги")
        self.future_btn = QPushButton("Будущее")

        top_menu.addWidget(self.finance_btn)
        top_menu.addWidget(self.debts_btn)
        top_menu.addWidget(self.future_btn)
        top_menu.addStretch()

        self.auth_layout = QHBoxLayout()
        self.login_btn = QPushButton("Зарегистрироваться / Войти")
        self.login_btn.setStyleSheet(
            "QPushButton { background-color: #7C3AED; font-weight: bold; } QPushButton:hover { background-color: #8B5CF6; }")
        self.login_btn.clicked.connect(self.open_register)

        self.username_label = QLabel("")
        self.username_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #F1F5F9; margin-right: 5px;")

        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedWidth(35)
        self.menu_btn.setFixedHeight(35)
        self.menu_btn.setStyleSheet(
            "QPushButton { background-color: #1E293B; font-size: 18px; font-weight: bold; border-radius: 10px; padding: 0px; }")
        self.menu_btn.clicked.connect(self.show_settings_menu)

        self.auth_layout.addWidget(self.login_btn)
        self.auth_layout.addWidget(self.username_label)
        self.auth_layout.addWidget(self.menu_btn)

        self.username_label.hide()
        self.menu_btn.hide()
        top_menu.addLayout(self.auth_layout)

        content_layout = QHBoxLayout()
        self.sidebar = Sidebar()
        self.dashboard = Dashboard()

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.dashboard)

        main_layout.addLayout(top_menu)
        main_layout.addSpacing(15)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        self.finance_btn.clicked.connect(lambda: self.dashboard.switch_mode("Финансы"))
        self.debts_btn.clicked.connect(lambda: self.dashboard.switch_mode("Долги"))
        self.future_btn.clicked.connect(lambda: self.dashboard.switch_mode("Будущее"))

        user_data = get_last_user_data()
        if user_data:
            username, saved_balance, user_id = user_data
            self.login_success(username, saved_balance)

    def open_register(self):
        dialog = RegisterDialog()
        if dialog.exec():
            self.login_success(dialog.username_value, dialog.money_value)

    def login_success(self, username, balance):
        self.login_btn.hide()
        self.username_label.setText(username)
        self.username_label.show()
        self.menu_btn.show()

        self.sidebar.set_user_greeting(username)
        self.sidebar.update_balance(balance)

        user_data = get_last_user_data()
        if user_data:
            user_id = user_data[2]
            self.dashboard.set_user_context(user_id, username, self)

    def show_settings_menu(self):
        settings_menu = QMenu(self)
        settings_menu.setStyleSheet("""
            QMenu { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 4px; }
            QMenu::item { color: white; padding: 6px 20px; border-radius: 4px; font-size: 13px; }
            QMenu::item:selected { background-color: #7C3AED; }
        """)
        profile_action = QAction("⚙️ Настройки аккаунта", self)
        reset_action = QAction("🔄 Сбросить данные", self)
        logout_action = QAction("🚪 Выйти из профиля", self)

        reset_action.triggered.connect(self.action_reset_data)
        logout_action.triggered.connect(self.action_logout)

        settings_menu.addAction(profile_action)
        settings_menu.addAction(reset_action)
        settings_menu.addSeparator()
        settings_menu.addAction(logout_action)
        settings_menu.exec(QCursor.pos())

    def action_reset_data(self):
        import sqlite3
        from logic.database import DB_PATH

        reply = QMessageBox.question(
            self,
            "Сброс данных",
            "Вы уверены, что хотите полностью стереть всю историю операций и обнулить баланс? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions")
                cursor.execute("UPDATE users SET balance = 0.0")
                conn.commit()
                conn.close()

                self.sidebar.update_balance(0.0)
                self.dashboard.refresh_content()

                QMessageBox.information(self, "Успех", "Все данные успешно сброшены!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сбросить данные: {e}")

    def action_logout(self):
        self.username_label.hide()
        self.menu_btn.hide()
        self.login_btn.show()
        self.sidebar.set_user_greeting("")
        self.sidebar.update_balance(0)