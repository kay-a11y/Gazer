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
史低价格：无法获取 元
上次史低时间：无法获取
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
- 玩家的游戏库需要设置为公开
- 建议使用try-except处理网络请求异常

这个工具可以帮助快速查询Steam游戏信息和玩家数据, 可扩展爬取史低信息。

## 教程和代码

## 1. 获取 Steam API

<https://steamcommunity.com/dev>

## 2. 玩家数据采集 (player_scraper.py)

```python
import requests
import json
import os 

STEAM_API_KEY = "YOU_API_KEY"  # API 密钥
STEAM_ID = "0000000000000000"  # 查询的玩家的 Steam ID
OUTPUT_DIR = r"E:\..." # 保存路径

def format_playtime(minutes):
    """将游戏时间分钟数格式化为"小时 分钟"的字符串。"""
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours} 小时 {remaining_minutes} 分钟"

def get_player_info(steam_id):
    try:

        # 1. 获取玩家基本信息和状态
        url_summaries = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}"
        response_summaries = requests.get(url_summaries)
        response_summaries.raise_for_status()
        player_summaries = response_summaries.json()['response']['players'][0]

        # 2. 获取玩家封禁状态
        url_bans = f"http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={STEAM_API_KEY}&steamids={steam_id}"
        response_bans = requests.get(url_bans)
        response_bans.raise_for_status()
        player_bans = response_bans.json()['players'][0]

        # 3. 获取玩家拥有的游戏
        url_owned_games = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&format=json&include_appinfo=1&include_played_free_games=1"
        response_owned_games = requests.get(url_owned_games)
        response_owned_games.raise_for_status()
        owned_games_data = response_owned_games.json()['response']
        owned_games = owned_games_data.get('games', [])

        # 4. 获取玩家最近玩过的游戏
        url_recent_games = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&format=json"
        response_recent_games = requests.get(url_recent_games)
        response_recent_games.raise_for_status()
        recent_games = response_recent_games.json()['response'].get('games', []) # 使用 .get() 防止 KeyError

        # 按照游玩时间排序
        owned_games.sort(key=lambda x: x.get('playtime_forever', 0), reverse=True)

        # 将所有数据整合到一个字典中
        all_data = {
            "basic_info": player_summaries,
            "ban_info": player_bans,
            "owned_games": owned_games, # 直接保存 owned_games 列表
            "recent_games": recent_games
        }

        # 创建输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 构建输出文件路径
        output_file = os.path.join(OUTPUT_DIR, f"{steam_id}_steam_data.json")

        # 将数据写入 JSON 文件，并使用 ensure_ascii=False 避免中文乱码
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

        print(f"数据已保存到：{output_file}")

        # 在终端预览信息 (根据需要注释/取消注释以下代码)
        print(f"玩家 SteamID: {steam_id}")
        print("-------------------- 基本信息 --------------------")
        print(f"昵称: {player_summaries['personaname']}")
        print(f"头像: {player_summaries['avatarfull']}")
        print(f"个人资料链接: {player_summaries['profileurl']}")
        print(f"在线状态: {player_summaries['personastate']}") # 0:离线, 1:在线, 2:忙碌, 3:离开, 4:睡眠, 5:希望交易, 6:希望交易
        if 'gameid' in player_summaries: # 判断是否在游戏中
            print(f"正在游玩游戏 AppID: {player_summaries['gameid']}")

        print("-------------------- 封禁信息 --------------------")
        print(f"VAC 封禁: {player_bans['VACBanned']}")
        print(f"游戏封禁: {player_bans['NumberOfGameBans']}")
        print(f"社区封禁: {player_bans['CommunityBanned']}")

        print("-------------------- 拥有游戏 --------------------")
        if owned_games:
            print(f"共拥有 {owned_games_data['game_count']} 款游戏:")
            max_app_id_length = max(len(str(game['appid'])) for game in owned_games) # 获取最长的 AppID 长度
            for game in owned_games:
                playtime_str = format_playtime(game.get('playtime_forever', 0))
                print(f"- (AppID: {str(game['appid']).rjust(max_app_id_length)}) {game['name'].ljust(50)} {playtime_str.rjust(15)}") # 右对齐
        else:
            print("该玩家没有公开游戏库或没有游戏。")

        print("-------------------- 最近游玩游戏 --------------------")
        if recent_games:
            print("最近游玩的游戏:")
            for game in recent_games:
                playtime_2weeks_str = format_playtime(game['playtime_2weeks'])
                playtime_forever_str = format_playtime(game['playtime_forever'])
                print(f"- {game['name'].ljust(50)} 最近两周游玩时间: {playtime_2weeks_str.rjust(15)}, 总游玩时间: {playtime_forever_str.rjust(15)}")
        else:
             print("该玩家最近没有玩过游戏。")

    except Exception as e:
        print(f"发生未知错误：{e}")
        return None # 发生错误时返回 None

def load_player_owned_games(steam_id):
    try:
        output_file = os.path.join(OUTPUT_DIR, f"{steam_id}_steam_data.json")
        with open(output_file, 'r', encoding='utf-8') as f:
            player_data = json.load(f)
            owned_games = [game.get('appid') for game in player_data.get('owned_games', [])] # 从 owned_games 键提取
            return owned_games
    except FileNotFoundError:
        print(f"玩家 {steam_id} 的数据文件未找到。")
        return None
    except json.JSONDecodeError:
        print(f"玩家 {steam_id} 的数据文件损坏，请重新获取数据。")
        return None
    except (KeyError, TypeError) as e:
        print(f"解析玩家 {steam_id} 数据时出错：{e}")
        return None
    except Exception as e:
        print(f"加载玩家 {steam_id} 数据时发生未知错误：{e}")
        return None

    
def get_player_owned_games(steam_id):
    try:
        api_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&format=json&include_appinfo=1"
        response = requests.get(api_url)
        response.raise_for_status()
        owned_games_data = response.json().get('response', {}).get('games', [])
        owned_games = [game.get('appid') for game in owned_games_data]
        return owned_games
    except requests.exceptions.RequestException as e:
        print(f"获取拥有游戏信息出错：{e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        print(f"解析拥有游戏JSON数据出错：{e}")
        return None
    except Exception as e:
        print(f"获取拥有游戏信息发生未知错误：{e}")
        return None

if __name__ == "__main__":
    get_player_info(STEAM_ID)
```

