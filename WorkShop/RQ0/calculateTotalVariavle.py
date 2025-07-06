import os
import json

# 替换为你的文件夹路径
folder_path = "../Data"

total_count = 0
file_counts = {}

# 遍历文件夹中的所有 JSON 文件
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                count = len(data)  # 每个 JSON 顶层是数组，元素是仓库
                file_counts[filename] = count
                total_count += count
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")

# 输出每个文件的统计结果
print("📊 Repository Count per JSON File:")
for file, count in sorted(file_counts.items()):
    print(f" - {file}: {count} repos")

print(f"\n✅ Total Repositories across all files: {total_count}")
