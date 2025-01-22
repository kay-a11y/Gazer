# 逆向工程入门 (二)：获取评论/点赞微博的 API

## 前言

在上一篇博客中，我们成功逆向获取了域名 `m.weibo.cn` 的发微博 API。根据我在其中详述的过滤 `POST` 方法来抓包互动请求的 API 接口，可以较容易地推理出评论/点赞微博的 API 接口。

## 遗留问题

上篇博客中曾提到一次 Cookie 的更新，我的 Cookie 从

```
SUB=_2A25KcMuXDeRhGeVL7VYV-SfFzzyIHXVpDEFfrDV6PUJbktANLXnQkW1NTCXsnxWC6W6onbf_fEsQaxfYXJQxPzJ3; ... XSRF-TOKEN=f13778
```

变成了

```
SUB=_2A25KcMuXDeRhGeVL7VYV-SfFzzyIHXVpDEFfrDV6PUJbktANLXnQkW1NTCXsnxWC6W6onbf_fEsQaxfYXJQxPzJ3; ... XSRF-TOKEN=8ea381; mweibo_short_token=bf3d747a9d
```

值得注意的是 `mweibo_short_token` 这个字段，不知道添加这个字段会不会可以延长 Cookie 刷新时间呢？可以看到，这个字段只在我第二次的 Cookie 中出现了，第一个 Cookie 中却没有，这是一个很有意思的现象！关于 Cookie 的有效期，我测试过至少 3 次，基本都是 15-19 分钟就过期了。

*   **可能的用途：**  `short_token`，从字面上理解，可能是一个“短期令牌”。它或许是为了增强安全性或者优化用户体验而设计的。我猜测它可能与维持登录状态、减少重复验证或者实现某些特定的功能（比如快速发布、自动刷新等）有关。
*   **出现时机：**  它只在第二次测试的 Cookie 中出现了，而第一次没有。这可能说明 `mweibo_short_token` 的生成和使用有一定的触发条件。
    *   **时间因素：**  会不会和登录时长有关呢？会不会第一次登录不生成，退出登录后再次登录才生成？
    *   **操作触发：**  会不会进行某些操作才会生成呢？比如修改账户设置，发布特定内容等等。
    *   **其他因素：**  或者与服务器端的一些策略更新或者 A/B 测试有关。
*   **与 Cookie 过期的关系：**  虽然 `mweibo_short_token` 看起来像是一个“短期令牌”，但目前我们还没有确凿的证据表明它能直接影响 Cookie 的过期时间（也就是测试的 15-19 分钟）。不过，这并不排除它们之间存在某种关联的可能性。毕竟，`mweibo_short_token` 的出现肯定是有其特定目的的，只是我们现在还不清楚。
*   **如何进一步探究：**  可以从以下几个方面入手，进一步研究 `mweibo_short_token` 的作用：
    *   **对比实验：**  我们可以进行更多次的登录测试，记录每次 Cookie 的详细信息，看看 `mweibo_short_token` 是否总是伴随 `XSRF-TOKEN` 一起变化。同时，我们可以尝试在两次登录之间执行一些特定的操作，看看是否会影响 `mweibo_short_token` 的生成。比如，第一次登录后什么都不做，记录 Cookie；第二次登录后，修改一下个人资料或者发布一条微博，再记录 Cookie，对比看看。
    *   **长期观察：**  我们可以延长观察时间，看看 `mweibo_short_token` 的值是否会在一段时间后发生变化，或者消失。比如，可以分别在获取到 Cookie 后的 5 分钟、10 分钟、15 分钟、20 分钟打印一下 Cookie，观察 `mweibo_short_token` 的变化，说不定有新的发现。
    *   **网络请求分析：**  我们可以仔细分析包含 `mweibo_short_token` 的网络请求和响应，看看是否有其他相关的参数或者数据。特别是看看这个 token 是否被用于后续的某些请求中。

