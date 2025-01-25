# Selenium 结合 Requests 爬取网易云音乐“我喜欢的”及评论数 API 分析

## 前言

基于 selenium 和 requests，在网易云音乐网页上爬取前 1000 首 "我喜欢的音乐" 以供后续数据分析。重点讲解了 `__init__.py` 文件的重要性、Cookie 的添加和检查方式、Selenium 选择器的使用技巧，特别是 `<iframe>` 的处理方法。同时，也分享了我对网易云评论数 API 接口的探索。提供完整的脚本。

## 爬取数据示例

1. 脚本输出示例

```txt
API package initialized
正在访问的页面标题: 网易云音乐
跳转后的页面标题: 三年二班夏树z喜欢的音乐 - 歌单 - 网易云音乐
已找到歌曲元素
评论数: 3118
已爬取 1 首歌曲
评论数: 841
已爬取 2 首歌曲
评论数: 115
已爬取 3 首歌曲
评论数: 8811
已爬取 4 首歌曲
评论数: 5089
已爬取 5 首歌曲
评论数: 209
已爬取 6 首歌曲
评论数: 56
已爬取 7 首歌曲
已达到最大爬取数量 7 或已爬取到最后一首歌曲，爬取结束
已达到最大爬取数量 7，爬取结束
已爬取的数据已保存到 E:\GazeKit\NeteaseCloudMusicGaze\data\raw\me_music_data.json
共爬取到 7 条数据。
```

2. json 文件示例

```json
[
    {
        "title": "Common Denominator [Bonus Track]",
        "singer": "Justin Bieber",
        "album": "My World",
        "comment": 3118
    },
    {
        "title": "I Found a Reason",
        "singer": "Cat Power",
        "album": "V for Vendetta",
        "comment": 841
    },
    {
        "title": "Bird Guhrl",
        "singer": "Antony and the Johnsons",
        "album": "V for Vendetta",
        "comment": 115
    },
    {
        "title": "Sunday Morning Birds (Singin' Hallelujah)",
        "singer": "Pajaro Sunrise",
        "album": "Pajaro Sunrise",
        "comment": 8811
    },
    {
        "title": "I'd Rather Be With You",
        "singer": "Joshua Radin",
        "album": "Simple Times",
        "comment": 5089
    },
    {
        "title": "Empty Apartment",
        "singer": "Johnny Stimson",
        "album": "Empty Apartment / Neighbors",
        "comment": 209
    },
    {
        "title": "lovely glow (feat. kayla)",
        "singer": "Sam Ock / Kayla",
        "album": "lovely glow",
        "comment": 56
    }
]
```

## 代码结构和使用方法

### **代码结构**

1. `create_edge_driver` 创建 Edge WebDriver
2. `add_cookies_to_driver` 将 Cookie 添加到 Edge WebDriver
3. `crawl_playlst_data` 爬取我喜欢的歌曲播放列表前 1000 首歌, 再通过`crawl_detail_page` 使用 requests 爬取歌曲详情页, 返回的包含歌曲信息的字典, 将每首歌的字典添加到列表, 最后返回所有歌曲信息的字典列表, 写入 Json 文件

### **使用方法**

1. 克隆或下载项目代码。
2. 安装依赖：`pip install -r requirements.txt`
3. 修改 `yo_i_pwned_your_playlist.py` 文件中的配置：
    *   填写你的 `COOKIE`。
    *   设置 `Edge WebDriver` 的路径。
    *   填写网易云“我喜欢的音乐”页面 `URL`
    *   设置最大爬取歌曲数量，默认为 1000
4. 运行 `yo_i_pwned_your_playlist.py` 文件
5. 爬取结果将保存在 `data/raw/me_music_data.json` 文件中

## `__init__.py` 文件的必要性

```python
# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将 API 目录添加到 Python 路径中, 确保 src 下的 __init__.py 不为空
sys.path.append(current_dir)

# print(sys.path)

# 导入 get_comment 函数
from API.get_comment import get_comment
```

### 代码解释

