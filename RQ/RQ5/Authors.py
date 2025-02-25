# 设定文件路径
import glob
import json
import os

import pandas as pd


def process_files(repo_list):
    # 提取 "Extract" 列
    extract_col = repo_list["Repository Name"].apply(lambda x: x.split('/')[0]).value_counts()
    print(extract_col)




folder_path = "../Data/"  # 修改为你的实际路径
file_pattern = os.path.join(folder_path, "*.csv")  # 查找所有 CSV 文件

# 获取所有匹配的文件列表
csv_files = sorted(glob.glob(file_pattern))

# 用于存储每个文件的 DataFrame
df_list = []

# 读取所有 CSV 文件并合并
for file in csv_files:
    df = pd.read_csv(file)  # 读取 CSV 文件
    df_list.append(df)  # 将 DataFrame 添加到列表中


# 获取正则
with open(os.path.join(os.path.dirname(__file__), "../regexes_v2.json"), 'r') as f:
    regexes = json.loads(f.read())
# 定义敏感信息的正则表达式
sensitive_patterns = regexes

# 使用 pd.concat 将所有 DataFrame 合并
combined_df = pd.concat(df_list, ignore_index=True)
processed_df = process_files(combined_df)