然而，以上方案都没有机会在今天实现，因为我记录了 3 个变化的 Cookie，均没有出现过之前只在“第二次”出现的 `mweibo_short_token=bf3d747a9d`，这让它看起来愈发神秘。

## 评论微博/删除评论的 API 接口

接下来进入正题，抓包 > 分析 > 写脚本。

### 评论微博的 API 接口

**想评论微博正文网址**： `https://m.weibo.cn/detail/xxxxxxxxxxxxxxxxx`

发送评论，在“载荷” (Payload) 处抓包：

**载荷**

```
content: 第5次 04:49 st4分测试
mid: xxxxxxxxxxxxxxxxx
st: 95e264
_spr: screen:1920x1080
```

#### 分析

*   **content:**  评论内容
*   **mid:**  微博正文网址最后的数字
*   **st:**  Cookie 的 `XSRF-TOKEN`
*   **_spr:**  屏幕分辨率

#### 代码实现思路

`get_cookie_and_st.py` 这个脚本依然用来获取记录 Cookie 和 `st`，评论脚本我们可以直接模仿之前的发微博脚本，修改一些数据，编写 `comment_weibo_api.py`。重点在于，如何构造 `mid` 合适呢？

> `mid` 其实就是微博的 ID，用来唯一标识一条微博。

1. `comment_weibo` 函数 (模仿 `send_weibo` 函数) 现在接收一个 `weibo_url` 参数，表示微博详情页的完整 URL。
2. `Referer` 直接使用传入的 `weibo_url`。
3. `mid` 从 `weibo_url` 中提取。

#### 代码示例

以下为 `comment_weibo` 函数示例：

```python
def comment_weibo(content, weibo_url, cookie=None, x_xsrf_token=None):
    """使用 requests 库评论微博

    Args:
        content (string): 评论内容
        weibo_url (string): 微博详情页的完整 URL
        cookie (string, optional): 你的微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/api/comments/create"  # 微博评论接口

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": weibo_url,  # 评论的微博正文网址, 后续继续逆向微博用户详情api, 改成检测用户新发微博的网址 TODO
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "content": content,
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080",  # 根据屏幕分辨率修改
        "mid": weibo_url.split("/")[-1],  # 从 weibo_url 中提取 mid
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博评论成功！")
            return True
        else:
            print(f"微博评论失败: {result['msg']}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

# 从文件中读取 Cookie 和 st
with open(r"E:\...\cookie_and_st.json", "r") as f:
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 获取当前时间
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 微博详情页的 URL，需要根据实际情况修改
weibo_url = "https://m.weibo.cn/detail/xxxxxxxxxxxxxxxxx" # 把你要评论的微博的url 传进来

# 使用 Cookie 和 st 评论微博
comment_weibo(f" valid - {now} 使用 py 评论微博 1", weibo_url, cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(30)

# 再次评论
comment_weibo(f" valid2 - {now} 使用 py 评论微博 2", weibo_url, cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(30)

# 再次评论
comment_weibo(f" valid3 - {now} 使用 py 评论微博 3", weibo_url, cookie=cookie_str, x_xsrf_token=st)
```

#### 代码测试

总共成功评论 2 条，第三条 403，服务器拒绝了，说明 Cookie 失效，好消息，比较精确地测得本次 Cookie 失效时间 5:04:54-05:19:27，大概 15 分钟左右。

### 删除该评论的接口 (非 API)

接下来我将删除评论的 API，并同样用 `requests` 库通过删除评论接口。

**微博正文网址**： `https://m.weibo.cn/detail/xxxxxxxxxxxxxxxxx` 
**删除评论接口载荷**

```
cid: xxxxxxxxxxxxxxxxx
st: 406044
_spr: screen:1920x1080
```

**这条评论创建时的载荷**

```
id: xxxxxxxxxxxxxxxxx
content: 1
mid: xxxxxxxxxxxxxxxxx
st: dd2ec9
_spr: screen:1920x1080
```

#### 分析

