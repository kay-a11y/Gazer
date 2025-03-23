import os
import requests
from pytubefix import YouTube 

COVER_FOLDER = r"E:\Gazer\YouTube\data\cover"

def get_highest_quality_thumbnail(video_url):
    try:
        yt = YouTube(video_url)
        thumbnail_url = yt.thumbnail_url

        # 检查是否已经是 maxresdefault
        if "maxresdefault.jpg" in thumbnail_url:
            return thumbnail_url

        # 尝试替换为 maxresdefault
        maxres_url = thumbnail_url.replace("hqdefault.jpg", "maxresdefault.jpg").replace("mqdefault.jpg", "maxresdefault.jpg")

        # 检查 maxres_url 是否有效
        response = requests.head(maxres_url) 
        if response.status_code == 200:
            return maxres_url
        else:
            return thumbnail_url 

    except Exception as e:
        print(f"发生错误: {e}")
        return None


if __name__ == "__main__":
    # 视频链接和封面名称
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # TODO
    cover_name = "songs_for_ya" # TODO

    highest_quality_url = get_highest_quality_thumbnail(video_url)

    if highest_quality_url:
        os.makedirs(COVER_FOLDER, exist_ok=True)
        
        print(f"最高清封面链接: {highest_quality_url}")

        # 下载图片
        response = requests.get(highest_quality_url, stream=True)
        if response.status_code == 200:
            cover_path = os.path.join(COVER_FOLDER, cover_name + ".jpg")
            with open(cover_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"最高清封面图片已下载为 {cover_path}")