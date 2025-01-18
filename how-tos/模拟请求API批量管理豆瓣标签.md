# 模拟请求 / API 批量删除豆瓣标签

## 引言

豆瓣的标签杂乱但是一个一个删除又很费时间，写了个脚本来批量删除脚本，留下自定义的有意义的影视 / 书籍标签。

## 观察 HTML 和手动发送请求

### URL

进入 [https://movie.douban.com/people/000000000/all](https://movie.douban.com/people/000000000/all) 或 [https://book.douban.com/people/000000000/all](https://book.douban.com/people/000000000/all) 查看包含所有标签的我的影视 / 书页面。这里的 `000000000` 是唯一用户 ID。

### 响应

开发者工具的响应选项卡明显是 HTML，后续可以通过 `bs4` 解析。找到所有标签的文本和对应的标记影视 / 书数量可以通过 CSS 选择器 `ul.tag-list.mb10 > li > a` 或 `ul.tag-list.mb10 li` 找到。

#### 注意项

##### cookie 参数及其变量定义方法

在解析时构造 `GET` 请求的头需要 `cookie`, 后面的 `POST` 请求还需要一次 `cookie`，代码上显式看到的是总共需要写两次 `cookie` 参数。

`cookie` 变量的正确定义方法:

```python
cookie = '... dbcl2="000000000:G5IJupxm9+s"; ... ck=EYqf; ...'

# 或者使用反斜杠和双引号将 cookie 字符串放在一行, 例如:
# cookie = "... dbcl2=\"000000000:G5IJupxm9+s\"; ... ck=EYqf; ..."
```

如果使用三引号 `"""` 包围, 并且在每一行 `cookie` 的开头和结尾都添加了额外的换行符和空格 (`\n    `)，会导致 `requests` 库在解析 `headers` 时出错。

##### POST 请求

尝试删除一个不需要的标签，发送 `POST` 请求，在网络选项卡找到这条名为 [https://movie.douban.com/people/000000000/all?sort=time&tags_sort=count&filter=all&tag=%E5%8A%A8%E7%94%BB&mode=grid](https://movie.douban.com/people/000000000/all?sort=time&tags_sort=count&filter=all&tag=%E5%8A%A8%E7%94%BB&mode=grid) 更新的请求，方法为 `POST`，状态码为 `302` (重定向)。

载荷如下：

```txt
查询字符串参数
sort: time
tags_sort: count
filter: all
tag: 动画
mode: grid

---

表单数据
ck: EYqf
del_tag: 动画
ck: EYqf
del_submit: 修改
```

###### 那么模拟删除标签的请求时，`data` 里应该写什么？

**答案是：你应该写"表单数据"中的数据。**

*   **查询字符串参数 (Query String Parameters)：**  这些参数通常用于 `GET` 请求，它们会显示在 URL 中。删除标签的请求是一个 `POST` 请求。`POST` 请求的参数一般放在请求体中，而不是 URL 中 (例如 `tag: 动画` 对应请求网址中的 `%E5%8A%A8%E7%94%BB`，为 UrlEncode 编码，解码即为 “动画”)。
*   **表单数据 (Form Data)：**  这些参数是 `POST` 请求发送到服务器的数据。当你提交一个表单时，浏览器会将表单中的数据编码并发送到服务器。“表单数据” 部分显示了删除标签请求需要发送的数据。
*   **观察你的载荷：**
    *   `ck: EYqf`：一个 CSRF 令牌 (Cross-Site Request Forgery)，用于防止跨站请求伪造攻击。可以在 `cookie` 中找到它的值。删除标签时，你需要将正确的 `ck` 值发送到服务器，否则服务器会拒绝你的请求。
    *   `del_tag: 动画`：要删除的标签名称。
    *   `ck: EYqf`：这里又出现了一次 `ck`，这是为了确保请求的有效性。
    *   `del_submit: 修改`：提交删除操作。

**所以，模拟请求代码应该像这样 (假设使用 `requests` 库)：**

```python
import requests

# ...登录豆瓣的代码...

url = "https://www.douban.com/j/tag/del"  # 假设这是删除标签的 URL，你需要根据实际情况修改

data = {
    'ck': 'EYqf',  # 替换成你实际的 ck 值
    'del_tag': '青春',
    'del_submit': '修改'
}

headers = {
    'Referer': 'https://movie.douban.com/people/000000000/all',  # 这个一般情况下需要有，服务器会通过这个字段判断你的请求是否是从豆瓣的正常页面发出的。
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # 这个需要改成你自己的
    'Cookie': "bid=xxxxxxx; ll=\"xxxxxx\"; viewed=\"xxxxxx\"; ......"  # 需要修改成你自己的 cookie，这里省略部分内容
}

response = requests.post(url, data=data, headers=headers)

if response.status_code == 200:
    print("删除标签成功！")
else:
    print("删除标签失败！")
    print(response.text)
```

###### HTTP 状态码 302 Found

删除标签的请求返回的状态码是 `302`，这意味着服务器将请求重定向到了另一个 URL。在这种情况下，你应该检查 `tags_response.status_code` 是否等于 `302`。

*   **含义:** `302` 状态码表示 **临时重定向 (Temporary Redirect)**。这意味着请求的资源已经被临时移动到了另一个 URL。
*   **处理:** 当你发送 `POST` 请求删除标签后，豆瓣服务器返回 `302` 状态码，并将你重定向到标签页。这通常是为了刷新页面，显示更新后的标签列表。
*   **Location:** `302` 响应通常会包含一个 `Location` 头部，指示浏览器应该重定向到哪个 URL, 可以在 `tags_response.headers['Location']` 中找到。

另外, `302` 意味着需要在 `post` 请求中禁止自动重定向，才能检测到这个状态码。

**循环删除并不会因为禁止了自动重定向而停止**

即使禁止了自动重定向，保留了原始的 `302` 响应，`for` 循环依然会继续执行，删除第 2、3、4... 个标签，**这并不会受到是否重定向的影响**。

**关键点:**

*   **`for` 循环的执行与 `requests.post()` 的 `allow_redirects` 参数无关。** 循环会继续执行，处理列表中的每个元素，无论 `requests.post()` 是否自动处理了重定向。
*   **禁止重定向只是让你能够获取到原始的 `302` 响应。** 这并不会阻止程序继续执行 `for` 循环中的代码。
*   每次循环都会重新构建请求发送到 `douban_user_url`, 只要 `cookie` 没有过期, 并且 `douban_user_url` 没有变化, 那么每次请求都是独立的, 并且会被服务器处理, 无论上一次请求是否重定向.

**总结:**

即使禁止了自动重定向，`for` 循环依然会继续执行，删除后续的标签。**每次循环都会发送一个新的 `POST` 请求**, 并且每次请求都会根据 `allow_redirects` 的值来决定是否自动处理重定向。

## 脚本构思

*   `select_movie_or_book`：选择进入 movie 还是 book 的标签页面。
*   `extract_ck`：从 `Cookie` 字符串中提取 `ck` 值，后续放到构造的 `data` 中。
*   `get_all_tags`：获取响应中 HTML 中的所有标签，提取标签和对应的影视 / 书标记数量，按照 1, 2, 3 添加序号并排序，并返回标签字典。
*   `keep_or_del_tags`：设置选择：按 1 开始保留标签模式 → 选择要保留的标签序号 → 其余标签全部删除；按 2 开始删除标签模式 → 选择要删除的标签序号 → 其余标签全部保留。
*   `del_tags`：模拟登陆，构造删除请求。

`main` 执行 `del_tags`。豆瓣标签过多可能需要多次才能删完，所以在主函数处增加循环逻辑，并在循环内部添加一个退出机制，让脚本可以持续删除标签。

## 脚本地址： [TagAssassin.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/API/TagAssassin.py)