```
cid: 评论的 ID，用来唯一标识一条评论。就像 mid 是微博的 ID 一样，cid 是评论的 ID。
```

**如何找到 `cid`？**

当发送评论成功后，**服务器的响应数据中就会包含这条评论的 `cid`**！需要把它提取出来，才能用于删除评论。

**对比创建评论和删除评论的载荷：**

*   **创建评论：**  `id`、`mid` 都是微博的 ID，`content` 是评论内容。
*   **删除评论：**  只需要 `cid` 评论 ID 和 `st`。

**`id` 和 `cid` 的区别：**

*   `id` 和 `mid` 在这里基本上是等价的，都指向微博的 ID。在创建评论的请求中，你发送了 `id` 和 `mid`，但实际上只需要其中一个就足够了，服务器应该会忽略掉多余的那个。
*   `cid` 则是评论的 ID，它是在评论创建成功后由服务器返回的，用于唯一标识该条评论。

#### 代码实现思路

1. **修改 `comment_weibo` 函数**：让它在评论成功后返回 `cid`。
2. **创建一个 `delete_comment` 函数**：用于发送删除评论的请求。
3. **调用 `comment_weibo` 发送评论，获取评论的 `cid`**：将获取到的 `cid` 保存下来，用于后续删除。
4. **调用 `delete_comment` 删除评论**：使用之前保存的 `cid` 删除评论。

#### 完整代码示例

```python
import requests
import time
import json
from datetime import datetime

def comment_weibo(content, weibo_url, cookie=None, x_xsrf_token=None):
    """使用 requests 库评论微博

    Args:
        content (string): 评论内容
        weibo_url (string): 微博详情页的完整 URL
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.

    Returns:
        string or None: 成功则返回评论的 cid，失败则返回 None
    """

    url = "https://m.weibo.cn/api/comments/create"  # 微博评论接口

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": weibo_url,  # 评论的微博正文网址, 后续继续逆向微博用户详情api, 改成检测用户新发微博的网址 TODO
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "content": content,
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080",  # 根据你的屏幕分辨率修改
        "mid": weibo_url.split("/")[-1],  # 从 weibo_url 中提取 mid
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result.get("ok") == 1:
            print("微博评论成功！")
            # 提取评论的 cid
            cid = result["data"]["rootidstr"]  # 使用 rootidstr 字段，更可靠
            print(f"评论的 cid: {cid}")
            return cid
        else:
            print(f"微博评论失败: {result['msg']}")
            return None
    else:
        print(f"请求失败: {response.status_code}")
        return None

def delete_comment(cid, cookie=None, x_xsrf_token=None):
    """使用 requests 库删除微博评论

    Args:
        cid (string): 评论的 ID
        cookie (string, optional): 微博 Cookie. Defaults to None.
        x_xsrf_token (string, optional): 用于验证的 token, 需要抓包获取. Defaults to None.
    """

    url = "https://m.weibo.cn/comments/destroy"  # 删除评论的请求接口

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://m.weibo.cn/",  # 删除评论的 Referer 可以是首页
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "cid": cid,
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080",
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        result = response.json()
        if result["ok"] == 1:
            print("微博评论删除成功！")
            return True
        else:
            print(f"微博评论删除失败: {result['msg']}")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

# 从文件中读取 Cookie 和 st
with open(r"E:\...\cookie_and_st.json", "r") as f: 
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 获取当前时间
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 微博详情页的 URL，你需要根据实际情况修改
weibo_url = "https://m.weibo.cn/detail/xxxxxxxxxxxxxxxxx" # 要评论的微博的url

# 使用 Cookie 和 st 发送评论
cid = comment_weibo(f"PLS DELETE ME IN 30s!! - {now}", weibo_url, cookie=cookie_str, x_xsrf_token=st)

# 30s 后, 如果评论发送成功, 删除评论
time.sleep(30)
if cid:
    delete_comment(cid, cookie=cookie_str, x_xsrf_token=st)
```

#### 代码重点

