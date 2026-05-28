from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QMessageBox, QMenu, QDateEdit
)
from PyQt6.QtCore import Qt, QDate


class AddTransactionDialog(QDialog):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Добавить операцию")
        self.setFixedSize(420, 540)

        self.setStyleSheet("""
            QDialog { background-color: #121826; }
            QLabel { color: #94A3B8; font-size: 15px; font-weight: 500; font-family: '.AppleSystemUIFont', 'Segoe UI'; }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #1E293B; border: 2px solid #2D3748; border-radius: 12px; padding: 12px; color: white; font-size: 15px;
            }
            QPushButton#SaveBtn {
                background-color: #7C3AED; border: none; border-radius: 14px; padding: 14px; color: white; font-size: 15px; font-weight: bold;
            }
            QPushButton#SaveBtn:hover { background-color: #8B5CF6; }
            
            QPushButton#HelpBtn {
                background-color: #334155; color: #E2E8F0; border: none; border-radius: 20px; font-size: 18px; font-weight: bold; outline: none;
            }
            QPushButton#HelpBtn:hover { background-color: #475569; color: white; }
        """)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(28, 28, 28, 28)
        self.main_layout.setSpacing(12)

        self.main_layout.addWidget(QLabel("Число (Расход пиши с минусом):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.main_layout.addWidget(self.amount_input)

        self.main_layout.addWidget(QLabel("Тег:"))
        self.tag_combo = QComboBox()
        self.tag_combo.addItems(["Обычный", "Купила", "Долг", "Работа"])
        self.tag_combo.currentTextChanged.connect(self.handle_tag_change)
        self.main_layout.addWidget(self.tag_combo)

        self.dynamic_layout = QVBoxLayout()
        self.main_layout.addLayout(self.dynamic_layout)

        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Что купила? (например: Кроссовки)")
        self.product_label = QLabel("Продукт:")
        
        self.debt_combo = QComboBox()
        self.debt_combo.addItems(["Мы взяли в долг", "У нас взяли в долг"])
        self.debt_combo.currentTextChanged.connect(self.handle_debt_type_change)
        self.debt_label = QLabel("Тип долга:")
        self.date_label = QLabel("Когда нужно вернуть:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.work_label = QLabel("Периодичность выплаты:")
        self.work_combo = QComboBox()
        self.work_combo.addItems(["Раз в неделю", "Раз в месяц", "Раз в год"])

        self.main_layout.addStretch()

        bottom_layout = QHBoxLayout()
        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("HelpBtn")
        self.help_btn.setFixedSize(40, 40)
        self.help_btn.clicked.connect(self.show_tags_hint)
        
        self.save_btn = QPushButton("Добавить")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.clicked.connect(self.save_data)

        bottom_layout.addWidget(self.help_btn)
        bottom_layout.addSpacing(12)
        bottom_layout.addWidget(self.save_btn)
        self.main_layout.addLayout(bottom_layout)
        
        self.setLayout(self.main_layout)

        self.result_amount = 0.0
        self.result_tag = ""
        self.result_extra = ""

    def handle_tag_change(self, current_tag):
        self.clear_dynamic_layout()
        if current_tag == "Купила":
            self.dynamic_layout.addWidget(self.product_label)
            self.dynamic_layout.addWidget(self.product_input)
        elif current_tag == "Долг":
            self.dynamic_layout.addWidget(self.debt_label)
            self.dynamic_layout.addWidget(self.debt_combo)
            self.handle_debt_type_change(self.debt_combo.currentText())
        elif current_tag == "Работа":
            self.dynamic_layout.addWidget(self.work_label)
            self.dynamic_layout.addWidget(self.work_combo)

    def handle_debt_type_change(self, debt_type):
        self.date_label.setParent(None)
        self.date_input.setParent(None)
        if debt_type == "Мы взяли в долг":
            self.dynamic_layout.addWidget(self.date_label)
            self.dynamic_layout.addWidget(self.date_input)

    def clear_dynamic_layout(self):
        widgets = [
            self.product_label, self.product_input, 
            self.debt_label, self.debt_combo, 
            self.date_label, self.date_input,
            self.work_label, self.work_combo
        ]
        for widget in widgets:
            widget.setParent(None)

    def show_tags_hint(self):
        hint_menu = QMenu(self)
        hint_menu.setStyleSheet("""
            QMenu { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 6px; }
            QMenu::item { color: #E2E8F0; font-size: 14px; padding: 6px 16px; }
            QMenu::item:selected { background-color: #7C3AED; }
        """)
        hint_menu.addAction("📌 Обычный — базовая транзакция")
        hint_menu.addAction("🛍️ Купила — расходы на вещи/продукты")
        hint_menu.addAction("💳 Долг — учет заемных средств")
        hint_menu.addAction("💼 Работа — доходы для умных прогнозов")
        hint_menu.exec(self.help_btn.mapToGlobal(self.help_btn.rect().topLeft()))

    def save_data(self):
        amount_text = self.amount_input.text().strip().replace(",", ".")
        try:
            amt = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное число.")
            return

        self.result_tag = self.tag_combo.currentText()
        
        if self.result_tag == "Купила":
            self.result_extra = self.product_input.text().strip()
            if not self.result_extra:
                QMessageBox.warning(self, "Ошибка", "Укажите продукт.")
                return
            self.result_amount = amt
        elif self.result_tag == "Долг":
            debt_type = self.debt_combo.currentText()
            if debt_type == "Мы взяли в долг":
                selected_date = self.date_input.date()
                self.result_extra = f"{debt_type} (До {selected_date.toString('dd.MM.yyyy')})"
                if selected_date <= QDate.currentDate():
                    self.result_amount = -abs(amt)
                else:
                    self.result_amount = abs(amt)
            else:
                self.result_extra = debt_type
                self.result_amount = amt
        elif self.result_tag == "Работа":
            self.result_extra = self.work_combo.currentText()
            self.result_amount = amt
        else:
            self.result_extra = ""
            self.result_amount = amt

        self.accept()