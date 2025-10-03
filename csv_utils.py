import csv
import os
from PySide6.QtWidgets import QFileDialog # QFileDialog 추가

WORDS_FILE_DEFAULT = 'words.csv' # 기본 파일명 변경
MEMORIZED_WORDS_FILE = 'memorized_words.csv'

# 현재 사용 중인 단어 파일 경로를 저장하는 변수
current_words_file = WORDS_FILE_DEFAULT

def set_words_file(file_path):
    """현재 사용할 단어 파일 경로를 설정합니다."""
    global current_words_file
    current_words_file = file_path

def get_words_file():
    """현재 사용 중인 단어 파일 경로를 반환합니다."""
    return current_words_file

def load_words(file_path=None): # file_path 인자 추가
    """CSV 파일에서 단어 데이터를 로드합니다."""
    target_file = file_path if file_path else current_words_file # 인자가 있으면 그 파일을 사용
    
    words_data = []
    if not os.path.exists(target_file):
        print(f"경고: 단어 파일 '{target_file}'을(를) 찾을 수 없습니다.")
        return []

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 첫 번째 줄(헤더) 건너뛰기
            header = next(reader, None) 
            if header is None: # 파일이 비어있는 경우
                return []

            for row in reader:
                if row:
                    word = row[0]
                    meanings = row[1].split(';') if len(row) > 1 and row[1] else []
                    sentences = row[2].split(';') if len(row) > 2 and row[2] else []
                    translations = row[3].split(';') if len(row) > 3 and row[3] else []
                    
                    meanings = [m.strip() for m in meanings if m.strip()]
                    sentences = [s.strip() for s in sentences if s.strip()]
                    translations = [t.strip() for t in translations if t.strip()]

                    words_data.append([word, meanings, sentences, translations])
        return words_data
    except Exception as e:
        print(f"단어 파일 '{target_file}' 로드 중 오류 발생: {e}")
        return []

def save_word(word, meanings, examples, translations):
    """새로운 단어를 CSV 파일에 저장합니다."""
    # 현재 설정된 파일이 없거나 기본 파일이 아닌 경우, 추가 모드가 아니라 덮어쓰기 위험이 있으므로
    # 단어 추가는 기본 WORDS_FILE_DEFAULT에만 하거나, 사용자에게 확인을 받는 것이 좋습니다.
    # 여기서는 기본 파일에만 저장하도록 구현합니다.
    file_exists = os.path.exists(WORDS_FILE_DEFAULT)
    with open(WORDS_FILE_DEFAULT, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 파일이 새로 생성된 경우 헤더를 추가합니다.
        if not file_exists:
            writer.writerow(['word', 'meaning', 'sentence', 'sentence_translation'])
        writer.writerow([
            word,
            ';'.join(meanings),
            ';'.join(examples),
            ';'.join(translations)
        ])

def load_memorized_words_state(for_words_file_path=None): # 외운 단어 상태도 특정 파일에 종속되도록 변경
    """외운 단어 상태를 파일에서 로드합니다."""
    # 각 단어 파일마다 고유한 memorized_words_XXX.csv 파일을 사용
    # 예: words.csv -> memorized_words_words.csv
    # my_words.csv -> memorized_words_my_words.csv
    base_name = os.path.basename(for_words_file_path if for_words_file_path else current_words_file)
    memorized_state_file = f"memorized_words_{base_name}"

    if not os.path.exists(memorized_state_file):
        return {}
    
    memorized_state = {}
    try:
        with open(memorized_state_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) == 2:
                    word = row[0]
                    is_memorized = row[1].lower() == 'true'
                    memorized_state[word] = is_memorized
        return memorized_state
    except Exception as e:
        print(f"외운 단어 상태 파일 '{memorized_state_file}' 로드 중 오류 발생: {e}")
        return {}


def save_memorized_words_state(memorized_state, for_words_file_path=None):
    """외운 단어 상태를 파일에 저장합니다."""
    base_name = os.path.basename(for_words_file_path if for_words_file_path else current_words_file)
    memorized_state_file = f"memorized_words_{base_name}"

    try:
        with open(memorized_state_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for word, is_memorized in memorized_state.items():
                writer.writerow([word, str(is_memorized)])
    except Exception as e:
        print(f"외운 단어 상태 파일 '{memorized_state_file}' 저장 중 오류 발생: {e}")

# 초기 current_words_file이 없을 경우를 대비하여 기본 파일로 설정 시도
if not os.path.exists(WORDS_FILE_DEFAULT):
    try:
        with open(WORDS_FILE_DEFAULT, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['word', 'meaning', 'sentence', 'sentence_translation'])
    except Exception as e:
        print(f"기본 단어 파일 '{WORDS_FILE_DEFAULT}' 생성 중 오류: {e}")