##### 如何判断出 `rootidstr`？

其实很简单，就是通过**对比分析不同的 API 接口的响应数据**，找到了 `rootidstr`。

1. **查看评论列表的 API 响应：**
    *   当你浏览一条微博的评论列表时，浏览器会发送一个请求到类似 `https://m.weibo.cn/comments/hotflow?id=xxxxxxxxxxxxxxxxx&mid=xxxxxxxxxxxxxxxxx&max_id_type=0` 的 网址，用于获取评论数据。
    *   在这个接口的响应数据中，你会发现每一条评论都有 `id`、`rootid` 和 `rootidstr` 三个字段。
    *   **例如：**

```json
    {
                "created_at": "Sat Jan 04 14:07:28 +0800 2025",
                "id": "xxxxxxxxxxxxxxxxx",
                "rootid": "xxxxxxxxxxxxxxxxx",
                "rootidstr": "xxxxxxxxxxxxxxxxx",
                "floor_number": 55,
                "text": "\u60e0\u60e0\u597d\u5e05<span class=\"url-icon\"><img alt=\"[\u9001\u82b1\u82b1]\" src=\"https:\/\/face.t.sinajs.cn\/t4\/appstyle\/expression\/ext\/normal\/cb\/2022_Flowers_org.png\" style=\"width:1em; height:1em;\" \/><\/span>",
                "disable_reply": 0,
                "restrictOperate": 0,
                "source": "\u6765\u81ea\u5e7f\u4e1c",
                ...
        ...
    }
```

    *   可以看到，每条评论都有 `id`、`rootid` 和 `rootidstr` 三个字段，而且它们的值看起来是一样的。

2. **对比创建评论的 API 响应：**
    *   当你发送评论后，浏览器会发送一个请求到 `https://m.weibo.cn/api/comments/create`，用于创建评论。
    *   在这个接口的响应数据中，你会发现也有一条关于新创建的评论的数据，其中也包含了 `id`、`rootid` 和 `rootidstr` 字段。

```json
    {
    "ok": 1,
    "data": {
        "created_at": "Mon Jan 06 01:03:28 +0800 2025",
        "id": "xxxxxxxxxxxxxxxxx",
        "rootid": "xxxxxxxxxxxxxxxxx",
        "rootidstr": "xxxxxxxxxxxxxxxxx",
        "floor_number": 2,
        "text": "222222hhhh",
        "disable_reply": 0,
        "restrictOperate": 0,
        "source": "\u6765\u81ea\u6d59\u6c5f",
        "comment_badge": [
```

3. **推断：**
    *   对比这两个接口的响应数据，我发现 `id` 和 `rootidstr` 的值在大多数情况下都是相同的。
    *   但是，`id` 是一个数字，而 `rootidstr` 是一个字符串。在编程中，使用字符串类型的 ID 更为常见，也更安全，因为它可以避免一些潜在的数字溢出问题，也方便修改。
    *   因此，我推断 `rootidstr` 可能是更标准的评论 ID，所以在代码中使用了 `rootidstr`。

**在哪里抓包？**

可以在**浏览器的开发者工具**中抓包！具体步骤如下：

1. **打开浏览器的开发者工具：**
    *   在 Chrome 浏览器中，你可以按 `F12` 键或右键点击页面，选择“检查”来打开开发者工具。
    *   在 Edge 浏览器中，你可以按 `F12` 键或右键点击页面，选择“检查”来打开开发者工具。

2. **切换到“网络” (Network) 选项卡：**
    *   在开发者工具中，切换到“网络” (Network) 选项卡。

3. **执行你要分析的操作：**
    *   例如，如果你要分析评论列表的 API，就浏览一条微博的评论列表。
    *   如果你要分析创建评论的 API，就发送一条评论。

4. **找到对应的 API 请求：**
    *   在“网络”选项卡中，你会看到浏览器发送的所有网络请求。
    *   找到你感兴趣的 API 请求，例如 `https://m.weibo.cn/api/comments/create`。
    *   你可以根据请求的 URL、方法 (GET 或 POST) 和状态码 (例如 200) 来筛选。

