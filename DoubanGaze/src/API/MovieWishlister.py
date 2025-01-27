from get_item_info import *
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import json, re
import time
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable()

def select_movie_or_book():
    """选择将进入 movie 或者 book 的搜索页面
    Args:
        douban_url (int): 豆瓣用户id.
    Returns:
        string or None: movie or book 搜索页面 url, 否则返回 None, 直到输入正确才返回
    """
    while True:
        select_msg = input('select 1 for movie, 2 for book \n')
        if select_msg == '1':
            douban_search_url = f"https://movie.douban.com/"
            print(f"douban_user_url = {douban_search_url}")
            return douban_search_url
        elif select_msg == '2':
            douban_search_url = f"https://book.douban.com/"
            print(f"douban_user_url = {douban_search_url}")
            return douban_search_url
        elif select_msg.lower() == 'q':
            print("Exiting program...")
            return "q"  # 返回 "q" 表示退出
        else:
            print("Wrong Input, must be 1 or 2 or q")

def is_item_id_recorded(item_id, douban_search_url, 
                        save_path=r"E:\Gazer\DoubanGaze\data\tags"):
    """
    检查 item_id 是否已经记录在 save_path 目录下的文件中。

    Args:
        item_id: 要检查的 item_id。
        douban_search_url: 用于判断是 movie 还是 book
        save_path: 目标目录。

    Returns:
        如果 item_id 已经记录在文件中，返回该文件路径，否则返回 False。
    """
    if not os.path.exists(save_path):  # 检查目录是否存在
        return False
    
    # 分离出 movie 或 book 字符串
    save_key_word = douban_search_url.replace("https://", "").split(".")[0]
    # 构建 movie 或 book 文件夹到路径中
    save_dir = os.path.join(save_path, save_key_word)

    if not os.path.exists(save_dir):
        return False
    
    file_lst = os.listdir(save_dir)
    for filename in file_lst:
        if item_id in filename:
            recorded_file_path = os.path.join(save_dir, filename)
            return recorded_file_path
    return False

def search_sth(cookie, douban_search_url, search_query):
    """模拟登陆, 构造subject_suggest GET请求模拟在搜索栏输入影视/书籍名称.
    找到后检查是否已经添加过想看/想读, 如果有则打印标记的标签和短评, 供后续更新参考;
    按 q 直接退出

    Args:
        cookie (string): 豆瓣 Cookie.
        douban_search_url (string): movie or book 搜索页面 url
        search_query (string): 你要搜索的影视/书籍名称.
    
    Return:
        item_url, item_title, item_id(tuple with 3 strings): (条目地址, 条目名, 条目id)
    """
    
    # 对 search_query 进行 UrlEncode
    encoded_query = quote(search_query)

    # 使用抓包看到的 JavaScript 实际请求的 URL
    add_tags_url = f"{douban_search_url}j/subject_suggest?q={encoded_query}" 

    # simulate headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": douban_search_url,
        # "Referer":"https://movie.douban.com/ OR https://book.douban.com/",
        "Origin": douban_search_url,
        # "Origin": "https://movie.douban.com/ OR https://book.douban.com/"",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookie,
        "X-Requested-With": "XMLHttpRequest"
    }

    # GET request
    response = requests.get(add_tags_url, headers=headers)

    if response.status_code == 200:
        print(f"请求成功")
        try:
            search_result = response.json() # 解析 JSON 响应
            print(json.dumps(search_result, indent=4, ensure_ascii=False))

            # 假设只关心第一个搜索结果
            if search_result:
                first_result = search_result[0]
                item_id = first_result["id"]
                item_title = first_result["title"]
                item_url = f"{douban_search_url}subject/{item_id}/"
                print(f"Movie ID: {item_id}")
                print(f"Movie URL: {item_url}")
                # 检测是否曾经记录过, 如果记录过直接从文件读取, 打印当前的tags, comments, 只是为了方便参照, 然后按照原来的步骤用户输入更新后的完整tags, comments 覆盖即可
                # 检查 item_id 是否已经记录在文件中 
                recorded_file_path = is_item_id_recorded(item_id, 
                            douban_search_url,
                            save_path=r"E:\Gazer\DoubanGaze\data\tags")
                if recorded_file_path:
                    print(f"当前条目已使用脚本标记过wish: {recorded_file_path}")
                    # 读取文件并打印已记录的标签和短评
                    with open(recorded_file_path, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f) # json.load 将文件内容解析为字典
                            print(f"tags: {data.get('tags')}")
                            print(f"comment: {data.get('comment')}")
                        except json.JSONDecodeError:
                            print("文件不是有效的 JSON 格式")
                else:
                    print(f"当前条目未使用脚本标记过wish")

                return item_id, item_title, item_url
            else:
                print("found no info")
                return None, None, None
            
        except json.JSONDecodeError as e:
            print(f"parse json failed")
            print(f"original response: {response.text}")
            return None
    else:
        print(f"请求失败! ❌ 状态码: {response.status_code}")
        print(response.text) # 打印错误信息, 方便调试
        return None

