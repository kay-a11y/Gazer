from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import requests
from bs4 import BeautifulSoup
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

def add_cookies_to_driver(driver, cookies, domain="douban.com"):
    """
    将 Cookie 添加到 Edge WebDriver。

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        cookies (str): Cookie 字符串, 格式为 "key1=value1; key2=value2; ..."。
        domain (str, optional): Cookie 的域名. 针对豆瓣, 可以设置为".douban.com". Defaults to "douban.com".
    """
    driver.delete_all_cookies()  # 清除所有 Cookie
    # 访问一个页面，以便设置 Cookie. 必须与cookie同域
    driver.get(f"https://www.{domain}") # 为了确保生效, 这里访问 www.douban.com
    cookies = cookies.split("; ")
    for cookie in cookies:
        try:
            key, value = cookie.split("=", 1)
            # 确保 domain 设置为 .douban.com
            driver.add_cookie({"name": key.strip(), "value": value.strip(), "domain": ".douban.com", "path": "/"})
        except ValueError:
            print(f"Invalid cookie format: {cookie}")
        
def get_movie_info(driver, item_url):
    """
    将搜索到的电影信息输出到终端: 用户相关: 是否标记, 标记日期, 我的标签, 我的短评
    条目信息: 类型, 官网(如果有), 制片国家, 语言, 首播, 季数, 集数, 单集片长, 又名, IMDb, 剧情简介

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        item_url (str): 电影/电视剧页面的 URL。
    """

    try:
        driver.get(item_url)
        time.sleep(3)  # 等待页面加载, 可以根据需要调整

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- 用户信息部分 (需要 Cookie) ---
        # 用 selenium 获取
        # 1. 是否标记
        marked_text = soup.select_one("#interest_sect_level > .j.a_stars > .mr10").contents[0].strip()
        print(f"是否标记: {marked_text}")

        # 2. 标记日期
        date_element = soup.select_one("#interest_sect_level .collection_date")
        if date_element:
            date_text = date_element.text.strip()
            print(f"标记日期: {date_text}")
        else:
            print("没有找到标记日期")

        # 3. 我的标签
        # 使用next_sibling获取标签文字
        tags_element = soup.select_one("#interest_sect_level .color_gray .color_gray")
        if tags_element:
            tags_text = tags_element.text.strip()
            print(f"我的{tags_text}")
        else:
            print("没有找到标签")

        # 4. 我的短评
        comments_element = soup.select_one("#interest_sect_level > .j.a_stars span:nth-child(7)")
        comments_element_2 = soup.select_one("#interest_sect_level > .j.a_stars span:nth-child(9)")
        if comments_element:
            comments_text = comments_element.text.strip()
            print(f"我的短评: {comments_text}")
        if comments_element_2:
            comments_text_2 = comments_element_2.text.strip()
            print(f"我的短评: {comments_text_2}")
        else:
            print("没有找到我的短评")
        
        print("-" * 20)
        
        # --- 非用户信息部分 (原本使用 requests，现在也使用 Selenium) ---
        info = soup.find(id="info")
        base_info = ""

        # 推荐按钮中的信息
        # 使用 a 标签的 data-xxx 属性提取
        general_info_title = soup.select_one('.rec-sec .rec a.lnk-sharing').get("data-name")
        general_info_desc = soup.select_one('.rec-sec .rec a.lnk-sharing').get("data-desc")
        general_info = general_info_title + "\n" + general_info_desc
        print(general_info)

        for child in info.contents:  # 使用 info.contents 代替 info.children
            if not isinstance(child, str) or child.strip(): # 过滤掉空文本节点
                logging.info(f"当前 child: {child}")

                if child.name == "span" and "pl" in child.get("class", []):
                    logging.info(f"  找到 span.pl: {child.text.strip()}")
                    val = ""
                    label = child.text.strip()

                    # 移除对 "导演"、"编剧"、"主演" 的处理逻辑
                    if label == "官方网站:":
                        logging.info(f"    进入处理 官方网站 分支")
                        next_a_tag = child.find_next_sibling("a")
                        if next_a_tag:
                            val = next_a_tag.get("href")
                        logging.info(f"    val: {val}")
                    elif label == "首播:":
                        logging.info(f"    进入处理 首播 分支")
                        next_span = child.find_next_sibling("span")
                        if next_span:
                            val = next_span.get("content")
                        logging.info(f"    val: {val}")
                    else:
                        # 循环查找 content, 直到找到一个非空白字符或非 <br> 标签
                        content = child.next_sibling
                        while content == '\n' or (content.name == "br" if content else False):
                            logging.info(f"    下一个兄弟节点是 空白或 <br>, 继续查找下一个兄弟节点")
                            content = content.next_sibling
                            logging.info(f"    content (content.next_sibling): {content}")

                        # 再次判断 content 类型
                        if content:
                            # 处理季数
                            if label == "季数:":
                                logging.info(f"    进入处理 季数 分支")
                                season = [option.text.strip() for option in child.find_next_sibling("select").find_all("option", selected="selected")]
                                val = " / ".join(season)
                                logging.info(f"    val: {val}")
                            # 特殊处理"类型", 因为类型有多个, 且都用`span`包裹, 不能使用`child.next_sibling.text`, 否则会只获取到第一个类型
                            elif label == "类型:":
                                logging.info(f"  进入处理 类型 分支")
                                genres = [span.text.strip() for span in child.find_next_siblings("span", property="v:genre")]
                                val = " / ".join(genres)
                                logging.info(f"    val: {val}")
                            elif isinstance(content, str): #判断是否是字符串
                                logging.info(f"    进入处理 字符串 分支")
                                val = content.strip()
                                logging.info(f"    val: {val}")
                            else:
                                logging.info(f"    进入处理 其他元素 分支")
                                val = content.text.strip()
                                logging.info(f"    val: {val}")

                    logging.info(f"  最终 val: {val}")
                    if val:
                        base_info += label + " " + val + "\n"

        print(base_info.strip())

    finally:
        driver.quit()
    print("-" * 20)
    # 剧情简介
    synopsis_text = soup.select_one(
        '.related-info .indent [property="v:summary"]'
        ).text.strip().replace(" ", "")
    print(f"剧情简介: {synopsis_text}")

