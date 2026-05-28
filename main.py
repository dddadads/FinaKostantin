import sys
from PyQt6.QtWidgets import QApplication
from logic.database import init_db

# Сначала создаем структуру таблиц!
init_db()

# А уже потом импортируем и запускаем интерфейс
from ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())