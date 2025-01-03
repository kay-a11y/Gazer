import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_cookie_and_st(user_data_dir):
    """
    使用 Selenium 打开微博登录页面, 手动扫码登录, 并获取 Cookie 和 st
    """
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')  # 无头模式
    options.add_argument("user-data-dir=" + user_data_dir)

    driver = webdriver.Edge(options=options)
    driver.get("https://passport.weibo.com/sso/signin?entry=wapsso&source=wapsso&url=https%3A%2F%2Fm.weibo.cn%2F")  # 打开微博登录页面
    # 等待用户登录, 最多等待300秒
    try:
        WebDriverWait(driver, 300).until(
            EC.url_to_be("https://m.weibo.cn/") # 等待直到跳转到手机版微博主页
        )
        print("登录成功! 保存cookie & st")
        # 获取 Cookie
        cookies = driver.get_cookies()
        # 提取 st (XSRF-TOKEN)
        st = ""
        for cookie in cookies:
            if cookie["name"] == "XSRF-TOKEN":
                st = cookie["value"]
                break
            if cookie["name"] == "SUB":
                st = cookie["value"].split(';')
                for i in st:
                    if 'f' in i:
                        st = i
                        break

        # 保存 Cookie 和 st 到文件
        with open(r"E:\...\cookie_and_st.json", "w") as f:
            json.dump({"cookies": cookies, "st": st}, f)

        print(f"Cookie 和 st 已保存到 {r'E:\...\cookie_and_st.json'} 文件中: st: {st}")
    except Exception as e:
        print(f"等待登录超时或出现错误: {e}")
    finally:
        driver.quit()

# 调用示例 (你需要根据你的实际情况修改 user_data_dir)
user_data_dir = r"C:\...\Default"  # 这里的路径需要根据你的实际情况修改, 该文件目录下有你的浏览器配置文件, 让selenium读取
get_cookie_and_st(user_data_dir)
