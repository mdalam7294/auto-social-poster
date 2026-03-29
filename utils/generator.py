import os
import requests
import uuid
from moviepy.editor import *
from gtts import gTTS
import json

# Hugging Face API key from env
HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')

def generate_images_from_script(scenes, style='cinematic'):
    """
    Generate images for each scene using Hugging Face's Stable Diffusion.
    For simplicity, we use a free inference API (flux or sdxl).
    Returns list of image file paths.
    """
    image_paths = []
    # Use a free model like "stabilityai/stable-diffusion-2-1"
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    for i, scene in enumerate(scenes):
        prompt = f"{style} style, {scene['visual']}"
        payload = {"inputs": prompt}
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            img_path = f"static/temp/img_{uuid.uuid4().hex}.png"
            with open(img_path, 'wb') as f:
                f.write(response.content)
            image_paths.append(img_path)
        else:
            # fallback: solid color image
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), scene['visual'], fill=(255,255,255))
            img_path = f"static/temp/img_{uuid.uuid4().hex}.png"
            img.save(img_path)
            image_paths.append(img_path)
    return image_paths

def text_to_speech_with_elevenlabs(text, voice='en-US'):
    """
    ElevenLabs alternative: use gTTS for free.
    """
    tts = gTTS(text=text, lang='en')
    audio_path = f"static/temp/audio_{uuid.uuid4().hex}.mp3"
    tts.save(audio_path)
    return audio_path

def create_video_from_scenes(scenes, output_path="faceless_video.mp4"):
    """
    Combine images and audio into a video.
    scenes: list of dict with 'duration', 'visual', 'narration'
    """
    clips = []
    for scene in scenes:
        # generate image for this scene
        img_path = generate_images_from_script([scene])[0]  # simplified
        # generate audio for narration
        audio_path = text_to_speech_with_elevenlabs(scene['narration'])
        # create image clip
        img_clip = ImageClip(img_path).set_duration(scene['duration'])
        # audio clip
        audio_clip = AudioFileClip(audio_path)
        # set audio to image clip
        img_clip = img_clip.set_audio(audio_clip)
        clips.append(img_clip)
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

def generate_faceless_video(idea, style='cinematic', duration=60):
    """
    High-level function: takes an idea, generates script, scenes, images, voice, compiles video.
    """
    # 1. Generate script using AI (free Hugging Face model)
    script_api = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    prompt = f"Write a short video script for a faceless video on the topic: {idea}. The script should be in English, with scenes. Each scene should have a visual description and a narration line. Use JSON format: [{{'visual': '...', 'narration': '...', 'duration': 5}}]"
    response = requests.post(script_api, headers=headers, json={"inputs": prompt})
    try:
        scenes = response.json()[0]['generated_text']
        # parse JSON from response (simplified - you may need better parsing)
        scenes = eval(scenes)  # careful
    except:
        # fallback scenes
        scenes = [
            {'visual': 'A person thinking about ' + idea, 'narration': f"Let's explore {idea}.", 'duration': 5},
            {'visual': 'Charts and data', 'narration': 'This is important because...', 'duration': 5}
        ]
    # 2. Generate video
    video_path = f"static/temp/video_{uuid.uuid4().hex}.mp4"
    create_video_from_scenes(scenes, video_path)
    return video_path, scenes
