from gtts import gTTS
import os
import hashlib
from typing import Optional

class TTSService:
    def __init__(self, audio_dir: str = "static/audio"):
        self.audio_dir = audio_dir
        os.makedirs(audio_dir, exist_ok=True)
    
    def generate_audio_filename(self, text: str) -> str:
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{text_hash}.mp3"
    
    async def text_to_speech(self, text: str, lang: str = 'ja') -> Optional[str]:
        try:
            filename = self.generate_audio_filename(text)
            filepath = os.path.join(self.audio_dir, filename)
            
            if os.path.exists(filepath):
                return filename
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(filepath)
            
            return filename
        
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
    
    def get_audio_url(self, filename: str) -> str:
        return f"/static/audio/{filename}"