1. **`current_dir = os.path.dirname(os.path.abspath(__file__))`:**

    *   `current_dir` 变量被赋值为 `"...\\NeteaseCloudMusicGaze\\src"`，也就是 `yo_i_pwned_your_playlist.py` 文件所在的目录的绝对路径。

    **代码目的：**

    这行代码的目的是**获取当前文件 (yo_i_pwned_your_playlist.py) 所在的目录 (src) 的绝对路径**。

    **为什么要获取这个路径？**

    在代码中，获取这个路径是为了将 `src` 目录添加到 `sys.path` 中，这样 Python 解释器才能找到 `src/API` 目录下的 `get_comment` 模块。

2. **`sys.path.append(current_dir)`:**
    *   `sys.path` 是一个 Python 列表，包含了 Python 解释器在导入模块时搜索的路径。
    *   `sys.path.append(current_dir)` 将 `current_dir` 添加到 `sys.path` 中，这意味着 Python 解释器在导入模块时，也会搜索 `"...\\NeteaseCloudMusicGaze\\src"` 这个目录。

3. **`from API.get_comment import get_comment`:**
    *   这行代码从 `API` 模块中导入 `get_comment` 函数。
    *   由于前面已经将 `"...\\NeteaseCloudMusicGaze\\src"` 添加到了 `sys.path`，Python 解释器能够找到 `API` 模块（也就是 `"...\\NeteaseCloudMusicGaze\\src\\API` 目录）。

### **`__init__.py` 文件的作用：**

`__init__.py` 文件有两个主要作用：

1. **将目录标记为 Python 包 (Package):**  一个包含 `__init__.py` 文件的目录被视为一个 Python 包。这使得你可以使用 `.` 运算符来导入包内的模块，例如 `from API.get_comment import get_comment`。
2. **执行包的初始化代码:**  当一个包被导入时，`__init__.py` 文件中的代码会被执行。你可以在 `__init__.py` 文件中放置一些初始化代码，例如导入常用的模块、定义全局变量等。

### **有必要删除 `__init__.py` 吗?**

*   **在 Python 3.3 之前，`__init__.py` 文件是必需的。**  如果一个目录中没有 `__init__.py` 文件，Python 解释器不会将其视为一个包，你也无法导入其中的模块。
*   **从 Python 3.3 开始，`__init__.py` 文件不再是必需的。**  这得益于 **Implicit Namespace Packages** (隐式命名空间包) 的引入。即使一个目录中没有 `__init__.py` 文件，Python 解释器也可以将其视为一个包。

**在这个项目中：**

*   **`src/API/__init__.py`:**  这个文件是必需的，因为它将 `API` 目录标记为一个包，使得你可以从其他模块中导入 `get_comment` 函数 (例如 `from API.get_comment import get_comment`)。
*   **`src/__init__.py`:**  这个文件不是必需的 (除非你在 Python 3.3 之前的版本中运行代码)。因为 `src` 目录下没有 `__init__.py` 文件, 你无法直接通过 `from src.API.get_comment import get_comment` 导入 `get_comment` 函数.

### **总结：**

*   `src/API/__init__.py` 是必需的，用于将 `API` 目录标记为包。
*   `src/__init__.py` 不是必需的 (除非你在 Python 3.3 之前的版本中运行代码)。
*   `sys.path.append(current_dir)` 这行代码使得 Python 解释器能够找到 `src` 目录下的模块。
*   为了代码的可读性和可维护性，建议保留 `src/API/__init__.py` 文件。
*   为了代码的兼容性，建议保留 `src/__init__.py` 文件。即使在 Python 3.3 及以后的版本中它不是必需的，但保留它可以确保你的代码在所有 Python 版本中都能正常工作。

## Cookie 添加、检查方法与 JavaScript 禁用问题

增加了 `access_cookie.py` 示例脚本, 可以测试是否成功添加cookie。

**如何知道是否添加 Cookie 成功？**

可以通过以下方法来判断 Cookie 是否添加成功：

