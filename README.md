# Gazer

![Python](https://img.shields.io/badge/Python-rgb(54,110,170)) [![GitHub Stars](https://img.shields.io/github/stars/kay-a11y/Gazer.svg?style=social&label=Star&maxAge=2592000)](https://github.com/kay-a11y/Gazer/stargazers) [![GitHub Forks](https://img.shields.io/github/forks/kay-a11y/Gazer.svg?style=social&label=Fork&maxAge=2592000)](https://github.com/kay-a11y/Gazer/fork) [![GitHub Issues](https://img.shields.io/github/issues/kay-a11y/Gazer.svg)](https://github.com/kay-a11y/Gazer/issues) [![Commit Activity](https://img.shields.io/github/commit-activity/m/kay-a11y/Gazer)](https://github.com/kay-a11y/Gazer/commits/main)


[English](README_en.md) | 简体中文

## 简介 (Introduction)

![Gazer](https://img.shields.io/badge/Gazer-v1.0-brightgreen) ![Build](https://img.shields.io/badge/Build-Passing-green)

**Gazer** 基于 Python 和 Web 逆向，探索各平台 API 的获取方式，简化数据抓取、分析和自动化各种~~奇怪的~~任务。

小白友好! 🌟 本项目为所有脚本提供了[详细的文档教程和使用说明](https://github.com/kay-a11y/Gazer/wiki)。

目前更新了微博、豆瓣、Bilibili、Steam、网易云音乐、欧路词典。未来还将支持更多平台。本项目包含多个实用/趣味脚本工具。 Have fun! 😸

持续更新中...🔥

## 功能特性 (Features)

*   **数据抓取:** 从微博、豆瓣、Bilibili、Steam、网易云音乐等平台抓取你感兴趣的数据。
*   **数据分析:** 分析抓取到的数据，发现有趣的 insights，并进行可视化展示。
*   **自动化:** 自动化执行各种重复性任务，例如：
    *   批量管理豆瓣标签
    *   批量爬取豆瓣电影海报
    *   自动发微博
    *   下载 B 站视频和弹幕
    *   ... （更多功能等你来探索！⭐）
*   **持续更新:** 喜欢 Gazer 吗？给个小星星支持一下吧～ 你的星星是我更新的动力哦！✨

## 支持平台 (Supported Platforms)

![Douban](https://img.shields.io/badge/豆瓣-Douban-rgb(34,194,82)) ![Bilibili](https://img.shields.io/badge/哔哩哔哩-Bilibili-rgb(0,146,208)) ![Weibo](https://img.shields.io/badge/微博-Weibo-rgb(175,179,65)) ![NeteaseCloudMusic](https://img.shields.io/badge/网易云音乐-NeteaseCloudMusic-rgb(196,68,68)) ![Steam](https://img.shields.io/badge/Steam-rgb(24,51,141)) ![Eudic](https://img.shields.io/badge/欧路词典-Eudic-rgb(36,91,163))


| 平台               | 功能                                                         | 代码链接                                                                                  |
| :----------------- | :----------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| **豆瓣** | 批量管理豆瓣影视/书籍标签 🤓                           | [TagAssassin_v2](/DoubanGaze/src/API/TagAssassin_v2.py)                                 |
|                    | 自定义影视/书籍标记和短评 📽️                              | [MovieWishlister](/DoubanGaze/src/API/MovieWishlister.py)                               |
|                    | 获取影视/书籍信息 🎫                              | [get_item_info](/DoubanGaze/src/API/get_item_info.py)                               |
|                    | 获取影视/书籍评分 & 评分人数(无须cookie) ⭐                              | [movie_rate](/DoubanGaze/src/API/movie_rate_no_crumbs.py), [book_rate](/DoubanGaze/src/API/book_rate_no_crumbs.py)                        |
|                    | 批量设置影视/书籍隐私 🙊                         | [no_peeking](/DoubanGaze/src/no_peeking.py), [no_peeking4book](/DoubanGaze/src/no_peeking4book.py) |
|                    | 指定日期批量爬取影视海报 🧩                           | [PosterBandit_v2](/DoubanGaze/src/PosterBandit_v2.py)                                     |
|                    | 无损智能拼接海报图片 📌                                   | [PixelWeaver](/DoubanGaze/utils/PixelWeaver.py)                                          |
|                    | 压缩图片 📌                                               | [pixel_squeezer_cv2](/DoubanGaze/utils/pixel_squeezer_cv2.py)                            |
| **哔哩哔哩** | 下载非会员视频 📺                           | [BiliGrab](/BilibiliGaze/src/BiliGrab.py)                                 |
|             | 下载视频弹幕 XML 文件 🔣                           | [dmGrab](/BilibiliGaze/src/dmGrab.py)                                 |
| **微博 (Weibo)**   | 基于 Selenium 在 IDE 上发微博 ⌨️                         | [GhostwriterWeibo_v2](/WeiboGaze/src/GhostwriterWeibo_v2.py)                           |
|                    | 评论/点赞 API 接口 🗣️                                       | [comment_weibo_api](/WeiboGaze/src/API/comment_weibo_api.py), [like_weibo_api](/WeiboGaze/src/API/like_weibo_api.py) |
| **网易云音乐**     | 获取评论数 API 接口 🗣️                                       | [get_comment](/NeteaseCloudMusicGaze/src/API/get_comment.py)                             |
|                    | 批量抓取个人歌曲信息 🎼                                       | [yo_i_pwned_your_playlist](/NeteaseCloudMusicGaze/src/yo_i_pwned_your_playlist.py)         |
|                    | 数据分析和可视化 🎶                                           | [visualization](/NeteaseCloudMusicGaze/src/visualization.py)                               |
| **Steam**         | 抓取游戏信息 🕹️                                             | [game_scraper](/SteamGaze/src/game_scraper.py)                                           |
|                    | 抓取玩家数据 🕹️                                             | [player_scraper](/SteamGaze/src/player_scraper.py)                                         |
| **欧路词典**       | 欧路词典语境翻译 API 🔣                                      | [eudic_api](/EudicGaze/src/eudic_api.py)                                                   |
| **YouTube**       | YouTube封面 & 视频下载 🌈                                      | [downloadCover](https://github.com/kay-a11y/Gazer/blob/main/YouTube/API/downloadCover.py), [downloadVideo](https://github.com/kay-a11y/Gazer/blob/main/YouTube/API/downloadVideo.py)                                                   |

## 项目结构 (Project Structure)

```
Gazer/
├── BilibiliGaze/            # 哔哩哔哩相关功能模块 📺
├── DoubanGaze/              # 豆瓣相关功能模块 🫛
├── WeiboGaze/               # 微博相关功能模块 ⌨️
├── NeteaseCloudMusicGaze/   # 网易云音乐相关功能模块 🎵
├── SteamGaze/               # Steam 相关功能模块 🎮
├── EudicGaze/               # 欧路词典相关功能模块 🔤
├── YouTube/                 # YouTube 相关功能模块 🌈
├── imgs/                    # 图片资源 🧩
├── README.md                # 项目说明文档 😸
└── requirements.txt         # 项目依赖 🖥️
```

## 快速开始 (Quick Start)

1. **克隆项目:**
    ```bash
    git clone https://github.com/kay-a11y/Gazer.git
    ```
2. **安装依赖:**
    ```bash
    cd Gazer
    pip install -r requirements.txt
    ```

## 使用指南 (Documentation)

所有文档和教程，请参阅 [Gazer Wiki](https://github.com/kay-a11y/Gazer/wiki).

## 贡献 (Contributing)

欢迎任何形式的贡献！如果你有任何建议或想法，请随时提出 Issue 或 Pull Request。

## **警告和免责声明 (Warning and Disclaimer)**

请参阅 [DISCLAIMER.md](DISCLAIMER.md)

## 许可证 (License)

本项目采用 AGPLv3 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系作者 (Contact)

任何问题或建议，欢迎通过以下方式联系作者！

* GitHub Issues: [https://github.com/kay-a11y/Gazer/issues](https://github.com/kay-a11y/Gazer/issues)