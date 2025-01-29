# 解锁豆瓣高清海报：深度爬虫与requests进阶之路

## 前瞻

`PosterBandit` 这个脚本能够根据用户指定的日期，爬取你看过的影视**最高清**的海报，并自动拼接成指定大小的长图。

你是否发现直接从豆瓣爬取下来的海报清晰度很低？ 使用 `.pic .nbg img` CSS 选择器，在 `我看过的影视` 界面找到图片元素并直接爬取（爬取深度为 0），甚至不用太重视 `time.sleep()`。好处是速度超快，坏处是这样爬取的海报都是被压缩过的，画质很差。任何一个脚本小子都不会屈服于这样的质量。

想要爬取**最高清的海报**，答案一定是**增加爬取深度**！

## **脚本地址:**

[PosterBandit.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/PosterBandit.py)

## 使用方法

1.  克隆或下载项目代码。
2.  安装依赖: `pip install requests`，或者克隆项目代码后 `pip install -r requirements.txt`
3.  修改脚本内部的常量 `DEFAULT_POSTER_PATH`，设置默认保存路径。
4.  修改主函数处的 `poster_save_path` 保存路径。
5.  修改主函数处的起始日期 `target_date_1` 和截止日期 `target_date_2`。
6.  填写你的 `cookies`。
7.  运行脚本 `PosterBandit`。

## 准备工作 - JavaScript 动态加载？

首先测试豆瓣海报相关页面是否是通过 **JavaScript 动态加载**的。在浏览器上设置“不允许网站使用 JavaScript”，刷新豆瓣界面，页面几乎全部正常加载。这很奇怪，和我之前做的脚本使用 requests 打印 raw HTML 得出用户相关信息以及影视相关信息都是使用 JS 动态加载的结论相悖。

先不管了，总之经过测试，完全可以只用 requests 爬取影视海报。😿

## 脚本构思

1.  默认从第 1 页开始爬取，根据**输入的起止日期**参数，依次检查每页的所有条目是否在指定日期之间，如果是，爬取该条目的海报图片，如果不是，停止爬取；（`requests`）
2.  根据输入的长宽（长x张, 宽x张）参数，将海报**拼接为长图**（`pillow` / `open CV`）
3.  **自动计算爬取耗时**，包括每条爬取耗时和总耗时，并在完成时输出。（`time`）

### 开始纸上谈兵

先以影视为例，书籍后面再核对元素选择器是否需要修改（做到书籍爬取的时候需要在开头增加选择书/影函数）。

构造请求来翻页，可以绕过使用选择器寻找 "下一页" 的元素。

首先访问 `https://movie.douban.com/mine?status=collect`，观察不同页的载荷。

第 1 页
载荷 / payload

```txt
start: 0
sort: time
rating: all
mode: grid
type: all
filter: all
```

请求网址 (GET)
`https://movie.douban.com/people/665544778/collect?start=0&sort=time&rating=all&mode=grid&type=all&filter=all`

---

第 2 页
载荷 / payload

```txt
start: 15
sort: time
rating: all
mode: grid
type: all
filter: all
```

请求网址 (GET)
`https://movie.douban.com/people/665544778/collect?start=15&sort=time&rating=all&mode=grid&type=all&filter=all`

---

第 3 页
载荷 / payload

```txt
start: 30
sort: time
rating: all
mode: grid
type: all
filter: all
```

请求网址 (GET)
`https://movie.douban.com/people/665544778/collect?start=30&sort=time&rating=all&mode=grid&type=all&filter=all`

**结论：**

要获取不同页数的 URL，只需要改变 URL 中的 `start=0` 参数，第 x 页 URL 的 `start` 参数是 `(x - 1) * 15`。

#### 代码实现方案

使用**广度优先搜索 (Breadth-First Search, BFS)**：一种常用的爬虫策略，先访问同一层级的所有页面，然后再访问下一层级的页面。**最大爬取深度为 3**，下面我在括号中标记了爬取深度。