1. **检查 `driver.get_cookies()`:**

    ```python
    add_cookies_to_driver(driver, cookie)
    print(driver.get_cookies())
    ```

    在添加 Cookie 后，打印 `driver.get_cookies()` 的返回值，查看你添加的 Cookie 是否在其中。

2. **访问需要登录的页面:**

    ```python
    add_cookies_to_driver(driver, cookie)
    driver.get("https://music.163.com/#/playlist?id=634065508")  # 访问我喜欢的音乐页面, 网易云未登录时只显示前6首, 登录时可以查看前1000首
    time.sleep(5)
    # 检查页面内容或 URL，判断是否处于登录状态
    ```

    添加 Cookie 后，访问一个需要登录才能访问的页面（例如个人主页），然后检查页面的内容或 URL，看看是否处于登录状态。

3. **查看浏览器的开发者工具:**
    *   在有头模式下, 打开浏览器的开发者工具 (F12)，切换到 "Application" (或 "Storage") 标签页，然后选择 "Cookies"，查看你的 Cookie 是否被正确添加。

**说明：**

*   在 `create_edge_driver` 函数中你可以选择禁用 JavaScript。

**但有时候取消注释 `edge_options.add_argument("--disable-javascript")` 来禁用 JavaScript 能提供的信息不够准确, 原因可能有：**

1. **你的 Cookie 中包含了足够的信息，让服务器认为你已经登录，即使没有 JavaScript，服务器也返回了包含歌曲数据的 HTML。**  这种情况是有可能的，特别是对于一些简单的页面，服务器可能不会强制要求客户端执行 JavaScript。
2. 即使代码中添加了禁用 JavaScript 的选项，在某些情况下，JavaScript 仍可能未被完全禁用。这可能是由于 **Selenium 版本、浏览器驱动或代码逻辑** 等原因造成的。

**如何验证 JavaScript 是否被禁用？**

你可以在 `driver.get(fav_lst_url)` 之后，添加以下代码：

```python
print(driver.execute_script("return navigator.userAgent;"))
print(driver.execute_script("return typeof window.cdc_adoQpoasnfa76pfcZLmcfl_Array === 'undefined'"))
```

这两行代码会分别打印：

1. **浏览器的 User-Agent:**  你可以查看 User-Agent 中是否包含 "Headless" 字样，以判断是否处于无头模式。
2. **`window.cdc_adoQpoasnfa76pfcZLmcfl_Array` 变量是否存在:**  一些网站会使用这个变量来检测 Selenium，如果返回 `True`，则表示 JavaScript 被禁用。如果返回 `False`，则表示 JavaScript 仍然在运行。

**为了稳定性和可靠性, 应该使用 Selenium 并且不要禁用 JavaScript.**

## selenium 的选择器一些说明

> 问题: 把选择器改成 `div.n-songtb` 和 `.m-table.m-table` , 以尝试选中整个 1000 首的歌曲列表, 在元素选项卡中可以搜索到, 但无法使用 selenium 找到歌曲元素。

**页面结构：**
    *   从 HTML 结构中我们可以看到，歌曲列表实际上包含在一个 `<iframe>` 标签中！
    *   `<iframe>` 标签用于在当前 HTML 文档中嵌入另一个 HTML 文档。
    *   **Selenium 默认情况下只能操作当前 HTML 文档中的元素，无法直接操作 `<iframe>` 中的元素。**
    *   所以，之前的选择器都无法选中歌曲列表，因为它们都在 `<iframe>` 中。

**解决方案：切换到 `<iframe>`**

我们需要先让 Selenium 将“视线”切换到 `<iframe>` 中，才能操作其中的元素。

**如何切换到 `<iframe>`？**

Selenium 提供了 `switch_to.frame()` 方法来切换到 `<iframe>`。

**你可以通过以下几种方式定位 `<iframe>`：**

*   **id 或 name 属性：** 
    *   如果 `<iframe>` 有 `id` 或 `name` 属性，可以直接使用这些属性来定位。

        ```python
        driver.switch_to.frame("g_iframe")  # 假设 <iframe> 的 id 或 name 是 "g_iframe"
        ```

