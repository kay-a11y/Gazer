import requests
import time
import json
from datetime import datetime

def like_or_unlike_weibo(weibo_url, action, cookie=None, x_xsrf_token=None):
    """使用 requests 库点赞或取消点赞微博

    Args:
        weibo_url (string): 微博详情页的完整 URL
        action (string): "like" 或 "unlike"
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    if action == "like":
        url = "https://m.weibo.cn/api/attitudes/create"
    elif action == "unlike":
        url = "https://m.weibo.cn/api/attitudes/destroy"
    else:
        print("无效的操作！")
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": weibo_url,
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "id": weibo_url.split("/")[-1],
        "attitude":"heart",
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
    }

    try:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            if response.text:
                result = response.json()
            else:
                print(f"{action} 操作: 返回数据为空")
                return False
            
            if result.get("ok") == 1:
                print(f"{action} 微博成功！")
                return True
            else:
                print(f"{action} 微博失败: {result.get('msg', '未知错误')}")
                return False
        else:
            print(f"请求失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"发生错误: {e}")
        return False
    
# 从文件中读取 Cookie 和 st
with open(r"E:\Gazer\WeiboGaze\data\cookie_st\cookie_and_st.json", "r") as f:
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 获取当前时间
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 微博详情页的 URL，需要根据实际情况修改
weibo_url = "https://m.weibo.cn/detail/5110000011111268" # 要点赞的微博的url

# 使用 Cookie 和 st 点赞微博
like_or_unlike_weibo(weibo_url, "like", cookie=cookie_str, x_xsrf_token=st)
print(f"点赞成功！{now}")

# 增加延时
time.sleep(10)

# 取消点赞
like_or_unlike_weibo(weibo_url, "unlike", cookie=cookie_str, x_xsrf_token=st)
print(f"取消点赞成功！{now}")

