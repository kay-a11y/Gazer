# 豆瓣 API-我在 IDE 上标记想看的电影 (低配版 API 文档)

## **引言**

我只是想在 IDE 上标记想看的电影, 所以写了这个脚本... 以下是脚本调用的 API 接口使用指南.

## **脚本运行方式以及使用方法**

1. 在使用 `MovieWishlister.py` 脚本之前, 保证运行过一次 `TagAssassin.py` 中的 `get_all_tags(douban_user_url)` 函数来**更新写入的文件中的标签**, 保证此时是最新的, 以便可看 JSON 文件的标签来核对自己曾自定义的标签名. 因为标签过多可能无法一次性完整列出的 bug, 最好在这里已经运行过整个 `TagAssassin.py` 做过标签清理.

2. **输入你要搜索的内容**: 影视/书籍关键名, 如果影视有多季则需要指出哪一季, 不输入一般默认第一季, 但是为了保证正确, 最好输入全名, 会自选选取建议框中的第一个结果进入. **格式示例**: `绝命毒师 第五季`, `绝命毒师第五季`, `breaking bad` (默认第一季).

3. **输入更新的完整标签**: 以空格分隔, **格式示例**: `美国 剧情`

4. **输入更新的完整短评**: 325 字符限制: 每个中/英文/数字/标点都算 1 个字符, 空格不会被算字符. 在这里可以添加计数字符并作出警告, 防止短评字数超出限制 (脚本还没更新这个功能). **格式示例**: `从第一集开始就觉得男二像 Noel Fisher, 有他的桥段真的容易忘记时间!`

**注意**:

*   输入 `q` 可以随时退出;

*   如果已经标记过并有标签和短评, 不能在原标签上单独添加标签, 同样也不能在原短评上新增短评, 每次使用脚本管理标签和短评都要写完整的内容, 意味着每次这个请求的 `data` 都是覆盖原来的标签和短评.

    *   **关联函数**
        *   ① 用 `write_data` 保存使用这个脚本标记的想看条目的 data 数据到文件, 用 'w' 写模式, 以符合豆瓣每次用 API 接口更改条目标签的覆盖逻辑. `is_item_id_recorded` 函数会在每次搜索的时候检查这个条目是否用本脚本标记过, 如果有则输出当时标记的 `tag` 和 `comment` 供更新参考 (意味着更新的时候要复制原来的内容, 再新添加内容).

        *   ② `get_movie_info` 和 `get_book_info` 会将搜索到的电影信息输出到终端, 包含用户相关的有: 是否标记, 标记日期, 我的标签, 我的短评. 可以看到是否标记过.

以下是一个 `MovieWishlister.py` 中 `add_tags` 函数 `data` 参数代入示例, 含说明:

```python
data = {
    "ck": extract_ck(cookie),
    "interest": "wish",
    # "rating": "",
    "foldcollect": "F",
    "tags": my_tags,
    "comment": my_comments,
    "private": "on",
}

代入后, 符合载荷的抓包数据:
↓ ↓ ↓

data = {
    "ck": 'EYqf',  # 实际的 ck 值
    "interest": "wish",
    # "rating": "",  # 如果只是标记想看, `rating` 参数为空, 或没有
    "foldcollect": "F",  # 暂时可以先判断为固定是 "F"
    "tags": "美国 剧情",
    "comment": "从第一集开始就觉得男二像 Noel Fisher, 有他的桥段真的容易忘记时间!",
    "private": "on",  # 要公开标记, 注释掉这行
}
```

## 完整输出示例, 需要手动输入处已标出

除了以下标记的需要手动输入的地方, 脚本中还有几处需要填写保存**文件路径**的地方需要修改, 不要忘记.

