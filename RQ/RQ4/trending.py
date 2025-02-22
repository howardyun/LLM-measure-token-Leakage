import json
import pandas as pd
import ast
import os
import glob


def process_files(json_file, csv_file):
    # 读取 JSON 文件
    with open(json_file, "r", encoding="utf-8") as f:
        repo_list = json.load(f)
    print("JSON 数据数量:", len(repo_list))

    # 读取 CSV 文件
    repo_list_leakage = pd.read_csv(csv_file)
    print("CSV 数据数量:", len(repo_list_leakage))

    # 提取 "Extract" 列
    extract_col = repo_list_leakage["Extract"]

    # 统计唯一 key-value 对数量的函数
    def count_unique_value_pairs(item):
        try:
            parsed_list = ast.literal_eval(item)  # 解析字符串为列表
            if isinstance(parsed_list, list):
                unique_raw_values = len(set(entry['raw'] for entry in parsed_list if 'raw' in entry))
                
                return unique_raw_values
        except (SyntaxError, ValueError):
            return None  # 解析失败返回 None

    # 计算 "Extract" 列中唯一 key-value 对数量
    repo_list_leakage["Extract_Key_Value_Count"] = extract_col.apply(count_unique_value_pairs)
    total_token = repo_list_leakage["Extract_Key_Value_Count"].sum()
    print("总 Token 数:", total_token)

    return len(repo_list),len(repo_list_leakage), total_token



# 设定文件路径
folder_path = "../Data/"  # 修改为你的实际路径
file_pattern = os.path.join(folder_path, "*.csv")  # 查找所有 CSV 文件

# 获取所有匹配的文件列表
csv_files = sorted(glob.glob(file_pattern))






# 遍历文件
for file in csv_files:
    filename = os.path.basename(file)  # 获取文件名
    time = filename.split("_")[0]
    repo_file_path = f"../../monthly_spaceId_files/{time}.json"
    scan_file_path = f"../Data/{time}_scan_results.csv"
    repo_list_num, repo_list_leakage_num, total_leakage_token_num = process_files(repo_file_path, scan_file_path)
    print(str(repo_list_leakage_num/repo_list_num*100)+'%')
    print(total_leakage_token_num)
    # 在这里添加你的处理逻辑，例如读取 CSV 进行处理



