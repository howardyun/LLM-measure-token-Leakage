import os
import pandas as pd

# def count_and_print_match_lengths(matched_folder: str):
#     """
#     打印每个匹配结果文件的长度，并输出总计行数
#     """
#     total_matches = 0
#
#     print("📄 每个匹配结果文件的行数如下：")
#     print("-" * 50)
#
#     for file in sorted(os.listdir(matched_folder)):
#         if file.endswith(".csv"):
#             file_path = os.path.join(matched_folder, file)
#             try:
#                 df = pd.read_csv(file_path)
#                 count = len(df)
#                 total_matches += count
#                 print(f"{file:<30} 匹配行数: {count}")
#             except Exception as e:
#                 print(f"{file:<30} 读取失败 ❌: {e}")
#
#     print("-" * 50)
#     print(f" 匹配总计行数: {total_matches}")

# 示例使用
# count_and_print_match_lengths("match_results")
def concat_and_count_unique_matched_repos(matched_folder: str):
    """
    合并所有 CSV 文件后，统计 matched_repo 去重后的数量
    """
    all_dfs = []

    print("📄 开始读取并合并所有 CSV 文件：")
    print("-" * 60)

    for file in sorted(os.listdir(matched_folder)):
        if file.endswith(".csv"):
            file_path = os.path.join(matched_folder, file)
            try:
                df = pd.read_csv(file_path)
                if "matched_repo" not in df.columns:
                    print(f"{file:<30} ⚠️ 缺少 matched_repo 列，跳过")
                    continue
                all_dfs.append(df[["matched_repo"]])
                print(f"{file:<30} ✅ 已读取")
            except Exception as e:
                print(f"{file:<30} ❌ 读取失败: {e}")

    if not all_dfs:
        print("⚠️ 没有可合并的数据")
        return

    combined_df = pd.concat(all_dfs, ignore_index=True)
    value_counts = combined_df['matched_repo'].value_counts()
    # 统计只出现一次的数量
    count_once = (value_counts == 1 ).sum()
    count_twice = (value_counts == 2).sum()
    # 所有 matched_repo 的总数
    total_repos = len(value_counts)

    # 占比
    percentage_once = (count_once+count_twice) / total_repos

    print(f"🧮 出现次数为 1 的 matched_repo 数量: {count_once}")
    print(f"📊 占全部唯一 matched_repo 的比例: {percentage_once:.2%}")


    combined_df.dropna(subset=["matched_repo"], inplace=True)
    unique_matched_repos = combined_df.drop_duplicates(subset=["matched_repo"])

    print("-" * 60)
    print(f"✨ 合并后 matched_repo 唯一值总数: {len(unique_matched_repos)}")

# 示例使用
concat_and_count_unique_matched_repos("match_results")