5. **可以同时过滤 `mime-type:application/json` 和 `domain:m.weibo.cn`**，这样可以更精确地找到你需要的请求。
    *   在过滤框中输入 `domain:m.weibo.cn mime-type:application/json`。
    *   按回车键进行过滤。

这样，就可以看到所有来自 `m.weibo.cn` 域名且响应类型为 `application/json` 的请求了。

5. **查看响应数据：**
    *   点击你感兴趣的 API 请求，然后在右侧的面板中切换到“响应” (Response) 选项卡。
    *   你就可以看到服务器返回的 JSON 数据了。

##### 为什么删除评论的 `Referer` 可以是首页？

**关于 `Referer`：**

*   `Referer` 是 HTTP 请求头中的一个字段，用来表示**发起请求的页面的 URL**。
*   服务器可以通过 `Referer` 来判断请求的来源，并根据来源进行一些处理，例如：
    *   **防盗链：**  一些网站会通过检查 `Referer` 来防止其他网站盗用它们的图片或资源。
    *   **统计分析：**  网站可以通过 `Referer` 来统计用户访问的来源，例如用户是从哪个网站跳转过来的。
    *   **安全防护：**  服务器可以根据 `Referer` 来判断请求是否合法，例如是否来自可信的来源。

**关于删除评论的 `Referer`：**

在微博的场景下，删除评论的 `Referer` 可以是首页 `https://m.weibo.cn/`，也可以是评论所在的微博详情页，**这两种情况通常都是可以的**。

**原因：**

1. **微博的 API 设计：** 微博的 API 在处理删除评论的请求时，对 `Referer` 的校验**可能并不严格**。它可能只校验了 `st` (也就是 `X-XSRF-TOKEN`)，确保你已经登录并且操作是你本人发出的。
2. **`Referer` 的主要作用：**  对于删除评论这个操作来说，`Referer` 的作用可能主要是为了**统计分析**，例如统计用户是从哪个页面删除评论的。或者用于最基本的安全防护，确认请求来自 `m.weibo.cn` 域名下。
3. **简化操作：**  将 `Referer` 设置为首页可以简化操作，因为你不需要获取评论所在的微博详情页的 URL。

**“删除评论的 Referer 可以是首页” 的依据：**

*   经过测试，将删除评论的 `Referer` 设置为首页，是可以成功删除评论的。
*   并且在网上的一些资料中，也提到可以将删除评论的 `Referer` 设置为首页。

##### 模拟请求

这里我发现了一个重要的问题，删除评论的请求 `https://m.weibo.cn/comments/destroy` 并不是调用的 API，但是取消赞却是调用 API 的网址 `https://m.weibo.cn/comments/destroy`。

我测试了直接把 `delete_comment` 函数中的 `url = "https://m.weibo.cn/api/comments/destroy"` 这行代码改成 `url = "https://m.weibo.cn/comments/destroy"`，能成功删除。但这和我们正在逆向 API 的目的相悖。这种模拟 “API” 接口的方法：“虽然没找到 API 接口，但是用 `requests` 请求那个请求接口，构造好请求头，就当做它是 API 接口一样，也能成功删除微博评论”。这种方法，其实就是“模拟请求”。虽然没有找到真正的 API 文档，但通过抓包找到了获取数据的请求，然后“模仿”了这个请求，构造了相同的请求头和参数，发送给服务器，服务器并不知道是“模仿”的，它以为是一个正常的浏览器，所以就返回了数据。这种方法是可行的，但也有局限性：

*   **不稳定：**  如果网站更新了 HTML 结构或 JavaScript 代码，“模仿”可能会失效。
*   **难以处理复杂的情况：**  如果网站使用了复杂的反爬措施，例如验证码、加密等，“模仿”可能会被识破。

###### 待解决的问题

