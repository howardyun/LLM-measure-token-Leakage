import json
import pandas as pd
import ast
import os
import glob
import matplotlib.pyplot as plt
import numpy as np

def figure_line_chart(months, total_repos, vulnerable_repos, vulnerable_ratio, unique_token):
    # 科研风格配色（柔和、专业）
    colors = {
        "total_repos":     (55 / 255, 139 / 255, 255 / 255),
        "vulnerable_repos":     (217 / 255, 73 / 255, 47 / 255),  # 红色（突出风险）
        "unique_token": (255 / 255, 154 / 255, 41 / 255),  # 紫色（对比明显）
        "vulnerable_ratio": "#2ca02c"  # 绿色（表示比例）
    }


    # 创建图表
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 绘制总仓库数量、出现漏洞数量和 Unique token 数量的折线图，调整格式
    ax1.plot(months, total_repos, label="Total Create Repos", color=colors["total_repos"], marker='o', linestyle='--', linewidth=2, markersize=8, alpha=0.9)
    ax1.plot(months, vulnerable_repos, label="Secret Leak Repos", color=colors["vulnerable_repos"], marker='s', linestyle='-.', linewidth=2, markersize=8, alpha=0.9)
    ax1.plot(months, unique_token, label="Unique Secret", color=colors["unique_token"], marker='^', linestyle=':', linewidth=2, markersize=8, alpha=0.9)

    # 设置对数尺度
    ax1.set_yscale('log')

    # 设置 x 轴和 y 轴标签
    ax1.set_xlabel('Month', fontsize=20)
    ax1.set_ylabel('Count (Log scale)', fontsize=22)
    ax1.tick_params(axis='y', labelsize=18)
    ax1.set_xticks(range(len(months)))

    # 设置 x 轴的标签，每三个显示一次，未显示的标签保留刻度线
    ax1.set_xticklabels([months[i] if i % 3 == 0 else '' for i in range(len(months))], rotation=70, fontsize=14)
    # step = 3
    # ax1.set_xticks(range(0, len(months), step))  # 每隔3个显示一个刻度
    # ax1.set_xticklabels(months[::step], rotation=70, fontsize=14)  # 每隔3个标签进行显示
    # ax1.set_xticks(range(len(months)))
    # ax1.set_xticklabels(months, rotation=70, fontsize=14)

    # 创建第二个 y 轴，绘制仓库出现漏洞的比例，调整格式
    ax2 = ax1.twinx()
    ax2.plot(months, vulnerable_ratio, label="Leak Ratio", color=colors["vulnerable_ratio"], marker='D', linestyle='-', linewidth=2, markersize=8, alpha=0.9)
    ax2.set_ylabel('Vulnerable Ratio (%)', fontsize=21)
    ax2.tick_params(axis='y', labelsize=18)

    # 添加图例，并设置字体大小
    # ax1.legend(loc='upper left', fontsize=17)
    # ax2.legend(loc='upper right', fontsize=17)
    ax1.legend(loc='upper left', fontsize=17,bbox_to_anchor=(0, 1))
    ax2.legend(loc='upper right', fontsize=17, bbox_to_anchor=(1.0, 0.2))
    # 调整布局
    plt.tight_layout()
    # 保存
    plt.savefig('Trending.pdf', format='pdf')

    # 显示图表
    plt.show()

def figure(months,total_repos,vulnerable_repos,vulnerable_ratio,unique_token):
    # 设置柱状图的宽度
    bar_width = 0.25
    index = np.arange(len(months))

    # 创建图表，使用对数尺度
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 对数尺度
    ax1.set_yscale('log')

    # # 绘制总仓库数量、出现漏洞数量和 Unique token 数量的柱状图
    # bar1 = ax1.bar(index, total_repos, bar_width, label="Total Repos", color='b')
    # bar2 = ax1.bar(index + bar_width, vulnerable_repos, bar_width, label="Vulnerable Repos", color='r')
    # bar3 = ax1.bar(index + 2 * bar_width, unique_token, bar_width, label="Unique Token", color='purple')

    bar1 = ax1.bar(index, total_repos, bar_width, label="Total Repos", color=(55 / 255, 139 / 255, 255 / 255))  # Blue
    bar2 = ax1.bar(index + bar_width, vulnerable_repos, bar_width, label="Vulnerable Repos",
                   color=(217 / 255, 73 / 255, 47 / 255))  # Red
    bar3 = ax1.bar(index + 2 * bar_width, unique_token, bar_width, label="Unique Token",
                   color=(255 / 255, 154 / 255, 41 / 255))  # Orange

    # 设置x轴标签和刻度
    ax1.set_xlabel('Month', fontsize=18,fontweight='bold')  # 设置x轴标签字体大小
    ax1.set_ylabel('Count (Log scale)', fontsize=20,fontweight='bold')  # 设置y轴标签字体大小
    ax1.set_xticks(index + bar_width)
    ax1.set_xticklabels(months, rotation=70, fontsize=14,fontweight='bold')  # 设置x轴刻度字体大小
    ax1.tick_params(axis='y', labelsize=16)  # 设置y轴刻度字体大小

    # 创建第二个y轴，绘制仓库出现漏洞的比例
    ax2 = ax1.twinx()
    ax2.plot(months, vulnerable_ratio, label="Vulnerable Ratio", color='g', marker='o', linestyle='-',
             linewidth=2)
    ax2.set_ylabel('Vulnerable Ratio (%)', fontsize=20,fontweight='bold')  # 设置右侧y轴标签字体大小
    ax2.tick_params(axis='y', labelsize=16)  # 设置右侧y轴刻度字体大小

    # 添加图例，并设置字体大小
    ax1.legend(loc='upper left', fontsize=14)
    ax2.legend(loc='upper right', fontsize=14)

    # 设置标题
    # plt.title('Repository Data from March 2022 to December 2024 (Log Scale for Counts)')

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
folder_path = "../../Data/Leak_repo_data/"  # 修改为你的实际路径
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
    repo_file_path = f"../../Data/monthly_spaceId_files/{time}.json"
    scan_file_path = f"../../Data/Leak_repo_data/{time}_scan_results.csv"
    months.append(time)
    print(time + ":")
    repo_list_num, repo_list_leakage_num, total_leakage_token_num = process_files(repo_file_path, scan_file_path)
    total_repos.append(repo_list_num)
    vulnerable_repos.append(repo_list_leakage_num)
    unique_token .append(total_leakage_token_num)
    vulnerable_ratio.append(repo_list_leakage_num/repo_list_num*100)
    # 在这里添加你的处理逻辑，例如读取 CSV 进行处理

figure_line_chart(months,total_repos,vulnerable_repos,vulnerable_ratio,unique_token)






