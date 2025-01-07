# import os
# import csv
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
# def search_in_file(file_path, search_terms):
#     """
#     在单个文件中搜索多个内容。
#     :param file_path: str，文件路径
#     :param search_terms: list[str]，要搜索的内容列表
#     :return: list[tuple[str, str, int]]，匹配内容 (搜索词, 匹配行, 行号)
#     """
#     matches = []
#     try:
#         with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#             for line_num, line in enumerate(f, start=1):
#                 for term in search_terms:
#                     if term in line:
#                         matches.append((term, line.strip(), line_num))
#                         break  # 如果匹配任意搜索词，跳出当前搜索词循环
#     except Exception as e:
#         print(f"无法读取文件 {file_path}，错误：{e}")
#     return matches
#
# def search_in_repo_folder(root_folder, search_terms, file_extensions=None, max_workers=8):
#     """
#     在文件夹中并发搜索多个内容，并记录仓库名、文件路径和匹配信息。
#     :param root_folder: str，包含代码仓库的根文件夹
#     :param search_terms: list[str]，要搜索的内容列表
#     :param file_extensions: list[str]，需要搜索的文件扩展名（默认为 None 表示所有文件）
#     :param max_workers: int，并发线程数
#     :return: list[dict]，匹配结果，每个字典包含仓库名、相对路径、文件名、搜索词、匹配行、行号
#     """
#     results = []
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = []
#
#         for root, _, files in os.walk(root_folder):
#             for file in files:
#                 if file_extensions and not file.endswith(tuple(file_extensions)):
#                     continue
#                 file_path = os.path.join(root, file)
#                 futures.append(executor.submit(search_in_file, file_path, search_terms))
#
#                 # 提取仓库名和相对路径
#                 relative_path = os.path.relpath(file_path, root_folder)
#                 repo_name = relative_path.split(os.sep)[0]  # 假设仓库名是根目录的直接子目录
#
#                 futures[-1].repo_name = repo_name
#                 futures[-1].relative_path = os.path.relpath(file_path, os.path.join(root_folder, repo_name))
#                 futures[-1].file_name = file
#
#         for future in as_completed(futures):
#             matches = future.result()
#             if matches:
#                 for term, match_line, line_num in matches:
#                     results.append({
#                         "repo_name": future.repo_name,
#                         "relative_path": future.relative_path,
#                         "file_name": future.file_name,
#                         "search_term": term,
#                         "match_line": match_line,
#                         "line_num": line_num
#                     })
#
#     return results
#
# def save_results_to_csv(results, output_csv):
#     """
#     保存结果到 CSV 文件。
#     :param results: list[dict]，匹配结果
#     :param output_csv: str，输出的 CSV 文件路径
#     """
#     with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
#         writer = csv.DictWriter(csv_file, fieldnames=["repo_name", "relative_path", "file_name", "search_term", "match_line", "line_num"])
#         writer.writeheader()
#         writer.writerows(results)
#
#
# if __name__ == "__main__":
#     # 根文件夹路径
#     root_folder = "E:/download_space/2024-03"  # 替换为包含2万个代码仓库的文件夹路径
#
#     # 要查找的内容
#     search_terms = ["api_token", "secret"]   # 替换为目标内容
#
#     # 文件扩展名过滤
#     file_extensions = [".py", ".json"]  # 替换为需要的扩展名，None 表示所有文件
#
#     # 输出 CSV 文件路径
#     output_csv = "E:/download_space/serchfile_scan/search_results_2024-03.csv"
#
#     # 开始搜索
#     print("正在搜索，请稍候...")
#     results = search_in_repo_folder(root_folder, search_terms, file_extensions, max_workers=16)
#
#     # 保存结果到 CSV
#     save_results_to_csv(results, output_csv)
#     print(f"搜索完成！结果已保存到 {output_csv}")


import os
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

def search_in_file(file_path, search_terms):
    """
    在单个文件中搜索多个内容。
    :param file_path: str，文件路径
    :param search_terms: list[str]，要搜索的内容列表
    :return: list[tuple[str, str, int]]，匹配内容 (搜索词, 匹配行, 行号)
    """
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                for term in search_terms:
                    if term in line:
                        matches.append((term, line.strip(), line_num))
                        break  # 如果匹配任意搜索词，跳出当前搜索词循环
    except Exception as e:
        print(f"无法读取文件 {file_path}，错误：{e}")
    return matches

def search_in_repo_folder(root_folder, search_terms, file_extensions=None, max_workers=8):
    """
    在文件夹中并发搜索多个内容，并记录仓库名、文件路径和匹配信息。
    :param root_folder: str，包含代码仓库的根文件夹
    :param search_terms: list[str]，要搜索的内容列表
    :param file_extensions: list[str]，需要搜索的文件扩展名（默认为 None 表示所有文件）
    :param max_workers: int，并发线程数
    :return: list[dict]，匹配结果，每个字典包含仓库名、相对路径、文件名、搜索词、匹配行、行号
    """
    results = []
    repo_count = 0  # 添加仓库计数器
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for root, _, files in os.walk(root_folder):
            for file in files:
                if file_extensions and not file.endswith(tuple(file_extensions)):
                    continue
                file_path = os.path.join(root, file)
                futures.append(executor.submit(search_in_file, file_path, search_terms))

                # 提取仓库名和相对路径
                relative_path = os.path.relpath(file_path, root_folder)
                repo_name = relative_path.split(os.sep)[0]  # 假设仓库名是根目录的直接子目录

                futures[-1].repo_name = repo_name
                futures[-1].relative_path = os.path.relpath(file_path, os.path.join(root_folder, repo_name))
                futures[-1].file_name = file

                # 每处理1000个仓库打印一次
                repo_count += 1
                if repo_count % 100 == 0:
                    print(f"已处理 {repo_count} 个仓库...")

        for future in as_completed(futures):
            matches = future.result()
            if matches:
                for term, match_line, line_num in matches:
                    results.append({
                        "repo_name": future.repo_name,
                        "relative_path": future.relative_path,
                        "file_name": future.file_name,
                        "search_term": term,
                        "match_line": match_line,
                        "line_num": line_num
                    })

    return results

def save_results_to_csv(results, output_csv):
    """
    保存结果到 CSV 文件。
    :param results: list[dict]，匹配结果
    :param output_csv: str，输出的 CSV 文件路径
    """
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["repo_name", "relative_path", "file_name", "search_term", "match_line", "line_num"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    # 根文件夹路径
    root_folder = "E:/download_space/2024-03"  # 替换为包含2万个代码仓库的文件夹路径

    # 要查找的内容
    search_terms = ["api_token", "secret"]   # 替换为目标内容

    # 文件扩展名过滤
    file_extensions = [".py", ".json"]  # 替换为需要的扩展名，None 表示所有文件

    # 输出 CSV 文件路径
    output_csv = "E:/download_space/serchfile_scan/search_results_2024-03.csv"

    # 开始搜索
    print("正在搜索，请稍候...")
    results = search_in_repo_folder(root_folder, search_terms, file_extensions, max_workers=16)

    # 保存结果到 CSV
    save_results_to_csv(results, output_csv)
    print(f"搜索完成！结果已保存到 {output_csv}")
