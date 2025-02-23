import json
import pandas as pd
import ast
import os
import glob
import matplotlib.pyplot as plt
import numpy as np


def figure(months,total_repos,vulnerable_repos,vulnerable_ratio,unique_token):
    # 设置柱状图的宽度
    bar_width = 0.25
    index = np.arange(len(months))

    # 创建图表，使用对数尺度
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 对数尺度
    ax1.set_yscale('log')

    # 绘制总仓库数量、出现漏洞数量和 Unique token 数量的柱状图
    bar1 = ax1.bar(index, total_repos, bar_width, label="Total Repos", color='b')
    bar2 = ax1.bar(index + bar_width, vulnerable_repos, bar_width, label="Vulnerable Repos", color='r')
    bar3 = ax1.bar(index + 2 * bar_width, unique_token, bar_width, label="Unique Token", color='purple')

    # 设置x轴标签和刻度
    ax1.set_xlabel('Month', fontsize=14)  # 设置x轴标签字体大小
    ax1.set_ylabel('Count (Log scale)', fontsize=14)  # 设置y轴标签字体大小
    ax1.set_xticks(index + bar_width)
    ax1.set_xticklabels(months, rotation=90, fontsize=12)  # 设置x轴刻度字体大小
    ax1.tick_params(axis='y', labelsize=12)  # 设置y轴刻度字体大小

    # 创建第二个y轴，绘制仓库出现漏洞的比例
    ax2 = ax1.twinx()
    ax2.plot(months, vulnerable_ratio, label="Vulnerable Ratio", color='g', marker='o', linestyle='-',
             linewidth=2)
    ax2.set_ylabel('Vulnerable Ratio (%)', fontsize=14)  # 设置右侧y轴标签字体大小
    ax2.tick_params(axis='y', labelsize=12)  # 设置右侧y轴刻度字体大小

    # 添加图例，并设置字体大小
    ax1.legend(loc='upper left', fontsize=12)
    ax2.legend(loc='upper right', fontsize=12)

    # 设置标题
    plt.title('Repository Data from March 2022 to December 2024 (Log Scale for Counts)')

    # 显示图表
    plt.tight_layout()
    plt.savefig('Trending.pdf', format='pdf')

    plt.show()


def process_files(json_file, csv_file):
    # 读取 JSON 文件
    with open(json_file, "r", encoding="utf-8") as f:
        repo_list = json.load(f)
    print("总仓库数量:", len(repo_list))

    # 读取 CSV 文件
    repo_list_leakage = pd.read_csv(csv_file)
    print("出现漏洞数量:", len(repo_list_leakage))

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
    # print("总 Token 数:", total_token)

    return len(repo_list),len(repo_list_leakage), total_token



# 设定文件路径
folder_path = "../Data/"  # 修改为你的实际路径
file_pattern = os.path.join(folder_path, "*.csv")  # 查找所有 CSV 文件

# 获取所有匹配的文件列表
csv_files = sorted(glob.glob(file_pattern))



months = []
total_repos = []
vulnerable_repos = []
vulnerable_ratio= []
unique_token= []


# 遍历文件
for file in csv_files:
    filename = os.path.basename(file)  # 获取文件名
    time = filename.split("_")[0]
    repo_file_path = f"../../monthly_spaceId_files/{time}.json"
    scan_file_path = f"../Data/{time}_scan_results.csv"
    months.append(time)
    print(time + ":")
    repo_list_num, repo_list_leakage_num, total_leakage_token_num = process_files(repo_file_path, scan_file_path)
    total_repos.append(repo_list_num)
    vulnerable_repos.append(repo_list_leakage_num)
    unique_token .append(total_leakage_token_num)
    vulnerable_ratio.append(repo_list_leakage_num/repo_list_num*100)
    # 在这里添加你的处理逻辑，例如读取 CSV 进行处理

figure(months,total_repos,vulnerable_repos,vulnerable_ratio,unique_token)






