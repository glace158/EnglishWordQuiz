# simple_tts_test.py
import pyttsx3

try:
    # 드라이버를 명시적으로 지정해봅니다.
    engine = pyttsx3.init('nsspeechsynthesizer') 
    
    # 설치된 모든 음성 목록을 출력하여 어떤 음성을 사용할 수 있는지 확인합니다.
    voices = engine.getProperty('voices')
    print("사용 가능한 음성:")
    for voice in voices:
        print(f"- ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")
        # 영어 음성을 찾아서 설정해 볼 수 있습니다.
        if "com.apple.speech.synthesis.voice.alex" in voice.id: # Alex 음성 ID (macOS 기본)
            engine.setProperty('voice', voice.id)
            print(f"-> Alex 음성으로 설정됨: {voice.name}")

    engine.say("Hello, this is a test from PyTTSX3 on macOS.")
    engine.runAndWait()
    engine.stop()
    print("음성 재생 완료.")

except Exception as e:
    print(f"TTS 오류 발생: {e}")
    import traceback
    traceback.print_exc()