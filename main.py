import sys
from PySide6.QtWidgets import QApplication, QStackedWidget, QPushButton, QVBoxLayout, QWidget
from quiz_ui import TypingQuizWidget
from add_word_ui import AddWordWidget  # 기존 add_word_ui.py 그대로 사용

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("영어 단어 퀴즈 & 단어 추가")

        self.stack = QStackedWidget()
        self.quiz_widget = TypingQuizWidget()
        self.add_widget = AddWordWidget()

        self.stack.addWidget(self.quiz_widget)
        self.stack.addWidget(self.add_widget)

        self.switch_button = QPushButton("단어 추가 화면으로 이동")
        self.switch_button.clicked.connect(self.switch_screen)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addWidget(self.switch_button)
        self.setLayout(layout)

    def switch_screen(self):
        current_index = self.stack.currentIndex()
        if current_index == 0:
            self.stack.setCurrentIndex(1)
            self.switch_button.setText("퀴즈 화면으로 이동")
        else:
            self.stack.setCurrentIndex(0)
            self.switch_button.setText("단어 추가 화면으로 이동")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec())
