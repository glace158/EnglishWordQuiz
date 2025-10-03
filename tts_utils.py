import pyttsx3
import threading
import time # sleep을 위해 추가

def speak_text(text, voice_name=None, rate=150):
    def run():
        engine = None # 초기화
        try:
            # 드라이버 명시 제거 (이전 답변에서 제안했던 대로)
            engine = pyttsx3.init() 
            engine.setProperty("rate", rate)
            
            if voice_name:
                found_voice = False
                voices = engine.getProperty("voices")
                for v in voices:
                    if voice_name.lower() in v.name.lower(): 
                        engine.setProperty("voice", v.id)
                        found_voice = True
                        break
                if not found_voice:
                    print(f"경고: TTS 음성 '{voice_name}'을(를) 찾을 수 없습니다. 기본 음성으로 재생합니다.")
            
            engine.say(text)
            engine.runAndWait()
            
            # 여기서 engine.stop()을 호출하지 않거나, 잠시 대기 후 호출해보세요.
            # 매우 짧은 음성에서 문제가 생긴다면, 이 줄을 아예 제거해보는 것도 한 방법입니다.
            # engine.stop() # 이 줄을 제거하거나, 아래처럼 잠시 대기 추가
            
            # 짧은 대기 시간을 추가하여 엔진이 완전히 종료되기 전에 음성이 재생되도록 보장
            # time.sleep(0.1) # 필요시 추가

        except Exception as e:
            print(f"TTS 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if engine:
                # 스레드가 종료될 때 엔진을 확실히 종료 (이 부분은 유지하는 것이 좋습니다)
                engine.stop() 

    threading.Thread(target=run, daemon=True).start()