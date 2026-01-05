import requests
import re
import os
import shutil
import subprocess
import imageio_ffmpeg
from requests.exceptions import ChunkedEncodingError

# Config
VIDEO_URL = "https://utexas.app.box.com/s/7jw2z3c2l5521xdz5uvs3m912shbq9ty"
OUTPUT_FILE = "test_video.mp4"
START_SEGMENT = 820
MAX_SEGMENTS = 20

def download_track_test(session, base_url, filename, params):
    print(f"Downloading {filename}...")
    with open(filename, 'wb') as f:
        # 1. Init Segment
        r = session.get(f"{base_url}init.m4s", params=params)
        f.write(r.content)
        
        # 2. Media Segments (Start from START_SEGMENT)
        i = START_SEGMENT
        count = 0
        while count < MAX_SEGMENTS:
            try:
                r = session.get(f"{base_url}{i}.m4s", params=params)
                if r.status_code == 404: 
                    print(f"\nStream ended naturally at {i}")
                    break
                if r.status_code != 200: 
                    print(f"\nStatus {r.status_code} at {i}")
                    break
                    
                f.write(r.content)
                print(f"  Downloaded segment {i}", end='\r')
                i += 1
                count += 1
            except (ChunkedEncodingError, requests.ConnectionError):
                print(f"\nStream ended with connection error at {i}")
                break
    print()

def test_download():
    print(f"Testing download from segment {START_SEGMENT}...")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # 1. Get Token
    page_resp = session.get(VIDEO_URL)
    file_id = re.findall(r'"type":"file","id":(\d+)', page_resp.text)[0]
    request_token = re.findall(r'"requestToken":"(\w+)"', page_resp.text)[0]
    
    session.headers.update({"x-request-token": request_token})
    token_resp = session.post("https://utexas.app.box.com/app-api/enduserapp/elements/tokens", 
                              json={"fileIDs": [file_id]})
    access_token = token_resp.json()[file_id]['read']

    # 2. Get Version
    session.headers.pop("x-request-token")
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    
    versions = re.findall(r'"type":"file_version","id":"(\d+)"', page_resp.text)
    if versions:
        file_version = versions[0]
    else:
        file_version = session.get(f"https://api.box.com/2.0/files/{file_id}?fields=file_version").json()['file_version']['id']

    # 3. Download
    session.headers.pop("Authorization")
    params = {
        "access_token": access_token, 
        "shared_link": VIDEO_URL, 
        "box_client_name": "box-content-preview", 
        "box_client_version": "3.16.0"
    }
    
    base_url = f"https://public.boxcloud.com/api/2.0/internal_files/{file_id}/versions/{file_version}/representations/dash/content"
    
    # Check Resolution
    res = "1080"
    try:
        if session.get(f"{base_url}/video/1080/init.m4s", params=params).status_code != 200:
            res = "480"
    except: res = "480"

    audio_tmp, video_tmp = "test_audio.mp4", "test_video_track.mp4"

    download_track_test(session, f"{base_url}/audio/0/", audio_tmp, params)
    download_track_test(session, f"{base_url}/video/{res}/", video_tmp, params)

    # Merge
    print("Merging...")
    if os.path.exists(video_tmp) and os.path.exists(audio_tmp):
        try:
            subprocess.run([
                imageio_ffmpeg.get_ffmpeg_exe(), "-y", 
                "-i", video_tmp, "-i", audio_tmp, 
                "-c", "copy", "-loglevel", "error", OUTPUT_FILE
            ], check=True)
            print(f"Success! Saved to {OUTPUT_FILE}")
            os.remove(audio_tmp)
            os.remove(video_tmp)
        except Exception as e:
            print(f"Merge failed: {e}")
    else:
        print("Missing track files, skipping merge.")

if __name__ == "__main__":
    test_download()
