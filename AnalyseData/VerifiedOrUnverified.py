import matplotlib.pyplot as plt
import csv
import json
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

# 读取所有文件内容
verified_secrets = 0
unverified_secrets = 0

for file_path in file_paths:
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if 'Scan Results' in row:
                    scan_results = row['Scan Results']
                    try:
                        # 解析JSON字符串
                        findings = json.loads(scan_results)['findings']
                        for finding in findings:
                            if 'verified_secrets' in finding and 'unverified_secrets' in finding:
                                verified_secrets += finding['verified_secrets']
                                unverified_secrets += finding['unverified_secrets']
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_path}: {e}")
                    except KeyError as e:
                        print(f"Key error in file {file_path}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

# 计算总数
total_secrets = verified_secrets + unverified_secrets

# 计算比例
verified_percentage = (verified_secrets / total_secrets) * 100 if total_secrets > 0 else 0
unverified_percentage = (unverified_secrets / total_secrets) * 100 if total_secrets > 0 else 0

# 数据
labels = ['Verified Secrets', 'Unverified Secrets']
sizes = [verified_percentage, unverified_percentage]
colors = ['lightgreen', 'lightcoral']
explode = (0.1, 0)  # 仅突出显示已验证秘密

# 绘制饼图
plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Proportion of Verified and Unverified Secrets')
plt.axis('equal')  # 等轴比例
plt.show()