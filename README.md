# Gazer

[![GitHub Stars](https://img.shields.io/github/stars/kay-a11y/Gazer.svg?style=social&label=Star&maxAge=2592000)](https://github.com/kay-a11y/Gazer/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/kay-a11y/Gazer.svg?style=social&label=Fork&maxAge=2592000)](https://github.com/kay-a11y/Gazer/fork)
[![GitHub Issues](https://img.shields.io/github/issues/kay-a11y/Gazer.svg)](https://github.com/kay-a11y/Gazer/issues)

## 简介 (Introduction)

**Gazer** 是一个多功能的 Python 工具集合，简化各种平台的数抓取、分析和自动化任务, 探讨API的获取方式。目前已支持微博、豆瓣和 Steam 平台，晚点🐱更新 Reddit 和 Telegram 等更多平台。本项目包含多个实用/趣味脚本工具 Have fun!

## 功能特性 (Features)

*   **数据抓取:** 从微博、豆瓣、Steam 等平台抓取数据。
*   **数据分析:** 对抓取到的数据进行分析和处理。
*   **自动化:** 自动化执行一些任务。
*   **持续更新:**  持续更新中

## 支持平台 (Supported Platforms)

*   **微博 (Weibo):** 抓取用户数据、微博内容等。
*   **豆瓣 (Douban):** 抓取电影、书籍、音乐等信息; 设置书影仅自己可见。
*   **Steam:** 抓取游戏信息、玩家数据等。
*   **Reddit (TODO):** 
*   **Telegram (TODO):** 
*   **Eudic**: 欧路词典语境翻译API

## 项目结构 (Project Structure)

```
Gazer                                                       //
├─ .gitignore                                               //
├─ DoubanGaze                                               //
│  └─ src                                                   //
│     ├─ no_peeking.py                                      //
│     ├─ no_peeking4book.py                                 //
│     └─ API
│         └─ TagAssassin.py                                 //
├─ how-tos                                                  //
│  ├─ Python Selenium 爬虫入门：批量将豆瓣书影标记设置为"仅自己可见".md                    // `no_peeking.py` `no_peeking4book.py`
│  ├─ 使用 Python 访问 Steam API：玩家与游戏信息提取.md                                  //`game_scraper.py` `player_scraper.py`
│  ├─ 基于 Selenium 的自动发微博脚本 (m.weibo.cn 版).md                                 // `GhostwriterWeibo_v2.py`
│  ├─ Debug 过程逐步分析：使用 JS 注入绕过 msedgedriver 的字符处理逻辑并触发表单提交元素.md  // `GhostwriterWeibo_v2.py`
│  ├─ Weibo_API_Exploration.md                                                       // `GhostwriterWeibo_v2.py`
│  ├─ Weibo_API_Exploration2.md                                                      // `comment_weibo_api.py` `like_weibo_api.py`
│  ├─ Eudic.md                                                                       // `eudic_api.py`
│  ├─ 模拟请求/api批量管理豆瓣标签.md                                                       // `TagAssassin.py`
│  └─ DISCLAIMER.md                                         //
├─ LICENSE                                                  //
├─ README.md                                                //
├─ SteamGaze                                                //
│  ├─ app_list.json                                         //
│  ├─ data                                                  //
│  └─ src                                                   //
│     ├─ game_scraper.py                                    //
│     └─ player_scraper.py                                  //
├─ WeiboGaze                                                //
│  ├─ data                                                  //
│  │  └─ sendpics                                           //
│  └─ src                                                   //
│     ├─ GhostwriterWeibo_v2.py                             //
│     └─ API                                                //
│         ├─ get_cookie_and_st.py                           //
│         ├─ send_weibo_api.py                              //
│         ├─ go_update_mycookie.py                          //
│         ├─ comment_weibo_api.py                           //
│         └─ like_weibo_api.py                              //
└─ EudicGaze
     └─ src                                                 //
        └─ eudic_api.py                                     //
    
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
3. **查看使用指南:**  每个脚本工具的具体使用方法，请参考 `how-tos` 文件夹中的使用指南。

## 使用指南 (How-Tos)

详细的使用指南和教程，请参考项目中的 `how-tos` 文件夹

## 贡献 (Contributing)

欢迎任何形式的贡献！如果你有任何建议或想法，请随时提出 Issue 或 Pull Request。

## **警告和免责声明 (Warning and Disclaimer)**

**本项目仅供学习和研究使用，请勿用于任何非法用途。使用本项目所产生的一切后果与项目作者无关。**

**在使用本项目之前，请务必仔细阅读并理解以下内容：**

*   **合法合规：** **请确保你的行为符合相关法律法规以及你所在平台的用户协议。未经授权的数据抓取和自动化操作可能构成侵权甚至违法行为。**
*   **隐私保护：** **尊重他人隐私，不要抓取或泄露任何未经授权的个人信息。**
*   **账号安全：** **使用自动化脚本可能会触发目标网站的反爬虫机制，导致你的账号被限制或封禁。请谨慎使用，并自行承担风险。**
*   **数据准确性：** **本项目无法保证抓取到的数据的准确性和完整性。**
*   **代码风险：** **本项目中的代码可能会存在一些安全漏洞或 bug。在使用之前，请务必仔细审查代码，并自行承担风险。**
*   **停止使用：** **如果你不同意上述任何条款，请立即停止使用本项目。**

**本项目作者对以下情况不承担任何责任：**

*   **因使用本项目而导致的任何直接或间接损失。**
*   **因使用本项目而导致的任何法律纠纷。**
*   **因使用本项目而导致的任何账号安全问题。**

**请记住，技术本身是中立的，但如何使用技术取决于使用者。请务必合法合规地使用本项目，做一个负责任的网络公民。**

## 许可证 (License)

本项目采用 AGPLv3 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系作者 (Contact)

如果你有任何问题或建议，~~不要~~通过以下方式联系作者：

*   GitHub Issues: [https://github.com/kay-a11y/Gazer/issues](https://github.com/kay-a11y/Gazer/issues)
