# Gazer [![GitHub Stars](https://img.shields.io/github/stars/kay-a11y/Gazer.svg?style=social&label=Star&maxAge=2592000)](https://github.com/kay-a11y/Gazer/stargazers) [![GitHub Forks](https://img.shields.io/github/forks/kay-a11y/Gazer.svg?style=social&label=Fork&maxAge=2592000)](https://github.com/kay-a11y/Gazer/fork) [![GitHub Issues](https://img.shields.io/github/issues/kay-a11y/Gazer.svg)](https://github.com/kay-a11y/Gazer/issues)

简体中文 | [English](README_en.md)

## Introduction

**Gazer** is based on Python and Web  reverse engineering, aiming to explore how to access APIs on different platforms. Gazer also simplifies data fetching, analysis, and automates some ~~weird~~ tasks.

Beginner-friendly! 🌟 The project offers [detailed documentation and guidance](https://github.com/kay-a11y/Gazer/wiki) for all scripts.

So far, the project has supported platforms like Weibo, Douban, Steam, Netease CloudMusic, and Eudic, and will support more in the future! The project includes various practical and interesting Python scripts. Have fun! 😸

Updating...🔥

## Features

*   **Data Crawling:** Crawl data you are interested in from Weibo, Douban, Steam and Netease CloudMusic.
*   **Data Analysis:** Analyze the data fetched to gain insights and visualize them.
*   **Automation:** Automate some repetitive tasks, like:
    *   mass manage your Douban Tags
    *   Post on Weibo automatically
    *   ... (Come on and find more useful features! ⭐)
*   **Constant Update:** Like Gazer? Just give a star! Your star will be my momentum to update! ✨

## Supported Platforms

| Platform               | Feature                               | Code Link                                                   |
| :----------------- | :----------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| **Douban** | Mass manage Douban film/book tags 🤓                           | [TagAssassin_v2](/DoubanGaze/src/API/TagAssassin_v2.py)                                 |
|                    | Customize film/book tags and comments 📽️                              | [MovieWishlister](/DoubanGaze/src/API/MovieWishlister.py)                               |
|                    | Get film/book information 🎫                              | [get_item_info](/DoubanGaze/src/API/get_item_info.py)                               |
|                    | Mass set film/book as private🙊                 | [no_peeking](/DoubanGaze/src/no_peeking.py), [no_peeking4book](/DoubanGaze/src/no_peeking4book.py) |
|                    | Mass crawl film posters by their viewing dates 🧩                  | [PosterBandit_v2](/DoubanGaze/src/PosterBandit_v2.py)                                     |
|                    | Seamlessly collage posters or any images 📌                                   | [PixelWeaver](/DoubanGaze/utils/PixelWeaver.py)                                          |
|                    | Compress posters/any images  📌                                               | [pixel_squeezer_cv2](/DoubanGaze/utils/pixel_squeezer_cv2.py)                            |
| **Weibo**   | Post on Weibo in IDE base on Selenium ⌨️                         | [GhostwriterWeibo_v2](/WeiboGaze/src/GhostwriterWeibo_v2.py)                           |
|                    | Comment/Like Post API 🗣️                                       | [comment_weibo_api](/WeiboGaze/src/API/comment_weibo_api.py), [like_weibo_api](/WeiboGaze/src/API/like_weibo_api.py) |
| **Netease CloudMusic**     | Get comment count API 🗣️                                       | [get_comment](/NeteaseCloudMusicGaze/src/API/get_comment.py)                             |
|                    | Mass crawl personal playlist information 🎼                                       | [yo_i_pwned_your_playlist](/NeteaseCloudMusicGaze/src/yo_i_pwned_your_playlist.py)         |
|                    | Data analysis and visualization 🎶                                           | [visualization](/NeteaseCloudMusicGaze/src/visualization.py)                               |
| **Steam**         | Scrape game information 🕹️                                             | [game_scraper](/SteamGaze/src/game_scraper.py)                                           |
|                    | Scrape player data 🕹️                                             | [player_scraper](/SteamGaze/src/player_scraper.py)                                         |
| **Eudic**       | AI Translation API 🔣                                      | [eudic_api](/EudicGaze/src/eudic_api.py)                                                   |


## Project Structure

```
Gazer/
├── DoubanGaze/              # Douban related module 🫛
├── WeiboGaze/               # Weibo related module ⌨️
├── NeteaseCloudMusicGaze/   # Netease Cloud Music related module 🎵
├── SteamGaze/               # Steam related module 🎮
├── EudicGaze/               # Eudic Dictionary related module 🔤
├── how-tos/                 # Tutorials 📚
├── imgs/                    # Images 🧩
├── README.md                # README file 😸
└── requirements.txt         # Requirements 🖥️
```

## Quick Start

1.  **Clone the project:**

    ```bash
    git clone https://github.com/kay-a11y/Gazer.git
    ```

2.  **Navigate to the project directory:**
    ```bash
     cd Gazer
    ```

3.  **Install the requirements:**

    ```bash
    pip install -r requirements.txt
    ```

## Documentation

For detailed documentation and tutorials, please visit the [Gazer Wiki](https://github.com/kay-a11y/Gazer/wiki).

## Contributing

Contributions of any kind are welcome! Got an idea? Feel free to open an issue or submit a pull request!

## **Warning and Disclaimer**

Please refer to [DISCLAIMER.md](DISCLAIMER.md)

## License

The project uses AGPLv3. For details, please refer to [LICENSE](LICENSE).

## Contact

If you have any ideas, feel free to contact me through: 👇🏻

* GitHub Issues: [https://github.com/kay-a11y/Gazer/issues](https://github.com/kay-a11y/Gazer/issues)