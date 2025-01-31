import cv2
import os

def compress_image_cv2(input_path, output_path, target_size_mb=10, max_width=None, max_height=None):
    """使用 OpenCV 压缩图片到指定大小 (MB) 以下, 可选地调整最大宽度和高度。

    Args:
        input_path (str): 输入图片路径。
        output_path (str): 输出图片路径。
        target_size_mb (float): 目标大小 (MB)。
        max_width (int, optional): 最大宽度。如果设置了, 且图片宽度超过此值, 则会按比例缩放. 默认为 None.
        max_height (int, optional): 最大高度。如果设置了, 且图片高度超过此值, 则会按比例缩放. 默认为 None.
    """
    try:
        image = cv2.imread(input_path)
        height, width = image.shape[:2]

        # 调整尺寸
        if max_width is not None and width > max_width:
            scale = max_width / width
            width = max_width
            height = int(height * scale)
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

        if max_height is not None and height > max_height:
            scale = max_height / height
            height = max_height
            width = int(width * scale)
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

        quality = 100
        while True:
            # 构建临时文件名
            temp_output_path = os.path.join(os.path.dirname(output_path), "temp_" + os.path.basename(output_path))

            # 压缩图片
            cv2.imwrite(temp_output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])

            # 检查文件大小
            file_size_mb = os.path.getsize(temp_output_path) / (1024 * 1024)

            print(f"Quality: {quality}, Size: {file_size_mb:.2f} MB")

            if file_size_mb <= target_size_mb:
                # 移动临时文件到最终输出路径
                os.replace(temp_output_path, output_path)
                print(f"图片压缩成功，输出路径：{output_path}")
                break
            elif quality <= 5:
                print("警告：质量已降至极低，可能无法满足目标大小。")
                os.replace(temp_output_path, output_path)
                break
            else:
                quality -= 5
                
    except FileNotFoundError:
        print(f"找不到文件：{input_path}")
    except Exception as e:
        print(f"压缩图片出错：{e}")

# ------------------------------------ run ----------------------------------- 
input_image = r"E:\Gazer\DoubanGaze\data\poster\movie_2025-2021.jpg"  # 替换为你的输入图片路径
output_image = r"E:\Gazer\DoubanGaze\data\poster\movie_2025-2021_compressed.jpg"  # 替换为你想要的输出图片路径
compress_image_cv2(input_image, output_image, target_size_mb=10, max_width=1600)  # 目标大小为 10MB 以下, 最大宽度为1600
