from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout,
    QMessageBox, QApplication, QCheckBox, QFileDialog # QFileDialog 추가
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont, QKeyEvent
import random
import re
from csv_utils import (
    load_words, load_memorized_words_state, save_memorized_words_state,
    set_words_file, get_words_file, WORDS_FILE_DEFAULT # WORDS_FILE_DEFAULT 추가
)
from tts_utils import speak_text

class TypingQuizWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("영어 단어 퀴즈")

        # 초기 단어 파일 로드 시도
        self._load_and_init_words(get_words_file()) # 함수로 분리

        self.previous_word = None
        self.mode_index = 0
        self.modes = ["뜻→영어", "영어→뜻", "예문→단어"]

        self.sequence_mode_index = 0
        self.sequence_modes = ["랜덤", "순서대로"]
        self.current_word_index = -1 

        self.start_index_label = None
        self.start_index_combo = None
        
        self.current_question_data = None 

        self.setup_ui()
        self.next_question()

    def _load_and_init_words(self, file_path):
        """지정된 파일 경로에서 단어를 로드하고 외운 단어 상태를 초기화합니다."""
        set_words_file(file_path) # 현재 사용할 파일 경로 설정
        self.words_data = load_words(file_path)
        
        if not self.words_data:
            # QMessageBox.critical(self, "오류", f"단어 파일 '{file_path}'을(를) 불러올 수 없거나 비어 있습니다.")
            # 오류 대신 경고를 띄우고 빈 상태로 진행할 수 있도록 변경
            print(f"경고: 단어 파일 '{file_path}'을(를) 불러올 수 없거나 비어 있습니다.")
            self.memorized_state = {}
            # 여기서 퀴즈 요소를 비활성화하는 대신, next_question에서 처리하도록 넘김
            return
        
        self.memorized_state = load_memorized_words_state(file_path)
        for word_info in self.words_data:
            word = word_info[0]
            if word not in self.memorized_state:
                self.memorized_state[word] = False
        
        # 콤보박스 업데이트 (setup_ui 이전에 호출될 경우를 대비)
        if hasattr(self, 'start_index_combo') and self.start_index_combo is not None:
            self.start_index_combo.clear()
            self.start_index_combo.addItems([f"{i+1}. {word[0]}" for i, word in enumerate(self.words_data)])
            # current_word_index를 유효한 범위로 조정
            if self.current_word_index >= len(self.words_data) or self.current_word_index < 0:
                self.current_word_index = 0

    def setup_ui(self):
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        self.mode_toggle = QPushButton(self.modes[self.mode_index])
        self.mode_toggle.setCheckable(True)
        self.mode_toggle.setFont(QFont("Arial", 14))
        self.mode_toggle.clicked.connect(self.toggle_mode)
        top_layout.addWidget(self.mode_toggle)

        self.sequence_mode_toggle = QPushButton(self.sequence_modes[self.sequence_mode_index])
        self.sequence_mode_toggle.setCheckable(True)
        self.sequence_mode_toggle.setFont(QFont("Arial", 14))
        self.sequence_mode_toggle.clicked.connect(self.toggle_sequence_mode)
        top_layout.addWidget(self.sequence_mode_toggle)

        self.start_index_label = QLabel("시작 단어:")
        self.start_index_label.setFont(QFont("Arial", 12))
        top_layout.addWidget(self.start_index_label)

        self.start_index_combo = QComboBox()
        self.start_index_combo.setFont(QFont("Arial", 12))
        self.start_index_combo.addItems([f"{i+1}. {word[0]}" for i, word in enumerate(self.words_data)])
        self.start_index_combo.currentIndexChanged.connect(self.set_start_index_and_reset_quiz)
        top_layout.addWidget(self.start_index_combo)

        tmp_engine = __import__("pyttsx3").init()
        voices = tmp_engine.getProperty("voices")
        tmp_engine.stop()
        self.voice_combo = QComboBox()
        self.voice_combo.setFont(QFont("Arial", 12))
        self.voice_combo.addItems([v.name for v in voices if "english" in v.name.lower()])
        self.voice_combo.setCurrentIndex(0)
        top_layout.addWidget(QLabel("Voice:"))
        top_layout.addWidget(self.voice_combo)

        layout.addLayout(top_layout)

        quiz_options_layout = QHBoxLayout()
        self.hide_memorized_checkbox = QCheckBox("외운 단어 안나오기")
        self.hide_memorized_checkbox.setFont(QFont("Arial", 12))
        self.hide_memorized_checkbox.stateChanged.connect(self.toggle_hide_memorized_words)
        quiz_options_layout.addWidget(self.hide_memorized_checkbox)
        
        # CSV 파일 변경 버튼 추가
        self.change_csv_button = QPushButton("CSV 파일 변경")
        self.change_csv_button.setFont(QFont("Arial", 12))
        self.change_csv_button.clicked.connect(self.change_csv_file)
        quiz_options_layout.addWidget(self.change_csv_button)

        layout.addLayout(quiz_options_layout)

        self.question_label = QLabel("")
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Arial", 18))
        layout.addWidget(self.question_label)

        word_answer_layout = QHBoxLayout()
        self.answer_edit = QLineEdit()
        self.answer_edit.setFont(QFont("Arial", 16))
        self.answer_edit.returnPressed.connect(self.handle_enter)
        self.answer_edit.installEventFilter(self)
        word_answer_layout.addWidget(self.answer_edit)

        self.memorized_toggle_button = QPushButton("외움")
        self.memorized_toggle_button.setCheckable(True)
        self.memorized_toggle_button.setFixedWidth(80)
        self.memorized_toggle_button.setFont(QFont("Arial", 12))
        self.memorized_toggle_button.clicked.connect(self.toggle_memorized_state)
        word_answer_layout.addWidget(self.memorized_toggle_button)
        layout.addLayout(word_answer_layout)

        self.hint_button = QPushButton("힌트 보기")
        self.hint_button.setFont(QFont("Arial", 12))
        self.hint_button.clicked.connect(self.show_hint)
        layout.addWidget(self.hint_button)

        self.hint_label = QLabel("")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setFont(QFont("Arial", 14))
        self.hint_label.setStyleSheet("color: black;")
        layout.addWidget(self.hint_label)

        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.feedback_label)

        button_bottom_layout = QHBoxLayout()

        self.retry_button = QPushButton("다시 풀기")
        self.retry_button.setFont(QFont("Arial", 12))
        self.retry_button.clicked.connect(self.retry_current_question)
        self.retry_button.hide()
        button_bottom_layout.addWidget(self.retry_button)

        self.next_button = QPushButton("다음 문제")
        self.next_button.setFont(QFont("Arial", 12))
        self.next_button.clicked.connect(self.next_question)
        self.next_button.hide()
        button_bottom_layout.addWidget(self.next_button)

        layout.addLayout(button_bottom_layout)
        
        self.setLayout(layout)
        self._update_sequence_ui_visibility()

    def change_csv_file(self):
        """CSV 파일을 선택하고 로드합니다."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("CSV Files (*.csv);;All Files (*)")
        file_dialog.setWindowTitle("단어장 CSV 파일 선택")
        file_dialog.setFileMode(QFileDialog.ExistingFile) # 기존 파일만 선택

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            if selected_file:
                # 새로운 파일 로드 및 초기화
                self._load_and_init_words(selected_file)
                self.reset_quiz_for_new_sequence_mode() # 퀴즈 재설정
                QMessageBox.information(self, "파일 로드", f"'{selected_file}' 파일을 성공적으로 로드했습니다.")
            else:
                QMessageBox.warning(self, "경고", "파일 선택이 취소되었습니다.")

    def eventFilter(self, obj, event):
        if obj is self.answer_edit and event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)

            # 'Shift' 또는 'Ctrl' 키가 눌렸을 때 힌트 보기
            if key_event.key() in [Qt.Key.Key_Shift, Qt.Key.Key_Control]:
                self.show_hint()
                return True
            
            # Backspace 키 처리 (읽기 전용일 때만 동작)
            if key_event.key() == Qt.Key.Key_Backspace and self.answer_edit.isReadOnly():
                self.retry_current_question()
                return True
                
        return super().eventFilter(obj, event)

    def toggle_mode(self):
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.mode_toggle.setText(self.modes[self.mode_index])
        self.next_question()

    def toggle_sequence_mode(self):
        self.sequence_mode_index = (self.sequence_mode_index + 1) % len(self.sequence_modes)
        self.sequence_mode_toggle.setText(self.sequence_modes[self.sequence_mode_index])
        
        self._update_sequence_ui_visibility()
        self.reset_quiz_for_new_sequence_mode()

    def toggle_hide_memorized_words(self):
        self.next_question()

    def toggle_memorized_state(self):
        if self.current_word:
            is_memorized = self.memorized_toggle_button.isChecked()
            # 현재 사용 중인 단어 파일의 경로를 load_memorized_words_state와 save_memorized_words_state에 전달
            self.memorized_state[self.current_word] = is_memorized
            save_memorized_words_state(self.memorized_state, get_words_file())
            self._update_memorized_button_style()
            print(f"'{self.current_word}' 외운 상태: {is_memorized}")
            
            if self.hide_memorized_checkbox.isChecked() and is_memorized:
                self.next_question()

    def _update_memorized_button_style(self):
        if self.current_word and self.memorized_state.get(self.current_word, False):
            self.memorized_toggle_button.setStyleSheet("background-color: lightgreen;")
            self.memorized_toggle_button.setChecked(True)
        else:
            self.memorized_toggle_button.setStyleSheet("")
            self.memorized_toggle_button.setChecked(False)

    def _update_sequence_ui_visibility(self):
        is_sequential_mode = (self.sequence_modes[self.sequence_mode_index] == "순서대로")
        
        if self.start_index_label:
            self.start_index_label.setVisible(is_sequential_mode)
        if self.start_index_combo:
            self.start_index_combo.setVisible(is_sequential_mode)

    def set_start_index_and_reset_quiz(self):
        if self.sequence_modes[self.sequence_mode_index] == "순서대로":
            self.current_word_index = self.start_index_combo.currentIndex()
            self.next_question()

    def reset_quiz_for_new_sequence_mode(self):
        if self.sequence_modes[self.sequence_mode_index] == "랜덤":
            self.current_word_index = -1
            self.previous_word = None
        else: # "순서대로" 모드
            self.current_word_index = self.start_index_combo.currentIndex()
        self.next_question()

    def refresh_words_and_quiz(self):
        # 현재 사용 중인 파일을 다시 로드
        self._load_and_init_words(get_words_file()) 
        self.reset_quiz_for_new_sequence_mode()

    def next_question(self):
        # words_data가 비어있을 경우를 대비
        if not self.words_data:
            self._disable_quiz_elements("단어 파일이 비어 있거나 로드되지 않았습니다.")
            return

        available_words_data_with_original_index = []
        for i, word_info in enumerate(self.words_data):
            word = word_info[0]
            if not self.hide_memorized_checkbox.isChecked() or not self.memorized_state.get(word, False):
                available_words_data_with_original_index.append((i, word_info))
        
        if not available_words_data_with_original_index:
            self._disable_quiz_elements("모든 단어를 외웠거나, 필터링 조건에 맞는 단어가 없습니다.")
            return

        if self.sequence_modes[self.sequence_mode_index] == "랜덤":
            _, word_data = random.choice(available_words_data_with_original_index)
        else: # "순서대로" 모드
            found_word = False
            start_search_original_index = self.current_word_index
            
            for _ in range(len(self.words_data) + 1): # 모든 단어를 검색할 수 있도록 +1
                if self.current_word_index >= len(self.words_data):
                    self.current_word_index = 0 # 인덱스 초과 시 처음부터 다시

                current_original_word_info = self.words_data[self.current_word_index]
                current_word_name = current_original_word_info[0]

                if not self.hide_memorized_checkbox.isChecked() or not self.memorized_state.get(current_word_name, False):
                    word_data = current_original_word_info
                    found_word = True
                    self.current_word_index = (self.current_word_index + 1) % len(self.words_data)
                    break
                else:
                    self.current_word_index = (self.current_word_index + 1) % len(self.words_data)
                    if self.current_word_index == start_search_original_index:
                        # 한 바퀴 돌았는데도 못 찾았으면 종료
                        break
            
            if not found_word:
                self._disable_quiz_elements("모든 단어를 외웠거나, 필터링 조건에 맞는 단어가 없습니다.")
                return

        self.current_question_data = word_data
        self._load_question_ui(word_data)

    def retry_current_question(self):
        if self.current_question_data:
            self._load_question_ui(self.current_question_data)
        else:
            self.next_question()

    def _load_question_ui(self, word_data):
        word, meanings, sentences, translations = word_data
        self.previous_word = word
        self.current_word = word
        self.current_meanings = meanings
        self.current_sentences = sentences
        # translations는 일반적으로 리스트 형태이므로, 번역 힌트로 사용할 첫 번째 요소만 저장합니다.
        self.current_translations = translations # 원본 리스트는 유지
        
        # 힌트 레이블은 항상 초기화
        self.hint_label.setText("") 
        self.feedback_label.setText("")
        self.next_button.hide()
        self.retry_button.hide()
        self.answer_edit.setReadOnly(False)
        self.answer_edit.clear()
        self.answer_edit.setFocus()
        self._update_memorized_button_style()

        if self.modes[self.mode_index] == "예문→단어" and self.current_sentences:
            self.hint_button.show()
            idx = random.randint(0, len(self.current_sentences)-1)
            sentence = self.current_sentences[idx]
            
            # 여기서 번역 힌트를 current_translation_selected에 정확히 저장합니다.
            # translations 리스트에 여러 번역이 있을 수 있으므로, 어떤 것을 보여줄지 결정합니다.
            # 일단 첫 번째 번역만 보여주는 것으로 가정합니다.
            selected_translation = translations[idx] if translations and idx < len(translations) else ""
            self.current_sentence_selected = sentence
            self.current_translation_selected = selected_translation 
            
            # 이 부분은 '문제'를 표시하는 로직입니다. 힌트를 표시하는 부분이 아닙니다.
            # 빈칸을 채울 단어의 첫 글자만 보여주는 마스킹 처리입니다.
            hint_char = self.current_word[0] if self.current_word else ''
            masked_placeholder = hint_char + "_" * (len(self.current_word)-1)
            
            # re.IGNORECASE를 사용하여 대소문자 무시
            masked_word_pattern = re.compile(re.escape(self.current_word), re.IGNORECASE)
            
            question_text = sentence
            if masked_word_pattern.search(sentence):
                # 찾은 단어를 (__)로 대체 (첫 번째 일치만)
                question_text = masked_word_pattern.sub(f"({masked_placeholder})", sentence, 1)
            else:
                question_text = f"{sentence}\n\n({masked_placeholder})"

            self.question_label.setText(f"다음 문장의 빈칸을 채우세요:\n\n➡ {question_text}")
            self.answer_edit.setPlaceholderText("빈칸에 들어갈 영어 단어 입력 후 Enter")
        else:
            self.hint_button.hide() # 예문 모드가 아니면 힌트 버튼 숨기기
            if self.modes[self.mode_index] == "뜻→영어":
                all_meanings = "; ".join(self.current_meanings)
                self.question_label.setText(f"다음 뜻의 영어 단어는?\n\n➡ {all_meanings}")
                self.answer_edit.setPlaceholderText("영어 단어 입력 후 Enter")
            else: # "영어→뜻" 모드
                self.question_label.setText(f"다음 영어 단어의 뜻은?\n\n➡ {self.current_word}")
                self.answer_edit.setPlaceholderText("뜻(한국어) 입력 후 Enter")

    def _disable_quiz_elements(self, message):
        self.question_label.setText(message)
        self.answer_edit.setEnabled(False)
        self.hint_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.retry_button.setEnabled(False)
        self.memorized_toggle_button.setEnabled(False)

    def show_hint(self):
        if self.modes[self.mode_index] == "예문→단어" and getattr(self, "current_translation_selected", None):
            self.hint_label.setText(self.current_translation_selected)

    def handle_enter(self):
        if not self.answer_edit.isReadOnly():
            self.show_answer()
        else:
            self.next_question() 

    def _normalize_text_for_comparison(self, text):
        """텍스트에서 특수문자를 제거하고 공백을 정규화합니다."""
        # 3. 정답에 ~이나 __ 같은게 있거나 없어도 정답 처리
        # 한글, 영어, 숫자만 남기고 제거 (공백은 그대로 둠)
        # ^(한글 범위)|^(영어 알파벳)|^(숫자)|^(공백)
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text) 
        text = text.lower().strip() # 소문자 변환 및 양쪽 공백 제거
        text = re.sub(r'\s+', ' ', text) # 여러 공백을 하나의 공백으로
        return text

    def show_answer(self):
        user_answer_raw = self.answer_edit.text().strip()
        if not user_answer_raw:
            return

        user_answer_normalized = self._normalize_text_for_comparison(user_answer_raw)
        mode = self.modes[self.mode_index]
        is_correct = False
        correct_info = ""

        if mode in ["뜻→영어", "예문→단어"]:
            correct_word_normalized = self._normalize_text_for_comparison(self.current_word)
            
            # 2. 예문 정답 작성 시 예문에 있는 모든 문장을 작성해도 정답 처리
            if mode == "예문→단어" and hasattr(self, "current_sentence_selected"):
                # 사용자가 입력한 내용이 원문 예문 (대소문자 및 특수문자 무시)과 같으면 정답 처리
                current_sentence_normalized = self._normalize_text_for_comparison(self.current_sentence_selected)
                if user_answer_normalized == current_sentence_normalized:
                    is_correct = True
                    correct_info = self.current_word # 정답 표시는 원래 단어로
                elif user_answer_normalized == correct_word_normalized: # 단어만 입력해도 정답
                    is_correct = True
                    correct_info = self.current_word
                else:
                    is_correct = False
                    correct_info = self.current_word # 오답 시에는 원래 단어 표시
            else: # 뜻→영어 모드 또는 예문인데 문장 일치 안되는 경우
                is_correct = user_answer_normalized == correct_word_normalized
                correct_info = self.current_word
                
        else: # "영어→뜻" 모드 (한국어 뜻)
            normalized_user_answer = self._normalize_text_for_comparison(user_answer_raw)
            normalized_meanings = [self._normalize_text_for_comparison(m) for m in self.current_meanings]
            is_correct = normalized_user_answer in normalized_meanings
            correct_info = ", ".join(self.current_meanings)

        if is_correct:
            self.feedback_label.setText(f"✅ 정답! ({correct_info})")
        else:
            self.feedback_label.setText(f"❌ 오답!\n입력: {user_answer_raw}\n정답: {correct_info}")

        self.answer_edit.setReadOnly(True) 
        self.next_button.show()
        self.retry_button.show()

        if mode == "예문→단어":
            text_to_speak = getattr(self, "current_sentence_selected", self.current_word)
        else:
            text_to_speak = self.current_word

        speak_text(text_to_speak, self.voice_combo.currentText())