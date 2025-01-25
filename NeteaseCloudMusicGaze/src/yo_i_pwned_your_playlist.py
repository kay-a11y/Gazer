import time 
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import os, json
import random, sys

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将 API 目录添加到 Python 路径中, 确保 src 下的 __init__.py 不为空
sys.path.append(current_dir)

# print(sys.path)

# 导入 get_comment 函数
from API.get_comment import get_comment

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

def crawl_playlst_data(driver, fav_lst_url, max_songs=1000):  # 设置最大爬取页数
    """
    爬取播放列表数据。

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        fav_lst_url (string): 我喜欢的音乐页面的URL.
        max_songs (int, optional): 最大爬取歌曲数. Defaults to 1000.

    Returns:
        list: 所有歌曲信息的字典列表
    """
    all_data = []
    url = fav_lst_url
    item_count = 0

    try:
        driver.get(url)
        print(f"正在访问的页面标题: {driver.title}")

        # 等待页面跳转完成
        time.sleep(5)
        print(f"跳转后的页面标题: {driver.title}")

        # 切换到 iframe
        driver.switch_to.frame("contentFrame")  # 使用 name 属性切换到 iframe

        while True:
            # 使用显式等待来确保元素加载完成后再选择
            wait = WebDriverWait(driver, 10) # 设置一个最长等待时间, 这里是10秒
            try:
                items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody > tr'))) 
                if len(items) == 1000:
                    print("已找到歌曲元素")
            except :
                print("等待超时, 未找到歌曲元素")
                items = []

            if not items:  # 如果当前页面没有歌曲，可能未找到歌曲元素
                print("未找到歌曲元素, 爬取结束")
                break
            
            for item in items[:max_songs]:
                time.sleep(random.uniform(2, 5)) # 在获取每首歌的信息之前休眠
                detail_url = None  # 先将 detail_url 初始化为 None
                try:
                    detail_link = item.find_element(
                        By.CSS_SELECTOR, "td:nth-child(2) > div > div > div > span > a"
                    )
                    if detail_link:
                        # https://music.163.com/#/song?id=1489099936
                        # <a href="/song?id=1489099936">
                        detail_url = f"{detail_link.get_attribute('href')}"
                        # print(f"歌曲详情: {detail_link}")

                        detail_data = crawl_detail_page(detail_url)   
                        if detail_data:
                            all_data.append(detail_data)
                            item_count += 1
                            print(f"已爬取 {item_count} 首歌曲")
                            if item_count >= max_songs:
                                print(
                                    f"已达到最大爬取数量 {max_songs} 或已爬取到最后一首歌曲，爬取结束"
                                )
                                break
                except Exception as e:
                    print(f"在爬取 {detail_url} 时发生错误: {e}")
                    print(f"错误类型：{type(e)}")
                    print(
                        f"错误发生在：{e.__traceback__.tb_frame.f_code.co_filename}，第 {e.__traceback__.tb_lineno} 行"
                    )
                    time.sleep(random.uniform(5, 10))

            else:
                print("所有歌曲已爬取完成")
                break

            # 滚动到页面底部 (这个可能不太起作用, 但是加上也没坏处)
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # print("已滚动到页面底部")
            # time.sleep(random.uniform(2, 5))

            # 检查是否已爬取到最大数量的歌曲或者是否已爬取到最后一首歌曲
            if item_count >= max_songs:
                print(f"已达到最大爬取数量 {max_songs}，爬取结束")
                break
            
            # 因为只有一页，所以不需要翻页，直接结束循环
            break

    except Exception as e:
        print(f"错误类型：{type(e)}")
        print(f"错误发生在：{e.__traceback__.tb_frame.f_code.co_filename}，第 {e.__traceback__.tb_lineno} 行")
        time.sleep(random.uniform(5, 10))
    finally: #无论是否发生异常，都会执行finally块中的代码
        # 切换回主文档
        driver.switch_to.default_content()
        save_path = r"E:\Gazer\NeteaseCloudMusicGaze\data\raw\me_music_data.json" # TODO
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            print(f"已爬取的数据已保存到 {save_path}")
        except IOError as e:
            print(f"保存文件出错：{e}")
        except Exception as e:
            print(f"其他错误：{e}")

    return all_data

def crawl_detail_page(detail_url):
    """
    使用 requests 爬取歌曲详情页

    Args:
        detail_url (str): 歌曲详情页 URL。

    Returns:
        dict or None: 包含歌曲信息的字典，如果爬取失败则返回 None
    """

    if detail_url is None:
        print("detail_url 为 None, 无法爬取详情页")
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    try:
        # 使用 requests 获取网页内容
        response = requests.get(detail_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        time.sleep(random.uniform(2, 4)) # 获取内容后休眠, 这个休眠时间可以根据需要调整

        # 使用 BeautifulSoup 解析网页内容
        detail_soup = BeautifulSoup(response.text, 'html.parser')

        # 提取信息
        title = detail_soup.select_one('div.tit > em.f-ff2').text.strip()
        singer_element = detail_soup.select_one('p.des.s-fc4:-soup-contains("歌手：") > span')
        singer = singer_element.get("title") if singer_element else "未能成功获取歌手"
        album_element = detail_soup.select_one('p.des.s-fc4:-soup-contains("所属专辑：") > a.s-fc7')
        album = album_element.text.strip() if album_element else "未能成功获取专辑"
        comment = get_comment(detail_url.split("=")[-1]) 

        return {
            'title': title,
            'singer': singer,
            'album': album,
            'comment': comment,
        }
    except Exception as e:
        print(f"爬取详情页 {detail_url} 失败：{e}")
        time.sleep(random.uniform(5, 10))
        return None

# 主函数
if __name__ == "__main__":

    cookies = 'SWEETCOOKIE'
    # 1. 设置 Edge WebDriver 的路径
    driver_path = r"E:\Gazer\drivers\msedgedriver.exe"
    # 2. 创建 Edge WebDriver
    driver = create_edge_driver(driver_path)
    # 最大化窗口
    # driver.maximize_window()
    # 3. 添加 cookie
    add_cookies_to_driver(driver, cookies)
    # print(driver.get_cookies())

    fav_lst_url = "https://music.163.com/#/playlist?id=000011122" # 网易云我喜欢的音乐页面URL TODO
    max_songs=7 # 设置最大爬取歌曲 TODO
    
    all_data = crawl_playlst_data(driver, fav_lst_url, max_songs) # 传递 cookies

    driver.quit()

    # 处理爬取到的数据
    print(f"共爬取到 {len(all_data)} 条数据。")

    