1.  构造不同页数的 URL，默认从第 1 页开始爬取。
2.  以默认第一页或指定的页数作为爬取的**起始页** (*Level 0*)，找到所有包含电影条目的 div 元素，最大为 15 个。 ▶️ `get_movie_elements`

    电影条目 CSS 选择器: `#content > div.grid-16-8.clearfix > div.article .item.comment-item`
3.  在电影条目的 div 元素内找到对应的**日期元素**和**具体条目链接** ▶️ `get_movie_info`

    日期 CSS 选择器: `#content div.info span.date`

    具体条目 CSS 选择器: `#content div.article div.pic > a`

    检查是否在指定的起止日期参数之间 ▶️ `compare_date`
4.  进入具体条目链接 (*Level 1*)，找到**清晰的海报列表链接** ▶️ `get_poster_url` `crawl_link`

    海报列表链接 CSS 选择器: `#mainpic > a`
5.  进入海报列表页 (*Level 2*)，找到默认的**第一张海报** ▶️ `crawl_link`

    第一张海报 CSS 选择器: `#content > div > div.article > ul > li:nth-child(1) > div.cover > a > img`
6.  进入未压缩的**最终海报的链接** (*Level 3*)  ▶️ `get_poster_url`

    最终海报 CSS 选择器: `#content div.article div.cover > a`
7.  下载图片**保存**到指定路径，创建文件夹名称，根据日期定义，如 `2024_1_1_2024_12_31`  ▶️ `create_folder` `save_poster`


### 文件结构

```txt
Gazer/
├── DoubanGaze/
│   ├── data/
│   │   └── poster/
│   │       └── 2024_1_1_2025_1_31/
│   └── src/
│       └── PosterBandit.py
└── ...
```

## 代码实践

### `find`, `find_all`, `select`, 和 `select_one` 几个方法的辨析

**先来说说 `find` 和 `find_all`，它们是一对，都是基于标签名和属性来查找元素：**

*   **`find(name, attrs, recursive, string, **kwargs)`**
    *   **用途：** 查找 **第一个** 匹配条件的 **标签**。
    *   **参数：**
        *   `name`:  标签名，比如 `'div'`, `'img'`, `'a'`。
        *   `attrs`:  一个字典，包含属性的键值对，比如 `{'class': 'title', 'id': 'myImage'}`。
        *   `recursive`:  一个布尔值，表示是否递归查找所有子孙标签，默认为 `True`。
        *   `string`:  查找包含特定文本的标签。
        *   `**kwargs`:  可以直接写属性名作为参数，比如 `class_='title'`, `id='myImage'`。
    *   **返回值：** 如果找到，返回一个 `Tag` 对象；如果没找到，返回 `None`。

*   **`find_all(name, attrs, recursive, string, limit, **kwargs)`**
    *   **用途：** 查找 **所有** 匹配条件的 **标签**。
    *   **参数：**
        *   `name`, `attrs`, `recursive`, `string`, `**kwargs`:  和 `find` 相同。
        *   `limit`:  一个整数，限制返回的结果数量。
    *   **返回值：** 返回一个 `ResultSet` 对象，它是一个包含所有匹配标签的列表。

**举个例子：**

```html
<html>
<body>
  <div class="movie">
    <img src="poster1.jpg" class="poster" id="poster1">
    <p class="title">电影1</p>
  </div>
  <div class="movie">
    <img src="poster2.jpg" class="poster" id="poster2">
    <p class="title">电影2</p>
  </div>
</body>
</html>
```

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, 'html.parser')

# 查找第一个 class 为 "movie" 的 div 标签
first_movie_div = soup.find('div', class_='movie')

# 查找所有 class 为 "movie" 的 div 标签
all_movie_divs = soup.find_all('div', class_='movie')

# 查找第一个 src 属性为 "poster1.jpg" 的 img 标签
first_poster = soup.find('img', src='poster1.jpg')

# 查找所有 class 为 "poster" 的 img 标签
all_posters = soup.find_all('img', class_='poster')

