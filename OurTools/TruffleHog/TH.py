import os
import subprocess
import json
import csv
import pandas as pd
import re
file_pattern = r'"file"\s*:\s*"([^"]+)"'
raw_pattern = r'"Raw"\s*:\s*"([^"]+)"'

def extractTokenandFile(scan_result):
    # 遍历findings中的每个条目
    row_data = []  # 用来存储每一行的file和raw信息
    scan_result = json.loads(scan_result)
    for finding in scan_result.get('findings', []):
        # 检查SourceMetadata是否存在
        source_metadata = finding.get('SourceMetadata')
        if source_metadata:
            # 从SourceMetadata提取file和Raw
            source_data = source_metadata.get('Data', {})
            filesystem_data = source_data.get('Filesystem', {})

            file_info = filesystem_data.get('file')
            raw_info = finding.get('Raw')

            if file_info and raw_info:
                if ".git" in file_info:
                    file_info = ".git"  # 只记录为'.git'
                else:
                    file_info = file_info.split("//")[-1]
                # 将提取的file和Raw信息存入字典
                row_data.append({
                    'file': file_info,
                    'raw': raw_info
                })
    return row_data



def scan_with_trufflehog(folder_path):
    """
    使用 TruffleHog 扫描指定文件夹中的代码仓库
    :param folder_path: 要扫描的文件夹路径
    :return: 仓库名称和扫描结果 (JSON 格式字符串)，如果没有结果返回 None
    """
    try:
        # 执行 TruffleHog 扫描
        result = subprocess.run(
            [
                "trufflehog", "filesystem",
                folder_path,
                "--results=verified,unknown", "--json"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        # 分割结果输出为 JSON 字符串列表
        json_strings = result.stdout.split('\n')
        print(json_strings)

        # 转换为 JSON 对象列表
        json_objects = [json.loads(js) for js in json_strings if js.strip()]

        # 检查最后一个 JSON 对象中的 verified_secrets 和 unverified_secrets
        if json_objects[-1]["verified_secrets"] == 0 and json_objects[-1]["unverified_secrets"] == 0:
            print(f"没有发现敏感信息: {folder_path}")
            merged_json = {"findings": []}
            return None  # 返回空表示没有结果
        else:
            print(f"发现敏感信息: {folder_path}")
            merged_json = {"findings": json_objects}
            return os.path.basename(folder_path), json.dumps(merged_json, indent=2)

    except Exception as e:
        print(f"扫描时发生错误: {e}")
        return None





if __name__ == "__main__":
    # 定义根目录和输出结果根目录
    # root_dir = "E:/download_space"
    trufflehog_output_dir = "D:/workspace/Demo_Secret_Reviewer/"
    #
    # # 调用根目录处理函数
    # process_root_directory(root_dir, trufflehog_output_dir)

    # 示例：扫描一个新添加的文件夹（例如 "E:/download_space/2024-12"）
    repo_path = r"D:\workspace\Demo_Secret_Reviewer"
    scan_with_trufflehog(repo_path)
    # process_single_folder(new_folder_path, trufflehog_output_dir)
