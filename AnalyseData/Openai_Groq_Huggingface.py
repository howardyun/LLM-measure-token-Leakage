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

# 初始化统计字典
monthly_counts = {}
for file_path in file_paths:
    month = file_path.split('_')[0]
    monthly_counts[month] = {'OpenAI': 0, 'Groq': 0, 'HuggingFace': 0}

# 读取所有文件内容
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
                            if 'DetectorName' in finding:
                                detector_name = finding['DetectorName']
                                if detector_name in monthly_counts[file_path.split('_')[0]]:
                                    monthly_counts[file_path.split('_')[0]][detector_name] += 1
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_path}: {e}")
                    except KeyError as e:
                        print(f"Key error in file {file_path}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

# 提取数据
months = list(monthly_counts.keys())
openai_counts = [monthly_counts[month]['OpenAI'] for month in months]
groq_counts = [monthly_counts[month]['Groq'] for month in months]
huggingface_counts = [monthly_counts[month]['HuggingFace'] for month in months]

# 绘制折线图
plt.figure(figsize=(14, 7))
plt.plot(months, openai_counts, marker='o', label='OpenAI')
plt.plot(months, groq_counts, marker='o', label='Groq')
plt.plot(months, huggingface_counts, marker='o', label='HuggingFace')

plt.xlabel('Month')
plt.ylabel('Number of Leaks')
plt.title('Monthly Leak Counts of Top 3 API Sources')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
