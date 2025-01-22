> **免责声明：** 在使用此指南之前，请务必仔细阅读并理解 [DISCLAIMER.md](DISCLAIMER.md) 文件中的免责声明。

---

# 使用 Python 访问 Steam API：玩家与游戏信息提取

## 介绍

这是一个用Python编写的Steam游戏数据采集工具, 分为玩家数据采集`player_scraper.py`和游戏信息采集`game_scraper.py`两个脚本。

**`player_scraper.py`输出预览:**

```text
数据已保存到：E:\...\0000000000000000_steam_data.json
玩家 SteamID: 0000000000000000
-------------------- 基本信息 --------------------
昵称: random_steamid
头像: https://avatars.steamstatic.com/00000000000000.jpg
个人资料链接: https://steamcommunity.com/profiles/0000000000000000/
在线状态: 0
-------------------- 封禁信息 --------------------
VAC 封禁: False
游戏封禁: 0
社区封禁: False
-------------------- 拥有游戏 --------------------
共拥有 41 款游戏:
- (AppID: 1172470) Apex Legends                                           222 小时 37 分钟
- (AppID: 1515210) The Past Within                                          4 小时 9 分钟
- (AppID:  365450) Hacknet                                                  3 小时 6 分钟
- (AppID:  230410) Warframe                                                 0 小时 0 分钟
-------------------- 最近游玩游戏 --------------------
该玩家最近没有玩过游戏。
```

**`game_scraper.py`输出预览:**

```text
请输入游戏名称：hacknet
AppID 365450 (Hacknet) 的数据已保存到：E:\...\365450_Hacknet.json

正在查询玩家 ID: 0000000000000000 玩家昵称: random_steamid
--------------------------------------------------
游戏名称：Hacknet
AppID：365450
是否拥有：是
发行商：Fellow Traveller
开发商：Team Fractal Alligator
游戏类型：Indie, Simulation
游戏模式：单人
支持手柄：是
当前价格：¥ 42.00
发行日期：12 Aug, 2015
--------------------------------------------------
```

## 使用方法

1. 设置配置信息(Steam API密钥和Steam ID)

2. 同时获取玩家数据和游戏数据:

```bash
python player_scraper.py
请输入游戏名称: hacknet
```

## 注意事项

- 需要有效的Steam API密钥
<https://steamcommunity.com/dev>

- 玩家的游戏库需要设置为公开

- 建议使用try-except处理网络请求异常

这个工具可以帮助快速查询Steam游戏信息和玩家数据, 可扩展爬取史低信息。

## 脚本地址：

[game_scraper.py](https://github.com/kay-a11y/Gazer/blob/main/SteamGaze/src/game_scraper.py)

[player_scraper.py](https://github.com/kay-a11y/Gazer/blob/main/SteamGaze/src/player_scraper.py)