# 查找所有包含文本 "电影" 的 p 标签
movie_titles = soup.find_all('p', string='电影') #注意这个用法, 和class_='title'是不一样的, 一个是找文本内容, 一个是找属性内容
```

**再来说说 `select` 和 `select_one`，它们是另一对，都是基于 CSS 选择器来查找元素：**

*   **`select_one(selector)`**
    *   **用途：** 使用 CSS 选择器查找 **第一个** 匹配的 **标签**。
    *   **参数：**
        *   `selector`:  一个字符串，表示 CSS 选择器。
    *   **返回值：** 如果找到，返回一个 `Tag` 对象；如果没找到，返回 `None`。

*   **`select(selector)`**
    *   **用途：** 使用 CSS 选择器查找 **所有** 匹配的 **标签**。
    *   **参数：**
        *   `selector`:  一个字符串，表示 CSS 选择器。
    *   **返回值：** 返回一个列表，包含所有匹配的标签。

**CSS 选择器的优点：**

*   **简洁灵活：**  CSS 选择器语法非常强大，可以非常灵活地定位元素。
*   **与前端开发衔接：**  如果你熟悉前端开发，使用 CSS 选择器会非常顺手。

**举个例子 (继续用上面的 HTML)：**

```python
# 查找第一个 class 为 "movie" 的 div 标签
first_movie_div = soup.select_one('div.movie')

# 查找所有 class 为 "movie" 的 div 标签
all_movie_divs = soup.select('div.movie')

# 查找第一个 id 为 "poster1" 的 img 标签
first_poster = soup.select_one('img#poster1')

# 查找所有 class 为 "poster" 的 img 标签
all_posters = soup.select('img.poster')

# 查找所有 class 为 "movie" 的 div 标签下的 p 标签
movie_titles = soup.select('div.movie p')
```

**总结一下：**

| 方法        | 用途                         | 基于                      | 返回值                                       |
| :---------- | :--------------------------- | :------------------------ | :------------------------------------------- |
| `find`      | 查找第一个匹配的标签         | 标签名和属性              | `Tag` 对象 或 `None`                          |
| `find_all`  | 查找所有匹配的标签         | 标签名和属性              | `ResultSet` 对象 (标签列表)                   |
| `select_one` | 查找第一个匹配的标签         | CSS 选择器                | `Tag` 对象 或 `None`                          |
| `select`    | 查找所有匹配的标签         | CSS 选择器                | 列表 (包含所有匹配的标签)                     |

**什么时候用哪个？**

*   **简单情况：** 如果只是根据简单的标签名和属性查找，`find` 和 `find_all` 就足够了。
*   **复杂情况：** 如果需要根据复杂的条件查找，或者你更熟悉 CSS 选择器，那么 `select` 和 `select_one` 更合适。
*   **只要一个结果：** 如果你确定只需要一个结果，或者只关心第一个结果，就用 `find` 或 `select_one`。
*   **需要所有结果：** 如果你需要所有匹配的结果，就用 `find_all` 或 `select`。

### **为什么 `headers` 中的 `"cookies": cookies` 要改成 `"Cookie": cookies`?**

这是因为在 HTTP 请求的头部信息中，**用于传递 Cookie 的字段名是 `Cookie`**（注意首字母大写），而不是 `cookies`。

*   **服务器端识别的是 `Cookie` 这个字段名。** 当服务器收到你的请求时，它会去解析 `Cookie` 字段，获取你发送的 Cookie 信息。如果你写成 `cookies`，服务器就无法正确识别和处理你的 Cookie 了。
*   **这是 HTTP 协议的规定。** 就像你写信要按照固定的格式写地址一样，HTTP 协议也规定了请求头和响应头中各个字段的名称和格式，`Cookie` 字段就是其中之一。

所以，为了让服务器能够正确识别你发送的 Cookie，我们必须使用 `"Cookie": cookies`。

### **关于在 `div` 元素内部继续查找的选择器，有两种选择：**

**1. 只针对 `div` 内部编写选择器 (相对路径)：**

*   这种方式更简洁，也更符合当前的代码逻辑。
*   选择器直接从当前 `div` 元素的子元素开始写。
*   例如，如果当前 `div` 元素是 `movie_element`，那么 `movie_element.select_one("div.info > ul > li:nth-child(3)")` 就表示选择当前 `div` 元素内部 `div.info > ul` 下的第三个 `li` 元素。

**2. 从 `#content` 开始编写选择器 (绝对路径)：**

