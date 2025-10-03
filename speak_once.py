import sys
import pyttsx3

if len(sys.argv) < 2:
    print("사용법: python test_tts.py \"말할 텍스트\" [선택적_음성_이름]")
    sys.exit(1)

text = sys.argv[1]

# 드라이버 명시 제거
engine = pyttsx3.init() # 'nsspeechsynthesizer' 인자를 제거했습니다.
engine.setProperty("rate", 150)

if len(sys.argv) >= 3:
    voice_name_to_find = sys.argv[2]
    found_voice = False
    for v in engine.getProperty("voices"):
        if voice_name_to_find.lower() in v.name.lower():
            engine.setProperty("voice", v.id)
            found_voice = True
            break
    if not found_voice:
        print(f"경고: '{voice_name_to_find}' 음성을 찾을 수 없습니다. 기본 음성으로 재생합니다.")

engine.say(text)
engine.runAndWait()
engine.stop()