def get_book_info(driver, item_url):
    """
    将搜索到的书籍信息输出到终端: 用户相关: 是否标记, 标记日期, 我的标签, 我的短评
    条目信息: 类型, 官网(如果有), 制片国家, 语言, 首播, 季数, 集数, 单集片长, 又名, IMDb, 剧情简介

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        item_url (str): 电影/电视剧页面的 URL。
    """

    try:
        driver.get(item_url)
        time.sleep(3)  # 等待页面加载, 可以根据需要调整

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # --- 用户信息部分 (需要 Cookie) ---
        # 用 selenium 获取
        # 1. 是否标记
        marked_element = soup.select_one("#interest_sect_level > .j.a_stars > .mr10")
        if marked_element:
            marked_text = marked_element.contents[0].strip()
            print(f"是否标记: {marked_text}")
        else: print(f"是否标记: 否")

        # 2. 标记日期
        date_element = soup.select_one("#interest_sect_level > .j.a_stars > .color_gray")
        if date_element:
            date_text = date_element.text.strip()
            print(f"标记日期: {date_text}")
        else:
            print("没有找到标记日期")

        # 3. 我的标签
        # 使用next_sibling获取标签文字
        tags_element = soup.select_one("#interest_sect_level > div > span:nth-child(6)")
        if tags_element:
            tags_text = tags_element.text.strip()
            print(f"我的{tags_text}")
        else:
            print("没有找到标签")

        # 4. 我的短评
        comments_element = soup.select_one("#interest_sect_level > div > span:nth-child(8)")
        if comments_element:
            comments_text = comments_element.text.strip()
            print(f"我的短评: {comments_text}")
        else:
            print("没有找到我的短评")
        print("-" * 20)
        
        # --- 非用户信息部分 (也使用 Selenium) ---
        info = soup.find(id="info")
        base_info = ""

        if info:  # 确保找到了 id="info" 的元素
            for child in info.children:
                if isinstance(child, str):
                    # 处理纯文本节点
                    if child.strip():
                        base_info += child.strip() + " "
                elif child.name == "span":
                    # 只处理 span 标签
                    logging.info(f"当前 child: {child}")

                    if "pl" in child.get("class", []):
                        logging.info(f"  找到 span.pl: {child.text.strip()}")
                        label = child.text.strip()

                        val = ""
                        for sibling in child.next_siblings:
                            if sibling.name == 'a':
                                val = sibling.text.strip()
                                break
                            elif sibling.name == 'span':
                                break
                            elif isinstance(sibling, str):
                                val = sibling.strip()

                        base_info += label + " " + val + "\n"
                    else:
                        logging.info(f"  找到 span (无 class='pl'): {child.text.strip()}")
        else:
            print("没有找到 info")

        print(base_info.strip())

    finally:
        driver.quit()
    print("-" * 20)
    # 简介
    synopsis_element = soup.select_one('#link-report > div > div') 
    if synopsis_element:
        synopsis_text = ""
        for p in synopsis_element.find_all('p'):  # 遍历该 div 下的所有 <p> 标签
            synopsis_text += p.text.strip() + "\n"
        print(f"简介: \n{synopsis_text.strip()}")
    else:
        print("没有找到简介")
    
    print(f"简介: {synopsis_text}")


if __name__ == "__main__":
    cookie = 'SWEETCOOKIE'

    item_url = "https://movie.douban.com/subject/35898751/" # TODO 输入电影网址
    # item_url = "https://book.douban.com/subject/4820710/"
    
    driver_path = "E:\Gazer\drivers\msedgedriver.exe"
    driver = create_edge_driver(driver_path)
    add_cookies_to_driver(driver, cookie)

    get_movie_info(driver, item_url)
    # get_book_info(driver, item_url)