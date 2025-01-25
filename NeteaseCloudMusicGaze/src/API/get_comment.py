import requests
import json

def get_comment(music_id):
    """模拟登陆, 构造comment POST请求comments数量
    Args:
        music_id(string): 单曲 id.
    """

    get_comment_api = f"https://music.163.com/api/v1/resource/comments/R_SO_4_{music_id}"
    

    # simulate headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    response = requests.get(get_comment_api, headers=headers)

    if response.status_code == 200:
        try:
            result = response.json()
            total_count = result["total"]
            print(f"评论数: {total_count}")
            return total_count
        except (KeyError, json.JSONDecodeError) as e:
            print(f"解析 JSON 失败: {e}")
            print(f"响应内容: {response.text}") # 打印响应内容以帮助调试

    else:
        print(f"请求添加标签或短评失败! ❌ 状态码: {response.status_code}")
        print(response.text) # 打印错误信息, 方便调试

if __name__ == '__main__':

    music_id = "1886064452"
    get_comment(music_id) # 共2581条评论