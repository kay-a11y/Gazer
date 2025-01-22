> **免责声明：** 在使用此指南之前，请务必仔细阅读并理解 [DISCLAIMER.md](DISCLAIMER.md) 文件中的免责声明。

---

# **基于 Selenium 的自动发微博脚本 (m.weibo.cn 版) - 在IDE中畅所欲言!**

Hi!! 分享一个刚写的自动发微博的 Python 脚本!

以下是你可能需要一个在IDE上发微博的脚本的原因:

*   打开网页手动发微博太慢🙅‍♀️
*   开启网页容易影响代码专注力, 看见微博就想刷停不下来
*   让 IDE **cover** 程序员/媛们, 即使是工作中也可以在IDE中尽情输出! （毕竟，谁会想到你在 IDE 里发微博呢？😏）

## **目标很明确：**

*   自动登录微博
*   填写微博内容!
*   上传图片（目前的版本只能上传一张图片）
*   选择微博可见性（有些内容~~见不得人~~只想分享给特定的人😉）
*   自动发布微博！

## **使用的工具和库：**

*   **Python 3:** 编程语言，简单易学，功能强大。
*   **Selenium:** 一个自动化测试工具，可以模拟用户在浏览器中的操作。
*   **Pillow (PIL):** 一个图像处理库，用来处理图片，比如从剪贴板读取图片。
*   **Beautiful Soup:** 用于解析HTML网页, 辅助调试。
*   **Edge WebDriver:** 微软 Edge 浏览器的驱动程序，用于控制 Edge 浏览器。
*   **send2trash:** 将文件安全地移动到回收站.

## **核心代码 (GhostwriterWeibo_v2.py)：**

```python
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

# ... (省略了部分函数)

def ghost_writer(driver, writer, onlyme=2, uppics=None):
    """填写微博文本, (可选)是否自己可见, (可选)上传图片, 自动发送微博"""
    wait = WebDriverWait(driver, 10)
    # 等待文本框可见
    weibo_textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div > span > textarea')))
    # 输入微博内容
    weibo_textarea.send_keys(writer)
    # 上传图片
    if uppics:
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        for path in uppics:
            file_input.send_keys(path)
        time.sleep(3)  # 等待上传
    # 选择可见性
    visible_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.visible')))
    visible_options = 3
    if 0 <= onlyme < visible_options:
        for i in range(onlyme):
            visible_button.click()
            time.sleep(0.3) # 增加延时, 确保选项加载完成
    # 提交微博
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.m-box.m-flex-grow1.m-box-model.m-fd-row.m-aln-center.m-justify-end.m-flex-base0 > a')))
    submit_button.click()
    time.sleep(2)
    print("微博发布成功")

def read_my_pics_from_clip(number=1):
    """读取剪贴板中的前number张图片, 储存并返回图片路径列表。
       注意: 目前只支持读取一张图片.
    """
    paths = []
    save_dir = r"E:\...\sendpics"  # TODO 修改为你自己的图片保存路径！
    os.makedirs(save_dir, exist_ok=True)  # 确保目录存在

    for i in range(number):
        try:
            # 从剪贴板获取图片
            im = ImageGrab.grabclipboard()
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

# ... (省略了部分函数)

if __name__ == "__main__":
    # 1. 设置 Edge WebDriver 的路径
    driver_path = "./drivers/msedgedriver.exe"  # TODO 修改为你自己的 WebDriver 路径！

    # 2. 创建 Edge WebDriver
    driver = create_edge_driver(driver_path)

    # 最大化窗口
    driver.maximize_window()

    # 3. 添加 Cookie
    cookies_str = "YOUR_Cookie" # TODO 将这里替换成你的 Cookie 字符串
    add_cookies_to_driver(driver, cookies_str, domain="m.weibo.cn")

    driver.get("https://m.weibo.cn/compose/")

    # 4. 填写微博内容、选择可见性、上传图片、发布微博
    writer = """
FU**K Johhny Silverhand
    """
    onlyme = 2  # 0:所有人, 1:好友圈, 2:仅自己
    uppics = read_my_pics_from_clip(number=1) # 读取图片数量目前只支持1张

    # 仅当 uppics 非空时才执行 ghost_writer 函数
    if uppics:
        ghost_writer(driver, writer, uppics=uppics, onlyme=onlyme)
        print(f"发送了 {len(uppics)} 张图片")
    else:
        ghost_writer(driver, writer, uppics=None, onlyme=onlyme)
        print("没有发送图片")

    # 5. 删除图片 (可选)
    if uppics:
        delete_pics(uppics, to_trash=True)  # to_trash=True/False 选择是否删除到回收站或直接删除

    # 6. 关闭浏览器
    driver.quit()
```

