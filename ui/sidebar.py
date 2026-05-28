from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QWidget,
    QGraphicsOpacityEffect
)
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve
)


# Улучшенный лейбл, который сжимает текст, чтобы он не вылезал
class AutoShrinkLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.base_font_size = 36  # Максимальный размер шрифта

    def set_smart_text(self, text):
        self.setText(text)
        self.adjust_font_size()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_size()

    def adjust_font_size(self):
        text = self.text()
        if not text:
            return

        font = QFont(".AppleSystemUIFont", self.base_font_size, QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.SansSerif)

        # Получаем доступную ширину с учетом небольших отступов карточки
        available_width = self.width() - 20
        if available_width <= 0:
            available_width = 240  # Запасной вариант

        # Уменьшаем шрифт, пока текст не влезет в ширину
        current_size = self.base_font_size
        while current_size > 14:
            metrics = QFontMetrics(font)
            if metrics.horizontalAdvance(text) <= available_width:
                break
            current_size -= 2
            font.setPointSize(current_size)

        self.setFont(font)


class Sidebar(QFrame):
    def __init__(self):
        super().__init__()

        self.current_money = 0.0
        self.setFixedWidth(320)

        self.setStyleSheet("""
            QFrame#SidebarContainer {
                background-color: #0B111E;
                border-radius: 24px;
                border: 1px solid #1E293B;
            }
        """)
        self.setObjectName("SidebarContainer")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 32, 24, 32)

        # ==================================
        # ДИНАМИЧЕСКОЕ ПРИВЕТСТВИЕ
        # ==================================
        self.greeting_label = QLabel("")
        self.greeting_label.setStyleSheet("""
            color: #F8FAFC;
            font-size: 18px;
            font-weight: 600;
            font-family: '.AppleSystemUIFont', 'Segoe UI';
        """)
        main_layout.addWidget(self.greeting_label)

        main_layout.addStretch()

        # ==================================
        # ЦЕНТРАЛЬНЫЙ БЛОК: КАРТОЧКА БАЛАНСА
        # ==================================
        self.balance_container = QWidget()
        self.balance_container.setStyleSheet("""
            QWidget#BalanceCard {
                background-color: #151F32;
                border: 2px solid #22314D;
                border-radius: 28px;
            }
        """)
        self.balance_container.setObjectName("BalanceCard")

        balance_layout = QVBoxLayout()
        balance_layout.setContentsMargins(16, 35, 16, 35)
        balance_layout.setSpacing(8)

        subtitle = QLabel("ТЕКУЩИЙ БАЛАНС")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.5px;
            background: transparent;
            font-family: '.AppleSystemUIFont', 'Segoe UI';
        """)

        # Используем наш новый умный лейбл вместо стандартного
        self.balance_label = AutoShrinkLabel("0.00")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balance_label.setStyleSheet("""
            color: #10B981;
            background: transparent;
            font-family: '.AppleSystemUIFont', 'Segoe UI';
        """)

        balance_layout.addWidget(subtitle)
        balance_layout.addWidget(self.balance_label)
        self.balance_container.setLayout(balance_layout)

        self.opacity_effect = QGraphicsOpacityEffect(self.balance_container)
        self.balance_container.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        main_layout.addWidget(self.balance_container)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def update_balance(self, money):
        old_money = self.current_money
        self.current_money = money

        formatted = f"{money:,.2f}".replace(",", " ")
        self.balance_label.set_smart_text(formatted)

        if money > old_money:
            self.balance_label.setStyleSheet(
                "color: #10B981; background: transparent; font-family: '.AppleSystemUIFont';")
        elif money < old_money:
            self.balance_label.setStyleSheet(
                "color: #F43F5E; background: transparent; font-family: '.AppleSystemUIFont';")

        self.animation.start()

    def set_user_greeting(self, username):
        if username:
            self.greeting_label.setText(f"С возвращением, {username}! ✨")
        else:
            self.greeting_label.setText("")