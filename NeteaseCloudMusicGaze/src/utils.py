import json
import logging
from typing import List

# 日志配置
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

# 从文件加载停用词列表
def load_stopwords_from_file(filepath):
    """
    从文件中加载停用词列表, 并且转换成集合.

    Args:
        filepath (str): 停用词文件的路径.

    Returns:
        set: 包含所有停用词的集合. 如果文件不存在, 返回空集合.
    """
    stopwords = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stopwords.add(line.strip())
    except FileNotFoundError:
        logging.error(f"停用词文件未找到: {filepath}")
    return stopwords

def load_json_data(filepath):
    """
    从指定的文件路径加载 JSON 数据.

    Args:
        filepath (str): 要加载的 JSON 文件的路径

    Returns:
        dict or list or None: 如果成功加载, 根据 JSON 文件的内容返回一个字典列表.
                              如果文件不存在 / JSON 格式错误 / 加载过程中发生任何
                              错误, 则返回 None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"Successfully loaded data from {filepath}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in: {filepath}")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred during JSON loading: {e}")
        return None

def load_and_extract_text(data_path: str) -> List[str]:
    """
    从 JSON 文件加载数据并提取 title 字段, 将这些值组成一个列表返回

    Args:
        data_path (str): JSON 文件的路径。

    Returns:
        List[str]: 一个包含所有提取出的 "title" 字段值的字符串列表。
                   如果文件不存在 / JSON 格式错误 / 加载过程中发生任何错误
                   / 数据中没有 "title" 字段, 则返回一个空列表
    """
    loaded_data = load_json_data(data_path)
    if loaded_data:
        return [item["title"] for item in loaded_data if item["title"] is not None]
    else:
        return []
