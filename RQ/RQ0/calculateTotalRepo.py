import json
import pandas as pd
import ast
import os
import glob
# Tools
def count_unique_value_pairs(item):
    try:
        parsed_list = ast.literal_eval(item)  # 解析字符串为列表
        if isinstance(parsed_list, list):
            unique_raw_values = len(set(entry['raw'] for entry in parsed_list if 'raw' in entry))
            return unique_raw_values
    except (SyntaxError, ValueError):
        return None  # 解析失败返回 None


# Function
def calculateTotalRepo(folder_path, pattern = "*.json"):
    file_pattern = os.path.join(folder_path, pattern)  # 查找所有 json 文件
    # 获取所有匹配的文件列表
    json_files = sorted(glob.glob(file_pattern))
    repo_count = 0

    # 遍历文件
    for file in json_files:
        filename = os.path.basename(file)  # 获取文件名
        time = filename.split("_")[0]
        repo_file_path = folder_path + f"{time}"
        # 打开JSON文件，统计数量
        with open(repo_file_path, "r", encoding="utf-8") as f:
            repo_list = json.load(f)
        repo_count += len(repo_list)
    print("repo数据数量:", repo_count)
    return repo_count

def calculateLeakageRepoandToken(folder_path, pattern = "*.csv"):
    file_pattern = os.path.join(folder_path, pattern)  # 查找所有 json 文件
    # 获取所有匹配的文件列表
    json_files = sorted(glob.glob(file_pattern))
    repo_count = 0
    total_token_cont = 0
    # 遍历文件
    for file in json_files:

        # 统计Repo数量
        filename = os.path.basename(file)  # 获取文件名
        time = filename.split("_")[0]
        csv_file_path = folder_path+f"{time}_scan_results.csv"

        # 读取 CSV 文件以及添加数量
        repo_list_leakage = pd.read_csv(csv_file_path)
        repo_count += len(repo_list_leakage)

        # 统计Unique token数量
        extract_col = repo_list_leakage["Extract"]
        repo_list_leakage["Extract_Key_Value_Count"] = extract_col.apply(count_unique_value_pairs)
        token_count = repo_list_leakage["Extract_Key_Value_Count"].sum()
        total_token_cont += token_count



    print("Token leakage repo数据数量:", repo_count)
    print("Token Unique leakage数据数量:", total_token_cont)
    return repo_count, total_token_cont




def main():
    # 统计全部的space数量
    total_repo_path = "../../Data/monthly_spaceId_files/"  # 修改为你的实际路径
    calculateTotalRepo(total_repo_path)

    # 统计具有token leakage的数量
    leakage_repo_path = "../../Data/Leak_repo_data/Data/"  # 修改为你的实际路径
    calculateLeakageRepoandToken(leakage_repo_path)


    print("TotalRepo:", calculateTotalRepo(total_repo_path))
    print("LeakageRepoandToken:", calculateLeakageRepoandToken(leakage_repo_path))


if __name__ == "__main__":
    main()



