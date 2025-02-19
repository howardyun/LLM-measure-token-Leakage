import json
import os
import subprocess
import re
from datetime import datetime

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

def scan_git_history(repo_path, sensitive_patterns):
    """
    扫描 Git 历史记录中的敏感信息。
    :param repo_path: Git 仓库路径
    :param sensitive_patterns: 敏感信息的正则表达式列表
    """
    print("提取提交历史...")
    commits = run_git_command(repo_path, ["rev-list", "--all"]).splitlines()
    print(f"发现 {len(commits)} 个提交，开始扫描...")
    for commit_hash in commits:
        try:
            diff_output = run_git_command(repo_path, ["show", commit_hash])
            match = re.search(r"Date:\s+(.+)", diff_output)
            if match:
                extracted_date = match.group(1)
                print(translate_time(extracted_date))  # 输出: Mon Nov 11 18:24:20 2024 +0800
            # print(diff_output)
            # 在变更中查找敏感信息
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, diff_output)
                if matches:
                    print(f"[!] 在提交 {commit_hash} 中发现敏感信息：")
                    for match in matches:
                        print(f"    匹配内容: {match}")

        except Exception as e:
            print(f"[!] 无法扫描提交 {commit_hash}：{e}")

if __name__ == "__main__":
    # Git 仓库路径
    git_repo_path = "/Users/howardyun/Desktop/workspace/Think-Out-Of-The-Box"

    with open(os.path.join(os.path.dirname(__file__), "regexes.json"), 'r') as f:
        regexes = json.loads(f.read())
    print(regexes.values)
    # 定义敏感信息的正则表达式
    sensitive_patterns = list(regexes.values())

    # 扫描 Git 历史记录
    scan_git_history(git_repo_path, sensitive_patterns)

