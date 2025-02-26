import json
import re

import pandas as pd
import ast
import os
import glob

from sympy import print_glsl


def process_files(repo_list,sensitive_patterns):

    # 提取 "Extract" 列
    extract_col = repo_list["Extract"]
    # 统计唯一 key-value 对数量的函数
    def count_unique_value_pairs(item):
        try:
            parsed_list = ast.literal_eval(item)  # 解析字符串为列表
            if isinstance(parsed_list, list):
                # 去重+获取所有的api_token
                unique_raw_values = list(set(entry['raw'] for entry in parsed_list if 'raw' in entry))
                # 开始正则匹配
                company_list = []
                for token in unique_raw_values:
                    for company, pattern in sensitive_patterns.items():
                        if re.search(pattern, token):
                            company_list.append(company)
                            break
                if company_list.__len__() == 0:
                    print(unique_raw_values)
                    # company_list.append('other')
                return company_list
        except (SyntaxError, ValueError):
            return None  # 解析失败返回 None

    # 计算 "Extract" 列中唯一 key-value 对数量
    s= extract_col.apply(count_unique_value_pairs)
    # 将 Series 中的每个列表展开成单独的元素
    expanded = s.explode()
    # 统计每个元素的出现次数
    value_counts = expanded.value_counts()

    print("文件数:", value_counts)
    print("文件总数：",len(expanded))
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





