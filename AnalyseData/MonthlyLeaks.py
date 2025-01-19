import os
import csv
import matplotlib.pyplot as plt
import pandas as pd

# 定义文件路径和时间范围
start_date = pd.to_datetime('2022-03')
end_date = pd.to_datetime('2024-12')
current_date = start_date

# 存储每个月的行数
monthly_leaks = []

# 生成每个月的文件名并读取行数
while current_date <= end_date:
    file_name = current_date.strftime('%Y-%m') + '_scan_results.csv'
    file_path = current_date.strftime('20%y-%m_scan_results.csv')

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader) - 1  # 减去标题行
            monthly_leaks.append((current_date.strftime('%Y-%m'), row_count))
    except FileNotFoundError:
        monthly_leaks.append((current_date.strftime('%Y-%m'), 0))  # 文件不存在时计为0

    current_date += pd.DateOffset(months=1)

# 转换为DataFrame
df = pd.DataFrame(monthly_leaks, columns=['Month', 'NewLeaks'])

# 转换Month列为日期类型
df['Month'] = pd.to_datetime(df['Month'])

# 绘制折线图
plt.figure(figsize=(10, 5))
plt.plot(df['Month'], df['NewLeaks'], marker='o', linestyle='-', color='blue')
plt.xlabel('Month')
plt.ylabel('Number of New API Leaks')
plt.title('Monthly New API Leaks from 2022-03 to 2024-12')
plt.grid(True)
plt.xticks(df['Month'], df['Month'].dt.strftime('%Y-%m'), rotation=45)
plt.tight_layout()
plt.show()