## **一些要点记录：**

### **1. Selenium 和 Bs4 元素定位对象和点击问题**

错误❌ *用 `soup` 定位到文本框之后, 直接点击*

```py
# 定位到文本框 (根据实际情况修改选择器)
textarea = soup.select_one('div > textarea')

if textarea:
    textarea.send_keys("这是我的第一条自动发布的微博！")
```

正确✅

`soup.select_one('div > textarea')` 返回的是 `BeautifulSoup` 对象，而不是 `Selenium` 的 `WebElement` 对象。所以，`textarea` 这个变量虽然代表了文本框，但它**没有 `send_keys()` 方法**。

`send_keys()` 方法是 `Selenium` 中 `WebElement` 对象特有的，用于模拟键盘输入。

```py
# 使用 driver.find_element 找到文本框元素
weibo_textarea = driver.find_element(By.CSS_SELECTOR, 'div > textarea')
# 点击文本框
weibo_textarea.click()
# 输入你想发布的微博内容
weibo_textarea.send_keys("这是我的第一条自动发布的微博！")

```

### **2. 上传文件按钮的元素定位:**

当点击网页上的"选择文件"按钮时，弹出的那个**选择本地文件的窗口**，它是**操作系统的原生窗口**，而不是浏览器窗口的一部分。`Selenium` 的 `WebDriver` 主要是用来操作浏览器内的网页元素的，它**无法直接控制这种原生的操作系统窗口**。

不过，可以用一些小技巧来绕过这个障碍。

**解决方案：**

通常，对于这种文件上传的场景，我们可以**直接把文件路径发送给那个隐藏的 `<input type="file">` 元素**，而不需要真正去操作那个弹出的文件选择窗口。

**具体步骤：**

1. **找到 `<input type="file">` 元素：**
    *   先用 `Selenium` 定位到那个用于上传文件的 `<input type="file">` 元素。通常，这个元素会被设置为隐藏，因为它在页面上的样式不美观, 而是通过一个按钮或者文字触发, 比如"选择文件", "上传图片"等等。
    *   用浏览器的开发者工具（F12）查看页面源代码，找到这个元素，并确定一个合适的 CSS 选择器或者其他定位方式。
    *   可以尝试搜索这个 input 元素的 selector 如 `input[type="file"]` 或 `[type="file"]` 来定位。

2. **使用 `send_keys()` 方法发送文件路径：**
    *   一旦找到了这个 `<input type="file">` 元素，就可以直接用 `send_keys()` 方法，把要上传的文件的**完整路径**作为参数传进去。
    *   例如：

    ```python
    # 定位到上传文件的 input 元素
    file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')

    # 发送文件路径 (改成你自己的文件路径)
    file_input.send_keys("C:/Users/Pictures/cute_Timid_Mushroom1.jpg")
    ```

### **3. 图片上传, 剪贴板读取:**

`pyperclip.paste()` 无法直接读取剪贴板中的图片. 需要使用 `Pillow` 库的 `ImageGrab.grabclipboard()` 来获取图片. 通过 `ImageGrab.grabclipboard()` 实现了从剪贴板读取图片. 支持使用截图软件将截图保存在剪贴板, 或在本地文件中复制的图片文件.

### **4.不同的网页版本选择**

一开始选择的是 `weibo.cn`, aka *微博手机版*, 这个版本需要先找到`高级`元素点击后跳转到发布微博 `https://weibo.cn/mblog/sendmblog?st=d00000`, 再次解析网页, 进行后续操作. 而且测试后发现发布的图片压缩严重, 转而使用 `m.weibo.cn` ( *微博HTML5版* ), 图片质量良好.

## **改进方向：**

*   **支持多张图片上传。**
*   **更智能的 Cookie 管理：** 自动获取最新的 Cookie，避免手动更新。
*   **更友好的用户界面：** 可以考虑使用图形界面，方便用户操作。
*   **支持更多的微博功能：** 例如定时发布、评论、转发等等。

### **使用和修改时的注意事项:**

*   **`driver_path`:** 修改为你自己的 `msedgedriver.exe` 的路径.
*   **`cookies_str`:** 修改成你自己的 `m.weibo.cn` 的 Cookie 字符串.
*   **图片保存路径:** `read_my_pics_from_clip` 函数中的 `save_dir` 修改成希望保存图片的路径.

### **脚本地址:** 

[GhostwriterWeibo_v2.py](https://github.com/kay-a11y/Gazer/blob/main/WeiboGaze/src/GhostwriterWeibo_v2.py)
