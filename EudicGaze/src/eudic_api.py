import requests
import base64
import urllib.parse
import json
from bs4 import BeautifulSoup
from pprint import pprint

def build_status_parameter(word, context, tag_number=1):
    """
    构建 status 参数。

    Args:
        word: 要查询的单词。
        context: 上下文句子。
        tag_number: 标签编号，1-11 分别代表：
            语境、例句、助记、词根、词源、搭配、同义词、形近词、替换、单词新解、派生词。
            默认为 1（语境）。如果没有 context，则默认为 2（例句）。

    Returns:
        构建好的 status 参数字符串。
    """

    tag_mapping = {
        1: "语境",
        2: "例句",
        3: "助记",
        4: "词根",
        5: "词源",
        6: "搭配",
        7: "同义词",
        8: "形近词",
        9: "替换",
        10: "单词新解",
        11: "派生词",
    }

    if not context:
        tag_number = 2  # 如果没有 context，则默认为例句

    tag = tag_mapping.get(tag_number, "语境")  # 默认为语境

    # 构建 status 的前缀
    status_prefix = "xxx"

    # 对 word 进行 Base64 编码
    encoded_word = base64.b64encode(word.encode("utf-8")).decode("utf-8")

    # 构建 word 部分
    word_part = f"{word}+ACI-"

    # 构建 context 部分
    if context:
        context_part = f"+ACI-context+ACI-:+ACI-{context}+ACI-"
    else:
        context_part = ""

    # 拼接 word_part 和 context_part
    middle_part = f"{word_part},{context_part}"

    # Base64 编码并去除填充符
    encoded_middle_part = base64.b64encode(middle_part.encode("utf-8")).decode("utf-8").rstrip("=")

    # 构建 status 的前缀
    status_prefix = "xxx"

    # 构建 status 的其余部分
    status_suffix = "xxx"

    # 拼接 status 参数
    status = f"{status_prefix}{encoded_middle_part}{status_suffix}"

    return status, tag


def send_ai_explain_request(word, context, tag_number=1):
    """
    发送 AI 解释请求。

    Args:
        word: 要查询的单词。
        context: 上下文句子。
        tag_number: 标签编号。

    Returns:
        服务器的响应内容。
    """

    url = "https://dict.eudic.net/dicts/AiExplainTabStream"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "SWEET_COOKIE"  # Replace with your actual Cookie
    }

    status, tag = build_status_parameter(word, context, tag_number)
    data = {
        "status": status,
        "tag": f"#{tag}" 
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        decoded_response = response.content.decode("utf-8")
        try:
            result_json = json.loads(decoded_response)
            if result_json['code'] == 200:
                html_content = result_json['data']['result']
                
                # 使用 Beautiful Soup 解析 HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text()

                # 替换转义字符
                text_content = text_content.replace("&#39;", "'").replace("&quot;", "\"")

                return text_content
            else:
                return f"AI 解释失败，错误信息：{result_json['message']}"
        except json.JSONDecodeError:
            return f"JSON 解析失败，原始响应内容：{decoded_response}"
    else:
        return f"请求失败，状态码：{response.status_code}"
    
# 测试
word = "world"
context = "Hello world"
tag_number = 1  # 1: "语境" 2: "例句", 3: "助记", 4: "词根", 5: "词源", 6: "搭配", 7: "同义词", 8: "形近词", 9: "替换", 10: "单词新解", 11: "派生词"

result = send_ai_explain_request(word, context, tag_number)
print(result) # 适用于 1
# pprint(result) # 适用于 2-11
