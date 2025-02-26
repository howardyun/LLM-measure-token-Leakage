# 设定文件路径
import glob
import time
import json
import os

import numpy as np
import pandas as pd
import requests
from click import pause
from huggingface_hub import HfApi
from matplotlib import pyplot as plt

API_TOKEN = "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"

# hf_api = HfApi(token=API_TOKEN)
hf_api = HfApi()

# Tools
def getHFUserInfo(username):
    space = hf_api.space_info(username)
    # 设置 API Token 和目标 URL
    headers = {
        # "Authorization": f"Bearer {API_TOKEN}"
    }
    url = f"https://huggingface.co/api/users/{username}/overview"

    # 发送 GET 请求
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
         # 输出返回的数据
        return response.json()
    else:
        print(f"Username: {username}")
        print(f"Error: {response.status_code}")
        return None
def getTotalRepoValueCount(file_list):
    # Define a list to store combined data
    combined_data = []

    # Read and combine data from each file
    for file_path in file_list:
        with open(file_path, 'r') as file:
            data = json.load(file)
            combined_data.extend(data)  # Combine the data

    # Now, combined_data contains all the combined entries from the files
    combined_data = [item.split('/')[0] for item in combined_data]
    combined_data = pd.Series(combined_data).value_counts()
    # 计算中位数
    median_value = combined_data.median()
    # 计算平均数
    mean_value = combined_data.mean()
    keys_below_mean = combined_data[combined_data < round(mean_value)].index.tolist()
    keys_over_mean = combined_data[combined_data >= round(mean_value)].index.tolist()

    return combined_data,keys_below_mean,keys_over_mean


def figure_pie(data):
    # 定义新的区间范围，合并 0.6-0.9
    bins = np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])  # 手动定义区间

    # 重新定义区间标签
    labels = ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']  # 合并后的标签

    # 使用 numpy 的 histogram 函数来计算各区间的频数
    hist, _ = np.histogram(data, bins)

    # 计算百分比
    total = len(data)
    percentage = (hist / total) * 100

    # 绘制饼状图
    plt.figure(figsize=(7, 7))
    wedges, texts, autotexts = plt.pie(percentage, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)

    # 添加标题
    plt.title('Data Distribution by Range (Percentage)')

    # 添加图例
    plt.legend(wedges, labels, title="Value Ranges", loc="center left", bbox_to_anchor=(1, 0.5))

    # 显示图表
    plt.axis('equal')  # 使饼图为圆形
    plt.tight_layout()  # 自动调整布局
    plt.show()
def figure_bar(data):
    # 定义区间范围
    bins = np.arange(0, 1.1, 0.1)  # 区间从0到1，每0.1一个区间
    labels = [f'{i:.1f}-{i + 0.1:.1f}' for i in bins[:-1]]  # 区间标签，如 '0.0-0.1', '0.1-0.2'

    # 使用 numpy 的 histogram 函数来计算各区间的频数
    hist, _ = np.histogram(data, bins)

    # 计算百分比
    total = len(data)
    percentage = (hist / total) * 100

    # 绘制柱状图
    plt.figure(figsize=(8, 6))
    plt.bar(labels, percentage, color=plt.cm.Paired.colors)

    # 添加标题和标签
    plt.title('Data Distribution by Range (Percentage)')
    plt.xlabel('Value Range')
    plt.ylabel('Percentage')

    # 显示图表
    plt.xticks(rotation=45)  # 使x轴标签倾斜，防止重叠
    plt.tight_layout()  # 自动调整布局
    plt.show()

# function
def calculate_ratio_by_userlist(userlist,total_repos_df,extract_col):
    calculate_ratio = []
    for username in userlist:
        user_total_spcaces_num = total_repos_df.get(username,-1)
        if user_total_spcaces_num !=-1:
            leakage_spcaces_num =extract_col.get(username)
            calculate_ratio.append( round(float(leakage_spcaces_num) / float(user_total_spcaces_num),2))
        else:
            calculate_ratio.append(1.0)
            continue
    return calculate_ratio


def process_files(repo_list,repo_file_list):
    # 找到所有的仓库记录
    total_repos_df,keys_below_mean,keys_over_mean = getTotalRepoValueCount(repo_file_list)
    # 分开处理，一个是大于平均数量的，一个是小于平均数量的
    # 提取 "Extract" 列

    extract_col = repo_list["Repository Name"].apply(lambda x: x.split('/')[0]).value_counts()
    # 获取泄露的用户列表
    userlist = extract_col.keys().tolist()

    # 先处理小于均值的
    intersection_below_mean = list(set(userlist) & set(keys_below_mean))
    calculate_ratio_below_mean = calculate_ratio_by_userlist(intersection_below_mean,total_repos_df,extract_col)

    # 再处理大于均值的
    intersection_over_mean = list(set(userlist) & set(keys_over_mean))
    calculate_ratio_over_mean = calculate_ratio_by_userlist(intersection_over_mean,total_repos_df,extract_col)
    return calculate_ratio_below_mean,calculate_ratio_over_mean



if __name__ == "__main__":
    folder_path = "../../Data/Leak_repo_data/Data/"  # 修改为你的实际路径
    file_pattern = os.path.join(folder_path, "*.csv")  # 查找所有 CSV 文件

    # 获取所有匹配的文件列表
    csv_files = sorted(glob.glob(file_pattern))

    # 用于存储每个文件的 DataFrame
    df_list = []

    repo_file_list = []

    # 读取所有 CSV 文件并合并
    for file in csv_files:
        filename = os.path.basename(file)  # 获取文件名
        time = filename.split("_")[0]
        repo_file_path = f"../../monthly_spaceId_files/{time}.json"
        repo_file_list.append(repo_file_path)
        df = pd.read_csv(file)  # 读取 CSV 文件
        df_list.append(df)  # 将 DataFrame 添加到列表中

    # 使用 pd.concat 将所有 DataFrame 合并
    combined_df = pd.concat(df_list, ignore_index=True)

    calculate_ratio_over_mean,calculate_ratio_over_mean= process_files(combined_df, repo_file_list)

    print(len(calculate_ratio_over_mean))
    figure_pie(calculate_ratio_over_mean)







# from huggingface_hub import HfApi
#
# # 初始化API对象
# api = HfApi()
#
# # 设置要查询的用户名
# username = "facebook"  # 你想查询的用户名
#
# # 获取用户信息
# # user_info = api.(username)
# print(api.get_space_variables('facebook/MelodyFlow'))
# # 输出用户信息


