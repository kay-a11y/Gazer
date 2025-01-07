import requests
import time
import json
from datetime import datetime

def comment_weibo(content, weibo_url, cookie=None, x_xsrf_token=None):
    """使用 requests 库评论微博

    Args:
        content (string): 评论内容
        weibo_url (string): 微博详情页的完整 URL
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.

    Returns:
        string or None: 成功则返回评论的 cid，失败则返回 None
    """

    url = "https://m.weibo.cn/api/comments/create" # 微博评论接口

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": weibo_url, # 评论的微博正文网址, 后续继续逆向微博用户详情api, 改成检测用户新发微博的网址 TODO
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "content": content,
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080",  # 根据你的屏幕分辨率修改
        "mid": weibo_url.split("/")[-1],  # 从 weibo_url 中提取 mid
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result.get("ok") == 1:
            print("微博评论成功！")
            # 提取评论的 cid
            cid = result["data"]["rootidstr"]  # 使用 rootidstr 字段，更可靠
            print(f"评论的 cid: {cid}")
            return cid
        else:
            print(f"微博评论失败: {result['msg']}")
            return None
    else:
        print(f"请求失败: {response.status_code}")
        return None
    
def delete_comment(cid, cookie=None, x_xsrf_token=None):
    """使用 requests 库删除微博评论

    Args:
        cid (string): 评论的 ID
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/comments/destroy"  # 删除评论的请求接口

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/",  # 删除评论的 Referer 可以是首页
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "cid": cid,
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080",
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博评论删除成功！")
            return True
        else:
            print(f"微博评论删除失败: {result['msg']}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
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

# 微博详情页的 URL，你需要根据实际情况修改
weibo_url = "https://m.weibo.cn/detail/5110000011111268" # 要评论的微博的url

# 使用 Cookie 和 st 评论微博
comment_weibo(f" valid - {now} 使用py评论微博1", weibo_url, cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(30)

# 再次评论
comment_weibo(f" valid2 - {now} 使用py评论微博2", weibo_url, cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(30)

# 再次评论
comment_weibo(f" valid3 - {now} 使用py评论微博3", weibo_url, cookie=cookie_str, x_xsrf_token=st)