过滤 "js"，找到实现删除评论的 JavaScript 代码，推理出 API 接口。

**如何找到删除评论的 JavaScript 代码？**

**1. 使用浏览器的开发者工具：**

*   **打开开发者工具：**  在 Chrome 或 Edge 浏览器中，按 `F12` 键或右键点击页面，选择“检查”来打开开发者工具。
*   **切换到“网络” (Network) 选项卡：**  在开发者工具中，切换到“网络” (Network) 选卡。

**2. 复现删除评论的操作：**

*   在网页上执行删除评论的操作。

**3. 过滤和查找请求：**

*   **方法一 (推荐): 使用 `Initiator` 过滤：**
    *   在"网络"面板中，点击 `Initiator` 这一列进行排序，找到与删除评论相关的请求，这样可以找到"调用堆栈"，也就是找到哪个 `js` 文件发起的请求。
    *   在 `Initiator` 列中，找到与删除评论相关的请求。通常，`Initiator` 会显示发起请求的 JavaScript 文件和代码行号。
    *   例如，你可能会看到类似 `VMxxx:1` 或 `xxx.js:123` 这样的 `Initiator`。`VMxxx` 表示代码在虚拟机中执行，通常是动态生成的 JavaScript 代码；`xxx.js` 表示代码在名为 `xxx.js` 的文件中。

*   **方法二: 搜索 URL 关键字：**
    *   在过滤框中输入与删除评论相关的 URL 关键字，例如 `delete`、`remove`、`comment` 等。
    *   这种方法可能不太精确，因为删除评论的请求 URL 中不一定包含这些关键字。

*   **方法三: 搜索请求参数：**
    *   在过滤框中输入请求参数的名称，例如 `cid`、`st` 等，选定"过滤"，并在弹出的菜单中选择"搜索"。
    *   这种方法可以找到包含这些参数的请求，但可能需要进一步筛选。

**4. 分析 `Initiator`：**

*   点击 `Initiator` 列中显示的文件名和行号，开发者工具会自动跳转到“源代码” (Sources) 选项卡，并定位到发起请求的代码行。
*   如果 `Initiator` 显示为 `VMxxx`，则表示代码是动态生成的，你可能需要使用一些技巧（例如 `debugger` 语句或 `console.log()`）来调试代码。

**5. 设置断点，单步调试：**

*   在找到可疑的代码行后，你可以在该行设置断点。
*   再次执行删除评论的操作，程序会在断点处暂停执行。
*   使用单步调试功能（例如 `Step over`、`Step into`、`Step out`）来逐行执行代码，并观察变量的值和程序的执行流程。

**6. 分析 JavaScript 代码：**

*   仔细分析 JavaScript 代码的逻辑，找到删除评论的具体实现方式。
*   注意观察代码是如何构建请求 URL、请求参数和请求头的。
*   查找关键函数调用，比如，整个代码中是否有 `$.ajax` 或 `fetch` 等函数，有这些函数才可能发起请求。

**示例 (仅供参考)：**

假设你找到了以下可疑的 JavaScript 代码：

```javascript
function deleteComment(cid) {
  var url = "/aj/comment/delete"; // 可能是删除评论的 URL
  var data = {
    cid: cid,
    st: getST() // 假设这是一个获取 st 值的函数
  };
  $.ajax({
    url: url,
    type: "POST",
    data: data,
    success: function(response) {
      if (response.code == 100000) {
        // 删除成功
        console.log("Comment deleted successfully!");
      } else {
        // 删除失败
        console.error("Failed to delete comment:", response.msg);
      }
    }
  });
}
```

**`/aj` 是什么？**

`/aj` 只是一个 URL 的路径前缀，它本身并没有固定的含义。**但是，在很多网站的开发实践中，`/aj` 或 `/api` 这样的前缀经常被用来表示这是一个 Ajax 请求或者 API 接口。**

**为什么 `/aj` 可能表示 Ajax 请求或 API 接口？**