*   **索引：**
    *   可以使用 `<iframe>` 的索引来定位，索引从 0 开始。

        ```python
        driver.switch_to.frame(0)  # 切换到第一个 <iframe>
        ```

*   **WebElement：**
    *   可以使用 `find_element` 方法先找到 `<iframe>` 元素，然后切换到该元素。

        ```python
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        ```

**在这个例子中，`<iframe>` 标签具有 `name` 属性，其值为 `contentFrame`。因此，我们可以使用 `driver.switch_to.frame("contentFrame")` 来切换到这个 `<iframe>`。**

```py
driver.switch_to.frame("contentFrame") 
```

## 接口探究

### **获取评论的接口 - 一个简化的评论数 API 接口**

一般的获取评论的接口是 `https://music.163.com/weapi/comment/resource/comments/get?csrf_token=`(使用 `POST` 方法)。

不同的单曲的 `params` 和 `encSecKey` 参数是唯一的。`get_comment` 函数在删除 `music_id` 的情况下依然可以根据某一个单曲的唯一 `params` 和 `encSecKey`得到音乐评论数, 所以这个函数其实不需要显式传入音乐id, `params` `encSecKey` 和音乐 id 是关联的。所以目标是要知道 `params` 和 `encSecKey` 是如何加密的。

这两个参数的值是通过 JavaScript 加密生成的, 需要找到对应的 JavaScript 代码, 分析它的加密逻辑, 然后用 Python 来实现这个加密过程。比较复杂, 后续有机会再更新。

参考知乎 `https://www.zhihu.com/question/36081767` 问题下提到的一个旧版的API接口, `https://music.163.com/api/v1/resource/comments/R_SO_4_{music_id}`, 但是它是使用GET请求获取评论数量的。

这个接口没有加密，我们可以直接构造 GET 请求来获取评论数据。

**代码示例:**

```py
import requests, json

music_id = "1886064452"  # 替换成你要查询的歌曲 ID
get_comment_url = f"https://music.163.com/api/v1/resource/comments/R_SO_4_{music_id}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

response = requests.get(get_comment_url, headers=headers)

if response.status_code == 200:
    try:
        result = response.json()
        total_count = result["total"]  # 注意，这里的键名是 "total"
        print(f"评论数: {total_count}")
    except (KeyError, json.JSONDecodeError) as e:
        print(f"解析 JSON 失败: {e}")
        print(f"响应内容: {response.text}")
else:
    print(f"请求失败! 状态码: {response.status_code}")
    print(response.text)

```

**需要注意的点：**

*   **不一定所有歌曲都适用：**  这个接口可能只适用于部分歌曲，或者可能在未来某个时间失效。
*   **限速：**  即使这个接口没有加密，网易云也可能会对请求频率进行限制，如果请求过于频繁，可能会被屏蔽。
*   **`total` 键:** 返回的 JSON 数据中，评论总数对应的键名是 `total`，而不是 `data` 里的 `totalCount`。

## **项目地址:** [Github 链接](https://github.com/kay-a11y/Gazer)
   **文件相对路径**: `NeteaseCloudMusicGaze/src/API/get_comment.py`
   `NeteaseCloudMusicGaze/src/access_cookie.py` `NeteaseCloudMusicGaze/src/yo_i_pwned_your_playlist.py`
   https://github.com/kay-a11y/Gazer/blob/main/NeteaseCloudMusicGaze/src/access_cookie.py

## **脚本地址:** 

[yo_i_pwned_your_playlist.py](https://github.com/kay-a11y/Gazer/blob/main/NeteaseCloudMusicGaze/src/yo_i_pwned_your_playlist.py)

[access_cookie.py](https://github.com/kay-a11y/Gazer/blob/main/NeteaseCloudMusicGaze/src/access_cookie.py)

[get_comment.py](https://github.com/kay-a11y/Gazer/blob/main/NeteaseCloudMusicGaze/src/API/get_comment.py)




