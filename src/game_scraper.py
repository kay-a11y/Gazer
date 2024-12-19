import requests
import json
import os
import player_scraper
import argparse  

STEAM_API_KEY = "YOU_API_KEY" # API 密钥 TODO
OUTPUT_DIR = r"E:SteamGaze\data\raw" # 路径填写 TODO

APP_LIST_FILE = r"E:SteamGaze\app_list.json" #app列表保存的文件名

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