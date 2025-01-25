from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import time

def create_edge_driver(driver_path, headers=None):
    """
    创建 Edge WebDriver。

    Args:
        driver_path (str): Edge WebDriver 的路径。
        headers (dict, optional): 请求头, 会被selenium忽略. Defaults to None.

    Returns:
        webdriver.Edge: Edge WebDriver 对象。
    """
    edge_options = EdgeOptions()
    edge_options.add_argument("--incognito")  # 隐身模式
    # 设置无头模式（可选）
    edge_options.add_argument("--headless")
    # 禁用 GPU 加速（在某些情况下可以提高稳定性）
    edge_options.add_argument("--disable-gpu")
    # 禁用 JavaScript（可选）
    # edge_options.add_argument("--disable-javascript")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 设置 driver 的路径
    service = EdgeService(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

def add_cookies_to_driver(driver, cookies, domain="music.163.com"):
    """
    将 Cookie 添加到 Edge WebDriver。

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        cookies (str): Cookie 字符串, 格式为 "key1=value1; key2=value2; ..."。
        domain (str, optional): Cookie 的域名. Defaults to "music.163.com".
    """
    driver.delete_all_cookies()  # 清除所有 Cookie
    # 访问一个页面，以便设置 Cookie. 必须与cookie同域
    driver.get(f"https://{domain}") 
    cookies = cookies.split("; ")
    for cookie in cookies:
        try:
            key, value = cookie.split("=", 1)
            # 确保 domain 设置为 music.163.com
            driver.add_cookie({"name": key.strip(), "value": value.strip(), "domain": "music.163.com", "path": "/"})
        except ValueError:
            print(f"Invalid cookie format: {cookie}")


if __name__ == "__main__":
    cookie = 'SWEETCOOKIE'
    
    driver_path = "E:\GazeKit\drivers\msedgedriver.exe"

    driver = create_edge_driver(driver_path)

    driver.maximize_window()

    add_cookies_to_driver(driver, cookie)
    # print(driver.get_cookies())
    driver.get("https://music.163.com/#/playlist?id=000011122")  # 访问网易云首页, 如果登录成功, 头像就会出现
    # 验证 JavaScript 是否被禁用
    print(driver.execute_script("return navigator.userAgent;"))
    print(driver.execute_script("return typeof window.cdc_adoQpoasnfa76pfcZLmcfl_Array === 'undefined'"))

    time.sleep(5)
    driver.quit()