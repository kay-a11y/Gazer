import os
from pytubefix import YouTube
import subprocess

VIDEO_FOLDER = r"E:\Gazer\YouTube\data\video"

def download_high_quality_video_with_audio(video_url, video_name):
    try:
        yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

        # 1. 获取所有可用流
        streams = yt.streams.filter(adaptive=True)

        # 2. 选择最佳视频流
        best_video_stream = streams.filter(only_video=True).order_by('resolution').desc().first()

        # 3. 选择最佳音频流
        best_audio_stream = streams.filter(only_audio=True).order_by('abr').desc().first()

        if not best_video_stream or not best_audio_stream:
            print("找不到合适的视频流或音频流")
            return

        # 获取视频帧率 (用于 ffmpeg 参数)
        fps = best_video_stream.fps
        print(f"视频帧率: {fps}")

        # 4. 下载视频和音频流
        os.makedirs(VIDEO_FOLDER, exist_ok=True)

        video_path = os.path.join(VIDEO_FOLDER, f"{video_name}_video.mp4")
        audio_path = os.path.join(VIDEO_FOLDER, f"{video_name}_audio.mp4")
        output_path = os.path.join(VIDEO_FOLDER, f"{video_name}.mp4")

        print(f"正在下载视频: {best_video_stream.title} ({best_video_stream.resolution})")
        best_video_stream.download(output_path=VIDEO_FOLDER, filename=f"{video_name}_video.mp4")

        print(f"正在下载音频: {best_audio_stream.title} ({best_audio_stream.abr})")
        best_audio_stream.download(output_path=VIDEO_FOLDER, filename=f"{video_name}_audio.mp4")

        # 5. 合并视频和音频 (使用 ffmpeg, 调整参数)
        print("正在合并视频和音频...")
        try:
            subprocess.run([
                'ffmpeg',
                '-r', str(fps),  
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  
                '-c:a', 'libmp3lame', 
                '-fps_mode', 'vfr',
                output_path 
            ], check=True)

            print(f"合并完成: {video_name}.mp4 已保存到 {VIDEO_FOLDER}")

            # (可选) 删除原始的视频和音频文件
            os.remove(video_path)
            os.remove(audio_path)
        except subprocess.CalledProcessError as e:
            print("合并失败")
            print(e)

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # TODO
    video_name = "a_normal_video"  # TODO

    download_high_quality_video_with_audio(video_url, video_name)

