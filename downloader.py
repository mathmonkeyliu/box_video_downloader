import requests
import re
import os
import shutil
import subprocess
import imageio_ffmpeg
from requests.exceptions import ChunkedEncodingError

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def download_track(session, base_url, filename, params):
    with open(filename, 'wb') as f:
        # Init segment
        try:
            r = session.get(f"{base_url}init.m4s", params=params)
            if r.status_code != 200: return False
            f.write(r.content)
        except Exception:
            return False
        
        # Media segments
        i = 1
        while True:
            try:
                r = session.get(f"{base_url}{i}.m4s", params=params)
                if r.status_code == 404: break
                if r.status_code != 200: break
                f.write(r.content)
                print(f"Downloaded segment {i}", end='\r')
                i += 1
            except (ChunkedEncodingError, requests.ConnectionError):
                # Treat encoding/connection errors at the end of a stream as the end
                print(f"\nStream ended at segment {i}")
                break
            except Exception as e:
                print(f"\nError at segment {i}: {e}")
                break
    print()
    return True

def download_video(video_url, title, output_dir):
    safe_title = sanitize_filename(title)
    output_path = os.path.join(output_dir, f"{safe_title}.mp4")
    
    if os.path.exists(output_path):
        print(f"Skipping {safe_title}")
        return

    print(f"Processing: {safe_title}")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # 1. Get Token
    try:
        page_resp = session.get(video_url)
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
    except Exception as e:
        print(f"Failed to setup download: {e}")
        return

    # 3. Download Streams
    session.headers.pop("Authorization")
    params = {
        "access_token": access_token, 
        "shared_link": video_url, 
        "box_client_name": "box-content-preview", 
        "box_client_version": "3.16.0"
    }
    
    base_url = f"https://public.boxcloud.com/api/2.0/internal_files/{file_id}/versions/{file_version}/representations/dash/content"
    
    res = "1080"
    try:
        if session.get(f"{base_url}/video/1080/init.m4s", params=params).status_code != 200:
            res = "480"
    except: res = "480"

    audio_tmp = f"temp_audio_{safe_title}.mp4"
    video_tmp = f"temp_video_{safe_title}.mp4"

    try:
        download_track(session, f"{base_url}/audio/0/", audio_tmp, params)
        download_track(session, f"{base_url}/video/{res}/", video_tmp, params)

        print("Merging...")
        subprocess.run([
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", 
            "-i", video_tmp, "-i", audio_tmp, 
            "-c", "copy", "-loglevel", "error", output_path
        ], check=True)
        print(f"Saved to {output_path}")

    finally:
        if os.path.exists(audio_tmp): os.remove(audio_tmp)
        if os.path.exists(video_tmp): os.remove(video_tmp)
