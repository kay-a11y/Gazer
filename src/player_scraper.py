import requests
import json, os 

STEAM_API_KEY = "YOU_API_KEY"  # API 密钥 TODO
STEAM_ID = "0000000000000000"  # 查询的玩家的 Steam ID TODO
OUTPUT_DIR = r"E:SteamGaze\data\raw"  # 路径填写 TODO

def format_playtime(minutes):
    """将分钟数格式化为"小时 分钟"的字符串。"""
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

        # 创建输出目录（如果不存在）
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 构建输出文件路径
        output_file = os.path.join(OUTPUT_DIR, f"{steam_id}_steam_data.json")

        # 将数据写入 JSON 文件，并使用 ensure_ascii=False 避免中文乱码
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

        print(f"数据已保存到：{output_file}")

        # 展示信息 (根据需要注释/取消注释以下代码)
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
        print(f"玩家 {steam_id} 的数据文件未找到，请先运行 player_scraper.py 获取数据。")
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