import json
import os
import subprocess
import re
from datetime import datetime
from huggingface_hub import HfApi

# API_TOKEN = ""

# 确保 Git 允许访问这个目录
subprocess.run(
    ["git", "config", "--global", "--add", "safe.directory", "F:/download_space/2022-06/awacke1_NLP-Lyric-Chorus-Image"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8"
)


# Tools
def translate_time(time_str):
    # 解析字符串为 datetime 对象
    return datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y %z")
def run_git_command(repo_path, command):
    """
    运行 Git 命令并返回结果。
    :param repo_path: Git 仓库路径
    :param command: Git 命令（列表形式）
    :return: 命令输出
    """
    result = subprocess.run(
        ["git", "-C", repo_path] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"  # 指定编码为 utf-8
    )
    if result.returncode != 0:
        raise Exception(f"Git command failed: {' '.join(command)}\\n{result.stderr}")
    return result.stdout
def get_repo_create_time(repo_name):
    HF = HfApi()
    space = HF.space_info(repo_name)
    return space.created_at




# function
def scan_git_history(repo_path, sensitive_patterns):
    """
    扫描 Git 历史记录中的敏感信息。
    :param repo_path: Git 仓库路径
    :param sensitive_patterns: 敏感信息的正则表达式列表
    """
    datetimelist = []
    print("提取提交历史...")
    # commits = run_git_command(repo_path, ["rev-list", "--all"]).splitlines()
    commits = run_git_command(repo_path, ["log", "--patch", "--full-history",
        "--date=format:%a %b %d %H:%M:%S %Y %z",
        "--pretty=fuller", "--notes"]).splitlines()

    print(f"发现 {len(commits)} 个提交，开始扫描...")
    for commit_hash in commits:
        try:
            diff_output = run_git_command(repo_path, ["show", commit_hash])
            match = re.search(r"Date:\s+(.+)", diff_output)
            # print(diff_output)
            if match:
                extracted_date = match.group(1) # 输出: Mon Nov 11 18:24:20 2024 +0800
            # print(diff_output)
            # 在变更中查找敏感信息
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, diff_output)
                if matches:
                    print(f"[!] 在提交 {commit_hash} 中发现敏感信息：")
                    datetimelist.append(extracted_date)
                    for match in matches:
                        print(f"    匹配内容: {match}")

        except Exception as e:
            print(f"[!] 无法扫描提交 {commit_hash}：{e}")
    return datetimelist

if __name__ == "__main__":
    # Git 仓库路径
    git_repo_path = r"F:\download_space\2022-06\awacke1_NLP-Lyric-Chorus-Image"
    # 获取正则
    with open(os.path.join(os.path.dirname(__file__), "regexes.json"), 'r') as f:
        regexes = json.loads(f.read())
    print(regexes.values)
    # 定义敏感信息的正则表达式
    sensitive_patterns = list(regexes.values())

    # 扫描 Git 历史记录
    time_list = scan_git_history(git_repo_path, sensitive_patterns)
    create_time = get_repo_create_time("awacke1/NLP-Lyric-Chorus-Image")
    for time in time_list:
        print(time-create_time)




