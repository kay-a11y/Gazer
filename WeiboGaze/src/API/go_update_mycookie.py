import subprocess
import time
import json
import os

# 假设你的 get_cookie_and_st.py 和 send_weibo_api.py 都在同一目录下
COOKIE_ST_PATH = r"E:\...\cookie_and_st.json"
GET_COOKIE_SCRIPT = r"E:\...\get_cookie_and_st.py"
SEND_WEIBO_SCRIPT = r"E:\...\send_weibo_api.py"
USER_DATA_DIR = r"C:\...\User Data\Default"

def run_script(script_path, *args):
    """运行 Python 脚本"""
    command = ["python", script_path] + list(args)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"运行脚本 {script_path} 出错：")
        print(stderr.decode("utf-8"))
        return False
    else:
        print(f"脚本 {script_path} 运行成功")
        return True

def main():
    """主函数"""
    while True:
        # 获取 Cookie 和 st
        if run_script(GET_COOKIE_SCRIPT, USER_DATA_DIR):
            # 发送微博
            # 确保文件存在
            if not os.path.exists(COOKIE_ST_PATH):
                print(f"错误：文件 {COOKIE_ST_PATH} 不存在。")
                time.sleep(60)  # 等待一段时间后重试
                continue
            
            with open(COOKIE_ST_PATH, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"错误：无法解析文件 {COOKIE_ST_PATH}。")
                    time.sleep(60)  # 等待一段时间后重试
                    continue

            # 检查 'cookies' 和 'st' 键是否存在
            if "cookies" not in data or "st" not in data:
                print(f"错误：文件 {COOKIE_ST_PATH} 中缺少必要的键 'cookies' 或 'st'。")
                time.sleep(60)  # 等待一段时间后重试
                continue
                
            cookies = data["cookies"]
            st = data["st"]

            # 将 Cookie 转换为 requests 可以使用的格式
            cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            # 这里content需要修改为你想要发送的内容
            run_script(SEND_WEIBO_SCRIPT, "你的微博内容", "1", cookie_str, st)

            # 等待一段时间（例如 17 分钟）
            print("等待 17 分钟...")
            time.sleep(17 * 60)
        else:
            print("获取 Cookie 和 st 失败，等待 60 秒后重试...")
            time.sleep(60)

if __name__ == "__main__":
    main()
