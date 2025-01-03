import time 
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from PIL import ImageGrab, Image
import shutil
import send2trash

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
    edge_options.add_argument("--headless")
    # 禁用 GPU 加速（在某些情况下可以提高稳定性）
    edge_options.add_argument("--disable-gpu")
    edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 设置 driver 的路径
    service = EdgeService(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

def add_cookies_to_driver(driver, cookies_str, domain="m.weibo.cn"):
    """
    将 Cookie 添加到 Edge WebDriver。

    Args:
        driver (webdriver.Edge): Edge WebDriver 对象。
        cookies_str (str): Cookie 字符串, 格式为 "key1=value1; key2=value2; ..."。
        domain (str, optional): Cookie 的域名. 针对微博, 可以设置为"m.weibo.cn". Defaults to "m.weibo.cn".
    """
    # 访问一个页面，以便设置 Cookie. 必须与cookie同域
    driver.get(f"https://{domain}")
    cookies = cookies_str.split("; ")
    for cookie in cookies:
        try:
            key, value = cookie.split("=", 1)
            driver.add_cookie({"name": key.strip(), "value": value.strip(), "domain": "m.weibo.cn", "path": "/"})
        except ValueError:
            print(f"Invalid cookie format: {cookie}")

def ghost_writer(driver, writer, onlyme=2, uppics=None):
    """填写微博文本, (可选)是否自己可见, (可选)上传图片成功后自动删除图片, 自动发送微博

    Args:
        driver (_type_): _description_
        writer (string): 填写微博文本
        onlyme (int, optional): 0:所有人, 1:好友圈, 2:仅自己. Defaults to 1.
        uppics (list, optional): 图片路径列表. Defaults to None.
    """

    wait = WebDriverWait(driver, 10)

    # 等待文本框可见
    weibo_textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div > span > textarea')))
    # driver.execute_script("arguments[0].scrollIntoView();", weibo_textarea)

    # 使用 JavaScript 设置文本框的值
    driver.execute_script("arguments[0].value = arguments[1];", weibo_textarea, writer)
    # 触发 input 事件
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", weibo_textarea)

    # 上传图片
    if uppics:
        # 等待上传按钮可见
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        for path in uppics:
            file_input.send_keys(path)
        # 等待上传完成的逻辑, 这里需要根据实际情况来写
        time.sleep(3)  # 假设上传需要3秒钟, 可以根据实际情况调整

    # 选择可见性
    # 等待可见性按钮可见
    visible_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.visible')))

    visible_options = 3 # 0:所有人, 1:好友圈, 2:仅自己
    if 0 <= onlyme < visible_options:
        for i in range(onlyme):
            visible_button.click()
            # time.sleep(0.3)
    else:
        print(f"可见性参数错误: onlyme={onlyme}, 应该在 0, 1, 2 中选择.")

    try:
        # 提交微博
        # 等待提交按钮可见
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.m-box.m-flex-grow1.m-box-model.m-fd-row.m-aln-center.m-justify-end.m-flex-base0 > a')))

        submit_button.click()
        print("微博发布成功")
    except Exception as e:
        print(f"微博发布失败: {e}")
    
def read_my_pics_from_clip(number=1):
    """读取剪贴板中的前number张图片, 储存并返回图片路径列表
    Args:
        number (int, optional): 读取图片数量目前只支持1张. Defaults to 1.
    Returns:
        list: 图片路径列表, 图片不存在则返回空列表
    """
    paths = []
    save_dir = r"E:\Gazer\WeiboGaze\data\sendpics"
    os.makedirs(save_dir, exist_ok=True)  # 确保目录存在

    for i in range(number):
        try:
            # 从剪贴板获取图片
            im = ImageGrab.grabclipboard()

            # ImageGrab.grabclipboard() 返回各种类型:
            # None: 剪贴板为空
            # Image: 剪贴板中有一张图片
            # list: 剪贴板中有一系列文件, 使用时需要再次判断列表内元素类型是否为str

            if im is None:
                print(f"剪贴板中没有图片或第{i+1}张图片不存在")
                break  # 剪贴板为空，停止循环
            elif isinstance(im, Image.Image):
                # 如果是图片, 则储存
                timestamp = int(time.time())
                filename = f"mypics_{timestamp}_{i}.png"
                filepath = os.path.join(save_dir, filename)
                im.save(filepath, 'PNG')
                paths.append(filepath)
            elif isinstance(im, list):
                # 如果是列表, 则判断是否为文件路径
                for item in im:
                    if isinstance(item, str) and os.path.isfile(item):
                        # 如果是文件，则复制到目标文件夹
                        timestamp = int(time.time())
                        filename = f"mypics_{timestamp}_{i}.png"
                        filepath = os.path.join(save_dir, filename)
                        shutil.copy(item, filepath)
                        paths.append(filepath)
                        break  # 只取列表中的第一个文件
                    else:
                        print("剪贴板中包含非图片文件或非字符串.")
                        return [] # 返回空列表
            else:
                print("剪贴板中包含无法识别的内容.")
                return [] # 返回空列表
            
        except Exception as e:
            print(f"处理第 {i+1} 张图片时出错: {e}")
            return [] # 返回空列表

    return paths

def delete_pics(paths, to_trash=True):
    """删除图片
    Args:
        paths (list): 图片路径列表
        to_trash (bool, optional): 是否删除到回收站. Defaults to True.
    """
    for path in paths:
        try:
            if to_trash:
                # 使用 send2trash 安全地删除文件到回收站
                send2trash.send2trash(path)
                print(f"已删除图片到回收站: {path}")
            else:
                # 使用os.remove 直接删除文件, 不会进入回收站
                os.remove(path)
                print(f"已删除图片: {path}")
        except Exception as e:
            print(f"删除图片 {path} 失败: {e}")

if __name__ == "__main__":

    # 1. 设置 Edge WebDriver 的路径
    driver_path = r"E:\..\msedgedriver.exe"

    # 2. 创建 Edge WebDriver
    driver = create_edge_driver(driver_path)

    # 最大化窗口
    driver.maximize_window()

    # 3. 添加 Cookie
    cookies_str = "SWEET_COOKIE🐱"  # TODO 将这里替换成你的 Cookie 字符串
    add_cookies_to_driver(driver, cookies_str)

    driver.get("https://m.weibo.cn/compose/") # TODO

    # 4. 填写微博内容、选择可见性、上传图片、发布微博
    writer = """
FU**K U Johhny Silverhand
    """ # TODO
    onlyme = 2 # TODO 0:所有人, 1:好友圈, 2:仅自己
    uppics = read_my_pics_from_clip(number=1) # 读取图片数量目前只支持1张

    # 仅当 uppics 非空时才执行 ghost_writer 函数
    if uppics:
        ghost_writer(driver, writer, uppics=uppics, onlyme=onlyme)
    else:
        ghost_writer(driver, writer, uppics=None, onlyme=onlyme)

    # 5. 删除图片 (可选)
    if uppics:
        delete_pics(uppics, to_trash=True)  # TODO: to_trash=True/False 选择是否删除到回收站或直接删除

    # 6. 关闭浏览器
    driver.quit()