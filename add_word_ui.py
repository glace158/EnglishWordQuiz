from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont
from csv_utils import save_word

class AddWordWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("단어 추가")
        self.entry_list=[]
        self.setup_ui()

    def setup_ui(self):
        self.main_layout=QVBoxLayout(self)
        # 상단
        title=QLabel("영어 단어")
        title.setFont(QFont("Arial",18))
        self.main_layout.addWidget(title)

        self.word_input=QLineEdit()
        self.word_input.setFont(QFont("Arial",14))
        self.word_input.setPlaceholderText("영어 단어 입력")
        self.main_layout.addWidget(self.word_input)

        self.entries_layout=QVBoxLayout()
        self.main_layout.addLayout(self.entries_layout)

        self.add_entry_row()
        self.add_button=QPushButton("추가 항목 +")
        self.add_button.clicked.connect(self.add_entry_row)
        self.main_layout.addWidget(self.add_button)

        bottom_layout=QHBoxLayout()
        self.save_button=QPushButton("저장")
        bottom_layout.addWidget(self.save_button)
        self.to_quiz_button=QPushButton("퀴즈 화면으로 이동")
        bottom_layout.addWidget(self.to_quiz_button)
        self.main_layout.addLayout(bottom_layout)

    def add_entry_row(self):
        row_widget=QWidget()
        row_layout=QHBoxLayout(row_widget)
        meaning_input=QLineEdit()
        meaning_input.setPlaceholderText("뜻")
        example_input=QLineEdit()
        example_input.setPlaceholderText("예문")
        translation_input=QLineEdit()
        translation_input.setPlaceholderText("예문 번역")
        del_button=QPushButton("삭제")
        del_button.setFixedWidth(60)
        def remove_row():
            if len(self.entry_list)>1:
                self.entries_layout.removeWidget(row_widget)
                row_widget.deleteLater()
                self.entry_list.remove((meaning_input,example_input,translation_input,del_button))
        del_button.clicked.connect(remove_row)
        row_layout.addWidget(meaning_input)
        row_layout.addWidget(example_input)
        row_layout.addWidget(translation_input)
        row_layout.addWidget(del_button)
        self.entries_layout.addWidget(row_widget)
        self.entry_list.append((meaning_input,example_input,translation_input,del_button))

    def save_word_to_csv(self):
        word=self.word_input.text().strip()
        meanings, examples, translations=[],[],[]
        for m,e,t,_ in self.entry_list:
            m_val,e_val,t_val=m.text().strip(),e.text().strip(),t.text().strip()
            if m_val:
                meanings.append(m_val)
                examples.append(e_val)
                translations.append(t_val)
        if word and meanings:
            save_word(word,meanings,examples,translations)
            self.word_input.clear()
            for m,e,t,_ in self.entry_list:
                m.clear()
                e.clear()
                t.clear()
