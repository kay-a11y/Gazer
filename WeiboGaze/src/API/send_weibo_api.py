import requests
import time
import json
from datetime import datetime

def send_weibo(content, visible=0, cookie=None, x_xsrf_token=None):
    """使用 requests 库发送微博

    Args:
        content (string): 微博内容
        visible (int, optional): 可见性. 0: 公开, 1: 仅自己可见, 6: 朋友圈可见. Defaults to 0.
        cookie (string, optional): 你的微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/api/statuses/update"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/compose/",
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }
    if visible == 0:
        data = {
            "content": content,
            "st": x_xsrf_token,
            "_spr": "screen:1920x1080" # 根据你的屏幕分辨率修改
        }
    else:
        data = {
            "content": content,
            "visible": visible,
            "st": x_xsrf_token,
            "_spr": "screen:1920x1080" # 根据你的屏幕分辨率修改
        }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博发送成功！")
            return True
        else:
            print(f"微博发送失败: {result['msg']}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False
    
# 从文件中读取 Cookie 和 st
with open(r"E:\...\cookie_and_st.json", "r") as f:
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 获取当前时间
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 使用 Cookie 和 st 发送微博
send_weibo(f" valid - {now}", cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(60)

# 再次发送
send_weibo(f" valid2 - {now}", visible=1, cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(60)

# 再次发送
send_weibo(f" valid3 - {now}", visible=6, cookie=cookie_str, x_xsrf_token=st)
