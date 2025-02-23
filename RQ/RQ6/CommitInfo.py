import json
import os
import subprocess
import re
from datetime import datetime

import git
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
                print(diffs)
                old_file, new_file, code_diff = file_change
                file_obj = FileChange(old_file, new_file, '00', '00',code_diff)
                commit_obj.add_file_change(file_obj)

        commit_objects.append(commit_obj)
    return commit_objects

# function
def scan_git_history(repo_path, Token_list):
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
    commit_objects = parse_git_commits(commits)
    # 输出解析后的 commit 对象
    for commit in commit_objects:
        for file in commit.file_changes:
            for token in Token_list:
                if token in file.code_diff:
                    datetimelist.append(commit.commit_date)
            print(f"      Code Changes:\n{file.code_diff}")
        print("=" * 80)
    return datetimelist

if __name__ == "__main__":
    Token_list = ['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']
    # Git 仓库路径
    git_repo_path = r"F:\download_space\2022-06\awacke1_NLP-Lyric-Chorus-Image"
    # 获取正则
    with open(os.path.join(os.path.dirname(__file__), "../regexes_v2.json"), 'r') as f:
        regexes = json.loads(f.read())
    print(regexes.values)
    # 定义敏感信息的正则表达式
    sensitive_patterns = list(regexes.values())

    # 扫描 Git 历史记录
    time_list = scan_git_history(git_repo_path, Token_list)
    print(time_list)
    create_time = get_repo_create_time("awacke1/NLP-Lyric-Chorus-Image")
    for date_str in time_list:
        print(datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z") - create_time)




