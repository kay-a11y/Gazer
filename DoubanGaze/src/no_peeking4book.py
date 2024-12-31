import time 
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random

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
    # 设置请求头, 会被selenium忽略, 没有意义
    if headers:
        edge_options.add_argument(f'--user-agent={headers["User-Agent"]}')
    edge_options.add_argument("--incognito")  # 隐身模式
    # 设置无头模式（可选）
    edge_options.add_argument("--headless")
    # 禁用 GPU 加速（在某些情况下可以提高稳定性）
    edge_options.add_argument("--disable-gpu")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # 屏蔽 Selenium 日志的关键：添加 --log-level=3 参数
    # --log-level=0 (INFO), 1 (WARNING), 2 (LOG_ERROR), and 3 (LOG_FATAL)
    edge_options.add_argument("--log-level=3")  
    # 设置 driver 的路径
    service = EdgeService(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

def add_cookies_to_driver(driver, cookies_str, domain="douban.com"):
    """
    将 Cookie 添加到 Edge WebDriver。

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        cookies_str (str): Cookie 字符串, 格式为 "key1=value1; key2=value2; ..."。
        domain (str, optional): Cookie 的域名. 针对豆瓣, 可以设置为"douban.com". Defaults to "douban.com".
    """
    driver.delete_all_cookies()  # 清除所有 Cookie
    # 访问一个页面，以便设置 Cookie. 必须与cookie同域
    driver.get(f"https://{domain}")
    cookies = cookies_str.split("; ")
    for cookie in cookies:
        try:
            key, value = cookie.split("=", 1)
            driver.add_cookie({"name": key.strip(), "value": value.strip(), "domain": "douban.com", "path": "/"})
        except ValueError:
            print(f"Invalid cookie format: {cookie}")
        
def change2private(driver, start_url, max_pages=20):  # 设置最大爬取页数 
    current_page = 1
    url = start_url
    item_count = 0

    while current_page <= max_pages:
        try:
            driver.get(url)
            time.sleep(random.uniform(1, 3))

            soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser') # 明确指定编码
            items = soup.select('li.subject-item')

            if not items:
                print("Here is the last page or no items found.")
                break
            
            # find all book links 
            book_links = [item.select_one('div.info > h2 > a').get('href') for item in items]
            print(f"book_links: {book_links}")

            for book_link in book_links:
                driver.get(book_link)
                time.sleep(random.uniform(3, 5))
                soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser')

                # judge if the book is already private
                private_status = soup.select_one('#interest_sect_level > div > span.mr10 > span')

                if private_status and private_status.get_text() == "(私人收藏)":
                    print(f"Book at {book_link} is already private 🤗")
                    continue # 已经是私人收藏，直接跳到下一个链接
                else:
                    print(f"Book at {book_link} needs to be changed to private 🔫")
                    change_button_js = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#interest_sect_level > div > a'))
                    )
                    driver.execute_script("arguments[0].click();", change_button_js)

                    # 等待模态框(勾选框)出现
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#inp-private'))
                    )

                    only_me = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#inp-private'))
                    )
                    if not only_me.is_selected():
                        driver.execute_script("arguments[0].click();", only_me)
                        print("checked the only me box using JavaScript")
                    
                    # 提交按钮并等待页面刷新
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#submits > span > input[type=submit]'))
                    )
                    driver.execute_script("arguments[0].click();", submit_button)
                    print(f"Submitted changes for {book_link}")

                    # 页面可能需要时间来更新，这里可以加入一个延迟
                    time.sleep(random.uniform(2, 4))
                    # 检查是否更改成功，如果更改成功，计数器加一
                    soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser')
                    private_status = soup.select_one('#interest_sect_level > div > span.mr10 > span')
                    if private_status and private_status.get_text() == "(私人收藏)":
                        item_count += 1
                        
            # 处理完当前页所有书籍链接后，跳转到下一页
            print("Going to next page.")
            current_page += 1
            driver.get(url)
            time.sleep(random.uniform(1, 3))

            soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser') # 明确指定编码
            next_page_link_a = soup.select_one('span.next > a')
            next_page_link_link = soup.select_one('link[rel="next"]')

            if next_page_link_a:
                url = next_page_link_a.get('href')
            elif next_page_link_link:
                url = next_page_link_link.get('href')
            else:
                url = None

            if url:
                url = urljoin(start_url, url)
                print(f"next page LINK(abs path): {url}")
                # current_page += 1
                print(f"I am now on PAGE {current_page}...")
            else:
                print("NO next page LINK, I am done!")
                break

        except Exception as e:
            print(f"something wrong when get to the next page: {e}")
            break

    return item_count


# 主函数
if __name__ == "__main__":
    # start_url = "https://book.douban.com/mine?status=collect" # 豆瓣标记页(看过的书) TODO
    start_url = "https://book.douban.com/mine?status=wish" # 豆瓣标记页(想看的书) TODO

    max_pages = 7 # 设置最大爬取页数 TODO
    max_items = max_pages * 15 #计算max_items
    
    # 1. 设置 Edge WebDriver 的路径
    driver_path = r"E:\...\msedgedriver.exe" # TODO
    # 2. 创建 Edge WebDriver
    driver = create_edge_driver(driver_path)
    # 最大化窗口
    driver.maximize_window()
    # 3. 添加 Cookie
    cookies_str = '''YOUR_COOKIE_STRING'''
    # TODO  Cookie 字符串

    add_cookies_to_driver(driver, cookies_str)

    change_status = change2private(driver, start_url, max_pages)

    driver.quit()

    # 处理爬取到的数据
    print(f"I have changed *{change_status}* marks to be private.")

    