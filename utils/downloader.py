import subprocess
import os

def download_video(url, output_path="temp_video.mp4"):
    """Download video from any platform using yt-dlp"""
    try:
        cmd = ["yt-dlp", "-f", "best", "-o", output_path, url]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")
