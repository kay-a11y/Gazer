import requests
from bs4 import BeautifulSoup
import time
import os, json, sys

# 全局变量
DOUBAN_USER_ID = YOUR_DOUBAN_USER_ID  # MY 豆瓣 User ID

def select_movie_or_book(douban_userid=DOUBAN_USER_ID):
    """选择将进入 movie 或者 book 的标签页面
    Args:
        douban_url (int): 豆瓣用户id.
    Returns:
        tuple or None: (douban_search_url, movie or book 页面 url), 否则返回 None, 直到输入正确才返回
    """
    while True:
        select_msg = input('select 1 for movie, 2 for book \n')
        if select_msg == '1':
            douban_search_url = f"https://movie.douban.com/"
            douban_user_url = f"https://movie.douban.com/people/{douban_userid}/all"
            print(f"douban_user_url = {douban_user_url}")
            return douban_search_url, douban_user_url
        elif select_msg == '2':
            douban_search_url = f"https://book.douban.com/"
            douban_user_url = f"https://book.douban.com/people/{douban_userid}/all"
            print(f"douban_user_url = {douban_user_url}")
            return douban_search_url, douban_user_url
        elif select_msg == 'q':
            print("Exiting program...")
            sys.exit()  # 返回 "q" 表示退出
        else:
            print("Wrong Input, must be 1 or 2 or q")
    
def extract_ck(cookie):
    """从 Cookie 字符串中提取 ck 值"""
    for item in cookie.split(';'):
        if item.strip().startswith('ck='):
            ck = item.split('=', 1)[-1].strip('"')
            return ck
    return None

def get_all_tags(douban_user_url):
    """获取响应中HTML中的所有标签, 提取标签, 按照1, 2, 3 添加序号并排序, 并返回标签字典. 将所有标签更新在 "E:\\Gazer\\DoubanGaze\\data\\tags" 的 my_book_tags.json 或 my_movie_tag.json 中
    Args:
        douban_user_url (string): 豆瓣用户页面的 URL

    Returns:
        dict: 标签字典, 键为序号, 值为标签信息(包含标签名和数量)
    """
    # get all tags 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Origin":"https://movie.douban.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie,
        # 可以添加其他 headers
    }
    response = requests.get(douban_user_url, headers=headers)
    response.encoding = 'utf-8' # 手动指定编码为 utf-8，避免中文乱码
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 同时选择标签链接和数量
    tags_elements = soup.select("ul.tag-list.mb10 li")
    tags_dict = {}
    if tags_elements:
        for index, tag_element in enumerate(tags_elements, 1):
            tag_link = tag_element.select_one("a")
            tag_count_span = tag_element.select_one("span")

            if tag_link and tag_count_span:
                tag_name = tag_link.text.strip()
                # 提取数量并去除括号
                tag_count = tag_count_span.text.strip()
                tags_dict[index] = {
                    "name": tag_name,
                    "count": tag_count
                }
    
            print(f"{index}. {tag_name} ({tag_count})")
        # print(tags_dict)
        save_key_word = douban_user_url.replace("https://", "").split(".")[0]
        save_dir = os.path.join(r"E:\Gazer\DoubanGaze\data\tags")
        save_path = os.path.join(save_dir, f"my_{save_key_word}_tags.json")
        try:
            os.makedirs(save_dir, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(tags_dict, f, ensure_ascii=False, indent=4)
            print(f"{save_key_word} tags saved in {save_path} 📌")
        except IOError as e:
            print(f"error during saving: {e}")
        except Exception as e:
            print(f"other errors: {e}")

        print(f"Found {len(tags_dict)} tags ✅")
        return tags_dict
    else:
        print("Did not find tags element❓")
        return None

def keep_or_del_tags(tags_dict):
    """设置选择: 按 1 开始保留标签模式 → 选择要保留的标签序号 → 其余标签全部删除;
    按 2 开始删除标签模式 → 选择要删除的标签序号 → 其余标签全部保留

    Args:
        tags_dict (dict): 标签字典, 键为序号, 值为标签文字

    Returns:
        list: 选择要保留/删除的标签序号的列表
    """
    while True:
        keep_or_del_msg = input('PRESS 1: start to keep tags; PRESS 2: start to delete tags; PRESS "q" to quit. \n')
        if keep_or_del_msg == "q":
            return "q"  # 返回 "q" 表示退出
        elif keep_or_del_msg == '1':
            selected_tags_nums = input('Choose tag number you want to keep, e.g. 3 15 77 \n')
            selected_tags = set(map(int, selected_tags_nums.split()))
            # 获取所有标签的序号
            all_tags_nums = set(tags_dict.keys())
            # 计算需要删除的标签序号
            tags_to_delete = all_tags_nums - selected_tags
            return list(tags_to_delete)

        elif keep_or_del_msg == '2':
            selected_tags_nums = input('Choose tag number you want to delete, e.g. 3 15 77 \n')
            selected_tags = set(map(int, selected_tags_nums.split()))
            return selected_tags
        else:
            print("Wrong Input, must be 1 or 2 or q")

def del_tags(cookie):
    """模拟登陆, 构造删除请求

    Args:
        cookie (string): 豆瓣 Cookie.
    """
    while True:
        douban_search_url, douban_user_url = select_movie_or_book()
        
        tags_dict = get_all_tags(douban_user_url)

        if not tags_dict:
            print("没有标签, 退出")
            return
        
        tags_to_delete = keep_or_del_tags(tags_dict)

        if tags_to_delete == "q":
            return  # 退出 del_tags 函数

        # simulate headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Referer": douban_user_url,
            "Origin": douban_search_url,
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie,
        }

        for tag_index in tags_to_delete:
            tag_name = tags_dict[tag_index]["name"] # 获取标签名
            data = {
            "ck": extract_ck(cookie), # 'EYqf', 替换成实际的 ck 值
            "del_tag": tag_name, # 使用标签名
            'del_submit': '修改',
            }

            tags_response = requests.post(douban_user_url, headers=headers, data=data, allow_redirects=False)  # 禁止自动重定向

            if tags_response.status_code == 302:
                print(f"删除 {tag_index}. {tag_name} 成功! 🔫 (重定向)")
            elif tags_response.status_code == 200:
                print(f"请求成功, 但不确定 {tag_name} 是否被删除, 可能是其他操作 ❓")
            else:
                print(f"请求已发送, 状态码: {tags_response.status_code}, 请检查标签页确认 {tag_name} 是否删除成功 ❓")
                print(tags_response.text)  # 打印返回内容, 方便调试
            
            time.sleep(1) # 每次请求之间间隔 1 秒
    

if __name__ == "__main__":
    cookie = 'SWEETCOOKIE'

    prompt = "----------------------------------------------\n| 删除标签steps:                              |\n| 1.选择将进入 movie 还是 book 页面的标签 🔛  | \n| 2.选择保留/删除模式 🔫                      | \n| 3.输出要保留/删除的标签字符串, 以空格分开 🎯| \n----------------------------------------------"
    print(prompt)
    # 选择将进入 movie 或者 book 页面的标签 → 打印所有标签 → 选择保留/删除模式 → post请求遍历列表删除
    del_tags(cookie)