*   这种方式也是可以的，但是**没有必要，也更繁琐**。
*   选择器需要从 `#content` 开始，写出完整的路径。
*   例如，`movie_element.select_one("#content > div.grid-16-8.clearfix > div.article .item.comment-item")` 也能选择到相同的日期元素，但是**这种写法很冗长，而且容易出错。而且我们已经通过`movie_elements`缩小了范围, 没有必要继续从`#content`开始了**

### **Python 的函数参数传递规则 - 关于 `page_id=1` 参数位置：**

把 `page_id=1` 这个参数放到任意参数前面会导致 IDE 提示错误，而放到最后就不会报错，这是因为 **Python 的函数参数传递规则**：

*   **位置参数：** 按照定义顺序传递的参数，必须按照顺序传入。
*   **关键字参数：** 通过参数名传递的参数，可以不按照顺序传入。
*   **默认参数：** 在函数定义时设置了默认值的参数，如果调用时没有传入该参数，则使用默认值。

**规则：**

*   **位置参数必须在关键字参数前面。**
*   **默认参数必须在位置参数后面。**
*   `page_id=1` 是一个默认参数，所以它必须放在位置参数 `cookies`, `target_date_1`, `target_date_2`, `poster_save_path` 后面，否则 IDE 会报错。

**所以，只能把 `page_id=1` 放到最后。**

### **关于 BeautifulSoup 解析：**

是否总是使用 `soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')`? 是否可以只用 `soup = BeautifulSoup(response, 'html.parser')`?

**答案是：不建议。**

*   `response` 对象默认是字节串，需要先解码成字符串，再交给 `BeautifulSoup` 解析。
*   如果你的 HTML 编码不是 `utf-8`，需要使用正确的编码方式来解码（例如 `gbk`，`iso-8859-1` 等）。

**建议：**
*   **始终使用 `response.content.decode('utf-8', errors='ignore')`** 来解码，`errors='ignore'` 是为了忽略解码错误, 如果遇到无法解码的字符, 会忽略它, 不会报错。
*   **最好在请求的时候设置正确的编码:**
    *   ```python
        response = requests.get(target_link)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        ```
    *   `response.apparent_encoding` 会根据响应内容尝试识别正确的编码方式，并设置到 `response.encoding` 中，这样 `response.text` 会使用正确的编码来解码.

### **关于 while 循环中的日期比较：**

*   在 while 循环中，已经有 `if not compare_date(target_date_1, target_date_2, viewed_date_text): break` 跳出循环，为什么还要在最后加上 `if not compare_date(target_date_1, target_date_2, viewed_date_text): break`?
*   **理解 `break` 的作用域**
    *   第一个 `if not compare_date(...) : break` 是在 `for movie_element in viewed_movie_elements:` 循环内部，它只能跳出当前的 `for` 循环。
    *   为了在所有页面都爬取完毕后跳出 `while True` 的循环，还需要在 while 循环的末尾加上 `if not compare_date(...) : break`。
    *   **但是需要注意的是:** `viewed_date_text`有可能为空, 这会导致错误, 你需要设置一个默认值 `viewed_date_text = ""`

### 418 I'm a teapot?? Bring 'em on!!

#### 418 错误

#### **在哪里开始碰到 418 错误?**

**在 `get_poster_url` 函数内部，当访问海报页面的时候，被豆瓣服务器拒绝了，并返回 `418` 错误。**
**之前所有的步骤，包括访问列表页和详情页，都是成功的 (200)**。

**错误信息：**

*   `418 Client Error:  for url: https://movie.douban.com/subject/3586996/`
*   `418 Client Error:  for url: https://movie.douban.com/subject/2373195/`
*   `418 Client Error:  for url: https://movie.douban.com/subject/10449575/`

#### **418 错误解决方案**

##### **1.  理解 418 错误**

