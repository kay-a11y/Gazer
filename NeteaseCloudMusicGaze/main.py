from src.visualization import visualize_keywords
import os

if __name__ == "__main__":
    # 使用相对路径
    data_path = r"E:\Gazer\NeteaseCloudMusicGaze\data\raw\me_music_data.json"
    output_dir = r"E:\Gazer\NeteaseCloudMusicGaze\output\visualizations"
    visualize_keywords(data_path, output_dir)
