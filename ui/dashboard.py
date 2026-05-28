import re
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QWidget, QInputDialog, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from datetime import datetime
from ui.add_transaction_dialog import AddTransactionDialog
from logic.database import add_transaction, get_transactions
from logic.finance_manager import calculate_future_prediction


class Dashboard(QFrame):
    def __init__(self):
        super().__init__()
        self.user_id = None
        self.username = "Пользователь"
        self.main_window = None
        self.current_mode = "Финансы"
        self.active_filter = "Самое свежее"

        self.setStyleSheet("QFrame#DashboardContainer { background-color: #111827; border-radius: 24px; border: 1px solid #1E293B; }")
        self.setObjectName("DashboardContainer")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(28, 28, 28, 28)

        # ВЕРХНЯЯ ПАНЕЛЬ
        top_bar = QHBoxLayout()
        self.board_title = QLabel("История операций")
        self.board_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #F8FAFC; font-family: '.AppleSystemUIFont', 'Segoe UI';")
        
        # Кнопка авто-импорта из буфера обмена (карта)
        self.auto_btn = QPushButton("🤖 Авто-импорт")
        self.auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981; color: white; font-size: 13px; font-weight: bold; padding: 10px 16px; border-radius: 12px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.auto_btn.clicked.connect(self.auto_process_clipboard)
        self.auto_btn.hide()

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(44, 44)
        self.add_btn.setStyleSheet("""
            QPushButton { 
                background-color: #7C3AED; color: white; font-size: 24px; font-weight: bold; border-radius: 22px; border: none;
            } 
            QPushButton:hover { background-color: #8B5CF6; }
        """)
        self.add_btn.clicked.connect(self.open_add_transaction)
        self.add_btn.hide()

        top_bar.addWidget(self.board_title)
        top_bar.addStretch()
        top_bar.addWidget(self.auto_btn)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.add_btn)
        self.layout.addLayout(top_bar)
        self.layout.addSpacing(5)

        # Фильтры
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setSpacing(10)
        
        self.filter_fresh_btn = QPushButton("Самое свежее")
        self.filter_old_btn = QPushButton("Самое древнее")
        self.filter_tag_btn = QPushButton("Найти по тегам")
        
        for btn in [self.filter_fresh_btn, self.filter_old_btn, self.filter_tag_btn]:
            btn.setStyleSheet("""
                QPushButton { 
                    background-color: #1E293B; font-size: 13px; font-weight: 600; padding: 8px 16px; border-radius: 10px; color: #94A3B8; border: none;
                } 
                QPushButton:hover { background-color: #334155; color: white; }
            """)
        
        self.filter_fresh_btn.clicked.connect(lambda: self.change_filter("Самое свежее"))
        self.filter_old_btn.clicked.connect(lambda: self.change_filter("Самое древнее"))
        self.filter_tag_btn.clicked.connect(self.filter_by_tag_dialog)

        self.filter_layout.addWidget(self.filter_fresh_btn)
        self.filter_layout.addWidget(self.filter_old_btn)
        self.filter_layout.addWidget(self.filter_tag_btn)
        self.filter_layout.addStretch()
        
        self.layout.addLayout(self.filter_layout)
        self.layout.addSpacing(15)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.scroll_content = QWidget()
        self.history_layout = QVBoxLayout(self.scroll_content)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(12)
        self.history_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        self.future_text_label = QLabel("")
        self.future_text_label.setWordWrap(True)
        self.future_text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.future_text_label.setStyleSheet("""
            QLabel {
                color: #E2E8F0; font-size: 18px; font-family: '.AppleSystemUIFont', 'Segoe UI'; line-height: 180%;
                padding: 24px; background-color: #1E293B; border-radius: 16px; border: 1px solid #2D3748;
            }
        """)
        self.future_text_label.hide()
        self.layout.addWidget(self.future_text_label)

        self.setLayout(self.layout)

    def set_user_context(self, user_id, username, main_window):
        self.user_id = user_id
        self.username = username
        self.main_window = main_window
        self.add_btn.show()
        self.auto_btn.show()
        self.switch_mode("Финансы")

    def auto_process_clipboard(self):
        clipboard_text = QApplication.clipboard().text().strip()
        if not clipboard_text:
            QMessageBox.warning(self, "Робот-помощник", "Буфер обмена пуст. Скопируйте текст пуша или SMS от банка!")
            return

        # Находим числовые значения (сумму)
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', clipboard_text.replace(",", "."))
        if not numbers:
            QMessageBox.warning(self, "Робот-помощник", "Не удалось автоматически вытащить сумму из текста.")
            return

        amount = float(numbers[0])
        detected_tag = "Купила"
        detected_extra = "Авто-импорт"

        lower_text = clipboard_text.lower()
        if any(word in lower_text for word in ["зачисление", "зарплата", "перевод от", "доход", "+"]):
            detected_tag = "Работа"
            detected_extra = "Раз в месяц"
        else:
            words = clipboard_text.split()
            if len(words) > 2:
                detected_extra = " ".join(words[1:4])
            amount = -abs(amount)

        reply = QMessageBox.question(
            self,
            "Умный разбор чека/карты",
            f"Распознанный текст:\n\"{clipboard_text}\"\n\nДобавить операцию?\n💰 Сумма: {amount:,.2f} денег\n🏷️ Тег: {detected_tag}\n📌 Детали: {detected_extra}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            new_balance = add_transaction(self.user_id, amount, detected_tag, detected_extra)
            if new_balance is not None:
                self.main_window.sidebar.update_balance(new_balance)
                self.refresh_content()

    def open_add_transaction(self):
        if not self.user_id: return
        dialog = AddTransactionDialog(self.username)
        if dialog.exec():
            new_balance = add_transaction(self.user_id, dialog.result_amount, dialog.result_tag, dialog.result_extra)
            if new_balance is not None:
                self.main_window.sidebar.update_balance(new_balance)
                self.refresh_content()

    def switch_mode(self, mode_name):
        self.current_mode = mode_name
        self.board_title.setText(f"Раздел: {mode_name}")
        self.refresh_content()

    def change_filter(self, filter_name):
        self.active_filter = filter_name
        self.refresh_content()

    def filter_by_tag_dialog(self):
        tag, ok = QInputDialog.getText(self, "Поиск по тегам", "Введите имя тега:")
        if ok and tag.strip():
            self.active_filter = f"Тег:{tag.strip()}"
            self.refresh_content()

    def refresh_content(self):
        if self.current_mode == "Будущее":
            self.scroll.hide()
            self.auto_btn.hide()
            for i in range(self.filter_layout.count()):
                w = self.filter_layout.itemAt(i).widget()
                if w: w.hide()
            self.future_text_label.show()
            self.render_future_screen()
        else:
            self.future_text_label.hide()
            self.scroll.show()
            if self.user_id: self.auto_btn.show()
            for i in range(self.filter_layout.count()):
                w = self.filter_layout.itemAt(i).widget()
                if w: w.show()
            self.render_history_screen()

    def render_future_screen(self):
        if not self.user_id: return
        all_tx = get_transactions(self.user_id)
        prediction = calculate_future_prediction(all_tx)
        self.future_text_label.setText(prediction)

    def render_history_screen(self):
        while self.history_layout.count() > 1:
            item = self.history_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not self.user_id: return
        transactions = get_transactions(self.user_id)

        if self.current_mode == "Долги":
            transactions = [tx for tx in transactions if tx[1] == "Долг"]
        elif self.active_filter.startswith("Тег:"):
            target_tag = self.active_filter.split(":")[1]
            transactions = [tx for tx in transactions if tx[1].lower() == target_tag.lower()]

        if self.active_filter == "Самое древнее":
            transactions.reverse()

        for amount, tag, extra, full_date_str in transactions:
            try:
                time_formatted = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            except ValueError:
                time_formatted = full_date_str

            tx_card = QFrame()
            tx_card.setStyleSheet("QFrame { background-color: #1E293B; border-radius: 16px; border: 1px solid #2D3748; }")
            tx_layout = QHBoxLayout(tx_card)
            tx_layout.setContentsMargins(20, 16, 20, 16)

            info = f" [{extra}]" if extra else ""
            text_label = QLabel(f"{self.username}: {tag}{info}")
            text_label.setStyleSheet("color: #E2E8F0; font-size: 15px; font-weight: 500; border: none;")
            
            time_label = QLabel(time_formatted)
            time_label.setStyleSheet("color: #64748B; font-size: 13px; border: none;")

            sign = "+" if amount > 0 else ""
            m_text = f"{sign}{amount:,.2f}".replace(",", " ")
            color = "#10B981" if amount > 0 else "#F43F5E"
            money_label = QLabel(m_text)
            money_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold; border: none;")

            tx_layout.addWidget(text_label)
            tx_layout.addWidget(time_label)
            tx_layout.addStretch()
            tx_layout.addWidget(money_label)

            self.history_layout.insertWidget(self.history_layout.count() - 1, tx_card)