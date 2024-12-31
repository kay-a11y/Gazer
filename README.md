# Gazer

[![GitHub Stars](https://img.shields.io/github/stars/kay-a11y/Gazer.svg?style=social&label=Star&maxAge=2592000)](https://github.com/kay-a11y/Gazer/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/kay-a11y/Gazer.svg?style=social&label=Fork&maxAge=2592000)](https://github.com/kay-a11y/Gazer/fork)
[![GitHub Issues](https://img.shields.io/github/issues/kay-a11y/Gazer.svg)](https://github.com/kay-a11y/Gazer/issues)

## 简介 (Introduction)

**Gazer** 是一个多功能的 Python 工具集合，简化各种平台的数抓取、分析和自动化任务。目前已支持微博、豆瓣和 Steam 平台，晚点🐱更新 Reddit 和 Telegram 等更多平台。本项目包含多个实用/趣味脚本工具 Have fun!

## 功能特性 (Features)

*   **数据抓取:** 从微博、豆瓣、Steam 等平台抓取数据。
*   **数据分析:** 对抓取到的数据进行分析和处理。
*   **自动化:** 自动化执行一些任务。
*   **持续更新:**  持续更新中

## 支持平台 (Supported Platforms)

*   **微博 (Weibo):** 抓取用户数据、微博内容等。
*   **豆瓣 (Douban):** 抓取电影、书籍、音乐等信息; 设置书影仅自己可见。
*   **Steam:** 抓取游戏信息、玩家数据等。
*   **Reddit (TODO):** 晚点🐱更新。
*   **Telegram (TODO):** 晚点🐱更新。

## 项目结构 (Project Structure)

```
Gazer                                                       //
├─ .gitignore                                               //
├─ DoubanGaze                                               //
│  └─ src                                                   //
│     ├─ no_peeking.py                                      //
│     └─ no_peeking4book.py                                 //
├─ how-tos                                                  //
│  ├─ Python Selenium 爬虫入门：批量将豆瓣书影标记设置为"仅自己可见".md  // `no_peeking.py` `no_peeking4book.py`
│  ├─ 使用 Python 访问 Steam API：玩家与游戏信息提取.md  //`game_scraper.py` `player_scraper.py`
│  └─ 基于 Selenium 的自动发微博脚本 (m.weibo.cn 版).md  // `GhostwriterWeibo_v2.py`
├─ LICENSE                                                  //
├─ README2.md                                               //
├─ SteamGaze                                                //
│  ├─ app_list.json                                         //
│  ├─ data                                                  //
│  └─ src                                                   //
│     ├─ game_scraper.py                                    //
│     └─ player_scraper.py                                  //
└─ WeiboGaze                                                //
   ├─ data                                                  //
   │  └─ sendpics                                           //
   └─ src                                                   //
      └─ GhostwriterWeibo_v2.py                             //

```

## 快速开始 (Quick Start)

1. **克隆项目:**
    ```bash
    git clone https://github.com/kay-a11y/Gazer.git
    ```
2. **安装依赖:**
    ```bash
    cd Gazer
    pip install -r requirements.txt # 晚点🐱更新
    ```
3. **查看使用指南:**  每个脚本工具的具体使用方法，请参考 `how-tos` 文件夹中的使用指南。

## 使用指南 (How-Tos)

详细的使用指南和教程，请参考项目中的 `how-tos` 文件夹：

## 贡献 (Contributing)

欢迎任何形式的贡献！如果你有任何建议或想法，请随时提出 Issue 或 Pull Request。

## 许可证 (License)

本项目采用 AGPLv3 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系作者 (Contact)

如果你有任何问题或建议，~~不要~~通过以下方式联系作者：

*   GitHub Issues: [https://github.com/kay-a11y/Gazer/issues](https://github.com/kay-a11y/Gazer/issues)
