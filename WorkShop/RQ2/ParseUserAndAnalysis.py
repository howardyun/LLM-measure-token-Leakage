import os
import pandas as pd

import pandas as pd
import requests
import time

from sympy.physics.units import electronvolt


def concat_and_count_authors(folder_path: str):
    """
    拼接所有 *_matches.csv 文件，并统计每个作者在 matched_repo 中出现的次数。

    参数:
        folder_path: 包含所有匹配结果文件的目录

    返回:
        拼接后的 DataFrame 和 作者计数 DataFrame
    """
    all_dfs = []

    for file in os.listdir(folder_path):
        if file.endswith("_matches.csv"):
            file_path = os.path.join(folder_path, file)
            try:
                df = pd.read_csv(file_path)
                all_dfs.append(df)
            except Exception as e:
                print(f"❌ 读取失败: {file} - {e}")

    # 拼接所有 CSV
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # 提取作者（matched_repo 的前缀）
    combined_df["author"] = combined_df["matched_repo"].str.split("/").str[0]

    # 统计作者出现次数
    author_counts = combined_df["author"].value_counts().reset_index()
    author_counts.columns = ["author", "count"]

    return combined_df, author_counts

# # 示例use
# all_data, author_stats = concat_and_count_authors("match_results")
# print(author_stats)
#
# # 保存为 CSV 文件
# author_stats.to_csv("author_stats.csv", index=False)
# print("✅ 作者统计结果已保存为 author_stats.csv")


def get_space_count(author: str) -> int:
    """
    查询 Hugging Face 上某作者的 Space 数量
    """
    url = f"https://huggingface.co/api/spaces?author={author}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            spaces = response.json()
            return len(spaces)
        else:
            print(f"⚠️ 请求失败 ({response.status_code}): {author}")
            return -1
    except Exception as e:
        print(f"❌ 请求异常: {author} - {e}")
        return -1

def add_space_counts_to_authors(csv_path: str, output_path: str):
    df = pd.read_csv(csv_path)
    space_counts = []
    for index, row in df.iterrows():
        author = row["author"]
        count_leakage = row["count"]
        count_total = get_space_count(author)
        if count_total == -1:
            print(author)
            space_counts.append(1)
            continue

        if count_leakage >=count_total:
            space_counts.append(1)
        else:
            space_counts.append(count_leakage/count_total)
        time.sleep(1)  # 加点间隔避免请求太频繁

    df["space_count"] = space_counts
    df.to_csv(output_path, index=False)
    print(f"✅ 带空间数量的作者统计已保存：{output_path}")

# 示例调用
# add_space_counts_to_authors("author_stats.csv", "author_stats_with_spaces.csv")



#######################################################
# 统计开发者信息
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # 读取数据
# df = pd.read_csv("author_stats_with_spaces.csv")
#
# # 分箱区间与标签
# bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
# labels = ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1']
#
# # 分别获取 count = 1 和 count > 1 的数据
# df_count_eq_1 = df[df['count'] == 1]
# df_count_gt_1 = df[df['count'] > 1]
#
# # 对 space_count 进行分段
# binned_eq_1 = pd.cut(df_count_eq_1['space_count'], bins=bins, labels=labels, include_lowest=True)
# binned_gt_1 = pd.cut(df_count_gt_1['space_count'], bins=bins, labels=labels, include_lowest=True)
#
# # 统计频数
# space_dist_eq_1 = binned_eq_1.value_counts().sort_index()
# space_dist_gt_1 = binned_gt_1.value_counts().sort_index()
#
# # 自定义颜色（匹配示例图片）
# colors = ['#FFB400', '#FF6D00', '#F44174', '#E041F4', '#1DB4FF']
#
# # 自定义显示百分比和数量的格式
# def make_autopct(values):
#     def my_autopct(pct):
#         total = sum(values)
#         count = int(round(pct * total / 100.0))
#         return f'{pct:.1f}% ({count})'
#     return my_autopct
#
# # 饼图：count = 1
# plt.figure(figsize=(6, 6))
# plt.pie(space_dist_eq_1, labels=labels, colors=colors,
#         autopct=make_autopct(space_dist_eq_1), startangle=140)
# # plt.title('Space Count Distribution (count = 1)')
# plt.tight_layout()
# plt.savefig("space_count_eq_1.pdf")
#
# # 饼图：count > 1
# plt.figure(figsize=(6, 6))
# plt.pie(space_dist_gt_1, labels=labels, colors=colors,
#         autopct=make_autopct(space_dist_gt_1), startangle=140)
# # plt.title('Space Count Distribution (count > 1)')
# plt.tight_layout()
# plt.savefig("space_count_gt_1.pdf")
import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv("author_stats_with_spaces.csv")

# 分箱区间与标签
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
labels = ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.99', '1']

# 分别获取 count = 1 和 count > 1 的数据
df_count_eq_1 = df[df['count'] == 1]
df_count_gt_1 = df[df['count'] > 1]

# 对 space_count 进行分段
binned_eq_1 = pd.cut(df_count_eq_1['space_count'], bins=bins, labels=labels, include_lowest=True)
binned_gt_1 = pd.cut(df_count_gt_1['space_count'], bins=bins, labels=labels, include_lowest=True)

# 统计频数
space_dist_eq_1 = binned_eq_1.value_counts().sort_index()
space_dist_gt_1 = binned_gt_1.value_counts().sort_index()

# 自定义颜色
colors = ['#FFB400', '#FF6D00', '#F44174', '#E041F4', '#1DB4FF']
# colors = ['#08519C', '#2171B5', '#4292C6', '#6BAED6', '#9ECAE1']


# 自定义百分比和数量的格式
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        count = int(round(pct * total / 100.0))
        return f'{pct:.1f}% ({count})'
    return my_autopct

plt.figure(figsize=(5, 5))
patches, texts, autotexts = plt.pie(
    space_dist_eq_1,
    labels=None,  # 不在饼图上显示标签
    colors=colors,
    autopct='%1.1f%%',  # 只显示百分比
    startangle=140,
    textprops={'fontsize': 16}
)

# 设置图例（显示区间和数量）
legend_labels = [f'{label}: {count}' for label, count in zip(labels, space_dist_eq_1)]
plt.legend(patches, legend_labels, title='Interval: Quantity', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12, title_fontsize=12)

plt.tight_layout()
plt.savefig("space_count_eq_1.pdf",bbox_inches='tight')
plt.show()

# 饼图：count > 1
plt.figure(figsize=(5, 5))
patches, texts, autotexts = plt.pie(
    space_dist_gt_1,
    labels=None,  # 不在饼图上显示标签
    colors=colors,
    autopct='%1.1f%%',  # 只显示百分比
    startangle=140,
    textprops={'fontsize': 16}
)

# 图例显示“区间: 数量”
legend_labels = [f'{label}: {count}' for label, count in zip(labels, space_dist_gt_1)]
plt.legend(
    patches,
    legend_labels,
    title='Interval: Quantity',
    loc='center left',
    bbox_to_anchor=(1, 0.5),
    fontsize=12,
    title_fontsize=12
)

plt.tight_layout()
plt.savefig("space_count_gt_1.pdf",bbox_inches='tight')
plt.show()







