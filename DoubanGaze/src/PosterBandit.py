import requests
from bs4 import BeautifulSoup
import os
import time, random
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import shutil
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

DEFAULT_POSTER_PATH = r"E:\Gazer\DoubanGaze\data\poster"

def compare_date(target_date_1, target_date_2, viewed_date):
    """比较条目标记日期是否在指定日期之间, 包含起止日期

    Args:
        target_date_1 (str (YYYY-MM-DD)): 指定的起始日期
        target_date_2 (str (YYYY-MM-DD)): 指定的结束日期
        viewed_date (str (YYYY-MM-DD)): 爬取的观看日期

    Returns:
        bool: 如果在在指定日期之间, 返回 True, 否则 False
    """
    try:
        target_date_1_obj = datetime.strptime(target_date_1, "%Y-%m-%d")
        target_date_2_obj = datetime.strptime(target_date_2, "%Y-%m-%d")
        viewed_date_obj = datetime.strptime(viewed_date, "%Y-%m-%d")
        return target_date_1_obj <= viewed_date_obj <= target_date_2_obj
    except ValueError as e:
        logging.error(f"日期格式错: {e}")
        return False
    
def crawl_link(target_link, session, headers):
    """爬取目标链接, 返回 soup 对象

    Args:
        target_link (string): 目标链接
        session (requests.Session): requests.Session 对象
        headers (dict): 请求头

    Returns:
        tuple[bs4.BeautifulSoup, int] : soup 对象 和 状态码
    """
    status_code = None
    try:
        target_response = session.get(target_link, headers=headers)
        status_code = target_response.status_code
        target_response.raise_for_status()
        target_soup = BeautifulSoup(target_response.content.decode('utf-8'), 'html.parser')
        return target_soup, status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"请求链接失败: {e}")
        return None, status_code
    except Exception as e:
       logging.error(f"其他错误: {e}")
       return None, status_code


def create_folder(target_date_1, target_date_2, poster_save_path=DEFAULT_POSTER_PATH):
    """在指定目录下创建要保存 <指定日期的条目海报> 的文件夹, 
    名称由填写的起止日期决定, 格式为{target_date_1}_{target_date_2}, 
    e.g. 2024_12_1_2024_12_31
    Args:
        target_date_1 (str (YYYY-MM-DD)): 指定的起始日期
        target_date_2 (str (YYYY-MM-DD)): 指定的结束日期
        poster_save_path (string): 保存海报图片的指定目录
        Defaults to "E:\\Gazer\\DoubanGaze\\data\\poster".

    Returns:
        single_poster_save_path(string): 保存每个条目海报图片的文件夹路径 
        e.g. "E:\\Gazer\\DoubanGaze\\data\\poster\\2024_12_1_2024_12_31".
    """
    date_filename = f"{target_date_1.replace('-', '_')}_{target_date_2.replace('-', '_')}"
    single_poster_save_path = os.path.join(poster_save_path, date_filename)
    os.makedirs(single_poster_save_path, exist_ok=True)
    return single_poster_save_path

def save_poster(poster_src, viewed_date_text, single_poster_save_path):
    """保存单独的海报到本地. 

    Args:
        poster_src (string): 爬取的海报下载 URL.
        viewed_date_text (string (YYYY-MM-DD)): 对应条目的标记日期.
        single_poster_save_path (string): create_folder 函数返回的
                                    保存每个条目海报图片的文件夹路径 
    """
    try:
        img_response = requests.get(poster_src, stream=True)
        img_response.raise_for_status()

        # 构建图片文件名
        date_filename = viewed_date_text.replace("-", "_")
        img_filename = f"poster_{date_filename}.jpg"

        img_path = os.path.join(single_poster_save_path, img_filename)

        # 保存图片到本地
        with open(img_path, 'wb') as f:
            # for chunk in img_response.iter_content(chunk_size=65536):
                # f.write(chunk)
            shutil.copyfileobj(img_response.raw, f) # 直接使用 shutil.copyfileobj
        print(f"img saved {img_filename}")
    except requests.exceptions.RequestException as e:
        logging.error(f"图片下载失败: {e}")
    except Exception as e:
        logging.error(f"保存图片时出现错误: {e}")

def get_movie_elements(soup):
    """从 soup 对象中获取并返回所有包含电影条目的 div 元素

    Args:
        soup (bs4.BeautifulSoup): 初始页的 soup 对象

    Returns:
        bs4.element.ResultSet: 所有电影条目的 div 元素列表
    """
    return soup.select("#content > div.grid-16-8.clearfix > div.article .item.comment-item")

def get_movie_info(movie_element):
    """从单个电影条目 div 元素中获取并返回观看日期和具体条目链接

    Args:
        movie_element (bs4.element.Tag): 单个电影条目的 div 元素

    Returns:
        tuple[str | None, str | None]: 
        观看日期+具体条目链接的 Tag 对象元组, 或 (None, None)
    """
    viewed_date_element = movie_element.select_one("div.info span.date")
    movie_link_element = movie_element.select_one("div.article div.pic > a")

    if viewed_date_element and movie_link_element:
        viewed_date_text = viewed_date_element.text.strip()
        movie_link = movie_link_element['href']
        return viewed_date_text, movie_link
    return None, None

