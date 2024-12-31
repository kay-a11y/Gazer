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
import sys
import itertools
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable()

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
    last_processed_index = -1  # 记录上一页最后一个被处理的item的索引

    while current_page <= max_pages:
        try:
            driver.get(url)
            time.sleep(random.uniform(1, 4))

            soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser') # 明确指定编码
            items = soup.select('div.item.comment-item')

            if not items:
                print("Here is the last page or no items found.")
                break

            item_index = 0  # 每次迭代都从0开始

            # 如果是第一页，则从第一个开始；否则从上一个已处理的下一个开始
            if current_page > 1:
                item_index = last_processed_index + 1

            while item_index < len(items):
                soup = BeautifulSoup(driver.page_source.encode('utf-8'), 'html.parser')
                items = soup.select('div.item.comment-item')
                item = items[item_index]
                private_status = item.select_one('div.info > ul > li.title > span.pl')

                if not private_status:
                    logging.debug(f"Found an item that needs to be changed to private (Item-{item_index + 1})")
                    change_button_js = f"document.querySelectorAll('div.item.comment-item')[{item_index}].querySelector('div > a.j.a_collect_btn').click();"
                    driver.execute_script(change_button_js)
                    logging.debug(f"After executing JS for Item-{item_index + 1}")
                    logging.debug("Clicked change_button using JavaScript")

                    time.sleep(1)  # 短暂延迟（可选）

                    # check the only me box
                    # 显式等待直到'#inp-private'元素可点击
                    only_me = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#inp-private'))
                    )
                    driver.execute_script(
                        "document.querySelector('#inp-private').click();"
                    )
                    logging.debug("checked the only me box using JavaScript")
                    # click the submit button
                    # 显式等待直到'#submits > span > input[type=submit]'元素可点击
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#submits > span > input[type=submit]'))
                    )
                    driver.execute_script(
                        "document.querySelector('#submits > span > input[type=submit]').click();"
                    )
                    # print("clicked the submit button")

                    time.sleep(random.uniform(1, 4))

                    # 提交后页面会刷新, 需要重新获取当前页面的元素
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.item.comment-item'))
                    )
                    print(f"Item-{item_index + 1} has been changed to private")
                    # time.sleep(random.uniform(1, 4))
                    item_count += 1
                    last_processed_index = item_index  # 记录当前处理的item索引

                    # 页面刷新后，重新加载当前页
                    driver.get(url)
                    time.sleep(random.uniform(1, 4))
                    
                    break  # 处理完一个item后，退出内部循环, 继续外层循环

                else:
                    # print(f"Item-{item_index + 1} is already private or private_status not found")
                    item_index += 1 #已经设置好私密的item,索引+1

            if item_index >= len(items): #如果内部while循环是因为遍历结束而退出, 则继续执行下面的代码, 即处理下一页
                print("Going to next page.")
                current_page += 1
                last_processed_index = -1  # 重置索引
                next_page_link_a = soup.select_one('a.next')
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
    # start_url = "https://movie.douban.com/people/0000/collect" # 豆瓣标记页(看过的影视) TODO
    start_url = "https://movie.douban.com/people/0000/wish" # 豆瓣标记页(想看的影视) TODO
    max_pages = 1 # 设置最大爬取页数 TODO
    max_items = max_pages * 15 #计算max_items
    
    # 1. 设置 Edge WebDriver 的路径
    driver_path = r"E:\...\msedgedriver.exe"
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

    