*   **约定俗成：**  很多网站开发者会使用 `/aj`、`/api`、`/json` 等前缀来标识 API 接口，这是一种约定俗成的做法，方便开发者和维护人员识别和管理 API 接口。
*   **Ajax (Asynchronous JavaScript and XML)：**  Ajax 是一种常用的 Web 开发技术，它可以在不刷新整个页面的情况下，与服务器进行异步通信，更新部分页面内容。Ajax 请求通常用于与 API 接口进行交互，获取数据或提交数据。
*   **前后端分离：**  在前后端分离的架构中，前端通过 Ajax 请求与后端的 API 接口进行通信，`/aj` 或 `/api` 这样的前缀可以帮助区分前端路由和后端 API 接口。

**`/aj/comment/delete` 推断：**

基于以上分析，我们可以推断出 `/aj/comment/delete` 很可能是一个 API 接口的 URL，用于删除评论。

*   `/aj` 暗示着这是一个 Ajax 请求或 API 接口。
*   `comment` 表示这个 API 接口与评论相关。
*   `delete` 表示这个 API 接口的操作是删除。

**如何验证？**

1. **在 “Network” 面板中查找：**  再次执行删除评论的操作，然后在 “Network” 面板中查找是否有以 `/aj/comment/delete` 开头的请求。如果有，那么就可以确定这是一个 API 接口的 URL。

2. **分析 JavaScript 代码：**  找到发起 `/aj/comment/delete` 请求的 JavaScript 代码，仔细分析代码逻辑，看看是如何构建请求 URL、请求参数和请求头的。

**需要注意的是：**

*   `/aj` 只是一个可能的标识，并不是所有的 API 接口都会使用这个前缀。有些网站可能会使用其他的  前缀，例如 `/api`、`/json`，甚至没有任何前缀。
*   即使找到了以 `/aj` 开头的请求，也不能完全确定这是一个公开的 API 接口，它可能只是网站内部使用的 API 接口。

**总而言之，`/aj/comment/delete` 是一个非常重要的线索，它很可能指向了一个 API 接口。接下来，你需要继续分析和验证，才能最终确定它是否是一个 API 接口，以及如何使用这个 API 接口。**

通过分析这段代码，我们可以推断出：

*   删除评论的 URL 可能是 `/aj/comment/delete`。
*   请求参数包括 `cid` 和 `st`。
*   请求类型是 `POST`。
*   `getST()` 函数可能用于获取 `st` 值。

**一些额外的技巧：**

*   **使用 `debugger` 语句：**  在 JavaScript 代码中插入 `debugger` 语句，可以让程序在执行到该语句时自动暂停，方便你进行调试。
*   **使用 `console.log()`：**  在 JavaScript 代码中插入 `console.log()` 语句，可以打印变量的值，帮助你理解程序的执行流程。
*   **美化 JavaScript 代码：**  如果 JavaScript 代码被压缩或混淆了，你可以使用一些在线工具或浏览器的开发者工具来美化代码，使其更易于阅读。

## 点赞微博的 API 接口

### 分析

**微博正文网址**： `https://m.weibo.cn/detail/xxxxxxxxxxxxxxxxx` 

**点赞载荷**

```
id: xxxxxxxxxxxxxxxxx
attitude: heart
st: 12f342
_spr: screen:1920x1080
```

**取消点赞载荷**

```
id: xxxxxxxxxxxxxxxxx
attitude: heart
st: 12f342
_spr: screen:1920x1080
```

**分析**

```
id: 微博正文网址最后的数字
attitude: heart 赞
st: Cookie 的 XSRF-TOKEN
_spr: 屏幕分辨率
```

### 代码实现思路

**`like_weibo` 和 `unlike_weibo` 函数：**

