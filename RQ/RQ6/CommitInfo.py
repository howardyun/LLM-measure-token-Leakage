import ast
import glob
import json
import os
import subprocess
import re
from datetime import datetime

import git
import pandas as pd
from huggingface_hub import HfApi

from RQ.RQ6.CommitInfoClass import Commit, FileChange

# API_TOKEN = ""
# 正则表达式匹配 commit 和 diff（支持每个文件的修改）
commit_diff_pattern = re.compile(r'''
    commit\s(?P<commit_hash>\w+)\n
    Author:\s+(?P<author>.+?)\n
    AuthorDate:\s+(?P<author_date>.*?)\n
    Commit:\s+(?P<committer>.+?)\n
    CommitDate:\s+(?P<commit_date>.*?)\n
    \n\s+(?P<message>.+?)\n
    (?P<diff>diff\s--git[\s\S]+?)(?=\ncommit|\Z)
''', re.VERBOSE | re.DOTALL)

# 正则表达式匹配 diff 具体的文件修改
file_diff_pattern = re.compile(r'''
    diff\s--git\s(?P<old_file>[^\s]+)\s(?P<new_file>[^\s]+)\n
    .*?  # 忽略所有中间内容，包括 index、文件模式等
    (?P<code_diff>@@[\s\S]+?(?=\ndiff|\ncommit|\Z))  # 提取 @@ 开头的代码变更部分
''', re.VERBOSE | re.DOTALL)


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
def parse_git_commits(commits_string):
    commit_objects = []
    commits_string = '\n'.join(commits_string)
    # print(commits_string)
    commit_objects = []
    commits = commit_diff_pattern.findall(commits_string)
    for commit in commits:
        commit_hash, author, author_date, committer, commit_date, message, diffs = commit
        commit_obj = Commit(commit_hash, author, author_date, committer, commit_date, message)
        if diffs:
            file_changes = file_diff_pattern.findall(diffs)
            for file_change in file_changes:
                old_file, new_file, code_diff = file_change
                file_obj = FileChange(old_file, new_file, '00', '00',code_diff)
                commit_obj.add_file_change(file_obj)

        commit_objects.append(commit_obj)
    return commit_objects

# function
def get_time_interval(token_list,git_repo_path):
    # 扫描 Git 历史记录
    time_list = scan_git_history(git_repo_path, token_list)
    create_time = get_repo_create_time("awacke1/NLP-Lyric-Chorus-Image")

    inter = []
    for date_str in time_list:
        inter.append(datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z") - create_time)

    return min(inter)
def scan_git_history(repo_path, Token_list):
    """
    扫描 Git 历史记录中的敏感信息。
    :param repo_path: Git 仓库路径
    :param sensitive_patterns: 敏感信息的正则表达式列表
    """
    # 确保 Git 允许访问这个目录
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory",
            repo_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        datetimelist = []
        # commits = run_git_command(repo_path, ["rev-list", "--all"]).splitlines()
        commits = run_git_command(repo_path, ["log", "--patch", "--full-history",
                                              "--date=format:%a %b %d %H:%M:%S %Y %z",
                                              "--pretty=fuller", "--notes"])

        if commits == None :
            return []
        commits = commits.splitlines()
        commit_objects = parse_git_commits(commits)
        # 输出解析后的 commit 对象
        for commit in commit_objects:
            for file in commit.file_changes:
                for token in Token_list:
                    if token in file.code_diff:
                        datetimelist.append(commit.commit_date)
        return datetimelist
    except Exception as e:
        print(e)
        print(repo_path)
        return []

def process_files(repo_root_path,scan_file_path):
    time_intervals = []
    # 读取 CSV 文件
    repo_list_leakage = pd.read_csv(scan_file_path)
    for row in repo_list_leakage.itertuples():
        # 有index的值所以是1和3
        repo_name = row[1]
        repo_extract = row[3]
        try:
            parsed_list = ast.literal_eval(repo_extract)  # 解析字符串为列表
            if isinstance(parsed_list, list):
                # 去重file信息
                unique_file_values = list(set(entry['file'] for entry in parsed_list if 'file' in entry))
                # 如果没有明文发现，则代表已经处理了
                if len(unique_file_values) == 1 and unique_file_values[0] == '.git':
                    # 获取token
                    token_list = list(set(entry['raw'] for entry in parsed_list if 'raw' in entry))
                    # 设置仓库路径
                    git_repo_path = repo_root_path+'/'+repo_name.replace('/','_')
                    # 获取时间间隔
                    time_intervals.append(get_time_interval(token_list,git_repo_path))
                else:
                    continue
        except (SyntaxError, ValueError):
            print(os.path.join(repo_root_path, repo_name))
            continue  # 解析失败返回 None
    return time_intervals


if __name__ == "__main__":
    # 设定文件路径
    folder_path = "../Data/"  # 修改为你的实际路径
    file_pattern = os.path.join(folder_path, "*.csv")  # 查找所有 CSV 文件
    all_time_interval = []
    # 获取所有匹配的文件列表
    csv_files = sorted(glob.glob(file_pattern))
    for file in csv_files:
        filename = os.path.basename(file)  # 获取文件名
        time = filename.split("_")[0]
        print("正在处理"+time+'.'*10)
        repo_file_path = f"../../monthly_spaceId_files/{time}.json"
        scan_file_path = f"../Data/{time}_scan_results.csv"
        # 将字符串转换为datetime对象
        repo_time = datetime.strptime(time, "%Y-%m")
        if repo_time >= datetime.strptime("2024-03", "%Y-%m"):
            repo_root_path = f"E:/download_space/{time}"
        else:
            repo_root_path = f"F:/download_space/{time}"
        time = process_files(repo_root_path, scan_file_path)
        all_time_interval.append(time)
        # 在这里添加你的处理逻辑，例如读取 CSV 进行处理
    flattened = [item for sublist in all_time_interval for item in sublist]
    # 将列表保存到 JSON 文件
    with open('time_interval.json', 'w') as f:
        json.dump(flattened, f)






