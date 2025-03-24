# # import json
# # import numpy as np
# # import matplotlib.pyplot as plt
# # import seaborn as sns
# # import pandas as pd
# # import matplotlib
# #
# # # 全局字体设置，放大所有文本并加粗
# # matplotlib.rcParams.update({
# #     'font.sans-serif': ['Arial'],  # 适用于英文，如有中文可换 SimHei
# #     'axes.unicode_minus': False,  # 解决负号显示问题
# #     'font.size': 18,  # 全局字体大小
# #     'axes.labelsize': 20,  # 坐标轴标签大小
# #     'axes.titlesize': 22,  # 标题字体大小
# #     'xtick.labelsize': 18,  # x 轴刻度大小
# #     'ytick.labelsize': 18,  # y 轴刻度大小
# #     'legend.fontsize': 18,  # 图例字体大小（如果有）
# #     'figure.figsize': (18, 8),  # 统一放大图片尺寸
# #     'font.weight': 'bold',  # 全局字体加粗
# #     'axes.titleweight': 'bold',  # 标题加粗
# #     'axes.labelweight': 'bold'  # 轴标签加粗
# # })
# #
# # # 读取 JSON 文件
# # file_path = "time_interval.json"
# # with open(file_path, "r") as file:
# #     time_intervals = json.load(file)
# #
# # # 取绝对值，转换为天
# # time_intervals_days = np.abs(np.array(time_intervals)) / 86400
# #
# # # 统计区间
# # bins = [0, 1, 7, 30, 90, 365, 1200]  # 1天、1周、1月、3月、1年、10年
# # bin_labels = ["<1 day", "1-7 days", "7-30 days", "30-90 days", "90-365 days", "Over 1 year"]
# #
# # # 计算区间直方图
# # hist, _ = np.histogram(time_intervals_days, bins=bins)
# #
# # # 创建子图（1行2列）
# # fig, axes = plt.subplots(1, 2)
# #
# # # 绘制直方图（Bar Plot） - 左侧
# # sns.barplot(x=bin_labels, y=hist, color="skyblue", ax=axes[0])
# # axes[0].set_xlabel("Bug Fix Time Range (Days)", fontsize=20, fontweight='bold')
# # axes[0].set_ylabel("Frequency", fontsize=20, fontweight='bold')
# # axes[0].set_title("Distribution of Bug Fix Time", fontsize=22, fontweight='bold')
# # axes[0].tick_params(axis='x', labelsize=18, rotation=-30)  # **倾斜 x 轴刻度**
# # axes[0].tick_params(axis='y', labelsize=18)  # y 轴加粗
# #
# # # 绘制箱线图（Box Plot） - 右侧
# # sns.boxplot(x=pd.cut(time_intervals_days, bins=bins, labels=bin_labels), y=time_intervals_days, ax=axes[1])
# # axes[1].set_xlabel("Bug Fix Time Range (Days)", fontsize=20, fontweight='bold')
# # axes[1].set_ylabel("Fix Time (Days)", fontsize=20, fontweight='bold')
# # axes[1].set_yscale("log")  # 采用对数刻度
# # axes[1].set_title("Box Plot of Bug Fix Time Distribution", fontsize=22, fontweight='bold')
# # axes[1].tick_params(axis='x', labelsize=18, rotation=-30)  # **倾斜 x 轴刻度**
# # axes[1].tick_params(axis='y', labelsize=18)  # y 轴加粗
# #
# # # 调整布局
# # plt.tight_layout()
# # plt.savefig('Commit Recover.pdf', format='pdf')
# # # 显示图像
# # plt.show()
# import json
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd
# import matplotlib
#
# # 全局字体设置，放大所有文本并加粗
# matplotlib.rcParams.update({
#     'font.sans-serif': ['Arial'],  # 适用于英文，如有中文可换 SimHei
#     'axes.unicode_minus': False,  # 解决负号显示问题
#     'font.size': 18,  # 全局字体大小
#     'axes.labelsize': 20,  # 坐标轴标签大小
#     'axes.titlesize': 22,  # 标题字体大小
#     'xtick.labelsize': 18,  # x 轴刻度大小
#     'ytick.labelsize': 18,  # y 轴刻度大小
#     'legend.fontsize': 18,  # 图例字体大小（如果有）
#     'figure.figsize': (14, 6),  # 增加宽度，使柱子显得更窄
#     'font.weight': 'bold',  # 全局字体加粗
#     'axes.titleweight': 'bold',  # 标题加粗
#     'axes.labelweight': 'bold'  # 轴标签加粗
# })
#
# # 读取 JSON 文件
# file_path = "time_interval.json"
# with open(file_path, "r") as file:
#     time_intervals = json.load(file)
#
#
# print(len(time_intervals))
# # 取绝对值，转换为天
# time_intervals_days = np.abs(np.array(time_intervals)) / 86400
#
# # 统计区间
# bins = [0, 1, 7, 30, 90, 365, 1200]  # 1天、1周、1月、3月、1年、10年
# bin_labels = ["<1 day", "1-7 days", "7-30 days", "30-90 days", "90-365 days", "Over 1 year"]
#
# # 计算区间直方图
# hist, _ = np.histogram(time_intervals_days, bins=bins)
#
# # 绘制直方图（Bar Plot）
# plt.figure(figsize=(8, 6))
# ax = sns.barplot(x=bin_labels, y=hist, color="skyblue", width=0.5)  # 通过 width 调整柱子宽度
# plt.xlabel("Bug Fix Time Range (Days)", fontsize=20, fontweight='bold')
# plt.ylabel("Frequency", fontsize=20, fontweight='bold')
# plt.title("Distribution of Bug Fix Time", fontsize=22, fontweight='bold')
# plt.xticks(rotation=-30, fontsize=18)
# plt.yticks(fontsize=18)
# plt.tight_layout()
# plt.savefig('Commit_Recover_BarPlot.pdf', format='pdf')
# plt.show()
#
# # 绘制箱线图（Box Plot）
# plt.figure(figsize=(10, 6))
# sns.boxplot(x=pd.cut(time_intervals_days, bins=bins, labels=bin_labels), y=time_intervals_days)
# plt.xlabel("Bug Fix Time Range (Days)", fontsize=20, fontweight='bold')
# plt.ylabel("Fix Time (Days)", fontsize=20, fontweight='bold')
# plt.yscale("log")  # 采用对数刻度
# plt.title("Box Plot of Bug Fix Time Distribution", fontsize=22, fontweight='bold')
# plt.xticks(rotation=-30, fontsize=18)
# plt.yticks(fontsize=18)
# plt.tight_layout()
# plt.savefig('Commit_Recover_BoxPlot.pdf', format='pdf')
# plt.show()
#


