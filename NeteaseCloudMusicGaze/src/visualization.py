from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os
from typing import List, Dict
import csv
from src.utils import load_json_data, load_and_extract_text, load_stopwords_from_file

# 常量定义
WORD_HEADER = "Word"
FREQUENCY_HEADER = "Frequency"
DEFAULT_FONT_PATH = "msyh.ttc"  # 字体路径
TITLE_STOPWORDS_PATH = r"E:\Gazer\NeteaseCloudMusicGaze\data\title_stopwords.txt"


def generate_wordcloud(text_list, output_path, stopwords=None):
    """
    根据文本列表生成词云图, 并返回词频字典

    Args:
        text_list (List[str]): `load_and_extract_text` 函数
                                返回的文本列表, 用于生成词云
        output_path (str): 生成的词云图的保存路径
        stopwords (set, optional): 可选参数, 一个包含停用词的集合.
            如果未提供此参数, 则使用 wordcloud 库的默认停用词列表.
            Defaults to None.

    Returns:
        Dict[str, float]: 一个字典, 表示词云中每个词及其对应的频率。
            键是词云中的词, 值是该词在文本中出现的频率（已归一化）。
    """
    text = " ".join(text_list)
    if stopwords is None:
        stopwords = set(STOPWORDS)
        # 从文件加载 title stopwords
        title_stopwords = load_stopwords_from_file(TITLE_STOPWORDS_PATH)
        stopwords.update(title_stopwords)

    wordcloud = WordCloud(
        width=960,   # 词云图宽度(px), 默认为 400
        height=600,  # 词云图高度(px), 默认为 200
        background_color=None,  # 设置背景颜色为透明, 或自定义如"white", "#000000", "(0,0,40)", 默认为 "black"
        stopwords=stopwords,
        font_path=DEFAULT_FONT_PATH,
        max_words=200,              # 词云图中显示的最大词数, 默认为 200
        max_font_size=100, # 词云图中最大的字体大小, 默认为None, 表示自动根据词频调整
        random_state=42,   # 随机数种子, 用于控制词云图的布局, 设置相同的值可以得到相同的布局 "The Answer to the Ultimate Question of Life, the Universe, and Everything is 42"
        mode="RGBA"        # 颜色模式，"RGB" 或 "RGBA"，默认为 "RGB" 
    )

    wordcloud.generate(text)
    wordcloud.to_file(output_path)
    return wordcloud.words_

def save_word_frequencies_to_csv(word_frequencies, csv_output_path):
    """
    将词频字典保存到 CSV 文件

    Args:
        word_frequencies (Dict[str, float]): 一个字典, 包含词语及其频率.
            键是词语 (str), 值是频率 (float)
        csv_output_path (str): CSV 文件的保存路径

    Returns:
        None: 不返回任何值. 将词频数据写入到指定的 CSV 文件中
    """
    with open(csv_output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([WORD_HEADER, FREQUENCY_HEADER])
        for word, frequency in word_frequencies.items():
            writer.writerow([word, frequency])

def visualize_keywords(data_path, output_dir):
    """
    统筹以上 2 个函数, 可视化关键词数据, 生成词云图并保存词频到 CSV 文件

    Args:
        data_path (str): 处理后的数据文件的路径, 应为 JSON 格式
        output_dir (str): 输出目录的路径, 用于保存生成的词云图和 CSV 文件

    Returns:
        None: 不返回任何值. 生成一个词云图并将其保存在 output_dir 中, 
              同时生成一个包含词频的 CSV 文件也保存在 output_dir 中
    """
    os.makedirs(output_dir, exist_ok=True)
    text_list = load_and_extract_text(data_path)
    if not text_list:
        print(f"无法从 {data_path} 中提取数据")
        return

    base_filename = os.path.basename(data_path).split('.')[0]
    wordcloud_output_path = os.path.join(output_dir, f"wordcloud_{base_filename}.png")
    csv_output_path = os.path.join(output_dir, f"word_frequencies_{base_filename}.csv")

    word_frequencies = generate_wordcloud(text_list, wordcloud_output_path, stopwords=None)
    save_word_frequencies_to_csv(word_frequencies, csv_output_path)

# if __name__ == "__main__":
#     # 移动到 main.py 中执行
#     pass