*   **状态码含义：** 418 是一个 HTTP 状态码，全称是 `I'm a teapot`，本意表示服务器是一个茶壶，而不是咖啡机，无法提供请求的服务。
*   **反爬虫应用：** 网站会故意返回 418 状态码，来识别和阻止爬虫的访问。
*   **选择 418 的原因：** 这是一个不常见的 HTTP 状态码，可以更好地迷惑和阻止爬虫程序。

##### **2. 418 错误产生的原因**

*   **请求头不完整:** 网站会检查 HTTP 请求头来判断是否是爬虫。
*   **User-Agent:** 缺失或使用默认爬虫 `User-Agent`，容易被识别为爬虫。
*  **其他请求头：** `Referer` 等信息不完整或不正确，也可能被识别为爬虫。
*   **访问频率过快:** 短时间内大量访问同一页面，也会被认为是爬虫行为。

##### **3. 解决 418 错误的思路：伪装成浏览器**

*   **核心思路：** 伪装成正常的浏览器访问行为，绕过网站的反爬虫机制。
*   **解决方案：**

    *   **3.1. 使用 `requests.Session()` 管理 Cookies 和连接池**

        *   `requests.Session` 是 `requests` 库中用于发送 HTTP 请求的类，它可以自动管理 Cookies 和连接池。
        *   **Cookies 管理：**
            *   `requests.Session` 可以自动保存和发送 Cookies，确保你的每次请求都携带了正确的 Cookies，从而避免被豆瓣服务器识别为爬虫。
            *   当你的爬虫第一次访问豆瓣时，豆瓣服务器会返回一些 Cookies，这些 Cookies 可以用来标识你的身份。使用 `requests.Session`，你可以确保你的每次请求都携带了正确的 Cookies。
        *   **连接池：**
            *  `requests.Session` 还可以管理连接池，从而提高你的爬虫的性能。
            * 当你使用 `requests.Session` 发送多个请求时，`requests.Session` 会自动重用连接，从而避免每次请求都建立新的连接，从而提高效率。
        *   **HTTP Keep-Alive (Persistent Connections):**
             *  HTTP Keep-Alive，也称为持久连接，是一种在 HTTP/1.1 中引入的机制，用于提高 HTTP 请求的性能。
             *  **传统 HTTP 请求：** 每次请求都会建立新的 TCP 连接，请求完成后会断开连接。
             *   **Keep-Alive：** 使用 Keep-Alive，可以在一个 TCP 连接上发送多个 HTTP 请求和响应，从而避免每次请求都建立新的 TCP 连接。
        * **正确使用 `session`**
            *   如果在 `get_poster_url` 函数内创建了新的 `session` ,  每次调用 `get_poster_url` 都会创建一个新的 `session`。
            *   这会导致 `session` 的 `Keep-Alive` 特性无法被利用，每次请求都会建立新的 TCP 连接。
            *  最佳实践：你需要在 `download_poster_images` 中创建 `session`，并将 `session` 作为参数传递给 `get_poster_url` 函数。

    *   **3.2 使用重试机制**

        *   使用 `requests.Session()` 和 `Retry`，以确保每个请求都有重试机制。
        *   **代码：**
            ```python
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
            ```
        *   **作用：**
            *   `Retry(connect=3, backoff_factor=0.5)` 创建一个 `Retry` 对象，用于定义重试策略。`connect=3` 表示连接错误最多重试 3 次，`backoff_factor=0.5` 表示重试的间隔时间会以 0.5 为系数逐渐增加。
            *   `HTTPAdapter(max_retries=retry)` 创建一个 `HTTPAdapter` 对象，用于将 `Retry` 对象应用到 `requests.Session` 对象中。
            *   `session.mount('http://', adapter)` 和 `session.mount('https://', adapter)` 将 `HTTPAdapter` 对象应用到 `http` 和 `https` 协议的请求中。
             *  **目的：**  当你的请求因为网络错误或者服务器错误而失败时，`requests` 会自动重试，从而提高你的代码的健壮性。

    *   **3.3 减慢请求速度**
        *   **添加 `time.sleep()`：** 在每次请求之前，设置随机的 `time.sleep()`，可以降低爬虫的访问频率，从而减少被网站识别为爬虫的风险。
            ```python
                time.sleep(random.randint(2, 5))
            ```
    *   **3.4 使用更真实的 `User-Agent`**

        *   使用真实的浏览器 `User-Agent`，让网站误认为我们是浏览器在访问。
        *   **代码示例:**
            ```python
            headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                }
            ```
        *  **添加其他头：** 添加常见的 HTTP 头，例如 `Accept`, `Accept-Language`, `Referer` 等, 添加浏览器常用的 header, 比如 `Upgrade-Insecure-Requests`, `Sec-Fetch-User`, `Sec-Fetch-Mode`, `Sec-Fetch-Dest`, `Sec-Fetch-Site`等.
   *    **3.5 动态获取 `headers`**
        *    定义一个返回 `headers` 的函数, 在 `while` 循环里面调用函数来动态获取 `headers`。
   *    **3.6 传递 `headers` 参数**
        *    将 `headers` 作为参数传递到 `get_poster_url` 函数中，让 `get_poster_url` 函数内部的每一个请求都能够携带正确的 `headers` 信息，包括 `User-Agent`、`Cookie`、`Referer` 等。
  *   **3.7 细粒度控制请求**
      *  使用 `session.get` 访问海报列表页面，使得我们能够更细粒度地控制请求，从而成功避开了豆瓣的反爬虫机制。