*   最初的版本写了 2 个函数, `like_weibo` 和 `unlike_weibo` 函数, 这两个函数非常相似，只有 URL 和函数名不同，故此考虑将它们合并成一个函数为 `like_or_unlike_weibo(weibo_url, action, cookie=None, x_xsrf_token=None)`，其中 `action` 参数可以是 `like` 或 `unlike`。这样可以减少代码冗余。
*   针对 `response.json()` 可能出现的错误, 应该在调用 `.json()` 前判断 `response.text` 是否为空, 否则可能导致 `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

**代码示例:**

```python
import requests
import time
import json

def like_or_unlike_weibo(weibo_url, action, cookie=None, x_xsrf_token=None):
    """
    点赞或取消点赞微博

    Args:
        weibo_url (str): 微博详情页的 URL
        action (str): "like" 表示点赞, "unlike" 表示取消点赞
        cookie (str, optional): 你的微博 Cookie. Defaults to None.
        x_xsrf_token (str, optional): 用于验证的 token, 需要抓包获取. Defaults to None.

    Returns:
        bool: 成功返回 True, 失败返回 False
    """

    if action == "like":
        url = "https://m.weibo.cn/api/attitudes/create"  # 点赞 API
    elif action == "unlike":
        url = "https://m.weibo.cn/api/attitudes/destroy"  # 取消点赞 API
    else:
        print("Invalid action. Must be 'like' or 'unlike'.")
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": weibo_url,
        "Origin": "https://m.weibo.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": x_xsrf_token,
        "Cookie": cookie,
    }

    data = {
        "id": weibo_url.split("/")[-1],  # 从 weibo_url 中提取 mid
        "attitude": "heart",  # 微博的点赞表情
        "st": x_xsrf_token,
        "_spr": "screen:1920x1080",  # 根据你的屏幕分辨率修改
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        if response.text.strip():  # 确保响应内容不为空
            result = response.json()
            if result.get("ok") == 1:
                print(f"微博{action}成功！")
                return True
            else:
                print(f"微博{action}失败: {result.get('msg')}")
                return False
        else:
            print(f"微博{action}失败: 响应内容为空")
            return False
    else:
        print(f"请求失败: {response.status_code}")
        return False

# 从文件中读取 Cookie 和 st
with open(r"E:\...\cookie_and_st.json", "r") as f: 
    data = json.load(f)
    cookies = data["cookies"]
    st = data["st"]

# 将 Cookie 转换为 requests 可以使用的格式
cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

# 微博详情页的 URL，需要根据实际情况修改
weibo_url = "https://m.weibo.cn/detail/xxxxxxxxxxxxxxxxx" 

# 使用 Cookie 和 st 点赞微博
like_or_unlike_weibo(weibo_url, "like", cookie=cookie_str, x_xsrf_token=st)

# 增加延时
time.sleep(30)

# 使用 Cookie 和 st 取消点赞微博
like_or_unlike_weibo(weibo_url, "unlike", cookie=cookie_str, x_xsrf_token=st)
```

## 总结

这篇博客记录了逆向微博评论和点赞 API 的过程。尽管还有一些遗留问题 (例如 `mweibo_short_token` 的作用，以及删除评论的真实 API 接口)，但我们已经成功地通过抓包和分析 JavaScript 代码，实现了评论和点赞微博的功能。

**主要收获：**

*   深入理解了如何使用浏览器的开发者工具来抓包和分析网络请求。
*   掌握了如何分析 JavaScript 代码，找到 API 接口的蛛丝马迹。
*   学会了如何使用 `requests` 库来模拟 API 请求。
*   体会到了逆向工程的魅力和挑战，体会到理论和实践相结合。

**后续工作：**

*   继续研究 `mweibo_short_token` 的作用和生成机制。
*   尝试找到删除评论的真正 API 接口。
*   探索更多的微博 API 接口，例如获取用户信息、获取评论列表等。

## 脚本地址：

[comment_weibo_api.py](https://github.com/kay-a11y/Gazer/tree/main/WeiboGaze/src/API/comment_weibo_api.py)

[like_weibo_api.py](https://github.com/kay-a11y/Gazer/tree/main/WeiboGaze/src/API/like_weibo_api.py)