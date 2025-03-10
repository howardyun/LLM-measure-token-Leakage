import matplotlib.pyplot as plt
# 更新数据
updated_values = [
    3883, 5522, 305, 88, 44, 6,
    957, 275, 8, 118, 74, 59, 13, 13,
    132, 21, 138, 129, 32
]

# 更新数据分类
updated_categories = {
    "Commit History": [(".git", updated_values[0])],
    "Code Files": [(".py", updated_values[1]), (".ipynb", updated_values[2]), (".js", updated_values[3]),
                   (".sh", updated_values[4]), (".go", updated_values[5])],
    "Config Files": [(".env", updated_values[6]), (".json", updated_values[7]), (".jsonl", updated_values[8]),
                     (".yml", updated_values[9]), ("DockerFile", updated_values[10]), (".toml", updated_values[11]),
                     (".ini", updated_values[12]), (".env-sample", updated_values[13])],
    "Text Files": [(".txt", updated_values[14]), (".example", updated_values[15]),
                   (".md", updated_values[16]), ("Others", updated_values[17])],
    "Data Files": [(".csv", updated_values[18])]
}

# 提取数据
all_labels = []
all_values = []
category_positions = {}  # 记录大分类的起始位置

position = 0
for category, files in updated_categories.items():
    category_positions[category] = position  # 记录大分类的位置
    for file, count in files:
        all_labels.append(file)
        all_values.append(count)
        position += 1

# 生成水平条形图
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(all_labels, all_values, alpha=0.7)

# 添加分类标记
for category, pos in category_positions.items():
    ax.text(-500, pos, category, fontsize=12, fontweight="bold", va="center", ha="right", color="darkred")
    ax.axhline(y=pos - 0.5, color="gray", linestyle="dashed", linewidth=1)  # 虚线分割

# 添加数值标签
for bar, value in zip(bars, all_values):
    ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, str(value), va='center')

# 美化图表
ax.set_xlabel("Count")
ax.set_ylabel("File Types")
ax.set_title("Updated Distribution of Leaked Files with Categories")
ax.grid(axis='x', linestyle='--', alpha=0.6)
ax.invert_yaxis()  # 让最大值在上方

plt.tight_layout()
# 显示图表
plt.show()
