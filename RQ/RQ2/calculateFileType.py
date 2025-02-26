import ast
import glob
import json
import os
import re

import pandas as pd


def process_files(repo_list,sensitive_patterns):
    # 提取 "Extract" 列
    extract_col = repo_list["Extract"]

    # 统计唯一 key-value 对数量的函数
    def count_unique_value_pairs(item):
        try:
            parsed_list = ast.literal_eval(item)  # 解析字符串为列表
            if isinstance(parsed_list, list):
                file_values = []
                for item in parsed_list:
                #正则匹配，如果这个token是对的，那么就将file加到file_values中
                    for company, pattern in sensitive_patterns.items():
                        if re.search(pattern, item['raw']):
                            file_values.append(item['file'])
                            break
                return list(set(file_values))
        except (SyntaxError, ValueError):
            return None  # 解析失败返回 None

    # 计算 "Extract" 列中唯一 key-value 对数量

    s= extract_col.apply(count_unique_value_pairs)
    # 将 Series 中的每个列表展开成单独的元素
    expanded = s.explode()
    file_suffix = expanded.str.split('.').str[-1]  # 提取点（.）后面的部分，即文件扩展名
    # 统计每个元素的出现次数
    value_counts = file_suffix.value_counts()
    print("文件后缀统计:", value_counts)
    print(len(file_suffix))
    return value_counts



# 设定文件路径
folder_path = "../../Data/Leak_repo_data/Data/"  # 修改为你的实际路径
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
processed_df = process_files(combined_df,sensitive_patterns)




