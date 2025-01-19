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
detector_names = []
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
                                detector_names.append(detector_name)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_path}: {e}")
                    except KeyError as e:
                        print(f"Key error in file {file_path}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

# 统计每个DetectorName的数量
detector_counts = Counter(detector_names)

# 计算总数
total_count = sum(detector_counts.values())

# 计算每个DetectorName的数量占比
detector_percentages = {detector: count / total_count * 100 for detector, count in detector_counts.items()}

# 打印结果
if detector_counts:
    for detector, count in detector_counts.items():
        percentage = detector_percentages[detector]
        print(f"{detector}: {count} ({percentage:.2f}%)")
else:
    print("No DetectorName entries found in any of the files.")

# 数据
api_leaks = {
    'OpenAI': 4467,
    'TwitterConsumerkey': 13,
    'HuggingFace': 1081,
    'WeightsAndBiases': 58,
    'JDBC': 9,
    'Postgres': 84,
    'MongoDB': 206,
    'Spoonacular': 7,
    'URI': 104,
    'Privacy': 23,
    'GoogleOauth2': 23,
    'AzureOpenAI': 88,
    'GCPApplicationDefaultCredentials': 64,
    'ElevenLabs': 22,
    'AWS': 14,
    'AzureStorage': 4,
    'OpenWeather': 19,
    'Github': 46,
    'Notion': 12,
    'Slack': 3,
    'Alibaba': 9,
    'Yelp': 3,
    'Box': 6,
    'Polygon': 1,
    'DetectLanguage': 2,
    'Apify': 3,
    'Twilio': 9,
    'Anthropic': 48,
    'Rawg': 2,
    'FTP': 6,
    'SlackWebhook': 3,
    'AssemblyAI': 6,
    'Snowflake': 1,
    'CloudflareApiToken': 4,
    'Apiflash': 2,
    'CryptoCompare': 4,
    'Clarifai': 6,
    'PrivateKey': 2,
    'GoDaddy': 6,
    'NVAPI': 28,
    'Deepgram': 14,
    'Groq': 1269,
    'Replicate': 38,
    'DatabricksToken': 4,
    'Coda': 4,
    'Monday': 2,
    'TicketMaster': 4,
    'Clearbit': 1,
    'Pixabay': 3,
    'Nutritionix': 2,
    'Redis': 1,
    'Mailgun': 3,
    'VirusTotal': 2,
    'Unsplash': 4,
    'LarkSuite': 2,
    'WeatherStack': 2,
    'Alchemy': 2,
    'Postmark': 2,
    'Azure': 2,
    'SQLServer': 1,
    'Adzuna': 1,
    'MicrosoftTeamsWebhook': 2,
    'LarkSuiteApiKey': 20,
    'TomorrowIO': 4,
    'Stripe': 1,
    'ExchangeRatesAPI': 2,
    'Vercel': 1
}

# 计算总泄露数量
total_leaks = sum(api_leaks.values())

# 计算每个API的泄露比例
api_leaks_percent = {api: (count / total_leaks) * 100 for api, count in api_leaks.items()}

# 排序并取前二十名
sorted_api_leaks = sorted(api_leaks_percent.items(), key=lambda x: x[1], reverse=True)[:20]

# 提取API名称和比例
api_names = [item[0] for item in sorted_api_leaks]
api_percentages = [item[1] for item in sorted_api_leaks]
api_counts = [api_leaks[api] for api in api_names]

# 绘制柱状图
plt.figure(figsize=(20, 10))
bars = plt.bar(api_names, api_percentages, color='skyblue')

# 添加每个柱子上方的标签
for bar, count, percentage in zip(bars, api_counts, api_percentages):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
             f'{count} ({percentage:.2f}%)',
             ha='center', va='bottom')

plt.xlabel('API')
plt.ylabel('Percentage of Total Leaks (%)')
plt.title('Top 20 API Leak Sources and Their Percentages')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()