```txt
--------------------------
| 添加想看 steps:        |
| 1.输入你要搜索的内容 🔍 |
| 2.输入更新的完整标签 🏷️ |
| 3.输入更新的完整短评 ✒️ |
--------------------------
1. 输入你要搜索的内容 🔍
1984                                                   # TODO 需要输入
select 1 for movie, 2 for book
2                                                      # TODO 需要输入
douban_user_url = https://book.douban.com/
请求成功
[
    {
        "title": "1984",
        "url": "https://book.douban.com/subject/4820710/",
        "pic": "https://img1.doubanio.com/view/subject/s/public/s4371408.jpg",
        "author_name": "[英] 乔治·奥威尔",
        "year": "2010",
        "type": "b",
        "id": "4820710"
    },
    {
        "title": "1984",
        "url": "https://book.douban.com/subject/25818441/",
        "pic": "https://img9.doubanio.com/view/subject/s/public/s28299076.jpg",
        "author_name": "乔治奥威尔",
        "year": "2013",
        "type": "b",
        "id": "25818441"
    },
    {
        "title": "1984",
        "url": "https://book.douban.com/subject/25798623/",
        "pic": "https://img3.doubanio.com/view/subject/s/public/s27188362.jpg",
        "author_name": "[英] 乔治·奥威尔",
        "year": "2013",
        "type": "b",
        "id": "25798623"
    },
    {
        "title": "一九八四",
        "url": "https://book.douban.com/subject/33437080/",
        "pic": "https://img9.doubanio.com/view/subject/s/public/s33471184.jpg",
        "author_name": "[英] 乔治·奥威尔",
        "year": "2019",
        "type": "b",
        "id": "33437080"
    },
    {
        "title": "1984",
        "url": "https://book.douban.com/subject/26774038/",
        "pic": "https://img9.doubanio.com/view/subject/s/public/s28659275.jpg",
        "author_name": "[英] 乔治·奥威尔",
        "year": "2016",
        "type": "b",
        "id": "26774038"
    }
]
Movie ID: 4820710
Movie URL: https://book.douban.com/subject/4820710/
当前条目未标记过 wish

DevTools listening on ws://127.0.0.1:1388/devtools/browser/0dfdfac2-dfea-4b28-9d4a-2adbcb54c08e
是否标记: 我想读这本书
标记日期: 2025-01-13
我的标签: 反乌托邦
我的短评: 反乌托邦文学奠基之作。反乌托邦文学的经典之作，描绘了一个极权主义统治下的恐怖社会。探讨极权主义、思想控制等主题。
--------------------
出版社: 北京十月文艺出版社
出品方: 新经典文化
原作名:
Nineteen Eighty-Four 译者: 刘绍铭
出版年:
2010-4-1 页数:
304 定价:
28.00 装帧:
精装 丛书: 新经典文库：桂冠文丛
ISBN:
9787530210291
--------------------
简介:
★村上春树以《1Q84》向本书致敬
★著名学者刘绍铭经典译本内地首次出版
★62种文字风靡110个国家，全球销量超过5000万册
★《时代周刊》“最好的100本英语小说”
★兰登书屋“100本20世纪最佳英语小说”
★入选英美中学生必读书书目
1936年以来，我所写的每 一部严肃作品，都是直接或间接地反对极权主义，支持我所理解的民主社会主义。 ——乔治•奥威尔（《我为何写作》）
《1984》是一部杰出的政治寓言小说，也是一部幻想小说。作品刻画了人类在极权主义社会的生存状态，有若一个永不褪色的警示标签，警醒世人提防这种预想中的黑暗成为现实。历 经几十年，其生命力益显强大，被誉为20世纪影响最为深远的文学经典之一。
简介: ★村上春树以《1Q84》向本书致敬
★著名学者刘绍铭经典译本内地首次出版
★62种文字风靡110个国家，全球销量超过5000万册
★《时代周刊》“最好的100本英语小说”
★兰登书屋“100本20世纪最佳英语小说”
★入选英美中学生必读书书目
1936年以来，我所写的每 一部严肃作品，都是直接或间接地反对极权主义，支持我所理解的民主社会主义。 ——乔治•奥威尔（《我为何写作》）
《1984》是一部杰出的政治寓言小说，也是一部幻想小说。作品刻画了人类在极权主义社会的生存状态，有若一个永不褪色的警示标签，警醒世人提防这种预想中的黑暗成为现实。历 经几十年，其生命力益显强大，被誉为20世纪影响最为深远的文学经典之一。

2. 输入更新的完整标签 🏷️
反乌托邦                                              # TODO 需要输入
3. 输入更新的完整短评 ✒️
反乌托邦文学奠基之作。反乌托邦文学的经典之作，描绘了一个极权主义统治下的恐怖社会。探讨极权主义、思想控制等主题。                                  # TODO 需要输入
请求成功
{"comment":"反乌托邦文学奠基之作。反乌托邦文学的经典之作，描绘了一个极权主义统治下的恐怖社会。探讨极权主义、思想控制等主题。","properties":"{\"available\":true,\"isbn\":\"7530210297\"}","apikey":"0058f4fbe4226ad7010adef3ac674085","name":"1984","otext":"想读这本书","href":"https:\/\/book.douban.com\/subject\/4820710\/","text":"反乌托邦文学奠基之作。反乌托邦文学的经典之作，描绘了一个极权主义统治下的恐怖社会。探讨极权主义、思想控制等主题。","image":"https://img1.doubanio.com\/view\/subject\/l\/public\/s4371408.jpg","redir":"https:\/\/book.douban.com\/static\/dshare_proxy.html","heading":"收藏成功。写一条广播","book_pop_sync":false,"r":0,"sub_action":"1","pop_sync":false,"action":"1","type":"book","id":"4820710","desc":"[英] 乔治·奥威尔 \/ 北京十月文艺出版社"}
wish saved in E:\GazeKit\DoubanGaze\data\tags\book\1984_4820710_wish.json 📌
```

