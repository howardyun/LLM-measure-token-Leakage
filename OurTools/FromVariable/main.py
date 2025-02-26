import concurrent
import datetime
import glob
import json
import os
from datetime import datetime
import pandas as pd
import requests
from huggingface_hub import HfApi

API_TOKEN = "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"

api = HfApi(token=API_TOKEN)


# 定义自定义序列化函数
def custom_serializer(obj):
    # 如果对象是 datetime 类型
    if isinstance(obj, datetime):
        # 转换为字符串
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    # 如果是其他不可序列化类型，抛出异常
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")






def search_varible(json_file):
    results = []
    count = 0
    # 读取 JSON 文件
    # 打开 JSON 文件读取 repo_list
    with open(json_file, "r", encoding="utf-8") as f:
        repo_list = json.load(f)

    # 创建一个列表用于存储查询结果
    results = []

    # 定义一个处理单个 repo 的函数
    def process_repo(repo):
        try:
            # 调用 API 获取 repo 的信息
            result = api.get_space_variables(repo)
            result_dict = {key: value.__dict__ if hasattr(value, '__dict__') else value for key, value in
                           result.items()}
            # 返回 repo 和转换后的字典
            return  {'repo':repo,'result':result_dict}
        except requests.exceptions.HTTPError as e:
            # 如果是 404 错误，可以选择跳过或重试
            if e.response.status_code == 404:
                print(f"404 Not Found for repo: {repo}")
                return {'repo':repo,'result':{}}  # 或者可以返回 None 来表示失败
            else:
                print(f"HTTP Error for {repo}: {e}")
                return  {'repo':repo,'result':{}}
        except Exception as e:
            # 捕获其他异常
            print(f"Error processing {repo}: {e}")
            return {'repo':repo,'result':{}}
    # 使用 ThreadPoolExecutor 来并行处理 repo_list
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # map 将 `process_repo` 函数应用到每个 repo 上
        results = list(executor.map(process_repo, repo_list))

    filtered_data = [item for item in results if item['result']]

    return filtered_data

if __name__ == "__main__":
    # 设定文件路径
    folder_path = "../../Data/Leak_repo_data"  # 修改为你的实际路径
    file_pattern = os.path.join(folder_path, "*.csv")  # 查找所有 CSV 文件
    all_time_interval = []
    # 获取所有匹配的文件列表
    csv_files = sorted(glob.glob(file_pattern))
    for file in csv_files:
        filename = os.path.basename(file)  # 获取文件名
        time = filename.split("_")[0]
        print("正在处理"+time+'.'*10)
        repo_file_path = f"../../Data/monthly_spaceId_files/{time}.json"
        scan_file_path = f"../../Data/Leak_repo_data/{time}_scan_results.csv"
        #查找
        filtered_data = search_varible(repo_file_path)
        output_file = 'Output/'+ f'{time}_space_variables.json'
        # 保存 filtered_data 到 JSON 文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4, default=custom_serializer)