##### **4. `requests.get` 和 `session.get` 的对比**

*   **`requests.get`：**
    *   `requests.get` 是 `requests` 库中用于发送 HTTP GET 请求的函数。
    *   每次调用 `requests.get`，都会建立一个新的 TCP 连接。
    *   不会自动保存 Cookies，每次请求都需要手动传递 Cookies。
    *   不会自动管理连接池。
*   **`session.get`：**
    *   `session.get` 是 `requests.Session` 对象中用于发送 HTTP GET 请求的方法。
    *   使用同一个 `requests.Session` 对象发送多个请求，可以重用同一个 TCP 连接，从而提高效率。
    *   可以自动保存和发送 Cookies，从而保持登录状态。
    *   会自动管理连接池。

*   **何时使用 `session.get`：**
    *   **需要保持登录状态的爬虫：** 如果你的爬虫需要访问需要登录才能访问的页面，那么你需要使用 `session.get` 来管理 Cookies，保持登录状态。
    *   **需要发送多个请求的爬虫：**  如果你的爬虫需要访问多个页面，那么你可以使用 `session.get` 来重用 TCP 连接，从而提高效率。
    *   **需要使用重试机制的爬虫：** 如果你的爬虫需要使用重试机制来处理请求失败的情况，你可以在 `requests.Session` 对象中配置重试策略。
    *   **总之，在很多时候 `session.get` 都是更合适的选择。**
*  **`session.get` 取决于爬虫深度吗？**
    *  **并不是完全取决于爬虫深度，**虽然深层次爬取需要更多请求，使用 `session.get` 效率会更高，但是并不是说，浅层次的爬取就不需要 `session.get`。
    *  **选择 `session.get` 还是 `requests.get`, 主要取决于你的爬虫的复杂度和具体需求。**
        * 如果你只需要发送一次请求，那么使用 `requests.get` 就可以。
        * 但是，如果你需要发送多个请求，或者需要管理 Cookies 或者重试机制，那么使用 `session.get` 是更合适的选择。

##### **5. 经验总结**

*   **遇到反爬机制强的网站，可以尝试在每一次更深层次爬取的时候，都带上构造好的 `headers`。**
*   反爬虫策略通常会对深层次的爬取进行更严格的限制，因为深层次的爬取通常会消耗更多的服务器资源。


### 优化写入速度