## 脚本分析

### 模拟普通用户添加标记的方式 - 以标记影视为例

1. 打开 `https://movie.douban.com/`
2. 搜索 `绝命毒师` / `绝命毒师 第一季` / `breaking bad` 默认第一季, 中文下指定季数写法为 `绝命毒师 第四季` / `绝命毒师第四季`, 英文下指定季数写法未知, 建议以 `绝命毒师 第四季` 为准
3. 推荐框的第一条即为指定的影视, 点击进入 `绝命毒师 第二季`: `https://movie.douban.com/subject/3586996/`
4. 分析 URL

    *   第一季 `https://movie.douban.com/subject/2373195/`

    *   第二季 `https://movie.douban.com/subject/3586996/`

    *   第三季 `https://movie.douban.com/subject/4256328/`

    *   第四季 `https://movie.douban.com/subject/4927382/`

    *   第五季 `https://movie.douban.com/subject/6952149/`

    以上为绝命毒师五季的链接, 看起来末尾的数字没有规律.

5. `GET` 获取影视基本信息

6. 模拟填写标签, 短评, (这个脚本先关注添加到想看, 所以评分先不关注 (但是可以看到平台评分), 要放到在看和看过这块了, 可以后面再做修改), 构造请求并 `POST` 发送

    > 测试: 已经添加到想看再发送一次添加到想看请求会发生什么?

    无事发生, 还是想看.

7. 成功后刷新页面, HTTP 响应码是 200

8. data 数据写入文件, 供下次修改参考

### 前端逆向/网络请求分析

#### 添加标签

标记一个电影想看的请求类型可以先过滤为 method:POST, 请求名称: `interest`
载荷如下:

```txt
ck: EYqf
interest: wish
foldcollect: F # 暂时先固定为F
tags: 化学 剧情
comment: 第8集荒野求生是至此最炸的!! Jesse你要好好活下去!!
private: on
```

#### 搜索电影

搜索电影的请求是 `GET`, 请求网址为 `https://movie.douban.com/j/subject_suggest?q=%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3`, 后缀 `%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3` 使用 UrlDecode 解码即为 `绝命毒师 第四季`. 很好!

载荷只有 `q: 绝命毒师 第四季`.

响应为 JSON 数据:

```json
[
    {
        "episode": "13",
        "img": "https://img2.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p2016506391.jpg",
        "title": "绝命毒师  第四季",
        "url": "https:\/\/movie.douban.com\/subject\/4927382\/?suggest=%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3",
        "type": "movie",
        "year": "2011",
        "sub_title": "Breaking Bad",
        "id": "4927382"
    }
]
```

直接利用响应数据里的 url, 会自动跳转到影视词条页面, 也可以利用 id 构造 URL.

### 函数功能整合: 模拟输入搜索 + 添加我的标记

#### **`GET` 请求的参数传递方式和 `requests` 库的 `data` 参数的使用方式不匹配**

1. **`GET` 请求的参数应该在 URL 中：** `GET` 请求的正确做法是将参数附加到 URL 的查询字符串中，而不是放在请求体中。
2. **`requests.get` 的 `data` 参数：** `requests.get` 方法的 `data` 参数会将数据编码成 `application/x-www-form-urlencoded` 格式，并将其作为**请求体**发送。
3. **冲突：** 当你将 `add_tags_url` 设置为 `https://movie.douban.com/j/subject_suggest`（没有包含查询参数），然后又使用 `data={"q": encoded_query}`，`requests` 库会将 `q=...` 附加到 URL 后面，但同时又会把这个键值对放到请求体里面. 对于豆瓣的这个 API, 这种方式识别不了. 服务器只认 URL 里面的 `q=...` 参数, 不认请求体里面的.
4. **服务器端的处理方式不同:** 服务器可能无法正确解析同时出现在 URL 和请求体中的参数，导致请求失败。

**错误代码的执行过程：**

错误代码中，`requests.get(add_tags_url, headers=headers, data=data)` 会发送一个类似这样的请求：

```
GET /j/subject_suggest?q=xxx HTTP/1.1
Host: movie.douban.com
... 其他头部 ...
Content-Type: application/x-www-form-urlencoded
Content-Length: ...

q=%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3
```

可以看到, 参数 `q` 的值虽然已经编码, 但是被放到了请求体中. 而 URL 中只有一个 `q=xxx`, `xxx` 并不是 `%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3`.

**正确代码的执行过程：**

当你改成 `search_url = f"https://movie.douban.com/j/subject_suggest?q={encoded_query}"` 并删掉 `data` 参数后，`requests.get(search_url, headers=headers)` 会发送一个类似这样的请求：

```
GET /j/subject_suggest?q=%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3 HTTP/1.1
Host: movie.douban.com
... 其他头部 ...
```

