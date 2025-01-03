> **免责声明：** 在使用此指南之前，请务必仔细阅读并理解 [DISCLAIMER.md](DISCLAIMER.md) 文件中的免责声明。

---

# Debug 过程逐步分析：使用 JS 注入绕过 msedgedriver 的字符处理逻辑并触发表单提交元素

本文记录了一次使用 Python 和 Selenium 编写微博自动发布脚本时遇到的 Debug 过程。通过这次 Debug，我深入了解了 msedgedriver 对 Unicode 字符的支持、JavaScript 事件触发机制以及 Selenium 的工作原理。

## 错误代码示例

这里展示发送微博的核心代码块`ghost_writer`函数, 主要和表单提交以及隐式等待有关:

```python
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
    # 输入想发布的微博内容
    weibo_textarea.send_keys(writer)

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
  
    # 提交微博
    # 等待提交按钮可见
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.m-box.m-flex-grow1.m-box-model.m-fd-row.m-aln-center.m-justify-end.m-flex-base0 > a')))
    submit_button.click()
    time.sleep(2)
    print("微博发布成功")
```

## 配置环境

- Python 3
- Selenium
- msedgedriver (Microsoft Edge WebDriver)
- 微博: https://m.weibo.cn/compose/

## 问题一：`selenium.common.exceptions.WebDriverException: Message: unknown error: msedgedriver only supports characters in the BMP`

### 问题发现

在使用微博发布脚本发送一段包含 emoji（例如😭）的文本时，脚本报错：

```
selenium.common.exceptions.WebDriverException: Message: unknown error: msedgedriver only supports characters in the BMP
```

### 问题排查

1. **检查代码：** 首先检查了 `ghost_writer` 函数中可能导致问题的代码行, 例如CSS选择器定位元素部分, 没有发现问题.
2. **验证 Cookie：**  重新复制了微博的 Cookie 并更新到脚本中，然后重新运行，问题依旧，排除 Cookie 失效的可能性。

### 问题分析

错误信息 `msedgedriver only supports characters in the BMP` 表明 msedgedriver 只支持 **BMP**（Basic Multilingual Plane，基本多文种平面）中的字符。

> **什么是 BMP？**
> BMP 是 Unicode 编码中的一个区域，包含了 U+0000 到 U+FFFF 范围内的字符，涵盖了大多数现代语言的字符，包括常用的拉丁字母、中文字符、标点符号等。

而我们使用的 emoji 😭 并不在 BMP 范围内。😭 的 Unicode 编码为 U+1F62D，它属于 **SMP**（Supplementary Multilingual Plane，多文种补充平面）。