def extract_ck(cookie):
    """从 Cookie 字符串中提取 ck 值"""
    for item in cookie.split(';'):
        if item.strip().startswith('ck='):
            ck = item.split('=', 1)[-1].strip('"')
            return ck
    return None

def write_data(douban_search_url, item_title, item_id, data, 
               save_path=r"E:\Gazer\DoubanGaze\data\tags"):
    """保存想看条目的 data 数据到文件

    Args:
        douban_search_url (string): movie or book 搜索页面 url
        item_title (string): 条目名称
        item_id (string): 条目id
        data (dict): interest POST请求的 data, 即 add_tags(cookie) 函数中的data
        save_path (regexp, optional): 保存路径, 将在这个路径中 (根据条目类型) 创建 movie 或 book 文件夹. Defaults to "E:\\Gazer\\DoubanGaze\\data\\tags".
    """
    # 分离出 movie 或 book 字符串
    save_key_word = douban_search_url.replace("https://", "").split(".")[0]
    # 构建 movie 或 book 文件夹到路径中
    save_dir = os.path.join(save_path, save_key_word)
    # 文件名清洗: 使用正则表达式将多个空格替换为一个空格
    item_title = re.sub(r"\s+", " ", item_title)
    # 构建文件名, 用下划线代替所有空格
    item_title = item_title.replace(" ", "_")
    # 构建文件路径, 保存为 json 格式
    save_path = os.path.join(save_dir, f"{item_title}_{item_id}_wish.json")
    try:
        # 在选定的路径中创建 movie 或 book 文件夹
        os.makedirs(save_dir, exist_ok=True)
        # 'w' 写模式和豆瓣每次更改条目标签的覆盖逻辑符合
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"wish saved in {save_path} 📌")
    except IOError as e:
        print(f"error during saving: {e}")
    except Exception as e:
        print(f"other errors: {e}")

def add_tags(cookie, douban_search_url, item_title, item_id, item_url, 
              my_tags, my_comments):
    """模拟登陆, 构造interest POST请求给找到的影视/书籍添加tags和comments(默认不公开);
        按 q 直接退出
    Args:
        cookie (string): 豆瓣 Cookie.
        douban_search_url: search_sth 函数的返回值之一
        item_title: search_sth 函数的返回值之一
        item_id: search_sth 函数的返回值之一
        item_url: search_sth 函数的返回值之一
        my_tags (string): 你对该条目的完整标签.
        my_comments (string): 你对该条目的完整短评.
    """

    # 使用抓包看到的 JavaScript 实际请求的 URL
    add_tags_url = f"{douban_search_url}j/subject/{item_id}/interest"
    logging.debug(f"add_tags_url = {add_tags_url}, 参考: https://movie.douban.com/j/subject/6952149/interest")

    # simulate headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": item_url,
        "Origin":douban_search_url,
        # "Origin":"https://movie.douban.com OR https://book.douban.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookie,
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
    "ck": extract_ck(cookie),
    "interest": "wish",
    # "rating": "",
    "foldcollect": "F", # 暂时先固定为F
    "tags": my_tags, 
    "comment": my_comments,
    "private": "on", # 要公开标记, 注释掉这行
    }

    response = requests.post(add_tags_url, headers=headers, data=data)

    if response.status_code == 200:
        print(f"请求成功")
        print(response.text) # 打印实际返回内容
        # 如果成功, 当前 data 写入文件
        write_data(douban_search_url, item_title, item_id, data, 
               save_path=r"E:\Gazer\DoubanGaze\data\tags")
    else:
        print(f"请求添加标签或短评失败! ❌ 状态码: {response.status_code}")
        print(response.text) # 打印错误信息, 方便调试
    

if __name__ == "__main__":
    cookie = 'SWEETCOOKIE'

    prompt = "--------------------------\n| 添加想看steps:         |\n| 1.输入你要搜索的内容 🔍| \n| 2.输入更新的完整标签 🏷️ | \n| 3.输入更新的完整短评 ✒️ | \n--------------------------"
    print(prompt)

while True:
        douban_search_url = select_movie_or_book()

        if douban_search_url == "q":
            sys.exit()
        else:
            search_query = input("1. 输入你要搜索的内容 🔍\n")
            if search_query.lower() == "q":
                sys.exit()
            else:
                # 只调用一次 search_sth 函数
                item_id, item_title, item_url = search_sth(cookie, douban_search_url, search_query)

                # 配置 driver
                driver_path = "E:\Gazer\drivers\msedgedriver.exe"
                driver = create_edge_driver(driver_path)
                add_cookies_to_driver(driver, cookie)

                # 输出搜索内容信息
                if "movie" in douban_search_url:
                    get_movie_info(driver, item_url)
                elif "book" in douban_search_url:
                    get_book_info(driver, item_url)

                if douban_search_url is not None:
                    my_tags = input("2. 输入更新的完整标签 🏷️\n")
                    if my_tags.lower() == "q":
                        sys.exit()
                    my_comments = input("3. 输入更新的完整短评 ✒️\n")
                    if my_comments.lower() == "q":
                        sys.exit()
                    else:
                        # 将 search_sth 的返回值传递给 add_tags 函数
                        add_tags(cookie, douban_search_url, item_title, item_id, item_url, my_tags, my_comments)