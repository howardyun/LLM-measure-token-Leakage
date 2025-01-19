import csv
import json
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta

# 生成文件路径列表
start_date = datetime(2022, 3, 1)
end_date = datetime(2024, 12, 1)
current_date = start_date
file_paths = []

while current_date <= end_date:
    file_path = current_date.strftime('20%y-%m_scan_results.csv')
    file_paths.append(file_path)
    current_date += timedelta(days=31)  # 增加一个月
    current_date = current_date.replace(day=1)  # 重置为该月的第一天

# 定义时长区间
time_intervals = ['0 - 2s', '2 - 4s', '4 - 6s', '6 - 8s', '>8s']
interval_counts = Counter()

# 读取所有文件内容
for file_path in file_paths:
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if 'Scan Results' in row:
                    scan_results = row['Scan Results']
                    try:
                        # 解析 JSON 字符串
                        findings = json.loads(scan_results)['findings']
                        for finding in findings:
                            if 'scan_duration' in finding:
                                duration_str = finding['scan_duration']
                                if 'ms' in duration_str:
                                    # 处理以毫秒为单位的数据
                                    duration = float(duration_str.replace('ms', '')) / 1000
                                else:
                                    # 处理以秒为单位的数据
                                    duration = float(duration_str.replace('s', ''))
                                if 0 <= duration < 2:
                                    interval_counts['0 - 2s'] += 1
                                elif 2 <= duration < 4:
                                    interval_counts['2 - 4s'] += 1
                                elif 4 <= duration < 6:
                                    interval_counts['4 - 6s'] += 1
                                elif 6 <= duration < 8:
                                    interval_counts['6 - 8s'] += 1
                                elif duration >= 8:
                                    interval_counts['>8s'] += 1
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_path}: {e}")
                    except KeyError as e:
                        print(f"Key error in file {file_path}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

# 确保所有区间都有数据，即使为 0
for interval in time_intervals:
    if interval not in interval_counts:
        interval_counts[interval] = 0

# 计算总数
total_count = sum(interval_counts.values())

# 计算每个区间的数量占比
interval_percentages = {interval: count / total_count * 100 for interval, count in interval_counts.items()}

# 打印结果
if interval_counts:
    for interval, count in interval_counts.items():
        percentage = interval_percentages[interval]
        print(f"{interval}: {count} ({percentage:.2f}%)")
else:
    print("No scan duration entries found in any of the files.")

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300


# 绘制饼状图
labels = list(interval_percentages.keys())
sizes = list(interval_percentages.values())

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=140)
plt.axis('equal')
plt.title('Distribution of Scan Durations')
plt.show()