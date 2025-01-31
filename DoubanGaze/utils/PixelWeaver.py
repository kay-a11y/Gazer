import cv2
import os
import re
import numpy as np

def process_image(image_path, target_size):
    """处理单张图片，进行智能裁剪或调整。

    Args:
      image_path(string): 图片路径。
      target_size(tuple): 目标尺寸 (width, height)。

    Returns:
      处理后的图像。
    """

    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to load image: {image_path}")
        return None
    height, width = img.shape[:2]
    target_w, target_h = target_size

    if width == target_w and height == target_h:
        # 尺寸相同，不需要裁剪或调整z
        return img

    if width > target_w or height > target_h:
        # 图片尺寸大于目标尺寸，进行裁剪
        cx, cy = width // 2, height // 2  # 中心点
        x1, y1 = cx - target_w // 2, cy - target_h // 2  # 裁剪区域左上角坐标
        x2, y2 = x1 + target_w, y1 + target_h  # 裁剪区域右下角坐标
        x1, y1 = max(0, x1), max(0, y1) # 确保不超出边界
        x2, y2 = min(width, x2), min(height, y2)

        cropped_img = img[y1:y2, x1:x2]
         # 如果裁剪后的图像尺寸和目标尺寸相差过大，进行一次缩放
        if (cropped_img.shape[1] != target_w) or (cropped_img.shape[0] != target_h) :
          cropped_img = cv2.resize(cropped_img, target_size, interpolation = cv2.INTER_AREA)
        return cropped_img
    else:
       #  如果图片尺寸小于目标尺寸，放大图片
        resized_img = cv2.resize(img, target_size, interpolation = cv2.INTER_CUBIC) # 使用 cv2.INTER_CUBIC
        return resized_img

def extract_date(filename):
    """从文件名中提取日期，用于排序。"""
    match = re.search(r"(\d{4}_\d{2}_\d{2})", filename) # 匹配2024_12_30
    if match:
        return match.group(1)
    else:
        return ""
    
def process_all_images(image_dirs, target_size):
    """处理目录下的所有图片，返回处理后的图片列表。

    Args:
        image_dirs(list): 图片目录列表。
        target_size(tuple): 目标尺寸 (width, height)。

    Returns:
        processed_images(list): 处理后的图片列表。
    """
    processed_images = []
    for image_dir in image_dirs:
        filenames = os.listdir(image_dir)
        # 使用自定义的排序函数，按照日期倒序排列
        filenames.sort(key=extract_date, reverse=True)
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(image_dir, filename)
                processed_image = process_image(image_path, target_size)
                if processed_image is not None:
                    processed_images.append(processed_image)
    return processed_images

def create_collage(processed_images, rows, cols, output_path):
  """创建海报拼接图

    Args:
        processed_images(list): 已经处理好的图片列表
        rows(int):  拼接的行数
        cols(int):  拼接的列数
        output_path(string): 输出图片路径
    """
  num_images = len(processed_images)
  if num_images != rows * cols:
    print(f"图像数量和输入拼接的数量不匹配, 实际图片数量: {num_images}, 输入数量: {rows * cols}")
    

  target_h = processed_images[0].shape[0]
  target_w = processed_images[0].shape[1]
  collage = np.zeros((target_h * rows, target_w * cols, 3), dtype = np.uint8)

  for i in range(num_images):
      row = i // cols
      col = i % cols
      if row >= rows or col >= cols:
          break  # 超出预设的行列范围，停止放置图片
      x = col * target_w
      y = row * target_h
      collage[y:y+target_h, x:x+target_w] = processed_images[i]
  cv2.imwrite(output_path, collage)

# 设置目标尺寸 (width, height) TODO
target_size = (1080, 1600) 

# 设置图片文件夹路径 TODO
image_dirs = [
    # r"E:\Gazer\DoubanGaze\data\poster\2025_1_1_2025_1_31",
    # r"E:\Gazer\DoubanGaze\data\poster\2024_1_1_2024_12_31",
    # r"E:\Gazer\DoubanGaze\data\poster\2023_1_1_2023_12_31",
    # r"E:\Gazer\DoubanGaze\data\poster\2022_1_1_2022_12_31",
    # r"E:\Gazer\DoubanGaze\data\poster\2021_1_1_2021_12_31",
    r"E:\Gazer\DoubanGaze\data\poster\example",
]
# 设置输出图片路径 TODO 一定要写文件名
output_path = r"E:\Gazer\DoubanGaze\data\poster\example.jpg"
# 设置拼接的行和列
rows = 3  # TODO
cols = 3  # TODO

processed_images = process_all_images(image_dirs,  target_size)
if processed_images:
  create_collage(processed_images, rows, cols, output_path)
  print(f"Success, saved in {output_path} 😽")
else:
  print("No images to collage ❓")