def get_poster_url(movie_link, session, headers):
    """根据电影详情页链接获取并返回海报链接

    Args:
        movie_link (str): 具体条目链接的 URL 字符串
        session (requests.Session): requests.Session 对象
        headers (dict): 请求头

    Returns:
        str | None: 海报链接的 URL 字符串, 或 None
    """
    try:
        movie_soup, status_code = crawl_link(movie_link, session, headers)

        if movie_soup:
            poster_img_url_element = movie_soup.select_one("#mainpic > a")
            if poster_img_url_element:
                poster_img_url = poster_img_url_element['href']
                # 如果以 .webp 结尾, 直接返回
                if poster_img_url.endswith(".webp"):
                    return poster_img_url
                else:
                    # 进入海报列表
                    poster_img_soup, status_code = crawl_link(poster_img_url, session, headers)

                if poster_img_soup:
                    fst_poster_url_element = poster_img_soup.select_one(
                        "#content div.article div.cover > a"
                        )
                    if fst_poster_url_element:
                        # 进入最终海报
                        poster_final_soup, status_code = crawl_link(fst_poster_url_element['href'], session, headers)

                        if poster_final_soup:
                            logging.debug("成功进入最终海报")
                            poster_final_url = poster_final_soup.select_one("#content > div > div.article a.mainphoto > img")
                            if poster_final_url:
                                logging.debug("成功找到最终海报")
                                return poster_final_url['src']
                            else:
                                logging.debug("没有找到最终海报")
                        else:
                            logging.debug("未进入最终海报")
    except requests.exceptions.RequestException as e:
       logging.error(f"请求链接失败: {e}")
       return None
    return None

def get_headers(cookies, viewed_movie_url):
    return  {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Cookie": cookies,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Referer": viewed_movie_url,
        # "Referer": "https://movie.douban.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Site": "none",
    }

def download_poster_images(cookies, target_date_1, target_date_2, poster_save_path, page_id=1):
    """
    从给定的 URL 中提取海报图片链接，并下载保存到指定的文件夹中

    Args:
        cookies: 包含登录信息的 cookies
        target_date_1 (str (YYYY-MM-DD)): 指定的起始日期
        target_date_2 (str (YYYY-MM-DD)): 指定的结束日期
        page_id: 爬取开始的页数 Defaults to 1.

    Returns:
        None
    
    Raises:
        requests.exceptions.RequestException: 如果请求网页失败。
        Exception: 其他可能发生的错误。
    """
    start_time = time.perf_counter() # 启动计时器
    single_poster_save_path = create_folder(target_date_1, target_date_2, poster_save_path)

    session = requests.Session() # 在这里创建 session
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    while True:
        page_processed = (int(page_id) - 1) * 15
        viewed_movie_url = f"https://movie.douban.com/people/122336654/collect?start={page_processed}&sort=time&rating=all&mode=grid&type=all&filter=all"

        headers = get_headers(cookies, viewed_movie_url)

        soup, status_code = crawl_link(viewed_movie_url, session, headers)
        if soup:
            print(f"NOW IN {viewed_movie_url}")
            try:
                # 打印响应的 HTML 以调试
                # print(soup.prettify())
                # 1. 找到所有包含电影条目的 div 元素
                viewed_movie_elements = get_movie_elements(soup)
                logging.debug(f"Found {len(viewed_movie_elements)} marks. FYI: 15.")

                count = 0
                viewed_date_text = "" # 初始化
                # 1. 遍历每个电影条目 div 元素
                for movie_element in viewed_movie_elements:
                    movie_start_time = time.perf_counter() # 启动单个电影条目的计时器
                    # 2. 获取观看日期和链接
                    viewed_date_text, movie_link = get_movie_info(movie_element)

                    if viewed_date_text:
                            logging.debug(f"Found date: {viewed_date_text}")

                            # 比较观看日期是否符合用户输入, 如果不, break
                            if not compare_date(target_date_1, target_date_2, viewed_date_text):
                                print("Done. 😺")
                                break # 跳出 for loop

                            # 3. 获取海报链接
                            if movie_link:
                                time.sleep(random.randint(2, 5))
                                fst_poster_url = get_poster_url(movie_link, session, headers) # 传递 session
                                if fst_poster_url:
                                    # 保存海报
                                    save_poster(fst_poster_url, viewed_date_text, single_poster_save_path)
                                    count += 1
                    movie_end_time = time.perf_counter() # 停止单个电影条目的计时器
                    movie_elapsed_time = movie_end_time - movie_start_time
                    logging.debug(f"单个电影条目爬取耗时：{movie_elapsed_time:.2f} 秒")

                # Loop for single page ended here.                        
                print(f"I have saved {count} posters for U. 😼")
                # Going to the next page.
                page_id += 1
            
            except Exception as e:
                print(f"ERROR: {e}")
        else:
            logging.debug(f"请求失败! 状态码: {status_code}")
        
        if not viewed_movie_elements or (viewed_date_text and not compare_date(target_date_1, target_date_2, viewed_date_text)):
            break
    end_time = time.perf_counter() # 停止计时器
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"总耗时：{minutes} 分 {seconds} 秒") # 避免重复格式化

if __name__ == "__main__":

    target_date_1 = "2025-1-1"  # TODO 填写起始日期
    target_date_2 = "2025-1-31" # TODO 填写截止日期
    poster_save_path = r"E:\Gazer\DoubanGaze\data\poster"

    cookies = 'SWEETCOOKIE'
    
    download_poster_images(cookies, target_date_1, target_date_2, poster_save_path, page_id=1)