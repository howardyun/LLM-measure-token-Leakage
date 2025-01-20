import os
import csv
import matplotlib.pyplot as plt
import pandas as pd

# 定义文件路径和时间范围
start_date = pd.to_datetime('2022-03')
end_date = pd.to_datetime('2024-12')
current_date = start_date

# 每月仓库总数量列表
total_spaces_per_month = [
    2524, 641, 790, 845, 1124, 1272, 1645, 1848, 2699, 3494, 4929, 5254,
    8196, 8204, 7645, 7903, 12998, 17902, 8322, 8799, 9934, 10870, 11536, 10738,
    14911, 12371, 13910, 14172, 15154, 17110, 16398, 19077, 20612, 19820
]

# 存储每个月的泄露仓库数量和总仓库数量的占比
monthly_leak_ratios = []

# 生成每个月的文件名并读取行数
index = 0  # 用于索引每月仓库总数量
while current_date <= end_date:
    file_name = current_date.strftime('%Y-%m') + '_scan_results.csv'
    file_path = current_date.strftime('20%y-%m_scan_results.csv')

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader) - 1  # 减去标题行
            leak_ratio = row_count / total_spaces_per_month[index] if total_spaces_per_month[index] > 0 else 0
            monthly_leak_ratios.append((current_date.strftime('%Y-%m'), leak_ratio))
    except FileNotFoundError:
        monthly_leak_ratios.append((current_date.strftime('%Y-%m'), 0))  # 文件不存在时计为0

    current_date += pd.DateOffset(months=1)
    index += 1

# 转换为DataFrame
df = pd.DataFrame(monthly_leak_ratios, columns=['Month', 'LeakRatio'])

# 转换Month列为日期类型
df['Month'] = pd.to_datetime(df['Month'])

# 绘制折线图
plt.figure(figsize=(10, 5))
plt.plot(df['Month'], df['LeakRatio'], marker='o', linestyle='-', color='blue')
plt.xlabel('Month')
plt.ylabel('Leak Ratio')
plt.title('Monthly Leak Ratio of Hugging Face Spaces from 2022-03 to 2024-12')
plt.grid(True)
plt.xticks(df['Month'], df['Month'].dt.strftime('%Y-%m'), rotation=45)
plt.tight_layout()
plt.show()


