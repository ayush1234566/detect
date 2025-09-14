import speech_recognition as sr
import os
import pyttsx3
from pathlib import Path

class SpeechModel:
    """Simple Speech Recognition Model using SpeechRecognition library"""
    
    def __init__(self):
        print("Initializing Speech Recognition Model...")
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        
        # Try to get default microphone
        try:
            self.microphone = sr.Microphone()
            print("✅ Microphone initialized successfully")
        except Exception as e:
            print(f"⚠️ Microphone initialization warning: {e}")
            
        print("✅ Speech Recognition Model ready!")
    
    def transcribe_audio_file(self, audio_file_path):
        """Transcribe an audio file to text"""
        try:
            if not os.path.exists(audio_file_path):
                return f"Error: Audio file {audio_file_path} not found"
            
            print(f"Transcribing audio file: {audio_file_path}")
            
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech using Google's free API
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}"
        except Exception as e:
            return f"Error processing audio file: {e}"
    
    def listen_from_microphone(self, timeout=5):
        """Listen to microphone and convert to text"""
        if not self.microphone:
            return "Error: No microphone available"
        
        try:
            print("Listening from microphone...")
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                print("Say something!")
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.WaitTimeoutError:
            return "No speech detected within timeout"
        except sr.UnknownValueError:
            return "Could not understand the speech"
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}"
        except Exception as e:
            return f"Error accessing microphone: {e}"
    
    def text_to_speech(self, text, save_to_file=None):
        """Convert text to speech"""
        try:
            if save_to_file:
                self.tts_engine.save_to_file(text, save_to_file)
                self.tts_engine.runAndWait()
                return f"Speech saved to {save_to_file}"
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return "Speech played successfully"
        except Exception as e:
            return f"Error with text-to-speech: {e}"
    
    def get_available_engines(self):
        """Get available TTS engines and microphone info"""
        try:
            engines_info = {
                "tts_engines": [],
                "microphone_available": self.microphone is not None,
                "speech_recognition_ready": True
            }
            
            # Get TTS engine info
            try:
                voices = self.tts_engine.getProperty('voices')
                for i, voice in enumerate(voices):
                    engines_info["tts_engines"].append({
                        "id": voice.id,
                        "name": voice.name,
                        "gender": getattr(voice, 'gender', 'Unknown'),
                        "age": getattr(voice, 'age', 'Unknown')
                    })
            except:
                engines_info["tts_engines"] = ["Default TTS Engine"]
            
            return engines_info
            
        except Exception as e:
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    print("🎤 Speech Recognition Model Test")
    print("=" * 50)
    
    # Initialize the model
    model = SpeechModel()
    
    # Test text-to-speech
    print("\n🔊 Testing Text-to-Speech...")
    result = model.text_to_speech("Hello! Speech recognition model is working perfectly.")
    print(f"TTS Result: {result}")
    
    # Test audio file transcription (if file exists)
    test_audio_files = ["2086-149220-0033.wav", "test.wav", "audio.wav", "speech.wav"]
    for audio_file in test_audio_files:
        if os.path.exists(audio_file):
            print(f"\n📁 Testing audio file: {audio_file}")
            transcription = model.transcribe_audio_file(audio_file)
            print(f"Transcription: {transcription}")
            break
    else:
        print("\n📁 No test audio files found")
    
    print("\n✅ Model testing completed!")
    print("🎉 Your speech recognition model is ready for the Flask backend!")
