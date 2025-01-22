> **免责声明：** 在使用此指南之前，请务必仔细阅读并理解 [DISCLAIMER.md](DISCLAIMER.md) 文件中的免责声明。

---

# [胆小菇] Python Selenium 爬虫入门：批量将豆瓣书影标记设置为"仅自己可见"

## **引言**

*胆小菇* 是一种"胆小"的植物，它决定使用爬虫工具，把豆瓣书影标记设置为"仅自己可见"，保护隐私的同时还能保持低调！

本文我将分享两个基于 Selenium 的 Python 脚本：

1. **no_peeking.py**：用于将豆瓣上的影视标记批量设置为"仅自己可见"。
2. **no_peeking4book.py**：用于将豆瓣上的书籍标记批量设置为"仅自己可见"。

文章还会详细解析脚本中的技术细节，帮助初学者快速入门。

---

## **技术选型与环境搭建**

1. **Edge WebDriver**：脚本使用 Edge 浏览器，确保本地已安装对应的 WebDriver。
2. **必要库安装**：安装以下 Python 库：

```bash
pip install selenium beautifulsoup4
```

---

## **核心代码解析**

### **1. 模拟登录：Cookie 处理**

由于豆瓣页面需要登录才能操作，脚本通过添加 Cookie 模拟登录。

#### **Cookie 获取步骤**
1. 登录豆瓣。
2. 按 `F12` 打开开发者工具，选择"网络"选项卡。
3. 刷新页面（`Ctrl + R`）。
4. 找到第一个请求，在其"标头"中复制 Cookie 字段。

#### **代码实现**
```python
def add_cookies_to_driver(driver, cookies_str, domain="douban.com"):
    driver.delete_all_cookies()  # 清除所有 Cookie
    driver.get(f"https://{domain}")
    cookies = cookies_str.split("; ")
    for cookie in cookies:
        try:
            key, value = cookie.split("=", 1)
            driver.add_cookie({"name": key.strip(), "value": value.strip(), "domain": domain, "path": "/"})
        except ValueError:
            print(f"Invalid cookie format: {cookie}")
```

### **2. 元素定位与操作**

脚本依赖 Selenium 定位 HTML 元素，通过点击操作完成标记设置。

#### **JavaScript 的使用**
在某些情况下，Selenium 的原生 `click()` 方法可能失效，脚本改用 JavaScript 直接操作 DOM：

```python
driver.execute_script("arguments[0].click();", element)
```

**`arguments[0].click();` 的含义：**
- 在 JavaScript 中，`arguments` 是一个特殊对象，包含函数的所有传递参数。
- `arguments[0]` 代表函数的第一个参数。
- 通过 Selenium 的 `execute_script` 方法，直接在浏览器端调用 `click()` 方法，模拟点击操作，绕过一些复杂的前端逻辑。

这种方法绕过了一些框架的限制，特别适用于动态页面。

#### **显式等待**
为了确保目标元素加载完成，脚本使用 `WebDriverWait`：

```python
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#inp-private'))
)
```

#### **HTML 元素选择提示**
有时候你和正确的选择器只有 `p1` 和 `pl` 的差距.

### **3. 处理分页逻辑**

#### **分页逻辑：no_peeking.py**
影视标记页面的下一页链接存在于以下 HTML 结构中：

```html
<span class="next">
    <link rel="next" href="/people/xxx/collect?start=15">
    <a href="/people/xxx/collect?start=15">后页&gt;</a>
</span>
```

脚本根据页面结构获取下一页链接：

```python
next_page_link_a = soup.select_one('span.next > a')
next_page_link_link = soup.select_one('link[rel="next"]')
if next_page_link_a:
    url = next_page_link_a.get('href')
elif next_page_link_link:
    url = next_page_link_link.get('href')
if url:
    url = urljoin(start_url, url)
    driver.get(url)
```

#### **书籍分页逻辑：no_peeking4book.py**
书籍页面稍显复杂，需要先获取书籍链接，再逐一访问。

```python
book_links = [item.select_one('div.info > h2 > a').get('href') for item in items]
for book_link in book_links:
    driver.get(book_link)
    # 处理每本书的隐私设置
```

---

## **脚本性能优化**

### **1. 随机延时**
为模拟真实用户操作，脚本在各操作间加入随机延时：

```python
time.sleep(random.uniform(1, 4))
```

### **2. 记录已处理状态**
通过 `last_processed_index` 避免重复处理：

```python
last_processed_index = item_index
```

### **3. 无头模式 (Headless) 和有头模式 (Headed)**
无头模式无需渲染 GUI，比有头模式更快。

#### **优点：**
- **速度更快**：省去渲染界面时间。
- **资源占用低**：减少 CPU 和内存使用。
- **自动化友好**：适合后台静默运行。

#### **缺点：**
- **调试不便**：无界面，难以观察操作过程。
- **某些反爬机制**：部分网站会检测无头浏览器特征。

启用无头模式的代码：

```python
edge_options.add_argument("--headless")
```

---

## **遇到的挑战与解决方案**

### **1. 反爬机制**
豆瓣可能通过以下方式检测爬虫：
- 请求频率过高。
- 无头浏览器特征。

**应对策略**：
1. 加入随机延时。
2. 使用更接近真实用户的请求头。

### **2. 元素定位失败**
页面结构可能变动，导致脚本失效。

**解决方案**：定期更新 CSS 选择器，使用更灵活的定位方式。

### **3. Selenium 日志屏蔽**
为了保持输出整洁，可以通过以下方式屏蔽 Selenium 的内部日志：

```python
edge_options.add_argument("--log-level=3")  # 0: INFO, 1: WARNING, 2: ERROR, 3: FATAL
```

这种方法可以有效减少无关的调试信息。

### **4. 脚本运行缓慢**
- 无头模式可显著提高速度。
- 调整显式等待时间。

---

## **总结与展望**

1. Selenium 强大且灵活，尤其适合处理动态页面。
2. 分页、Cookie、JavaScript 等技术的结合，使爬虫更高效。

脚本写完了，胆小菇很开心。

**未来改进方向：**
- 增加支持的标记类型。
- 为脚本添加 GUI 界面，提升用户体验。
- 提高运行效率，优化性能。

---

## 脚本地址： 

[no_peeking.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/no_peeking.py)

[no_peeking4book.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/no_peeking4book.py)