import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib

# 全局字体设置，放大所有文本并加粗
matplotlib.rcParams.update({
    'font.sans-serif': ['Arial'],  # 适用于英文，如有中文可换 SimHei
    'axes.unicode_minus': False,  # 解决负号显示问题
    'font.size': 18,  # 全局字体大小
    'axes.labelsize': 20,  # 坐标轴标签大小
    'axes.titlesize': 22,  # 标题字体大小
    'xtick.labelsize': 18,  # x 轴刻度大小
    'ytick.labelsize': 18,  # y 轴刻度大小
    'legend.fontsize': 14,  # 图例字体大小（如果有）
    # 'figure.figsize': (14, 6),  # 增加宽度，使柱子显得更窄
    'font.weight': 'bold',  # 全局字体加粗
    'axes.titleweight': 'bold',  # 标题加粗
    'axes.labelweight': 'bold'  # 轴标签加粗
})

# 读取 JSON 文件
file_path = "time_interval.json"
with open(file_path, "r") as file:
    time_intervals = json.load(file)

print(len(time_intervals))
# 取绝对值，转换为天
time_intervals_days = np.abs(np.array(time_intervals)) / 86400

# 统计区间
bins = [0, 1, 7, 30, 90, 365, 1200]  # 1天、1周、1月、3月、1年、10年
bin_labels = ["<1 day", "1-7 days", "7-30 days", "30-90 days", "90-365 days", "Over 1 year"]

# 计算区间直方图
hist, _ = np.histogram(time_intervals_days, bins=bins)

# 计算比例
total = sum(hist)
percentages = [(count / total) * 100 for count in hist]

# 绘制饼状图
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(hist, labels=None, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"), pctdistance=0.85)

# 设置饼状图中百分比文本的样式
for autotext in autotexts:
    autotext.set_fontsize(18)
    autotext.set_fontweight('bold')

# 添加图例
legend_labels = [f"{label}: {count} ({percentage:.1f}%)" for label, count, percentage in zip(bin_labels, hist, percentages)]
plt.legend(wedges, legend_labels, title="Bug Fix Time Range", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=16)

# 设置标题
plt.title("Distribution of Token leakage Fix Time", fontsize=22, fontweight='bold')

# 调整布局
plt.tight_layout()
plt.savefig('Commit_Recover_PieChart.pdf', format='pdf')
plt.show()