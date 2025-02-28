import requests
from bs4 import BeautifulSoup
import json
import re
import os
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

# ------------------------- CONST ------------------------ #
FOLDER_PATH = r"E:\Gazer\BilibiliGaze\data\raw" # TODO default saving folder
# ------------------------- CONST ------------------------ #

def get_url(cookie, url):
    """get urls from `window.__playinfo__` in HTML

    Args:
        url (str): direct link to Bilibili video

    Returns:
        video_url, audio_url (tuple with 2 strings): request URLs
    """
    headers = {
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", 
        "Cookie": cookie,
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

    play_info_match = re.search(r'window\.__playinfo__\s*=\s*({.*?"video":.*?"audio":.*?"session":.*?})\s*', soup.prettify())

    # initialize video_url & audio_url
    video_url = None
    audio_url = None

    if play_info_match:
        try:
            play_info = json.loads(play_info_match.group(1))
            video_url = play_info['data']['dash']['video'][2]['baseUrl']
            logging.info(f'video_url = {video_url} 📺')
            audio_url = play_info['data']['dash']['audio'][0]['baseUrl']
            logging.info(f'audio_url = {audio_url} 🔉')
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"parse play_info FAILED: {e} ❌")
            return None, None
    else:
        print("window.__playinfo__ NOT FOUND ❓")
    return video_url, audio_url

def download_video(FOLDER_PATH, file_name, request_url):
    """download video/audio files

    Args:
        FOLDER_PATH (str): default saving folder
        file_name (str): file name for video/audio files
        request_url (str): return from `get_url`
    """
    headers = {
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", 
    }

    response = requests.get(request_url, headers=headers, stream=True)

    os.makedirs(FOLDER_PATH, exist_ok=True)
    saving_path = os.path.join(FOLDER_PATH, file_name)

    if response.status_code == 200 or response.status_code == 206:
        with open(f"{saving_path}", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"video/audio part SAVED IN 📂 {saving_path}")
    else:
        print(f"video/audio part download FAILED! 💦")
        print(response.status_code)

if __name__ == '__main__':
    cookie = 'SWEET_COOKIE' # TODO 

    url = "https://www.bilibili.com/video/BV1sp42117UA/?spm_id_from=333.1387.upload.video_card.click&vd_source=8442209456a10c982626f270cd3d9b7c" # TODO
    
    video_file_name = "video.m4s" # TODO give file name 
    audio_file_name = "audio.m4s" # TODO give file name 

    video_url, audio_url = get_url(url)

    if video_url != None and audio_url != None:
        # video
        download_video(FOLDER_PATH, video_file_name, video_url)
        
        # audio
        download_video(FOLDER_PATH, audio_file_name, audio_url)