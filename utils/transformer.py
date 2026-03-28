import whisper
import os
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip
import requests

# For translation, we'll use a free API (MyMemory or Google Translate via requests)
def translate_text(text, target_lang='en'):
    # Simple free translation using MyMemory API (no key required, but limited)
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=auto|en"
        response = requests.get(url)
        data = response.json()
        return data['responseData']['translatedText']
    except:
        return text

def extract_audio(video_path, audio_path="temp_audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()
    return audio_path

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def text_to_speech(text, lang='en', output="new_voice.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(output)
    return output

def replace_audio(video_path, new_audio_path, output_path="final_video.mp4"):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(new_audio_path)
    final = video.set_audio(audio)
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')
    return output_path

def recreate_video(original_url, output_path="final_video.mp4"):
    # Step 1: download
    video_file = download_video(original_url)
    # Step 2: extract audio
    audio_file = extract_audio(video_file)
    # Step 3: transcribe
    transcript = transcribe_audio(audio_file)
    # Step 4: translate to English (if needed)
    translated = translate_text(transcript)
    # Step 5: generate new voiceover
    new_audio = text_to_speech(translated)
    # Step 6: replace audio
    final_video = replace_audio(video_file, new_audio, output_path)
    # Cleanup temp files (optional)
    os.remove(video_file)
    os.remove(audio_file)
    os.remove(new_audio)
    return final_video