### 2.2 获取玩家信息  (game_scraper.py)

```python
import requests
import json
import os
import player_scraper
import argparse  # 导入 argparse 模块用于处理命令行参数

STEAM_API_KEY = "YOU_API_KEY"
OUTPUT_DIR = r"E:\..."

APP_LIST_FILE = r"E:\...\app_list.json" #app列表保存的文件名

def find_app_name_by_id(app_id):
    try:
        with open(APP_LIST_FILE, 'r', encoding='utf-8') as f:
            app_list = json.load(f)
        for app in app_list:
            if app['appid'] == app_id:
                return app['name']
        return None  # 如果没有找到对应的 App ID，返回 None
    except FileNotFoundError:
        print("App list file not found. Updating...")
        update_app_list() #调用更新app列表的函数
        return find_app_name_by_id(app_id) # 递归调用自身，重新查找
    except json.JSONDecodeError:
        print("App list file Corrupted, Updating...")
        update_app_list()
        return find_app_name_by_id(app_id)
    except Exception as e:
        print(f"查找App名称发生未知错误：{e}")
        return None
    
def update_app_list(): #更新app列表
    try:
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        with open(APP_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data['applist']['apps'], f, indent=4)
        print("App list file updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error updating app list: {e}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

def find_app_id_by_name(app_name):
    try:
        with open(APP_LIST_FILE, 'r', encoding='utf-8') as f:
            app_list = json.load(f)
        for app in app_list:
            if app['name'].lower() == app_name.lower(): #转换为小写进行比较，忽略大小写
                return app['appid']
        return None
    except FileNotFoundError:
        print("App list file not found. Updating...")
        update_app_list()
        return find_app_id_by_name(app_name) # 递归调用自身，重新查找
    except json.JSONDecodeError:
        print("App list file Corrupted, Updating...")
        update_app_list()
        return find_app_id_by_name(app_name)
    except Exception as e:
        print(f"查找AppID发生未知错误：{e}")
        return None
    
def get_app_info(app_id, update_player_data=False):
    try:
        if update_player_data: # 如果需要更新玩家数据
            print("正在更新玩家数据...")
            player_scraper.get_player_info(player_scraper.STEAM_ID) #调用player_scraper更新数据
            print("玩家数据更新完成。")

        url_app_details = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=cn&l=zh-cn"
        response_app_details = requests.get(url_app_details)
        response_app_details.raise_for_status()
        app_data = response_app_details.json().get(str(app_id), {}).get('data', {})

        if not app_data:
            print(f"AppID {app_id} 信息不存在或获取失败。")
            return

        app_name = app_data.get('name', f"AppID {app_id} 未知名称")
        publishers = app_data.get('publishers', [])
        developers = app_data.get('developers', [])
        genres = app_data.get('genres', [])
        categories = app_data.get('categories', [])
        platforms = app_data.get('platforms', {})
        price_overview = app_data.get('price_overview', {})
        release_date = app_data.get('release_date', {})
        price_overview = app_data.get('price_overview', {})

        # 处理价格信息
        if price_overview:  # 如果有价格信息
            final_price = price_overview.get('final_formatted')
            initial_price = price_overview.get('initial_formatted')
            discount_pct = price_overview.get('discount_pct', 0)

            if final_price and initial_price: # 确保两个价格都存在
                if discount_pct > 0:
                    current_price = final_price
                else:
                    current_price = initial_price
            elif final_price: #只有final_price的情况
                current_price = final_price
                initial_price = "未知"
            elif initial_price: #只有initial_price的情况
                current_price = initial_price
            else: # 两个价格都不存在
                current_price = "价格信息不完整"
                initial_price = "价格信息不完整"
        else:
            current_price = "免费/未发售/未知"  # 更明确的提示
            initial_price = "免费/未发售/未知"
            discount_pct = 0

        # 检查是否拥有游戏
        is_owned = "未检查"
        game_name = find_app_name_by_id(app_id) # 获取游戏名称用于错误提示
        owned_games = player_scraper.load_player_owned_games(player_scraper.STEAM_ID)
        if owned_games is not None:
            is_owned = "是" if app_id in owned_games else "未拥有"
        elif game_name:
          print(f"由于未找到玩家数据，无法判断游戏 {game_name} ({app_id}) 是否拥有。")
        else:
          print(f"由于未找到玩家数据，且无法获取游戏名称，无法判断游戏({app_id}) 是否拥有。")

        app_info = {
            "app_id": app_id,
            "name": app_name,
            "publishers": publishers,
            "developers": developers,
            "genres": [genre['description'] for genre in genres],
            "categories": [category['description'] for category in categories],
            "supports_controller": platforms.get('windows', False) or platforms.get('mac', False) or platforms.get('linux', False),
            "price": current_price,
            "initial_price": initial_price,
            "discount_pct": discount_pct,
            "release_date": release_date.get('date', "未知"),
            "is_owned": is_owned, #是否拥有
        }
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, f"{app_id}_{app_name}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(app_info, f, indent=4, ensure_ascii=False)

        print(f"AppID {app_id} ({app_name}) 的数据已保存到：{output_file}\n") # 添加空行分隔

        # 中文概览输出
        if owned_games is not None:
            player_name = get_player_name(player_scraper.STEAM_ID)
            if player_name:
                print(f"正在查询玩家 ID: {player_scraper.STEAM_ID} 玩家昵称: {player_name}")
            else:
                print(f"正在查询玩家 ID: {player_scraper.STEAM_ID} 无法获取玩家昵称")
        print("-" * 50)
        print(f"游戏名称：{app_name}")
        print(f"AppID：{app_id}")
        print(f"是否拥有：{app_info['is_owned']}") #输出是否拥有信息
        print(f"发行商：{', '.join(publishers) or '未知'}")
        print(f"开发商：{', '.join(developers) or '未知'}")
        print(f"游戏类型：{', '.join(app_info['genres']) or '未知'}")
        categories_str = ', '.join(app_info['categories'])
        if "Single-player" in categories_str and ("Multi-player" in categories_str or "MMO" in categories_str):
            print("游戏模式：单人/多人")
        elif "Single-player" in categories_str:
            print("游戏模式：单人")
        elif "Multi-player" in categories_str or "MMO" in categories_str:
            print("游戏模式：多人")
        else:
            print("游戏模式：未知")

        print(f"支持手柄：{'是' if app_info['supports_controller'] else '否'}")
        print(f"当前价格：{app_info['price']}")
        if app_info['discount_pct'] > 0:
            print(f"原价：{app_info['initial_price']}")
            print(f"折扣：{app_info['discount_pct']}%")
        print(f"发行日期：{app_info['release_date']}")
        print("-" * 50)
        print("\n")

    except Exception as e:
        if game_name:
            print(f"处理游戏 {game_name} ({app_id}) 时发生错误：{e}")
        else:
            print(f"处理游戏 ({app_id}) 时发生错误：{e}")

def get_player_name(steam_id): #根据steamid获取玩家昵称
    try:
        output_file = os.path.join(OUTPUT_DIR, f"{steam_id}_steam_data.json")
        with open(output_file, 'r', encoding='utf-8') as f:
            player_data = json.load(f)
            player_name = player_data["basic_info"]["personaname"]
            return player_name
    except FileNotFoundError:
        print(f"玩家 {steam_id} 的数据文件未找到。")
        return None
    except json.JSONDecodeError:
        print(f"玩家 {steam_id} 的数据文件损坏。")
        return None
    except (KeyError, TypeError, IndexError) as e:
        print(f"解析玩家 {steam_id} 数据时出错：{e}")
        return None
    except Exception as e:
        print(f"获取玩家 {steam_id} 昵称时发生未知错误：{e}")
        return None
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="查询 Steam 游戏信息。") # 创建 ArgumentParser 对象
    parser.add_argument("-u", "--update", action="store_true", help="更新玩家数据。") # 添加 -u 或 --update 参数
    args = parser.parse_args() # 解析命令行参数

    game_name = input("请输入游戏名称：")
    app_id = find_app_id_by_name(game_name)
    if app_id:
        get_app_info(app_id, args.update) # 将 update 参数传递给 get_app_info
    else:
        print(f"未找到名为 '{game_name}' 的游戏。")
```

