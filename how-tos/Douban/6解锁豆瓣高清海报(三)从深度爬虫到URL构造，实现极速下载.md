# 解锁豆瓣高清海报 (三)：从深度爬虫到 URL 构造, 实现极速下载

## **脚本地址:** 

[项目地址: Gazer](https://github.com/kay-a11y/Gazer)

[PosterBandit_v2.py](https://github.com/kay-a11y/Gazer/blob/main/DoubanGaze/src/PosterBandit_v2.py)

## 前瞻

之前的 [PosterBandit.py](..\DoubanGaze\src\PosterBandit.py) 是按照深度爬虫的思路一步步进入海报界面来爬取, 是个值得学习的思路, 但缺点是它爬取慢, 仍然容易碰到豆瓣的 418 错误, 本文也会指出彻底解决旧版 418 错误的方法并提高爬取速度. 现在我将介绍优化版, 这个版本通过直接构造 URL 来实现获取海报原图, 准确识别、更快爬取. 本文会重点讲解动态 headers 及其应用于请求的必要性.

## 使用方法

1.  克隆或下载项目代码. 
2.  安装依赖: `pip install requests`, 或者克隆项目代码后 `pip install -r requirements.txt`
3.  修改脚本内部的常量 `DEFAULT_POSTER_PATH`, 设置默认保存路径. 
4.  修改主函数处的 `poster_save_path` 保存路径. 
5.  修改主函数处的起始日期 `target_date_1` 和截止日期 `target_date_2`. 同时修改起始爬取页参数为包含截止日期标记的页数 `page_id=1`.
6.  填写你的 `cookies`. 
7.  运行脚本 `PosterBandit_v2`. 

**注意**

* 起止日期不要写错, 否则判断逻辑会出错. 
* 见免责声明.

示例:

```py
    target_date_1 = "2024-12-1"  # TODO 填写起始日期
    target_date_2 = "2024-12-31" # TODO 填写截止日期
```

### 文件结构

```txt
Gazer/
├── DoubanGaze/
│   ├── data/
│   │   └── poster/
│   │       └── 2024_1_1_2025_1_31/
│   └── src/
│       ├── PosterBandit.py
│       └── PosterBandit_v2.py
└──...
```

## 脚本构思详解

V2 版本处理了深度为 1 的数据 (缩略图链接) 和深度为 2 的数据 (最终海报 URL), 但它 *爬取* 的深度仍然是 0. 依然在括号中标记了爬取深度.

1. 以默认第一页或指定的页数作为爬取的**起始页** (**爬取深度 0**), 找到所有包含电影条目的 div 元素, 最大为 15 个.  ▶️ `get_movie_elements`

    电影条目 CSS 选择器: `#content > div.grid-16-8.clearfix > div.article .item.comment-item`

3.  在电影条目的 div 元素内找到对应的**日期元素**和**压缩的海报图片链接** ▶️ `get_movie_info`

    1. 日期 CSS 选择器: `#content div.info span.date`

        检查是否在指定的起止日期参数之间 ▶️ `compare_date`

    2. 这个页面的海报图片元素 CSS 选择器: `#content div.pic img`

        1. 以 <绝命毒师 第二季> 为例, 在这里 `<img>` 标签的 source 链接是 `https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2016505705.webp` (可以认为是**数据深度 1**, 因为它直接来源于起始页), 高清海报页面 `https://movie.douban.com/photos/photo/2016505705/` 的海报元素 source 链接是 `https://img9.doubanio.com/view/photo/l/public/p2016505705.webp` (**数据深度 2**, 因为它需要通过详情页才能获取, 或者说, 如果按照 V1 的"点击"流程, 需要经过两层(收藏页 -> 电影详情页 -> 海报大图)页面跳转才能到达).
            > 注意: ![poster html](/imgs/poster_html.png) 这个 `div` 中放了 2 个可下载图片资源链接. 首先, 后一个 jpg 链接需要通过 JS 动态加载激活, 直接下载是不可用的; 其次, 一般 WebP 文件会更小, 基于 WebP 更先进的压缩算法, 肉眼观察可能会感觉 WebP 更清晰. 所以这里第一个链接是最优选择.

        2. 观察两个链接, 可以知道, 只要在这个页面找到第一个链接, 即可构造第二个: `https://img9.doubanio.com/view/photo/l/public/p{photo_id}.webp` (**数据深度 2**, 但 V2 版本是直接构造这个 URL, 没有爬取这个深度的页面)

        检查是否在指定的起止日期参数之间 ▶️ `compare_date`

4.  下载图片**保存**到指定路径, 创建文件夹名称, 根据日期定义, 如 `2024_1_1_2024_12_31`  ▶️ `create_folder` `save_poster`


## 爬虫效率优化

V2 版本 ( `PosterBandit_v2.py` ) 确实比 V1 版本 ( `PosterBandit.py` ) 理论上应该更快, 因为减少了不必要的请求 (不再需要进入每个电影的详情页, 直接构造海报 URL).   而且用 `save_poster()` 函数单独测试海报下载也是成功的, 这说明问题很可能出在 V2 版本的爬虫逻辑上, 而不是 `save_poster()` 函数本身. 

### **问题:**

* V2 版本: 出现高频率 418 错误 (只能下载第一张);
* V1 版本: (深度爬虫) 能正常下载. 但速度慢, 可能会有 418. 

### **V1 和 V2 的主要区别 (请求层面)：**

* **V1 (深度爬虫):**
    1. 请求豆瓣电影收藏页面 (`https://movie.douban.com/people/{user_id}/collect...`). 
    2. 对于页面上的每个电影条目, 获取电影详情页链接. 
    3. 请求每个电影详情页链接 (`https://movie.douban.com/subject/{movie_id}/`). 
    4. 从电影详情页中获取海报列表页链接. 
    5. 请求海报列表页链接 (`https://movie.douban.com/subject/{movie_id}/photos...`). 
    6. 从海报列表页中获取第一张海报的详情页链接. 
    7. 请求第一张海报的详情页链接 (`https://movie.douban.com/photos/photo/{photo_id}/`). 
    8. 从海报详情页中获取最终的海报图片 URL. 
    9. 请求最终的海报图片 URL, 下载海报. 

* **V2 (构造 URL):**
    1. 请求豆瓣电影收藏页面 (`https://movie.douban.com/people/{user_id}/collect...`). 
    2. 对于页面上的每个电影条目, 获取电影的 *缩略图* 链接 (例如 `https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2016505705.webp`). 
    3. 从缩略图链接中提取 photo ID. 
    4. 直接构造海报图片 URL (`https://img9.doubanio.com/view/photo/l/public/p{photo_id}.webp`). 
    5. 请求构造的海报图片 URL, 下载海报. 

### **V2 版本高频率 418 的原因：**

1. **请求频率过高：**

   * **V1 的 “缓冲” 作用：**  V1 版本虽然请求次数多, 但每次请求之间都有一定的 “缓冲”.   它需要逐个进入电影详情页、海报列表页等, 这些页面加载本身就需要时间.   这些 “无意” 的延迟, 反而降低了请求频率, 不容易触发豆瓣的反爬机制. 
   * **V2 的 “集中” 请求：**  V2 版本大大减少了请求次数, 理论上更快.   但它把对海报图片 URL 的请求 **集中** 在了一起.  在循环中, 它会快速地、连续地请求多个海报图片 URL, 这很容易被豆瓣服务器识别为爬虫行为, 从而触发 418 错误 (或者其他更严厉的封禁). 

2. **`Referer` 头的问题：**

   * **`Referer`：** 2 个版本, 当请求最终的海报图片 URL 时, `Referer` 头理应是海报详情页的 URL, 但实际都是直接请求它. 此时, `Referer` 头会是豆瓣电影收藏页面 URL (例如 `https://movie.douban.com/people/{user_id}/collect...`).  服务器可能会认为, 直接从收藏页面请求海报图片 URL 这种行为不太正常, 因为用户通常会先点击海报进入详情页, 然后再查看大图.  因此, 豆瓣可能会对这种 `Referer` 头的请求更加警惕. 

### **解决: 修改后的 V2 版本代码 (重点是增加延迟和修改 Referer)：**

**主要修改：**

1. **`get_headers()` 函数修改：**
   * 参数名 `viewed_movie_url` 改为 `referer`, 更通用. 
   * 函数内部使用传入的 `referer` 参数设置 `Referer` 请求头. 

2. **`save_poster()` 函数：**
   *   增加了一个 `headers` 参数. 
   *   在 `requests.get()` 中使用传入的 `headers` 参数. 

3. **`download_poster_images()` 函数修改：**
   * 在首次请求豆瓣电影收藏页面时, 使用 `viewed_movie_url` 作为 `Referer`. 
   * 在循环内部, 构造好 `headers` 后, 调用 `save_poster()` 函数时, 传入 `headers` 参数. 
   * **在每次循环请求海报 URL 之前, 增加 `time.sleep(random.uniform(2, 6))`, 随机延迟 2-6 秒或更长**. 用于降低请求频率. 

 V1 版本代码也作了同样的修改, 测试后显著**提高了速度**以及**避免了 418**.

## 性能对比

对比一下, 同样的内容完整爬取, 包括延迟时间, 总耗时:

* 38 张图片: V1 版本 5 分 29 秒, V2 版本 2 分 50 秒.
* 110 张图片: V1 版本 15 分 10 秒, V2 版本 8 分 15 秒.

V1 版本 (深度爬虫) 的速度提升也很明显, 这说明 **`Referer` 头** 的正确设置确实非常重要！ 豆瓣的反爬机制很可能对 `Referer` 做了比较严格的检查. 

V2 版本 (构造 URL) 会比 V1 快近一倍. 因为 V2 版本减少了大量不必要的请求 (不需要访问每个电影的详情页和海报列表页), 直接构造最终的海报 URL, 所以速度最快. 

**总结：**

*   **解决了 418 错误：**  通过增加延迟和正确设置 `Referer` 头. 
*   **优化了 V1 版本：**  给 V1 版本增加 `Referer` 头更新, 提高了 V1 的速度 (从超过 5 分钟缩短到大约 2 分半钟). 
*   **性能对比：**  对比了 V1 和 V2 版本的性能, 验证了 V2 版本 (构造 URL) 的速度优势. 