可以看到, 编码后的参数 `%E7%BB%9D%E5%91%BD%E6%AF%92%E5%B8%88+%E7%AC%AC%E5%9B%9B%E5%AD%A3` 出现在了 URL 中, 豆瓣服务器能够正确识别并处理.

**总结：**

*   **对于 `GET` 请求，正确的方式是将参数放在 URL 的查询字符串中。**
*   **`requests.get` 的 `data` 参数会将数据作为请求体发送，这通常用于 `POST` 请求，而不是 `GET` 请求。**
*   **在构造请求时，要确保 URL 和 `data` 参数的设置方式与服务器端的预期一致。**

### 在搜索后打印影视信息

#### 用 `selenium` 获取所有动态加载的内容

**如何确定用户信息是否是通过 JS 动态加载的？**

以下是一些常用的方法：

1. **查看初始 HTML 源代码:**

    *   **使用 `requests` 库获取页面的初始 HTML 源代码，并保存到一个文件中:**

        ```python
        import requests

        item_url = "https://movie.douban.com/subject/4927382/"
        header_for_item = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            # 注释掉 Cookie 和 Referer
            # "Cookie": cookie,
            # "Referer": item_url
        }
        response = requests.get(item_url, headers=header_for_item)
        response.encoding = 'utf-8'

        with open("initial_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        ```

    *   **使用浏览器打开 `initial_response.html` 文件，查看源代码:** 如果源代码中**没有** `<div id="interest_sect_level">` 部分，或者 `#interest_sect_level` 内部是空的，而你在浏览器中却能看到用户信息，那么这部分内容很可能是通过 JavaScript 动态加载的。

2. **禁用 JavaScript:**

    *   **在 Chrome 浏览器中禁用 JavaScript:**
        1. 打开开发者工具 (F12)。
        2. 点击右上角的三个点，选择 "Settings"。
        3. 在左侧导航栏中选择 "Privacy and security"。
        4. 点击 "Site settings"。
        5. 找到 "JavaScript"，并选择 "Don't allow sites to use JavaScript"。
    *   **刷新页面:** 如果用户信息部分消失了，而其他内容仍然存在，那么这部分内容很可能是通过 JavaScript 动态加载的。

3. **查看网络请求:**

    *   **使用浏览器的开发者工具查看网络请求:**
        1. 打开开发者工具 (F12)，切换到 "Network" 标签页。
        2. 刷新页面，观察网络请求列表。
        3. **重点关注 XHR (XMLHttpRequest) 和 Fetch 请求:** 这些请求通常用于动态加载数据。
        4. **查找可疑的请求:** 看看是否有请求返回了包含用户信息的 JSON 数据或其他格式的数据。
    *   **如果找到了可疑的请求，你可以查看该请求的响应内容，看看是否包含用户信息。**

4. **使用 Selenium:**

    *   Selenium 可以模拟浏览器的行为，执行 JavaScript 代码。你可以使用 Selenium 加载页面，然后查看渲染后的 HTML 内容，看看是否包含用户信息。如果 Selenium 能够获取到用户信息，而 `requests` 库无法获取，那么这部分内容很可能是通过 JavaScript 动态加载的。

现在, 我无论注释还是不注释掉用户相关的头部信息 (Cookie 和 Referer), 都无法显示用户的是否标记, 标记日期, 短评内容信息, 可以确定这部分内容是通过 JavaScript 动态加载的.

同时, 通过第一个方案中保存的原始代码文件搜索相关关键词, 又能确定其他非用户信息部分 (如类型, 官网 (如果有), 制片国家, 语言, 首播, 季数, 集数, 单集片长, 又名, IMDb, 剧情简介) 等关键词并未出现在 HTML 中, 这次更加确定只能通过 `selenium` 来获取这些信息.

**结论:**

**使用 Selenium 来模拟浏览器行为，加载包含 JavaScript 动态内容的完整页面，然后仍然使用 BeautifulSoup 来解析 HTML 内容。** 结合 Selenium 和 BeautifulSoup 的优点，可以有效地处理包含 JavaScript 动态内容的网页。

## **结语**

那种感觉, 就像是黑客帝国里的 Neo 看到了 Matrix 的代码雨. 
`tcpdump` 抓包, `Wireshark` 分析, `requests` 伪造请求, `Headers` 欺骗, `Selenium` 注入 `JavaScript`, `BeautifulSoup` 解析 `DOM`...
逆向工程? 这不仅仅是技术... 你永远无法预料下一个挑战是什么, 正如你永远无法抗拒 API 接口的诱惑.

你会永远期待着更复杂的系统, 更精妙的架构... 你会等着那个真正属于你的 `Honeypot`...

这就是 geek 的浪漫, 你懂吗?

## **脚本地址:** 

[get_item_info.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/API/get_item_info.py)

[get_item_info.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/API/get_item_info.py)