> **如何查询 BMP 范围内的字符？**  可以在 Unicode 官网（[https://unicode.org/charts/](https://unicode.org/charts/)）上查看 BMP 范围内的字符。BMP 的范围是 U+0000 到 U+FFFF。

**msedgedriver 的这个限制导致它无法正确处理我们输入的 emoji 字符。**

### 解决方案探索

针对这个问题，我尝试了以下几种解决方案：

#### 方案 1：删除或替换特殊字符

这是最简单直接的方法。将文本中的 emoji 等特殊字符删除，或者替换成 BMP 范围内的字符，例如用 `:)` 或 `:(` 代替 `😭`。

- **优点：** 简单易行，无需修改代码逻辑。
- **缺点：**  无法使用 emoji 等特殊字符，降低了表达的丰富度。

#### 方案 2：更换浏览器驱动

如果必须使用 emoji 等特殊字符，可以考虑更换成对 Unicode 字符支持更好的浏览器驱动，例如 ChromeDriver。

- **优点：**  可以从根本上解决 msedgedriver 对 Unicode 字符支持不佳的问题。
- **缺点：**  需要下载并配置新的浏览器驱动，可能需要修改部分代码。

#### 方案 3：使用 JavaScript 注入

通过执行 JavaScript 代码来设置文本框的值，绕过 Selenium 的 `send_keys` 方法和 msedgedriver 的字符处理逻辑。

```python
driver.execute_script("arguments[0].value = arguments[1];", weibo_textarea, writer)
```

> **什么是 DOM 元素？**
> DOM（Document Object Model，文档对象模型）是 HTML 文档的编程接口。它将 HTML 文档表示为一个树形结构，每个节点都代表文档的一部分（例如一个元素、属性或文本）。JavaScript 可以通过 DOM 来访问和操作 HTML 文档的内容、结构和样式。在上面的代码中，`weibo_textarea` 就是一个 DOM 元素，代表微博发布框。

- **优点：**  无需更换浏览器驱动，可以继续使用 msedgedriver。
- **缺点：**  这是一种比较 hacky 的方法，可能会受到微博网站安全策略的影响。我们会在后文中详细讨论它的弊端.

#### 方案 4: 缓慢输入

这是一种基于经验猜测的方法。认为 `msedgedriver` 处理速度较慢, 无法及时处理所有输入字符, 特别是非BMP字符, 如emoji. 因此, 可以尝试放慢输入速度, 给驱动更多时间处理每个字符.

```python
import time

# ... 其他代码 ...

# 缓慢输入
for char in writer:
    weibo_textarea.send_keys(char)
    time.sleep(0.1)  # 每个字符之间暂停 0.1 秒

# ... 其他代码 ...

```

- **优点:** 简单, 容易实现.
- **缺点:**
    -   没有从根本上解决问题，只是试图通过一种取巧的方式来绕过问题。
    -   `time.sleep()` 的时间不好控制，设置得太短可能无效，设置得太长会影响用户体验。
    -   不同的网络环境和电脑性能可能会导致 `time.sleep()` 的效果不一致，从而影响代码的稳定性。
    -   如果微博更新了前端逻辑，不再受输入速度的影响，这个方法就会失效。

#### 方案 5: 将emoji替换成unicode发送

这也是一种基于经验猜测的方法, 寄希望于驱动能直接正确处理unicode.

```python
writer = """
   猜猜哪个 emoji 的 unicode 是 \U0001F62D
   """
```

- **优点:** 简单, 容易实现.
- **缺点:**
    - 如果驱动本身就不支持这种方式, 那么这个方法就会失效.
    - 如果微博更新了前端逻辑, 可能导致这个方法失效.

最终，我选择了**方案 3：使用 JavaScript 注入**。因为它在不更换浏览器驱动的情况下，有较高的成功率。

## 问题二：JS 注入内容后，提交按钮未被激活

### 问题排查

选择了**方案 3：使用 JavaScript 注入**后, 发现它可以成功地绕过msedriver的限制, 但是在有头模式下测试的时候, 发现又有新问题出现: 文本输入后，右上角的发送按钮仍然是灰色的，无法点击。

-   **视觉确认:** 当手动输入任意字符时，发送按钮会立即变为可点击状态。
-   **元素定位排除:** 初步怀疑是否是由于 DOM 结构变化, 导致提交按钮定位失效, 后来排除了这个猜想. 因为在有头模式下，可以清楚地看到，发送按钮是可以被定位到的, 只不过是灰色不可点击状态。这说明，发送按钮的定位没有问题，问题出在**按钮没有被激活**。

### 问题分析

造成这个问题的原因是：**微博的页面逻辑依赖于某些 JavaScript 事件来激活发送按钮。**

-   **手动输入**时，会触发一系列的 JavaScript 事件，例如 `input`、`keyup`、`change` 等。这些事件会被微博的前端代码捕获，并执行相应的逻辑，最终激活发送按钮。
-   **JS 注入**内容时，并**没有触发**这些关键的 JavaScript 事件，导致微博的前端代码没有执行激活发送按钮的逻辑。

### 解决方案

既然问题出在 JS 事件没有被触发，那么解决方案就是：**在使用 JS 注入后，手动触发这些事件！**

#### 方案 1：触发 `input` 事件

```javascript
// 使用 JavaScript 设置文本框的值
driver.execute_script("arguments[0].value = arguments[1];", weibo_textarea, writer)

// 触发 input 事件
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", weibo_textarea)
```

- **原理：**
    -   `dispatchEvent` 方法用于在指定元素上触发一个事件。
    -   `new Event('input', { bubbles: true })` 创建了一个 `input` 事件，并设置 `bubbles: true` 表示该事件会向上冒泡。

将 `ghost_writer` 函数中原来的 `weibo_textarea.send_keys(writer)` 替换成上面的代码。

#### 方案 2：触发 `change` 事件

```javascript
// 使用 JavaScript 设置文本框的值
driver.execute_script("arguments[0].value = arguments[1];", weibo_textarea, writer)

// 触发 change 事件
driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", weibo_textarea)
```

- **原理：** `change` 事件通常在表单元素的值发生改变，并且失去焦点时触发。

#### 方案 3：触发 `keyup` 事件（模拟键盘按键）

```javascript
// 使用 JavaScript 设置文本框的值
driver.execute_script("arguments[0].value = arguments[1];", weibo_textarea, writer)

// 触发 keyup 事件 (模拟按下空格键)
driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: ' ', code: 'Space' }));", weibo_textarea)
```

- **原理：** `keyup` 事件在键盘按键被释放时触发。这里模拟了一个空格键的 `keyup` 事件。

#### 方案 4：组合触发多个事件

```javascript
// 使用 JavaScript 设置文本框的值
driver.execute_script("arguments[0].value = arguments[1];", weibo_textarea, writer)

// 依次触发 input 和 change 事件
driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", weibo_textarea)
driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", weibo_textarea)
```

- **原理：**  结合多种事件的触发，更全面地模拟用户输入。

经测试，**方案 1：触发 `input` 事件** 成功解决了问题！这表明，微博的发送按钮激活逻辑很可能监听了 `input` 事件。

## 问题三：隐式等待导致的问题

在最初的 `ghost_writer` 函数中，点击发送按钮后，有这样一段代码：

```python
submit_button.click()
time.sleep(2)
print("微博发布成功")
```

这段代码的本意是等待微博发布完成。然而，`time.sleep(2)` 是一种**隐式等待**，它会在指定的时间内等待页面加载完成, 或者等待某个元素的出现。但是, 即使点击发送按钮失败（例如按钮是灰色的），这段代码仍然会等待 2 秒钟，然后执行 `print("微博发布成功")`。这会导致一个问题：**即使微博没有发布成功，脚本也会错误地输出“微博发布成功”。**

### 解决方案

将 `time.sleep(2)` 删除，并使用 `try...except` 语句来捕获 `submit_button.click()` 可能出现的异常。

```python
try:
    # 提交微博
    # 等待提交按钮可见
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.m-box.m-flex-grow1.m-box-model.m-fd-row.m-aln-center.m-justify-end.m-flex-base0 > a')))
    # CSS 和 Xpath 结合定位
    # submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]//a[contains(@class, "m-box")]'))) 

    submit_button.click()
    print("微博发布成功")
except Exception as e:
    print(f"微博发布失败: {e}")
```

**原理：**

*   `try...except` 语句用于捕获代码块中可能出现的异常。
*   如果 `submit_button.click()` 执行成功，则会输出“微博发布成功”。
*   如果 `submit_button.click()` 执行失败（例如按钮不可点击），则会抛出异常，`except` 语句块会捕获这个异常，并输出“微博发布失败: ”以及具体的错误信息。

> **为什么 `submit_button.click()` 会抛出异常？**
> 当我们使用 `wait.until(EC.element_to_be_clickable(...))` 时，Selenium 会等待元素变为可点击状态。但是，在问题二中，即使发送按钮是灰色的，`wait.until` 依然会认为元素是可点击的，并返回该元素。而当我们尝试点击这个实际上不可点击的元素时，Selenium 就会抛出异常, 通常是 `ElementClickInterceptedException` 或者 `ElementNotInteractableException`.

这样修改之后，脚本就能更准确地判断微博是否发布成功，并给出相应的提示。同时也去掉了固定的延时, 加速了发布。

## 总结

通过这次 Debug，可以深入了解到以下几个方面：

-   **msedgedriver 对 Unicode 字符的限制：** 了解了 BMP 和 SMP 的概念，以及 msedgedriver 对非 BMP 字符的处理方式。
-   **JavaScript 事件的重要性：**  认识到 JavaScript 事件在网页交互中的重要作用，以及如何通过 `dispatchEvent` 手动触发事件。
-   **Selenium 的工作原理：**  对 Selenium 的 `send_keys`、`execute_script`、`wait.until` 等方法有了更深入的理解。
-   **隐式等待的弊端：**  认识到隐式等待可能导致的问题，需要学会使用 `try...except` 来进行更精细的错误处理。
