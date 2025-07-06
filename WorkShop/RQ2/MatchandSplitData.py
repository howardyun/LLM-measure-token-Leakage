import pandas as pd
import os
import os
import pandas as pd
import json
def split_data():
    # 原始 CSV 文件路径
    input_file = "api_verification_results.csv"  # 替换为你的文件路径
    output_dir = "split_by_month"

    # 创建保存输出的文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 读取数据
    df = pd.read_csv(input_file)

    # 从 source_file 中提取年月信息，添加为新列
    df["year_month"] = df["source_file"].str.extract(r"(\d{4}-\d{2})")

    # 按年月分组并保存为单独的 CSV 文件
    for year_month, group in df.groupby("year_month"):
        if pd.isna(year_month):
            continue
        file_name = f"{year_month}.csv"
        file_path = os.path.join(output_dir, file_name)
        group.to_csv(file_path, index=False)

    print("按月份划分完毕，文件已保存在", output_dir)

def match_all_csv_with_json(csv_folder: str, json_folder: str, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(csv_folder):
        if file_name.endswith(".csv"):
            # 提取年月（如 2023-03）
            prefix = file_name.replace(".csv", "")
            csv_path = os.path.join(csv_folder, file_name)
            json_name = f"{prefix}_space_variables.json"
            json_path = os.path.join(json_folder, json_name)

            if not os.path.exists(json_path):
                print(f"❌ JSON 文件不存在: {json_name}")
                continue

            print(f"🔍 处理: {file_name} 和 {json_name}")

            # 读取 CSV
            df = pd.read_csv(csv_path)
            raw_values = df["raw"].dropna()

            # 读取 JSON
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # 匹配逻辑
            matches = []
            for raw_value in raw_values:
                for entry in json_data:
                    repo = entry.get("repo")
                    result = entry.get("result", {})
                    for key, var in result.items():
                        if raw_value == var.get("value"):
                            matches.append({
                                "raw": raw_value,
                                "matched_repo": repo,
                                "matched_key": key,
                                "matched_updated_at": var.get("updated_at"),
                                "matched_description": var.get("description")
                            })

            # 保存结果
            output_path = os.path.join(output_folder, f"{prefix}_matches.csv")
            pd.DataFrame(matches).to_csv(output_path, index=False)
            print(f"✅ 写入结果: {output_path}")

# Use
match_all_csv_with_json(
    csv_folder="split_by_month",
    json_folder="../Data",
    output_folder="match_results"
)


