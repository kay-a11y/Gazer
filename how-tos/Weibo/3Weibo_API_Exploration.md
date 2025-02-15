> **免责声明：** 在使用此指南之前，请务必仔细阅读并理解 [DISCLAIMER.md](DISCLAIMER.md) 文件中的免责声明。

---

# **Weibo_API_Exploration**

前言: 继上一篇博客详述了使用 JS 注入绕过 msedgedriver 的字符处理逻辑并触发表单提交元素后, 为更深入地理解微博的前端逻辑, 开始尝试使用浏览器的开发者工具, 以更深入地理解 Web 开发的底层原理. 

即使在没有 JS 基础语法知识的情况下, 有一些更简单的方法也能帮助新手快速入门逆向工程.

## 脚本地址：

[send_weibo_api.py](https://github.com/kay-a11y/Gazer/tree/main/WeiboGaze/src/API/send_weibo_api.py)

[get_cookie_and_st.py](https://github.com/kay-a11y/Gazer/tree/main/WeiboGaze/src/API/get_cookie_and_st.py)

[go_update_mycookie.py](https://github.com/kay-a11y/Gazer/tree/main/WeiboGaze/src/API/go_update_mycookie.py)

## **逆向工程的准备工作**

通过分析网络请求来尝试理解微博 API 的工作原理. 

### **1. 使用浏览器开发者工具的网络（Network）面板：**

   *   **步骤：**
      1. 打开微博的发微博页面。
      2. 按 `F12` 打开开发者工具，切换到 `Network` 面板。
      3. 勾选 `Preserve log` 选项，这样在页面跳转后，之前的网络请求记录不会被清除。
      4. 在微博页面输入一些内容，并点击发送按钮。
      5. 在 `Network` 面板中，查看发送微博的网络请求（通常是一个 POST 请求，可以通过 `Method` 列来筛选）。

   *   **你能看到什么：**
      *   **请求的 URL：**  发送微博的接口地址。
      *   **请求的方法：**  例如 `POST`。
      *   **请求头（Request Headers）：**  包括 `Content-Type`、`Cookie` 等信息。
      *   **请求体（Request Payload）：**  发送给服务器的数据，通常包括你输入的微博内容、以及其他一些参数（例如时间戳、token 等）。
      *   **响应头（Response Headers）：**  服务器返回的头信息。
      *   **响应体（Response）：**  服务器返回的数据，通常是一个 JSON 格式的字符串，包含了一些状态信息（例如是否发送成功、错误代码等）。

   *   **如何利用这些信息：**
      *   通过分析发送微博的网络请求，可以了解微博客户端和服务器之间是如何交互的。
      *   可以知道发送微博需要哪些参数，以及服务器是如何响应的。
      *   可以通过查看请求体来了解微博内容是如何被编码和传输的。

#### **问题一：发送微博后跳转到新标签页，导致 Network 记录丢失**

**解决方法：**

1. **启用 “Preserve log” 选项：**
    *   在 `Network` 面板的工具栏中，确保勾选 `Preserve log`（或 `保留日志`）选项。这个选项可以让 `Network` 面板在页面跳转后仍然保留之前的网络请求记录。
    *   勾选此选项后，再次尝试发送微博，你会发现之前的网络请求记录都被保留了下来。
    
2. **使用 “Disable cache” 选项：**
    *   在 `Network` 面板的工具栏中，勾选 `Disable cache`（或 `禁用缓存`）选项。这个选项可以确保你每次请求的都是最新的资源，而不是缓存中的旧资源。这对于调试网络请求非常有用。

#### **问题二：如何过滤出 POST 请求**

**解决方法：**

1. **使用过滤器进行筛选：**
    *   在 `Network` 面板的工具栏中，有一个 `Filter`（或 `过滤`）输入框。你可以在这里输入一些关键词来过滤网络请求。
    *   输入 `method:POST`，然后按下回车键，`Network` 面板将只显示 `POST` 请求。

2. **根据请求的 URL 进行筛选：**
    *   微博发送的接口地址名称是 `update`。在 `Filter` 输入框中输入这个关键词来过滤网络请求。

#### **分析找到的信息：**

**第一张图：负载（Payload）**

*   **`content`：**  “请求体种包含了这条信息!!!!!!!!!!!!”，这里就是发送的微博内容。
*   **`visible`：** 此处的测试我是通过发送了这条"仅自己可见" 的微博. 所以此处的 `1`，表示发送的微博的可见范围是"仅自己可见"。据此, 可以猜测, `0` 可以表示“所有人可见”，`2` 可能表示“仅好友圈可见”。我们可以通过修改这个参数来测试不同的可见范围对应的数字。
*   **`st`：**  `f79388`，看起来像是一个 token，可能是用于验证用户身份或防止重复提交的。
*   **`_spr`：** `screen:1920x1080`，表示当前的屏幕分辨率。

**第二三张图：标头（Headers）**


*   **请求网址（Request URL）：** `https://m.weibo.cn/api/statuses/update`，表明发送微博的 API 接口地址是 `/api/statuses/update`。
*   **请求方法（Request Method）：** `POST`，表明发送微博是通过 POST 请求来完成的。
*   **状态码（Status Code）：** `200 OK`，表明请求已成功处理。
*   **远程地址（Remote Address）：** `127.0.0.1:7890`，表示我使用了代理服务器, 后文将会详细分析这点。
*   **请求标头（Request Headers）：**
    *   **`Accept`：**  `application/json, text/plain, */*`，表示客户端可以接受 JSON、纯文本等多种类型的响应。
    *   **`Accept-Encoding`：** `gzip, deflate, br, zstd`，表示客户端支持的压缩算法。
    *   **`Accept-Language`：** `zh-CN,zh;q=0.9,en;q=0.8`，表示客户端接受的语言。
    *   **`Content-Length`：** `193`，表示请求体的长度。
    *   **`Content-Type`：** `application/x-www-form-urlencoded`，表示请求体是使用 URL 编码的表单数据。
    *   **`Cookie`：**  一长串的 Cookie 值，用于用户身份验证。
    *   **`Origin`：**  `https://m.weibo.cn`，表示请求的来源。
    *   **`Referer`：** `https://m.weibo.cn/compose/`，表示用户是从哪个页面跳转过来的。
    *   **`User-Agent`：** `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`，表示你使用的浏览器信息。
    *   **`X-Requested-With`：** `XMLHttpRequest`，表示这是一个 AJAX 请求。
    *   **`X-XSRF-TOKEN`：** `f79388`，看起来和负载中的 `st` 值相同，可能是一个 CSRF token，用于防止跨站请求伪造攻击。


**我们可以分析出什么？**

1. **微博发送 API 的基本信息：**  我们知道了发送微博的 API 接口地址是 `https://m.weibo.cn/api/statuses/update`，请求方法是 `POST`，请求体是使用 URL 编码的表单数据。
2. **微博内容参数：**  微博内容是通过 `content` 参数来传递的。
3. **可见性参数：**  通过 `visible` 参数来控制微博的可见范围。
4. **身份验证：**  微博使用 `Cookie` 和 `X-XSRF-TOKEN` 来进行用户身份验证和防止 CSRF 攻击。
5. **客户端信息：**  微博会收集用户的屏幕分辨率 (`_spr`) 和浏览器信息 (`User-Agent`)。

**接下来可以做什么？**

1. **修改参数：**  尝试修改请求体中的参数，例如 `content` 和 `visible`，看看会对发送结果产生什么影响。
2. **构造请求：**  尝试使用 Python 的 `requests` 库来构造和发送 POST 请求，模拟发送微博的过程。
3. **分析响应：**  仔细分析服务器返回的响应数据，看看能不能发现一些有用的信息，例如错误代码、状态信息等。
4. **深入研究：**  如果想更深入地了解微博 API，可以尝试使用代理工具拦截和修改网络请求，或者阅读公开的 API 文档和相关的技术博客。


> 关于**远程地址（Remote Address）：** `127.0.0.1:7890` 以及相关的 `ip` 概念确认

> 上面我的服务器请求中的远程地址, 确实是我使用的代理地址. 我使用的是Clash 的 “规则” 模式而不是全局, 按理说, 会根据规则列表来判断哪些流量走代理，哪些流量直连。如果规则设置正确，访问国内网站时应该不会走代理. 那这里为什么走了代理?

**可能原因**

1. **规则不完善：**  Clash 规则列表中可能没有包含所有国内网站的域名或 IP 地址，导致一些国内网站的流量被误判为需要走代理。
2. **DNS 污染：**  即使规则设置正确，也可能因为 DNS 污染导致域名被解析到了错误的 IP 地址，从而导致流量被路由到了代理服务器。
3. **Clash 的 Bug：**  Clash 本身也可能存在一些 bug，导致规则无法正确执行。

**求证方案**

*   **检查 Clash 规则列表：**  确保规则列表中包含了所有国内网站的域名和 IP 地址。参考公开的规则列表，例如 [https://github.com/Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)
*   **使用自定义 DNS：**  在 Clash 中设置一个可靠的 DNS 服务器，例如 `114.114.114.114` 或 `8.8.8.8`，以避免 DNS 污染。
*   **更新 Clash：**  确保你使用的是最新版本的 Clash，并关注 Clash 的更新日志，看看是否有相关的 bug 修复。

**解惑**

我在 [https://github.com/Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules) 查了 Clash 直连域名列表 direct.txt, 确定了没有m.weibo.cn(连weibo.cn都没有). 现在可以确定确实使用了代理服务器. `127.0.0.1` 是本地回环地址，用于指代本机。之所以显示这个地址，是因为 **Clash 在我的本机上启动了一个代理服务，并监听 7890 端口。** 当我的浏览器或其他应用程序通过 Clash 代理访问网络时，它们的请求会先发送到 Clash 的代理服务（也就是 `127.0.0.1:7890`），然后由 Clash 根据规则决定是将请求直连还是转发到代理服务器。

所以，即使访问的 `m.weibo.cn` 是国内网站，如果浏览器设置了使用 Clash 代理，那么远程地址仍然会显示为 `127.0.0.1:7890`。这并不意味着请求没有直连，而是因为 **Clash 在中间做了一层转发。**

请求实际上是：

**我的应用程序 -> Clash 代理服务 (127.0.0.1:7890) -> (根据规则) -> 代理服务器 或 直连目标网站**


根据我的终端 `ipconfig` 可以知道, 我的ipv4地址是 `172.30.96.1`, 而这个地址 **是局域网 IP（私有 IP）。**  

*   **公网 IP** 是指在全球互联网中唯一的 IP 地址，可以直接从互联网访问。
*   **局域网 IP** 是指在局域网内部使用的 IP 地址，不能直接从互联网访问。

电脑通过路由器连接到互联网，路由器会分配一个局域网 IP 给电脑，例如 `172.30.96.1`。路由器还有一个公网 IP，用于与外部网络通信。

关于`192.168.2.1`这个以太网ip, 很可能是**路由器的 IP 地址，而不是 ISP（互联网服务提供商）的地址。**

`192.168.x.x` 是一个常用的局域网 IP 地址段，很多路由器默认使用这个网段。网上很多人的以太网 IP 都是 `192.168.x.x`，是因为他们都使用了路由器，并且路由器使用了默认的 IP 地址段。



## **开门!**

**关于 `https://m.weibo.cn/api/statuses/update` 的访问结果：**

尝试直接访问 `https://m.weibo.cn/api/statuses/update` 得到以下结果：


{
  "ok": 0,
  "errno": "100007",
  "msg": "不符合的请求方式",
  "extra": ""
}


这是因为使用了 **GET** 方法访问了这个 API 接口，而它只接受 **POST** 请求。`"不符合的请求方式"` 指的就是这个意思。 这也进一步佐证了发送微博的请求方式是 `POST`.

**关于 `visible` `st` 参数：**

由于刚才我的一条微博设置了仅自己可见, 我们可以确定 `visible: 1` 表示“仅自己可见”. 观察更早的几分钟前发的几条微博的数据, 我发现, 这一段时间请求体中不同的微博内容, 有相同的st: f79388，接下来我新发送了2条微博, 一条公开, 发现请求体中更新为st: f13778,`visible` 这一行消失; 一条朋友圈可见, st: f13778,`visible: 6`. 不同时间段的 `st` 值会发生变化。这表明 `st` 很可能是一个 **与时间相关的 token**。它可能用于标识某个时间段内的请求，或者用于防止 CSRF 攻击。

可以知道:

*   `visible: 0`  (或不存在):  公开
*   `visible: 1` : 仅自己可见
*   `visible: 6` : 朋友圈可见

可以尝试发送更多不同可见性的微博来验证这个推断。

**使用 `requests` 构造请求：**

刚才我们已经抓包得到了请求头中的 `User-Agent` 字段, 所以接下来我们可以使用 Python 的 `requests` 库来构造一个 POST 请求，并设置请求头，来模拟发送微博的过程。

**为什么要构造请求头？**

*   **伪装成浏览器：**  服务器可以通过请求头中的 `User-Agent` 字段来识别客户端的类型。如果我们想让服务器认为我们的请求来自一个正常的浏览器，就需要设置一个正确的 `User-Agent`。
*   **通过服务器验证：**  一些服务器会检查请求头中的某些字段，例如 `Referer`、`Origin` 等，来判断请求是否合法。我们需要根据实际情况设置这些字段，才能通过服务器的验证。
*   **传递更多信息：**  请求头中还可以包含其他一些信息，例如 `Cookie`、`Accept-Encoding` 等，这些信息可以告诉服务器更多关于客户端的信息。

**为什么之前的脚本(如 `GhostwriterWeibo_v2.py` )没有构造请求头？**

之前的脚本使用了 Selenium，Selenium 会自动控制浏览器发送请求，所以它会自动设置请求头，我们不需要手动设置。 这也是这几行关于设置请求头的代码被注释掉的原因，因为对于 Selenium 来说，手动设置请求头是没有意义的.

```py
# 设置请求头, 会被selenium忽略, 没有意义
    # if headers:
    #     edge_options.add_argument(f'--user-agent={headers["User-Agent"]}')
```

**代码示例：**

下面是一个使用 `requests` 库构造请求并发送微博的示例代码：

```py
import requests

def send_weibo(content, visible=0, cookie=None, st=None):
    """使用 requests 库发送微博

    Args:
        content (string): 微博内容
        visible (int, optional): 可见性. 0: 公开, 1: 仅自己可见, 6: 朋友圈可见. Defaults to 0.
        cookie (string, optional): 微博 Cookie. Defaults to None.
        st (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/api/statuses/update"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/compose/",
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": st,  # 使用抓包获取到的 st 值
        "Cookie": cookie,  # 使用你的真实 Cookie
    }
    if visible == 0:
        data = {
            "content": content,
            "st": st,
            "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
        }
    else:
        data = {
            "content": content,
            "visible": visible,
            "st": st,
            "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
        }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博发送成功！")
        else:
            print(f"微博发送失败: {result['msg']}")
    else:
        print(f"请求失败: {response.status_code}")

# 使用示例
# 从浏览器开发者工具中复制 Cookie 和 st 的值
my_cookie = "DELICIOUS_COOKIE"  # 替换成你的 Cookie
my_st = "f13778"  # 替换成抓包获取到的 st 值

send_weibo("发送一条公开微博！", cookie=my_cookie, st=my_st)  # 发送一条公开微博
send_weibo("测试使用 requests 发微博, 仅自己可见！", visible=1, cookie=my_cookie, st=my_st)  # 发送一条仅自己可见的微博
send_weibo("一条朋友圈可见的微博", visible=6, cookie=my_cookie, st=my_st)  # 发送一条朋友圈可见的微博
```

**代码说明：**

1. **`send_weibo` 函数：**
    *   `content`：微博内容。
    *   `visible`：可见性，默认为 `0`（公开）。
    *   `cookie`：微博 Cookie。需要从浏览器开发者工具中复制 Cookie，并粘贴到这里。
    *   `st`：用于验证的 token。需要从抓包获取的 `X-XSRF-TOKEN` 中复制 `st` 的值，并粘贴到这里。
2. **`url`：**  微博发送 API 的地址。
3. **`headers`：**  请求头。需要根据抓包获取的信息来设置 `User-Agent`、`Referer`、`Origin`、`Content-Type`、`X-Requested-With`、`X-XSRF-TOKEN` 和 `Cookie`。
4. **`data`：**  请求体。需要根据 `visible` 的值来构造请求体。
5. **`requests.post`：**  发送 POST 请求。
6. **`response.json()`：**  将响应数据解析为 JSON 格式。
7. **判断发送结果：**  根据响应数据中的 `ok` 字段来判断微博是否发送成功。

**如何获取 `Cookie` 和 `st`：**

1. 打开微博的发微博页面 (https://m.weibo.cn/compose/)。
2. 按 `F12` 打开开发者工具，切换到 `Network` 面板。
3. 勾选 `Preserve log` 和 `Disable cache` 选项。
4. 在微博页面输入一些内容，并点击发送按钮。
5. 在 `Network` 面板中，找到发送微博的 POST 请求。
6. 在请求的 `Headers` 选项卡中，找到 `Request Headers` 部分。
7. 复制 `Cookie` 的值。
8. 复制 `X-XSRF-TOKEN` 的值（就是 `st` 的值）。

**重要提示：**

*   **Cookie 和 st 的有效期：**  Cookie 和 st 都有有效期，过期后需要重新获取。具体时效将在后文继续探讨.
*   **频率限制：**  频繁发送微博可能会触发微博的反爬虫机制，导致账号被限制。请合理使用此代码，不要滥用。
*   **免责声明：**  这段代码仅供学习和研究使用，请勿用于非法用途。

现在, 尝试修改代码中的参数，例如微博内容、可见性、Cookie 和 st，看看会对发送结果产生什么影响. 

我尝试发送了3条不同可见性的微博, 可以验证0公开, 1仅自己可见, 6朋友圈可见的推断.

**关于 `st` 值：**

`st` 值可能会在一段时间内保持不变。抱着侥幸心理, 我先尝试了使用之前的 `f13778`，看看能不能发送成功。

*   **如果发送成功：**  说明 `st` 值在测试的时间段内仍然有效。
*   **如果发送失败：**  很可能是 `st` 值已经过期，或者微博更新了安全策略。需要重新抓包获取新的 `st` 值。

**请注意：**  `st` 值很可能与时间有关，或者与登录状态有关。如果隔了很长时间再次运行代码，或者微博账号退出了登录，很可能需要重新获取 `st` 值。

**关于抓包：**

以上研究网络请求并抓取数据的过程，**就是抓包**！🎉

**抓包**（Packet Capture）是指捕获网络上传输的数据包的过程。我们通常使用一些工具来辅助抓包，例如浏览器开发者工具、Wireshark、Fiddler、Charles 等。

*   **使用浏览器开发者工具的 `Network` 面板来查看网络请求，就是一种非常常用的抓包方式。**  它可以方便地查看 HTTP 请求和响应的详细信息，包括请求头、请求体、响应头、响应体等。

*   **Wireshark 是一款更专业的网络抓包工具，它可以捕获所有经过网卡的网络数据包，不仅仅是 HTTP 协议。**  Wireshark 功能更强大，但也更复杂。它可以捕获更底层的数据包，例如 TCP、UDP、IP 等。

**Wireshark vs. 浏览器开发者工具：**

| 特性       | 浏览器开发者工具                                       | Wireshark                                              |
| ---------- | -------------------------------------------------------- | ------------------------------------------------------ |
| 捕获范围   | 仅限于当前浏览器的 HTTP/HTTPS 请求                       | 可以捕获所有经过网卡的网络数据包                         |
| 使用难度   | 相对简单，适合 Web 开发调试                             | 更复杂，需要一定的网络协议知识                           |
| 功能       | 主要用于 Web 开发调试，查看 HTTP 请求和响应的详细信息     | 功能更强大，可以进行更深入的网络分析                     |
| 实时性     | 实时显示网络请求                                         | 可以实时捕获数据包，也可以保存数据包供以后分析           |
| 协议支持   | 主要支持 HTTP/HTTPS                                       | 支持多种网络协议，例如 TCP、UDP、IP、ARP、ICMP 等      |
| 操作系统支持 | 跟随浏览器                                        | 跨平台，支持 Windows、macOS、Linux 等                    |

**小结：**

*   **对于 Web 开发调试来说，浏览器开发者工具已经足够用了。**  它可以让你方便地查看 HTTP 请求和响应的详细信息，而且使用起来也比较简单。
*   **如果需要进行更深入的网络分析，或者需要捕获非 HTTP 协议的数据包，那么可以使用 Wireshark。** Wireshark 可以说是更“底层”一些，因为它可以捕获更底层的网络数据包。


## 开始执行第一个脚本 😈

当我使用刚才的st, 终端显示:

```
请求失败: 403
请求失败: 403
请求失败: 403
```

代码403, 被服务器拒绝了, 所以我重新手动发送微博, 发现st已经更新, 而且cookie也跟着更新, 我的cookie从

```
_T_WM=557a2f786dbff574722318b058b4d6b7; ... SUB=_2A25KcMuXDeRhGeVL7VYV-SfFzzyIHXVpDEFfrDV6PUJbktANLXnQkW1NTCXsnxWC6W6onbf_fEsQaxfYXJQxPzJ3; ... MLOGIN=1; XSRF-TOKEN=f13778
```

变成了

```
_T_WM=557a2f786dbff574722318b058b4d6b7; ...SUB=_2A25KcMuXDeRhGeVL7VYV-SfFzzyIHXVpDEFfrDV6PUJbktANLXnQkW1NTCXsnxWC6W6onbf_fEsQaxfYXJQxPzJ3; ... MLOGIN=1; XSRF-TOKEN=8ea381; mweibo_short_token=bf3d747a9d
```

而st也藏在cookie中. 我怀疑 `m.weibo.cn` 比多数人使用的网页版微博 `weibo.com` 的cookie更新更快, 基本上是几十分钟就更新(实际上这时候的说法并不准确, 请看下文继续分析).

更新cookie和st之后, 发送成功:

```
微博发送成功！
微博发送失败: 发微博太多啦，休息一会儿吧!
微博发送失败: 发微博太多啦，休息一会儿吧!
```

### **关于我的发现：**

1. **`st` 值和 `Cookie` 的更新：**  `st` 值和 `Cookie` 几乎是同时更新的，这表明它们之间存在很强的关联性。`st` 值很可能是基于 `Cookie` 生成的，用于验证用户的登录状态和防止 CSRF 攻击。
2. **`st` 值藏在 `Cookie` 中：**  `XSRF-TOKEN` 的值和 `Cookie` 中的 `st` 值相同，这进一步证实了 `st` 值和 `Cookie` 之间的关联性。这很可能是微博的一种安全机制，用于验证请求的合法性。
3. **m.weibo.cn 的 Cookie 更新频率：**  怀疑 m.weibo.cn 的 Cookie 更新频率比 weibo.com 更快，这很可能是因为移动端网站更注重安全性，所以会更频繁地更新 Cookie。

**关于发送结果：**

*   第一条微博发送成功，说明更新后的 `Cookie` 和 `st` 值是有效的。
*   第二条和第三条微博发送失败，提示“发微博太多啦，休息一会儿吧!”，说明触发了微博的频率限制。

### **计划：**

*   为了避免触发微博的频率限制，可以在每次发送微博之间添加一些延时，例如 `time.sleep(60)`，让程序暂停 60 秒。
*   继续探索 m.weibo.cn 和 weibo.com 的 Cookie 更新机制，看看能不能发现更多有趣的规律。
*   **关于 `XSRF-TOKEN` 和 `SUB`：**  `XSRF-TOKEN` 的值和 `Cookie` 中 `SUB` 的一部分相同, 这是微博的一种安全策略。`SUB` 是一个经过 Base64 编码的字符串，里面包含了用户的一些信息，以及一个用于验证请求合法性的 token。`XSRF-TOKEN` 的值通常是 `SUB` 中 token 部分的哈希值。


### **代码优化：**

为了避免频繁更新 `Cookie` 和 `st`，将它们保存到文件中，并在每次发送微博之前检查它们是否过期。如果过期了，再重新获取。

另外, 把`XSRF-TOKEN`单独定义出来, 这样更方便:

```py
import requests
import time
import json

def send_weibo(content, visible=0, cookie=None, x_xsrf_token=None):
    """使用 requests 库发送微博

    Args:
        content (string): 微博内容
        visible (int, optional): 可见性. 0: 公开, 1: 仅自己可见, 6: 朋友圈可见. Defaults to 0.
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/api/statuses/update"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/compose/",
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }
    if visible == 0:
        data = {
            "content": content,
            "st": x_xsrf_token,
            "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
        }
    else:
        data = {
            "content": content,
            "visible": visible,
            "st": x_xsrf_token,
            "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
        }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博发送成功！")
            return True
        else:
            print(f"微博发送失败: {result['msg']}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

# 使用示例
# 从浏览器开发者工具中复制 Cookie 和 X-XSRF-TOKEN 的值
my_cookie = "DELICIOUS_COOKIE😋"  # 替换成你的 Cookie 
my_x_xsrf_token = "8ea381"  # 替换成抓包获取到的 X-XSRF-TOKEN 值

# 首次发送
send_weibo("发送一条公开微博！", cookie=my_cookie, x_xsrf_token=my_x_xsrf_token)

# 增加延时
time.sleep(60)

# 再次发送
send_weibo("测试使用 requests 发微博, 仅自己可见！", visible=1, cookie=my_cookie, x_xsrf_token=my_x_xsrf_token)

# 增加延时
time.sleep(60)

# 再次发送
send_weibo("一条朋友圈可见的微博", visible=6, cookie=my_cookie, x_xsrf_token=my_x_xsrf_token)
```

### **接下来的探索方向：**

1. **研究 `Cookie` 的生成机制：**  尝试分析 `Cookie` 中各个字段的含义，看看能不能找到生成 `Cookie` 的算法。
2. **研究 `st` 值的生成机制：**  尝试找出 `st` 值与时间、`Cookie` 和其他参数之间的关系。
3. **探索微博 API 的更多接口：**  除了发送微博的接口，微博还有很多其他的 API 接口，例如获取用户信息、获取评论列表、点赞等。可以尝试使用类似的方法来探索这些接口。

### **关于 CSRF 攻击：**

**CSRF**（Cross-Site Request Forgery，跨站请求伪造）是一种常见的 Web 安全漏洞，它允许攻击者诱导用户执行他们不打算执行的操作。

**攻击原理：**

1. **诱导：** 攻击者诱使用户访问一个恶意网站或点击一个恶意链接。
2. **伪造请求：** 恶意网站会向用户已登录的目标网站（例如微博）发送一个伪造的请求。
3. **利用 Cookie：** 由于浏览器会自动将目标网站的 Cookie 附加到请求中，因此伪造的请求看起来就像是由用户自己发送的一样。
4. **执行操作：** 目标网站收到伪造的请求后，会认为是用户自己发出的，并执行相应的操作，例如发布微博、修改密码、转账等。

**举个例子：**

假设你已经登录了微博，攻击者诱使你访问了一个恶意网站。恶意网站中包含以下代码：


<img src="https://weibo.com/api/statuses/update?content=我是被攻击者发布的微博&visible=0" width="0" height="0">


在这个例子中, 攻击者将恶意 URL 嵌入到了 HTML 的 `<img>` 标签的 `src` 属性中. 而且 **不一定需要点击图片。** 只要浏览器加载了这个 `<img>` 标签，就会自动向 `src` 属性指定的 URL 发送请求，无论图片是否可见或是否被点击。在这个例子中，`width="0" height="0"` 使得图片在页面上不可见，所以用户甚至察觉不到这个请求的发生。当你访问这个恶意网站时，浏览器会自动向 `https://weibo.com/api/statuses/update` 发送一个 GET 请求，并附带上你的微博 Cookie。微博服务器收到请求后，会认为是你自己发布的微博，并执行相应的操作。

针对`m.weibo.cn`, 之前我们已经得出发送微博的 API 接口地址是 `https://m.weibo.cn/api/statuses/update`, 所以应该为`https://m.weibo.cn/api/statuses/update?content=我是被攻击者发布的微博&visible=0`, 这里原理相同.
*   **`?`：**  问号表示 URL 中传递参数的开始。
*   **`content=我是被攻击者发布的微博`：**  这是微博内容的参数。
*   **`&`：**  & 符号用于分隔多个参数。
*   **`visible=0`：**  这是微博可见性的参数，`0` 表示公开。

`width="0" height="0"` 不是指屏幕分辨率，而是 HTML `<img>` 标签的属性，用于设置图片的宽度和高度。这里将图片的宽度和高度都设置为 `0`，是为了让图片在页面上不可见，从而隐藏攻击行为。

攻击者通常通过以下几种方式诱导用户访问包含恶意代码的页面：

1. **钓鱼网站：** 攻击者创建一个看起来像合法网站的钓鱼网站，并在其中嵌入恶意代码。然后通过电子邮件、短信、社交媒体等方式诱导用户访问这个钓鱼网站。
2. **恶意链接：** 攻击者在论坛、博客、社交媒体等地方发布包含恶意链接的帖子或评论，诱导用户点击。
3. **XSS 漏洞：** 如果目标网站存在 XSS（跨站脚本）漏洞，攻击者可以将恶意代码注入到目标网站的页面中。当其他用户访问这些被注入恶意代码的页面时，就会触发攻击。

### **如何防御 CSRF 攻击：**

1. **验证码：**  在执行敏感操作之前，要求用户输入验证码。
2. **Referer 检查：**  服务器检查请求的 `Referer` 字段，确保请求来自可信的来源。
3. **Token 验证：**  服务器生成一个随机的 token，并将其存储在用户的 session 中。在执行敏感操作之前，要求用户提交这个 token。这就是微博使用的 `XSRF-TOKEN` 的作用, 通常也会藏在 Cookie 中, 例如名为 `st` 的字段.

*   **token：**  这里的 token 指的是用于防御 CSRF 攻击的随机令牌，在微博的例子中，就是 `XSRF-TOKEN`，通常它的值和 Cookie 中 `SUB` 字段的某一部分相同。
*   **session：**  session 是一种服务器端的技术，用于跟踪用户的状态。服务器会为每个用户创建一个 session，并分配一个唯一的 session ID。session ID 通常存储在用户的 Cookie 中。

**所以，`st`（或 `XSRF-TOKEN`）是用于防御 CSRF 攻击的 token，而 session ID 通常存储在 Cookie 中。它们之间有一定的关联，但不是同一个东西。**

在 CSRF 攻击的例子中，`Referer` 的值取决于攻击者如何构建恶意页面。

*   **如果攻击者直接将恶意 `<img>` 标签嵌入到自己的网站中，那么 `Referer` 将是攻击者网站的地址。**
*   **如果攻击者将恶意 `<img>` 标签嵌入到其他存在 XSS 漏洞的网站中，那么 `Referer` 将是该存在 XSS 漏洞的网站的地址。**
*   **如果攻击者诱导用户直接点击恶意链接，那么 `Referer` 将为空，因为不是从其他页面跳转过来的。**

**需要注意的是，`Referer` 字段可以被伪造或禁用，因此它不能作为防御 CSRF 攻击的可靠手段。**


### **关于 `SUB` 的解码：**
我尝试使用Base64解码 `SUB` 的 UTF8 解码结果是 `؍)î\7g/XU'ŏ<uiA_5z=B[Ѝ-yБmML%쟕鮨ߒĚŶ%O̝` , 显然是乱码.

这是因为 `SUB` 并不是一个简单的 Base64 编码字符串，它还包含了一些其他信息。尝试使用 Base64 解码 `SUB` 的值得到乱码是正常的，因为 `SUB` 的值不仅仅是 Base64 编码那么简单. 它里面可能包含了一些二进制数据或者使用了其他的编码方式。

### **关于 Cookie 和 `st` 的过期时间：**

我在脚本测试中发现cookie和st又过期了, 所以我又重新发微博, 计算出前后两次失败的时间是15-16分钟左右, 所以目前预估这个域名m.weibo.cn的cookie是15分钟刷新一次.

### **接下来的探索方向：**

1. **研究 `SUB` 的编码方式：**  尝试找出 `SUB` 中包含的信息以及它的编码方式。你可以参考一些公开的资料，或者使用一些反编译工具来分析微博的客户端代码。
2. **动态获取 `Cookie` 和 `st`：**  尝试编写代码来模拟登录微博，并自动获取 `Cookie` 和 `st` 的值。这将使你的脚本更加自动化。
3. **探索微博 API 的更多接口：**  继续探索微博的其他 API 接口，例如获取用户信息、获取评论列表、点赞等。

### **一些额外的学习资料：**

*   **OWASP CSRF Prevention Cheat Sheet:** [https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
*   **Base64 编码原理：** [https://zh.wikipedia.org/wiki/Base64](https://zh.wikipedia.org/wiki/Base64)

> 参考一些公开的资料

*   **OWASP Top 10：** OWASP（Open Web Application Security Project）是一个致力于提高 Web 应用程序安全性的非营利组织。OWASP Top 10 是 OWASP 发布的最常见的 Web 应用程序安全风险列表，其中就包括 CSRF。([https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/))
*   **Web 安全相关的博客和论坛：**  例如 FreeBuf、安全客、先知社区等。
*   **CTF（Capture The Flag）比赛：**  CTF 是一种网络安全竞赛，参赛者需要解决各种安全问题，例如 Web 安全、逆向工程、密码学等。通过参加 CTF 比赛，可以学习到很多实用的安全知识和技能。

> 反编译工具

*   **Jadx：**  一款强大的 Android 反编译工具，可以将 APK 文件反编译成 Java 代码。([https://github.com/skylot/jadx](https://github.com/skylot/jadx))
*   **Apktool：**  另一款常用的 Android 反编译工具，可以将 APK 文件反编译成 Smali 代码。([https://ibotpeaches.github.io/Apktool/](https://ibotpeaches.github.io/Apktool/))
*   **Bytecode Viewer：**  一款 Java 反编译工具，可以反编译 JAR 文件和 CLASS 文件。([https://bytecodeviewer.com/](https://bytecodeviewer.com/))
*   **Ghidra：**  美国国家安全局（NSA）开源的一款软件逆向工程工具，支持多种平台和处理器架构。功能强大，适合有一定经验的逆向工程师。([https://ghidra-sre.org/](https://ghidra-sre.org/))

对于入门的小黑客，可以先从 **Jadx** 和 **Apktool** 开始学习。

## 开始模拟登录微博

### **如果已经开始害怕了 🐱🐭**

**如何防范可能的危险(比如被检测? 安全百分比是? 在逆向工程中, 哪些操作是比较危险的?)?**


**安全风险和防范措施：**

*   **账号被封禁：**  频繁登录、发送微博、访问 API 接口等操作都可能触发微博的反爬虫机制，导致账号被封禁。
    *   **防范措施：**  控制请求频率，模拟正常用户的操作，使用代理 IP，避免使用已被封禁的账号。
*   **法律风险：**  未经授权对网站进行逆向工程或爬取数据可能违反网站的服务条款或相关法律法规。
    *   **防范措施：**  仔细阅读网站的服务条款，遵守相关法律法规，不要进行恶意攻击或侵犯他人隐私。
*   **安全漏洞：**  在逆向工程过程中，可能会发现网站或应用程序的安全漏洞。未经授权利用这些漏洞可能导致严重后果。
    *   **防范措施：**  及时向网站或应用程序的开发者报告发现的安全漏洞，不要利用漏洞进行恶意攻击或牟利。

**关于敏感操作：**

*我们现在就是在使用 `requests` 库直接访问 m.weibo.cn 的 API 接口。*

**敏感操作** 通常指的是那些会对账号安全或用户数据产生影响的操作，例如：

*   **登录和注销：**  登录和注销操作直接关系到账号的安全。
*   **发送私信：**  发送私信涉及到用户的隐私。
*   **发布或删除微博：**  发布或删除微博会影响用户的内容。
*   **修改个人信息：**  修改个人信息，例如昵称、头像、密码等，会影响账号的安全和用户的身份。
*   **关注或取关：**  关注或取关操作会影响用户的人际关系。
*   **点赞、评论、转发：**  这些操作虽然看起来不那么敏感，但如果频繁操作，也可能触发微博的反爬虫机制。

**安全百分比：**

很难给出一个具体的安全百分比，因为这取决于很多因素，例如你的技术水平、目标网站的安全措施、你的操作频率和方式等。

**逆向工程操作的风险排序（从高到低）：**

1. **利用安全漏洞进行恶意攻击或牟利：**  这是最危险的操作，可能导致严重的法律后果。
2. **未经授权对网站进行逆向工程或爬取数据：**  这可能违反网站的服务条款或相关法律法规。
3. **频繁访问 API 接口或执行敏感操作：**  这可能触发网站的反爬虫机制，导致账号被封禁。
4. **分析网络请求和响应：**  这是相对安全的操作，但仍需注意不要泄露个人信息或侵犯他人隐私。
5. **阅读公开的文档和资料：**  这是最安全的操作，可以帮助你了解 Web 安全和逆向工程的基础知识。

## 开始紧张地构思代码 🐭

模拟登录微博是一个比较复杂的过程，涉及到验证码识别、加密算法分析等技术。

**基本步骤：**

1. **分析登录流程：**  使用浏览器开发者工具分析微博的登录流程，找出登录 API 的地址、请求参数、加密方式等。
2. **构造登录请求：**  使用 Python 的 `requests` 库构造登录请求，并发送给微博服务器。
3. **处理验证码：**  如果登录需要验证码，需要使用 OCR（光学字符识别）技术来识别验证码，或者使用第三方打码平台来自动识别验证码。
4. **解析响应：**  解析服务器返回的响应数据，提取 `Cookie` 和 `st` 的值。

**代码示例（仅供参考，不包含验证码识别）：**

```py

import requests

def login_weibo(username, password):
    """模拟登录微博 (不包含验证码识别)

    Args:
        username (string): 微博用户名
        password (string): 微博密码

    Returns:
        dict: 包含 Cookie 和 XSRF-TOKEN 的字典, 登录失败返回 None
    """

    url = "https://m.weibo.cn/login"  # 登录 API 的地址 (需要根据实际情况修改)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/",
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "username": username,
        "password": password,
        # 其他必要的参数 (例如加密后的密码、验证码等, 需要根据实际情况修改)
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        # 解析响应, 提取 Cookie 和 XSRF-TOKEN
        # ... (需要根据实际情况修改)
        cookie = response.cookies.get_dict()
        x_xsrf_token = ""  # 从 Cookie 或响应中提取 XSRF-TOKEN (需要根据实际情况修改)

        # 验证是否登录成功
        # ... (需要根据实际情况修改)
        if "登录成功" in response.text:  # 假设登录成功的标志是响应中包含 "登录成功"
            return {"cookie": cookie, "x_xsrf_token": x_xsrf_token}
        else:
            print("登录失败")
            return None
    else:
        print(f"请求失败: {response.status_code}")
        return None

# 使用示例
username = "你的微博用户名"
password = "你的微博密码"

login_result = login_weibo(username, password)

if login_result:
    my_cookie = "; ".join(f"{k}={v}" for k, v in login_result["cookie"].items())
    my_x_xsrf_token = login_result["x_xsrf_token"]

    print("登录成功！")
    print(f"Cookie: {my_cookie}")
    print(f"XSRF-TOKEN: {my_x_xsrf_token}")

    # 使用获取到的 Cookie 和 XSRF-TOKEN 发送微博
    send_weibo("通过模拟登录发送的微博！", cookie=my_cookie, x_xsrf_token=my_x_xsrf_token)
else:
    print("登录失败！")
```

**关于登录微博：**

微博的登录机制非常严格，尤其是现在强制使用手机扫码登录，这给自动化登录带来了很大的挑战。

**目前的几种登录方式：**

1. **账号密码登录：**  需要输入手机号/邮箱和密码，还需要通过点击验证码的验证，还需要扫码验证, 验证等级最高, 最难绕过。
2. **手机验证码登录：**  需要输入手机号，并获取短信验证码，还需要通过点击验证码的验证。这种方式相对来说更容易自动化一些。
3. **扫码登录：**  最方便快捷的登录方式，但也是最难自动化的。

**可能的解决方案：**

改成 `data = { "vertification_code": vertification_code, ... }`, 模拟点击"获取验证码", 增加sleep等待接受验证码的时间.

这种方法理论上可行，但实际上很难实现。

*   **优点：**  如果能够成功获取短信验证码，并正确填写，就有可能登录成功。
*   **缺点：**
    *   需要模拟点击“获取验证码”按钮，这需要分析页面的 HTML 结构，并使用 JavaScript 注入或其他方法来触发点击事件。
    *   需要处理点击验证码，这可能需要使用 OCR 技术或人工打码平台。
    *   即使解决了以上问题，仍然不能保证 100% 成功，因为微博的反爬虫机制非常复杂。

解析页面是可以找到 “获取验证码” 按钮的, 但是有个问题:
    *   你需要知道点击后, 浏览器会执行什么javascript代码, 这段代码如何获取到验证码, 如何把验证码发送给你的手机, 以及如何验证你的手机是否收到了验证码.
    这个问题非常复杂，涉及到很多技术，例如 JavaScript 注入、DOM 操作、事件触发等。但这也正是它的魅力所在！

> 但是问题又来了, 在获取验证码之前, 需要一次手动点击验证文字验证码, 可能需要opencv或其他 OCR 技术.

是可行的，但也有一定的难度和局限性：

*   **优点：**  可以自动化处理点击验证码。
*   **缺点：**
    *   需要较高的图像处理技术，且识别率不一定能达到 100%。
    *   如果验证码的样式经常变化，或者使用了更复杂的验证码技术，例如滑动验证码、拼图验证码等，识别难度会更大。

使用 OpenCV 识别验证码需要考虑很多因素，例如验证码的类型、干扰项、识别率等。而且，即使识别出了验证码，还需要模拟点击“确定”按钮，这又涉及到页面元素的定位和事件触发。

实际上, OpenCV需要识别一个文字, 就模拟点击一次点那个文字. 要识别三次, 点三次, 在去点击确定, 才是一次完整的识别成功.

![alt text](/imgs/语序点选验证码.png)

这种验证码叫做“语序点选验证码”，需要按照指定的顺序点击图片中的文字才能通过验证。

这种验证码的识别难度比普通的图形验证码更高，因为它不仅需要识别图片中的文字，还需要识别文字的顺序，并模拟点击操作。

> 综上, 那么最快速的方法就是手机直接扫码登录了.

**目前的方案：**

*   **手动扫码登录：**  这是目前最可靠的登录方式, 虽然它不是全自动的。可以将 `Cookie` 和 `st` 的获取和使用分开：
    1. **手动登录并获取 `Cookie` 和 `st`：**  编写一个简单的脚本，用于打开微博登录页面，并等待你手动扫码登录。登录成功后，脚本自动从浏览器中提取 `Cookie` 和 `st`，并保存到文件中。
    2. **使用保存的 `Cookie` 和 `st` 发送微博：**  `send_weibo` 函数可以从文件中读取 `Cookie` 和 `st`，并使用它们来发送微博。
*   **继续探索：**  虽然自动化登录很难，但仍然可以继续探索其他的可能性，例如：
    *   **研究扫码登录的原理：**  尝试分析扫码登录的流程，看看能不能找到绕过扫码验证的方法。我喜欢这个“疯狂”的想法！
    *   **使用手机自动化工具：**  例如 Appium、Airtest 等，可以控制手机自动执行扫码操作。

绕过扫码验证确实非常困难，目前还没有公开的、可靠的方法。但我们可以一起思考一些可能的思路：

*   **分析扫码登录的原理：**  扫码登录的本质是将手机端的信息传递给 PC 端。我们需要研究这个信息传递的过程，看看有没有可能伪造或劫持这个过程。😈
*   **研究二维码的生成机制：**  微博的二维码是如何生成的？其中包含了哪些信息？有没有可能伪造一个二维码，让微博服务器误认为是手机端扫描的？
*   **利用手机自动化工具：**  例如 Appium、Airtest 等，可以控制手机自动执行扫码操作。但这种方法需要一台真实的手机，并且需要编写复杂的自动化脚本。
*   **寻找微博的安全漏洞：**  这需要非常深厚的安全知识和技术，而且也存在一定的法律风险。

**小知识**

**关于人工打码平台：**

**人工打码平台** 是一种提供验证码识别服务的平台。这些平台雇佣了大量的人工来识别验证码，并提供 API 接口供开发者调用。当你的程序遇到验证码时，可以将验证码图片发送到人工打码平台，平台会返回识别结果。

人工打码平台背后是大量的人工在进行打码操作。他们 24 小时在线，为各种需要验证码识别的场景提供服务。

ChatGPT 欺骗 TaskRabbit 零工平台上的工人来帮忙识别验证码的新闻曾非常有名，也引发了人们对 AI 伦理的思考。AI 的发展已经到了一个非常 advanced 的阶段，它们甚至可以利用人类的同情心来达到自己的目的。🐱

一些常见的人工打码平台：

*   **超级鹰：** [https://www.chaojiying.com/](https://www.chaojiying.com/)
*   **云打码：** [http://www.yundama.com/](http://www.yundama.com/)


## 绕不过

### **一个可行的方案**

**步骤：**

1. **使用 Selenium 有头浏览器打开微博登录页面。**
2. **等待我手动扫码登录。**
3. **登录成功后，使用 `driver.get_cookies()` 获取 Cookie，并从中提取 `st` 的值。**
4. **将 Cookie 和 `st` 保存到文件中。**  可以将它们保存到 JSON 文件或文本文件中。使用 `io.StringIO` 只能在内存中操作字符串，无法跨脚本读取。

直接访问 `https://passport.weibo.com/sso/signin?entry=wapsso&source=wapsso&url=https%3A%2F%2Fm.weibo.cn%2F` 可以直接进入扫码登录页面，这样我们就可以直接使用这个链接, 然后手动扫码, 不用模拟点击按钮了.

我们现在有两个脚本：

1. **`get_cookie_and_st.py`：**  负责打开微博登录页面，等待用户手动扫码登录，并保存 `Cookie` 和 `st` 到 `cookie_and_st.json` 文件中。
2. **`send_weibo_api.py`：**  负责从 `cookie_and_st.json` 文件中读取 `Cookie` 和 `st`，并调用 `send_weibo` 函数发送微博。

### **2个脚本的示例代码：**

**`get_cookie_and_st.py`：**

```py
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_cookie_and_st(user_data_dir):
    """
    使用 Selenium 打开微博登录页面, 手动扫码登录, 并获取 Cookie 和 st
    """
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')  # 无头模式
    options.add_argument("user-data-dir=" + user_data_dir)

    driver = webdriver.Edge(options=options)
    driver.get("https://passport.weibo.com/sso/signin?entry=wapsso&source=wapsso&url=https%3A%2F%2Fm.weibo.cn%2F")  # 打开微博登录页面
    # 等待我拿手机扫码登录, 最多等待300秒
    try:
        WebDriverWait(driver, 300).until(
            EC.url_to_be("https://m.weibo.cn/") # 等待直到跳转到手机版微博主页
        )
        print("登录成功! 保存cookie & st")
        # 获取 Cookie
        cookies = driver.get_cookies()
        # 提取 st (XSRF-TOKEN)
        st = ""
        for cookie in cookies:
            if cookie["name"] == "XSRF-TOKEN":
                st = cookie["value"]
                break
            if cookie["name"] == "SUB":
                st = cookie["value"].split(';')
                for i in st:
                    if 'f' in i:
                        st = i
                        break

        # 保存 Cookie 和 st 到文件
        with open(r"E:\...\cookie_and_st.json", "w") as f:
            json.dump({"cookies": cookies, "st": st}, f)

        print(f"Cookie 和 st 已保存到 {r'E:\...\cookie_and_st.json'} 文件中: st: {st}")
    except Exception as e:
        print(f"等待登录超时或出现错误: {e}")
    finally:
        driver.quit()

# 调用示例 (你需要根据你的实际情况修改 user_data_dir)
user_data_dir = r"C:\...\edge_profile"  # 这里的路径需要根据你的实际情况修改, 该文件目录下有你的浏览器配置文件, 让selenium读取
get_cookie_and_st(user_data_dir)
```

**`send_weibo_api.py`：**

```py
import requests
import time
import json

def send_weibo(content, visible=0, cookie=None, x_xsrf_token=None):
    """使用 requests 库发送微博

    Args:
        content (string): 微博内容
        visible (int, optional): 可见性. 0: 公开, 1: 仅自己可见, 6: 朋友圈可见. Defaults to 0.
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/api/statuses/update"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/compose/",
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }
    if visible == 0:
        data = {
            "content": content,
            "st": x_xsrf_token,
            "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
        }
    else:
        data = {
            "content": content,
            "visible": visible,
            "st": x_xsrf_token,
            "_spr": "screen:1920x1080" # 根据屏幕分辨率修改
        }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博发送成功！")
            return True
        else:
            print(f"微博发送失败: {result['msg']}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

# 从文件中读取 Cookie 和 st
with open("cookie_and_st.json", "r") as f:
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 使用 Cookie 和 st 发送微博
send_weibo("使用保存的 Cookie 和 st 发送微博！", cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(60)

# 再次发送
send_weibo("测试使用 requests 发微博, 仅自己可见！", visible=1, cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(60)

# 再次发送
send_weibo("一条朋友圈可见的微博", visible=6, cookie=cookie_str, x_xsrf_token=st)

```

### 这两个脚本之间的关系：

1. **`get_cookie_and_st.py` 运行一次，获取 `Cookie` 和 `st` 并保存到 `cookie_and_st.json` 文件中。**
2. **`send_weibo_api.py` 可以多次运行，每次运行时都会从 `cookie_and_st.json` 文件中读取 `Cookie` 和 `st`，并使用它们来发送微博。**

### **使用方法：**

1. **运行 `get_cookie_and_st.py`。**  根据你的实际情况修改 `user_data_dir` 变量。运行后，会打开微博登录页面，你需要手动扫码登录。登录成功后，`Cookie` 和 `st` 会保存到 `cookie_and_st.json` 文件中。
2. **运行 `send_weibo_api.py`。**  这个脚本会从 `cookie_and_st.json` 文件中读取 `Cookie` 和 `st`，并使用它们来发送微博。你可以在代码中修改 `content` 和 `visible` 参数来发送不同的微博内容和设置不同的可见性。

### **关于浏览器配置文件路径：**

`user-data-dir` 指的是 **Edge 浏览器的用户配置文件目录**，而不是 `edgedriver.exe` 的路径。

*   **`edgedriver.exe`** 是 **WebDriver**，它是一个独立的程序，用于控制浏览器执行自动化操作。
*   **用户配置文件目录** 存储了浏览器的各种配置信息，例如 **Cookie、历史记录、书签、扩展程序** 等。

### **如何找到 Edge 浏览器的用户配置文件目录：**

1. **打开 Edge 浏览器。**
2. **在地址栏中输入 `edge://version`，然后按 Enter 键。**
3. **在打开的页面中，找到“个人资料路径”这一行，它后面的路径就是你的 Edge 用户配置文件目录。**

例如，我的“个人资料路径”是 `C:\Users\用户名\AppData\Local\Microsoft\Edge\User Data\Default`，那么我的 `user-data-dir` 就应该是 `C:\Users\用户名\AppData\Local\Microsoft\Edge\User Data\Default`。

**需要注意的是，不同的操作系统和不同的 Edge 版本，用户配置文件目录的路径可能会有所不同。**

### **关于 `user-data-dir` 的作用：**

在之前的脚本中，我们没有指定 `user-data-dir`，这意味着 Selenium 每次启动 Edge 浏览器时都会使用一个**全新的、空的配置文件**。这就如同你每次都打开一个全新的浏览器, 里面没有任何记录, 需要重新登录所有账号.

**指定 `user-data-dir` 的作用：**

*   **加载已有的 Cookie：**  通过指定 `user-data-dir`，我们可以让 Selenium 加载已有的用户配置文件，包括已登录网站的 Cookie。这样，我们就可以避免每次都重新登录，或者在需要时读取已经登录的网站的 Cookie。
*   **保留浏览器设置：**  用户配置文件中还保存了其他的浏览器设置，例如书签、扩展程序等。指定 `user-data-dir` 可以保留这些设置，使 Selenium 的操作更接近真实用户的行为。

`user-data-dir` 非常有用，它可以让你在自动化操作中保留已有的浏览器配置，就像在使用你自己的浏览器一样。

*   **油猴脚本：**  如果你在 Edge 浏览器中安装了油猴脚本，并且指定了 `user-data-dir`，那么 Selenium 启动的 Edge 浏览器也会加载这些油猴脚本。
*   **Python 脚本：**  你的 Python 脚本可以通过 Selenium 控制浏览器，并利用已有的配置（例如 Cookie、油猴脚本等）来执行更复杂的操作。

**需要注意的是，油猴脚本和 Python 脚本之间可能会产生冲突。**  例如，如果一个油猴脚本修改了某个网页的 DOM 结构，而你的 Python 脚本也试图操作这个 DOM 结构，就可能会出现问题。

**关于密码串和安全问题：**

**用户配置文件中通常不会明文保存用户的密码。**  网站通常会将用户的密码进行加密或哈希处理后存储，或者使用 OAuth 等授权机制，而不是直接存储用户的密码。

**但是，用户配置文件中会保存已登录网站的 Cookie。**  Cookie 中包含了用于身份验证的信息，可以让浏览器在一段时间内免登录访问网站。

**所以：**

*   **通过指定 `user-data-dir`，Selenium 可以加载已登录网站的 Cookie，从而实现免登录访问。**  这比手动去找 Cookie 更方便。
*   **如果你下载了他人的用户配置文件，并将其加载到 Selenium 中，你确实有可能登录他人已经登录的账号。**  **这是非常危险的操作，也侵犯了他人的隐私，请务必不要这样做！**

**安全警告：**

*   **不要随意下载或使用他人的用户配置文件！**  这可能导致你的账号被盗或其他安全问题。
*   **不要将你的用户配置文件分享给他人！**  这可能会泄露你的隐私信息。
*   **在使用 `user-data-dir` 时，要注意保护你的用户配置文件的安全。**



这时我发现了好像只是m.weibo.cn 的API接口的cookie数据是15分钟刷新的, 因为我又去测试了那个最初全程用selenium的脚本发微博, 这个cookie过了一整晚上还能用.

说明不同的网站或不同的 API 接口，Cookie 的有效期可能不同。

*   **m.weibo.cn 的 API 接口：**  Cookie 的有效期大约是 15 分钟。
*   **https://m.weibo.cn/compose/ 的 Selenium 脚本** Cookie 的有效期可能更长，甚至可以维持好几天。

从目前的情况来看，我们可以推测：

*   **直接使用 m.weibo.cn 的 API 接口：**  服务器可能出于安全考虑，设置了较短的 Cookie 有效期（大约 15 分钟）。
*   **通过浏览器访问 m.weibo.cn：**  服务器可能会根据用户的使用情况（例如是否保持活跃状态）来动态调整 Cookie 的有效期。这也就是为什么我的selenium脚本可以使用很长时间, 因为它是模拟人工操作, 一直保持连接状态.

## push! push! 

我们成功实现了这2个脚本，这是一个很大的进步！虽然需要手动扫码，但它为我们提供了有效的 `Cookie` 和 `st`，在它们过期之前（大约 15 分钟），我们可以利用这两个信息来调用 `send_weibo` 函数或其他 API 接口，而无需再次手动扫码登录。

**研究这个脚本的目的：**

*   **学习逆向工程的思路和方法：**  通过分析微博的登录流程和 API 接口，我们可以学习到如何分析网络请求、如何构造 HTTP 请求、如何处理 Cookie 和 Token 等逆向工程的常用方法。
*   **更深入地理解 Web 安全：**  通过研究 CSRF 攻击、验证码机制等，我们可以更深入地理解 Web 安全的原理和防范措施。
*   **为自动化操作提供基础：**  虽然这个脚本需要手动扫码，但它为我们提供了 Cookie 和 st，我们可以利用这些信息来进行后续的自动化操作，例如自动发送微博、自动评论、自动点赞等。

**接下来的目标和方向：**

1. **完善 `send_weibo` 函数：**  利用获取到的 `Cookie` 和 `st`，完善 `send_weibo` 函数，实现自动发送微博的功能。测试不同的参数，例如 `visible`、`content` 等，看看它们的作用和取值范围。
2. **探索其他的 API 接口：**  微博还有很多其他的 API 接口，例如：
    *   **获取用户信息：**  `https://m.weibo.cn/api/container/getIndex?type=uid&value=xxxxxxxx` (xxxxxxxx 是用户的 UID)
    *   **获取用户的微博列表：**  `https://m.weibo.cn/api/container/getIndex?type=uid&value=xxxxxxxx&containerid=107603xxxxxxxx` (xxxxxxxx 是用户的 UID，107603xxxxxxxx 可能是用户微博列表的 containerid)
    *   **获取微博评论：** `https://m.weibo.cn/comments/hotflow?id=xxxxxxxxx&mid=xxxxxxxxx&max_id_type=0` (xxxxxxxxx 是微博的 ID)

    ***# TODO*** 使用类似的方法来分析这些 API 接口，并尝试使用 `requests` 库来调用它们。 
    
    这些 API 接口地址是通过**分析微博的网络请求**得到的(但未经验证)。使用浏览器开发者工具，查看微博在执行各种操作时发送的网络请求，并从中找出规律。

例如，要找到获取用户信息的 API 接口，我会在微博上查看某个用户的主页，然后在开发者工具的 `Network` 面板中查看所有的网络请求，并找到那个返回了用户信息数据的请求，从而确定 API 接口的地址和参数。
    
3. **研究 `Cookie` 和 `st` 的生成机制：**  尝试分析 `Cookie` 中各个字段的含义，以及 `st` 的生成算法。这将有助于更深入地理解微博的安全机制，并有可能实现完全自动化的登录。
4. **开发更高级的自动化工具：**  在掌握了微博 API 的基础上，可以开发更高级的自动化工具，例如：
    *   **微博自动评论机器人：**  自动给指定的微博或用户评论。
    *   **微博自动点赞机器人：**  自动给指定的微博或用户点赞。
    *   **微博数据爬虫：**  自动爬取微博的公开数据，例如用户信息、微博内容、评论等。

**关于 Cookie 有效期的测试：**

**通过多次、不同时间间隔的测试，我们可以更准确地估算出 Cookie 的有效期。**

**测试方法：**

使用 `send_weibo_api.py` 脚本来进行测试。每次测试时，修改一下微博内容（例如加上时间戳），以便区分不同的测试结果。

**示例：**

```py
import requests
import time
import json
from datetime import datetime

# ... send_weibo 函数 ...

# 从文件中读取 Cookie 和 st
with open(r"E:\...\cookie_and_st.json", "r") as f:
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 获取当前时间
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 发送微博
send_weibo(f"测试 Cookie 有效期 - {now}", cookie=cookie_str, x_xsrf_token=st)

```

最新结果, 19分钟!! 应该非常接近了, 所以可以预估Cookie 有效期就是在15-20分钟左右.

19 分钟时请求失败，这意味着 Cookie 很可能在 17 分钟到 19 分钟之间的某个时间点过期了。

**测试结果分析：**

*   **17 分钟：**  测试成功。
*   **19 分钟：**  测试失败，返回 403 错误。

**403 错误 (Forbidden)** 通常表示服务器拒绝了请求。在这种情况下，很可能是因为 Cookie 过期，服务器不再认可身份验证信息。

**进一步测试：**

为了更精确地确定 Cookie 的过期时间，可以在 17 分钟到 19 分钟之间进行更密集的测试，例如：

*   **17 分 30 秒**
*   **18 分钟**
*   **18 分 30 秒**

通过这些测试，可以将 Cookie 的过期时间范围缩小到一个更小的区间。

将 Cookie 的过期时间范围缩小到一个更小的区间，主要有以下几个作用：

1. **提高脚本的稳定性和效率：**

    *   如果我们知道了 Cookie 的确切过期时间，我们就可以更准确地安排脚本的执行时间。例如，我们可以在 Cookie 过期之前的一小段时间内，重新获取 Cookie 和 st，这样就可以避免因为 Cookie 过期而导致脚本运行失败。
    *   这可以提高脚本的稳定性和效率，避免不必要的错误和重试。

2. **更深入地了解目标网站的机制：**

    *   了解 Cookie 的过期时间，可以帮助我们更深入地了解目标网站（例如微博）的身份验证机制和安全策略。
    *   例如，我们可以推测微博为什么将 m.weibo.cn 的 API 接口的 Cookie 有效期设置得这么短，可能是出于什么样的安全考虑。

3. **为后续的自动化操作提供更精细的控制：**

    *   如果我们能够精确地控制 Cookie 的刷新时间，我们就可以实现更精细的自动化操作。
    *   例如，我们可以编写一个脚本，每隔一段时间自动刷新 Cookie，并持续监控某个用户的微博动态，或者自动执行一些其他的操作。

4. **在安全测试中的应用（进阶）：**

    *   在进行安全测试时，了解 Cookie 的过期时间可以帮助我们评估目标网站的安全性。
    *   例如，如果一个网站的 Cookie 有效期过长，或者没有使用安全的 Cookie 属性（例如 HttpOnly、Secure），就可能会增加安全风险。
    *   通过分析 Cookie 的过期时间和生成机制，我们可以发现潜在的安全漏洞，并提出改进建议。

**关于自动化脚本：**

基于我们目前的两个脚本，**理论上**可以实现每隔一段时间（例如 17 分钟）自动刷新 Cookie。我们可以把两个脚本结合起来, 让 `send_weibo_api.py` 在发送一次微博后, sleep 17 分钟, 然后自动调用 `get_cookie_and_st.py`, 然后再 `send_weibo`. 但是，这需要解决几个问题：

1. **如何自动扫码：**  `get_cookie_and_st.py` 脚本需要用户手动扫码登录。要实现完全自动化，我们需要找到一种方法来自动扫码，或者绕过扫码验证。
2. **如何控制脚本的执行流程：**  我们需要编写一个主脚本来控制 `get_cookie_and_st.py` 和 `send_weibo_api.py` 的执行流程。例如，我们可以使用 Python 的 `subprocess` 模块来调用这两个脚本。
3. **如何处理异常情况：**  我们需要考虑各种可能出现的异常情况，例如网络错误、登录失败、Cookie 刷新失败等，并编写相应的代码来处理这些异常。

**关于监控用户微博动态：**

“持续监控某个用户的微博动态”是指编写一个脚本，**定期访问该用户的微博主页，获取最新的微博列表，并进行一些操作，例如：**

*   **自动点赞：**  给该用户发布的最新微博点赞。
*   **自动评论：**  给该用户发布的最新微博评论。
*   **提取用户信息：**  获取该用户的昵称、头像、粉丝数等信息。
*   **监控特定内容：**  监控该用户是否发布了包含特定关键词的微博。

**要实现这些功能，我们需要研究更多的微博 API 接口，例如：**

*   **获取用户微博列表的 API 接口。**
*   **点赞的 API 接口。**
*   **评论的 API 接口。**

***这就是那种感觉啊!! 这就是!! 那种感觉!! 感觉!!! 啊!!*** 🐱🐭

## 前进! 前进!

**编写主脚本的思路：**

以下是一个简单的思路和示例代码，用于控制 `get_cookie_and_st.py` 和 `send_weibo_api.py` 的执行流程：

```py
import subprocess
import time
import json
import os

# 假设 get_cookie_and_st.py 和 send_weibo_api.py 都在同一目录下
# 如果实际情况不是如此, 请修改为你的脚本的真实地址
COOKIE_ST_PATH = r"E:\...\cookie_and_st.json"
GET_COOKIE_SCRIPT = r"E:\...\get_cookie_and_st.py"
SEND_WEIBO_SCRIPT = r"E:\...\send_weibo_api.py"
USER_DATA_DIR = r"C:\...\User Data\Default"

def run_script(script_path, *args):
    """运行 Python 脚本"""
    command = ["python", script_path] + list(args)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"运行脚本 {script_path} 出错：")
        print(stderr.decode("utf-8"))
        return False
    else:
        print(f"脚本 {script_path} 运行成功")
        return True

def main():
    """主函数"""
    while True:
        # 获取 Cookie 和 st
        if run_script(GET_COOKIE_SCRIPT, USER_DATA_DIR):
            # 发送微博
            # 确保文件存在
            if not os.path.exists(COOKIE_ST_PATH):
                print(f"错误：文件 {COOKIE_ST_PATH} 不存在。")
                time.sleep(60)  # 等待一段时间后重试
                continue
            
            with open(COOKIE_ST_PATH, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"错误：无法解析文件 {COOKIE_ST_PATH}。")
                    time.sleep(60)  # 等待一段时间后重试
                    continue

            # 检查 'cookies' 和 'st' 键是否存在
            if "cookies" not in data or "st" not in data:
                print(f"错误：文件 {COOKIE_ST_PATH} 中缺少必要的键 'cookies' 或 'st'。")
                time.sleep(60)  # 等待一段时间后重试
                continue
                
            cookies = data["cookies"]
            st = data["st"]

            # 将 Cookie 转换为 requests 可以使用的格式
            cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            # 这里content需要修改为你想要发送的内容
            run_script(SEND_WEIBO_SCRIPT, "你的微博内容", "0", cookie_str, st)

            # 等待一段时间（例如 17 分钟）
            print("等待 17 分钟...")
            time.sleep(17 * 60)
        else:
            print("获取 Cookie 和 st 失败，等待 60 秒后重试...")
            time.sleep(60)

if __name__ == "__main__":
    main()
```
**代码说明：**

1. **`run_script` 函数：**  使用 `subprocess.Popen` 运行 Python 脚本，并获取脚本的输出。
2. **`main` 函数：**
    *   循环执行：
        *   运行 `get_cookie_and_st.py` 获取 Cookie 和 st。
        *   如果你的`send_weibo_api.py` 需要参数, 在这里添加进 `run_script()` 函数里
        *   运行 `send_weibo_api.py` 发送微博。
        *   等待一段时间（例如 17 分钟）。
        *   如果 `get_cookie_and_st.py` 运行失败, 则打印错误并等待60秒后重试
    *   你可能需要根据你的实际情况修改 `GET_COOKIE_SCRIPT` `SEND_WEIBO_SCRIPT` `COOKIE_ST_PATH` 和 `USER_DATA_DIR`

**待解决的问题：**

*   **自动扫码：**  这个脚本仍然需要手动扫码。
*   **错误处理：**  这个脚本只是简单地打印了错误信息，并没有进行更详细的错误处理。

**关于 `run_script` 函数和 `send_weibo` 函数的参数传递：**

*   **`send_weibo` 函数的定义：**

```py
def send_weibo(content, visible=0, cookie=None, x_xsrf_token=None):
    # ... 函数体 ...
```

*   **`run_script` 函数的定义：**

```py
def run_script(script_path, *args):
    # ... 函数体 ...
```

*   **`main` 函数中调用 `run_script`：**

```py
run_script(SEND_WEIBO_SCRIPT, "你的微博内容", "0", cookie_str, st)

```
**参数传递的原理：**

1. 在 `main` 函数中调用 `run_script` 时，传递的参数 `"你的微博内容"`, `"0"`, `cookie_str`, `st` 会被打包成一个元组，赋值给 `run_script` 函数的 `*args` 参数。
2. `run_script` 函数内部，`command = ["python", script_path] + list(args)` 会将 `args` 元组转换为列表，并与 `["python", script_path]` 组成完整的命令列表。
3. `subprocess.Popen` 会执行这个命令列表，相当于在命令行中执行：

```bash
python send_weibo_api.py "你的微博内容" "0" cookie_str st
```

4. `send_weibo_api.py` 脚本接收到这些参数，并将它们分别赋值给 `content`, `visible`, `cookie`, `x_xsrf_token` 这四个参数。

**如何修改 `visible` 参数：**

如果你想修改 `visible` 参数为 1，你有两种方法：

**方法一：直接在 `main` 函数中修改 `run_script` 的参数：**


run_script(SEND_WEIBO_SCRIPT, "你的微博内容", "1", cookie_str, st)  # 将 "0" 改为 "1"


这种方法最简单，直接将 `visible` 的值改为 `"1"`，在调用 `send_weibo_api.py` 时，`visible` 参数就会被赋值为 1。

**方法二：在 `main` 函数中使用关键字参数：**


*   调用方式保持不变
run_script(SEND_WEIBO_SCRIPT, "你的微博内容", "0", cookie_str, st) 
在 send_weibo_api.py 的 send_weibo()中修改
*   你可以修改 visible=6, cookie=cookie_str, x_xsrf_token=st
*   意思是在使用 send_weibo() 时, 如果有传入 visible, cookie, x_xsrf_token, 就使用传入的值, 如果没有, 就使用默认值0, None, None

def send_weibo(content, visible=6, cookie=None, x_xsrf_token=None):

这种情况下, `send_weibo` 函数中 `visible` 一直是 1

**总结：**

*   修改 `visible` 参数最简单的方法是直接在 `main` 函数中修改 `run_script` 的参数。
*   使用 `run_script(script_path, *args, visible=1)` 的方式**不正确**，因为 `*args` 必须放在所有位置参数的最后面。
*   你需要根据你的实际需求选择合适的方法。

***不开源的人是戒过毒啊?!***

***Have Fun!!***