1.  **为什么写入图片会很慢？**
    *   **原因：**
        *   **同步 I/O：** 现在的代码使用同步 I/O 来写入图片，这意味着程序会阻塞在写入操作上，直到写入完成才会继续执行。
        *   **磁盘写入速度：** 磁盘写入速度通常比内存读写速度慢很多。
        *   **`chunk_size`：** 在代码中设置了 `chunk_size=8192`，每次读取 8KB 的数据进行写入。
        *   **CPU 负载：**虽然CPU性能足够，但是如果频繁读取和写入大量小块数据，会增加CPU的负载。
    *   **结论：**
        *   **同步 I/O 加上磁盘写入速度限制导致了写入图片的速度较慢。**

2.  **如何优化写入速度？**

    *   **使用更大的 `chunk_size`：**
        *   增加 `chunk_size` 可以减少读取和写入的次数，从而提高写入速度。
        *   你可以尝试将 `chunk_size` 设置为 65536 (64KB) 或者更大。
        *  **但是：**  `chunk_size` 过大也可能导致内存使用过高，你需要根据实际情况进行调整。
    *   **使用异步 I/O：**
        *   使用异步 I/O 可以让程序在写入图片的同时，执行其他操作，从而提高程序的效率。
        *  **需要使用异步 I/O库，例如 `asyncio` 和 `aiohttp`，这将大大增加代码的复杂度。**
        * **需要异步处理，也需要修改 `save_poster` 的调用方式。**
    * **使用多线程或多进程:**
        *   使用多线程或多进程可以并发地进行多个写入操作，从而提高整体的写入速度。
        *  **但是：** 多线程可能受到 GIL 的限制，多进程可能会增加系统开销。
    * **使用 `shutil.copyfileobj`：**
       * `shutil.copyfileobj` 可以更高效地将文件对象复制到磁盘，减少代码量。

#### **`iter_content(chunk_size=65536)` 和 `shutil.copyfileobj` 在不同情况下的性能问题**

**在爬取少量图片时，`iter_content(chunk_size=65536)` 和 `shutil.copyfileobj` 的性能差异不大，甚至 `shutil.copyfileobj` 还可能略慢。**

**爬取更多图片时，应该选择哪个？**

*   **`shutil.copyfileobj` 的优势：**
    *   **更高效：**  `shutil.copyfileobj` 使用了更高效的底层实现，可以减少 Python 代码的开销，避免频繁读写操作，从而在大量数据传输时表现更好。
    *   **更简洁：**  `shutil.copyfileobj` 的代码更简洁，易于维护。
    *   **更稳定：** 由于 `shutil.copyfileobj` 由 Python 官方维护， 可以保证其稳定性。
*   **`iter_content(chunk_size=65536)` 的局限：**
    *   **Python 代码开销：**  每次循环读取 `chunk_size` 大小的数据都需要进行 Python 代码的执行，这会增加 Python 代码的开销。
    *   **需要手动处理：** 需要自己编写代码来处理读取到的数据，容易出错。
*   **建议：**
    *   **在爬取更多图片时，`shutil.copyfileobj` 是更稳定和更好的选择。**
    *   **不需要自己处理分块的数据，从而简化你的代码，让代码更易于维护。**
    *   **如果你不希望使用 `shutil.copyfileobj`， 你可以尝试使用更大的`chunk_size`，但是不建议这样操作。**

### 代码计时

#### **增加计时器来计算每次爬取耗时**

1.  **在哪里增加计时器？**

    *   **核心问题：**  需要决定计时器应该放在代码的哪个位置，才能准确地计算每次爬取的耗时。
    *   **方案：**
        *   **在 `download_poster_images` 函数开始时启动计时器：** 这样可以计算整个爬取过程的耗时。
        *   **在 `download_poster_images` 函数结束时停止计时器：** 这样可以获取整个爬取过程的耗时。
        *   **在 `while` 循环开始时记录时间，在 `while` 循环结束时记录时间：** 了解每次循环的耗时。
        *   **在 `for` 循环开始时记录时间，在 `for` 循环结束时记录时间：** 了解每次处理电影条目的耗时。
    *   **选择：**
        *   **将计时器放在 `download_poster_images` 函数的开始和结束处，这样可以计算整个爬取过程的耗时。**
        *  **同时，将计时器放在 `for` 循环的开始和结束处， 从而得到单个条目的爬取时间。**

