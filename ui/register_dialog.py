from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt
from logic.database import register_user


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Регистрация")
        self.setFixedSize(420, 450)

        self.money_value = 0.0
        self.username_value = ""

        self.setStyleSheet("""
            QDialog {
                background-color: #121826;
            }

            QLabel {
                color: white;
            }

            QLineEdit {
                background-color: #1E293B;
                border: 2px solid #2D3748;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }

            QPushButton {
                background-color: #7C3AED;
                border-radius: 12px;
                padding: 12px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #8B5CF6;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("Создание аккаунта")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.money_input = QLineEdit()
        self.money_input.setPlaceholderText("Нынешние деньги")

        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Привязать карту (необязательно)")

        create_btn = QPushButton("Создать аккаунт")
        create_btn.clicked.connect(self.create_account)

        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addWidget(self.name_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.money_input)
        layout.addWidget(self.card_input)
        layout.addSpacing(10)
        layout.addWidget(create_btn)

        self.setLayout(layout)

    def create_account(self):
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()
        money = self.money_input.text().strip()

        if not name or not password or not money:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля.")
            return

        try:
            # Заменяем запятую на точку, если ввели копейки через запятую
            money_number = float(money.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму.")
            return

        # Сохраняем в локальную бессерверную БД
        user_id = register_user(name, password, money_number)

        if user_id:
            self.money_value = money_number
            self.username_value = name
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные в базу.")