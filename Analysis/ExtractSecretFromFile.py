
print("raw file")

# import pandas as pd
# import json
#
# # 读取CSV文件
# df = pd.read_csv('2024-03_scan_results.csv')
#
# # 创建一个空列表来存储提取的键值对信息
# extracted_data = []
#
# # 遍历Scan Results列
# for scan_result in df['Scan Results']:
#     row_data = []  # 用来存储每一行的file和raw信息
#
#     try:
#         # 解析Scan Results为JSON
#         data = json.loads(scan_result)
#
#         # 遍历findings中的每个条目
#         for finding in data.get('findings', []):
#             # 检查SourceMetadata是否存在
#             source_metadata = finding.get('SourceMetadata')
#             if source_metadata:
#                 # 从SourceMetadata提取file和Raw
#                 source_data = source_metadata.get('Data', {})
#                 filesystem_data = source_data.get('Filesystem', {})
#
#                 file_info = filesystem_data.get('file')
#                 raw_info = finding.get('Raw')
#
#                 if file_info and raw_info:
#                     # 将提取的file和Raw信息存入字典
#                     row_data.append({
#                         'file': file_info,
#                         'raw': raw_info
#                     })
#     except json.JSONDecodeError:
#         print(f"无法解析Scan Result: {scan_result}")
#         row_data.append({'file': None, 'raw': None})  # 如果解析失败，可以插入默认值
#
#     # 将每一行的提取信息添加到新的列中
#     extracted_data.append(row_data)
#
# # 将提取的数据转换成字符串形式，以便添加到新的列中
# extracted_data_str = [json.dumps(row) for row in extracted_data]
#
# # 将提取的列添加到DataFrame中
# df['Extracted Metadata'] = extracted_data_str
#
# # 保存更新后的CSV文件
# df.to_csv('updated_file.csv', index=False)
#
# # 输出新CSV文件的前几行以检查
# print(df.head())

# import pandas as pd
# import re
#
# for i in range(10,13):
#     # 读取CSV文件
#     df = pd.read_csv(f'./trufflehog_scan_results/2023-{i}_scan_results.csv')
#
#     # 用于存储提取的键值对列表
#     extracted_data = []
#
#     # 定义正则表达式模式来匹配file和raw字段
#     file_pattern = r'"file"\s*:\s*"([^"]+)"'
#     raw_pattern = r'"Raw"\s*:\s*"([^"]+)"'
#
#     # 遍历Scan Results列
#     for scan_result in df['Scan Results']:
#         row_data = []  # 用来存储每一行的file和raw信息
#
#         # 使用正则表达式查找所有的file字段
#         files = re.findall(file_pattern, scan_result)
#         raws = re.findall(raw_pattern, scan_result)
#         raws=set(raws)
#         raws=list(raws)
#
#
#
#         # 将找到的file和raw成对存储（如果数量不匹配，跳过这行）
#         for file, raw in zip(files, raws):
#             row_data.append(raw)
#
#         # 如果没有找到file和raw信息，插入空值
#         if not row_data:
#             row_data.append(None)
#
#         # 将每一行的提取信息添加到新的列中
#         extracted_data.append(row_data)
#
#     # 将提取的数据转换成字符串形式，以便添加到新的列中
#     extracted_data_str = [str(row) for row in extracted_data]
#
#     # 将提取的列添加到DataFrame中
#     df['Extracted Metadata'] = extracted_data_str
#
#     # 保存更新后的CSV文件
#     df.to_csv(f'./raw/2023-{i}_scan_results.csv', index=False)
#
#     # 输出新CSV文件的前几行以检查
#     print(df.head())