2.  **如何使用 Python 实现计时器？**

    *   **使用 `time` 模块：**  Python 的 `time` 模块提供了 `time()` 函数，可以获取当前时间的时间戳（以秒为单位）。
    *   **代码示例：**
        ```python
        import time

        start_time = time.time()  # 启动计时器

        # 执行一些代码

        end_time = time.time()  # 停止计时器
        elapsed_time = end_time - start_time  # 计算耗时
        print(f"耗时：{elapsed_time:.2f} 秒")
        ```
    *  **`time.perf_counter()`**: 
        * `time.perf_counter()` 返回性能计数器的值（以秒为单位），该计数器提供尽可能高的可用分辨率测量时间。
        *  **这个方法通常用来测量时间间隔， 非常适合我们的情景。**
        * 它的原理是基于CPU的硬件计时器，因此具有非常高的精度，可以达到纳秒级别。

#### **`time.perf_counter()` 和 `time.time()` 的区别**

1.  **`time.time()` 的特点：**

    *   **返回时间戳：** `time.time()` 返回的是当前时间的时间戳，即从 Unix 纪元（1970年1月1日00:00:00 UTC）到现在的秒数，是一个浮点数。
    *   **系统时间：** `time.time()` 获取的是系统的实时时间，可能会受到系统时间调整的影响，例如：时钟同步、手动调整时间等。
    *   **精度较低：** `time.time()` 的精度通常较低，可能只能达到毫秒级别，甚至秒级别，具体取决于操作系统的实现。

2.  **`time.perf_counter()` 的特点：**

    *   **返回性能计数器值：** `time.perf_counter()` 返回的是性能计数器的值，这是一个单调递增的计时器，不会受到系统时间调整的影响。
    *   **高精度：** `time.perf_counter()` 的精度通常比 `time.time()` 高很多，可以达到纳秒级别，具体取决于 CPU 的硬件实现。
    *   **适用于测量时间间隔：** `time.perf_counter()` 主要用于测量代码执行的时间间隔，而不是测量绝对时间。
    *   **不受系统时间影响:** `time.perf_counter()` 不受系统时间调整的影响，可以提供更准确的计时结果。

3.  **`time.perf_counter()` 为什么比 `time.time()` 好？**

    *   **核心问题：**  为什么在测量代码执行时间时，`time.perf_counter()` 通常比 `time.time()` 更好？
    *   **原因：**
        *   **高精度：** `time.perf_counter()` 的精度比 `time.time()` 高，可以提供更准确的计时结果。这对于测量执行时间较短的代码片段，尤其重要。
        *   **不受系统时间影响：**  `time.perf_counter()` 不受系统时间调整的影响，可以提供更稳定的计时结果。这对于长时间运行的代码或者在不同环境下运行的代码，尤其重要。
        *   **单调递增：** `time.perf_counter()` 返回的值是单调递增的，这意味着它可以确保时间测量的顺序性，避免出现时间回溯的问题。
    *   **结论：**
        *   **在测量代码执行时间时，`time.perf_counter()` 是更合适的选择，因为它提供了更高的精度、更稳定的结果，并且不受系统时间调整的影响。**

4.  **什么时候使用 `time.time()`？**

    *   **获取当前时间：** 如果你需要获取当前时间，例如：记录日志的时间、设置定时任务等，那么可以使用 `time.time()`。
    *   **需要系统时间：** 如果你的程序需要使用系统时间，并且对精度要求不高，那么可以使用 `time.time()`。
    *   **例如:** 需要获得当前的日期， 你可能需要 `time.time()` 结合 `datetime` 来实现。

5.  **总结：**

    *   **`time.time()`：** 用于获取当前时间，精度较低，可能会受到系统时间调整的影响。
    *   **`time.perf_counter()`：** 用于测量时间间隔，精度高，不受系统时间调整的影响。
    *   **在测量代码执行时间时，通常使用 `time.perf_counter()`，因为它可以提供更高的精度和更稳定的结果。**


## 待更新

下一篇将完善如何利用 open CV 或 pillow 来自动化拼接 `PosterBandit.py` 保存的图片 😽

