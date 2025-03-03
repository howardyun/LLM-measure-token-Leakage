import math
import os
import re
import subprocess
import json

import chardet

from RQ.RQ6.CommitInfoClass import Commit, FileChange

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


# # 获取密钥正则
# with open(os.path.join(os.path.dirname(__file__), "../regexes_v2.json"), 'r') as f:
#     regexes = json.loads(f.read())
# # 定义敏感信息的正则表达式
# sensitive_patterns = regexes


# Tools
def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    frequency = {char: data.count(char) for char in set(data)}
    total_chars = len(data)
    return -sum((freq / total_chars) * math.log2(freq / total_chars) for freq in frequency.values())
def run_git_command_utf8(repo_path, command):
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
def run_git_command(repo_path, git_args):
    result = subprocess.run(
        ["git"] + git_args,
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    raw_data = result.stdout
    detected_encoding = chardet.detect(raw_data)["encoding"] or "utf-8"

    return raw_data.decode(detected_encoding, errors="ignore")
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
def scan_git_history(repo_path, Token_list):
    """
    扫描 Git 历史记录中的敏感信息。
    :param repo_path: Git 仓库路径
    :param sensitive_patterns: 敏感信息的正则表达式列表
    """
    # 确保 Git 允许访问这个目录
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
    commits = run_git_command(repo_path, ["log", "--all", "--patch", "--full-history",
                                          "--date=format:%a %b %d %H:%M:%S %Y %z",
                                          "--pretty=fuller", "--notes"])

    if commits == None:
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
def detect_secrets_from_string(file_content: str, entropy_threshold=5.0):
    # 按行拆分
    lines = file_content.split("\n")
    high_entropy_line = []
    for line_number, line in enumerate(lines, start=1):
        entropy = shannon_entropy(line.strip())

        # 如果熵值高于阈值，记录该行
        if entropy > entropy_threshold:
            high_entropy_line.append(line.strip())
    if len(high_entropy_line) > 0:
        return True,high_entropy_line
    return False,high_entropy_line

def read_file(file_path):
    # 判断文件类型
    file_extension = file_path.split('.')[-1]

    content = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_extension == 'py':
                # 读取Python文件，将内容按行存储到数组
                content = f.readlines()

            elif file_extension == 'json':
                # 读取JSON文件，将内容解析为Python对象（通常是字典或列表）
                content = json.load(f)

            elif file_extension == 'env':
                # 读取.env文件，按行处理每一行并去除空行和注释
                for line in f.readlines():
                    line = line.strip()
                    if line and not line.startswith('#'):  # 忽略空行和注释
                        content.append(line)
            else:
                print(f"Unsupported file type: {file_extension}")
                for line in f.readlines():
                    line = line.strip()
                    if line and not line.startswith('#'):  # 忽略空行和注释
                        content.append(line)

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    return ''.join(content)
def read_commitInfo(repo_path):
    # 确保 Git 允许访问这个目录
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
    commits = run_git_command(repo_path, ["log", "--all", "--patch", "--full-history",
                                          "--date=format:%a %b %d %H:%M:%S %Y %z",
                                          "--pretty=fuller", "--notes"])
    if commits == None:
        return []
    content = []
    commits = commits.splitlines()
    commit_objects = parse_git_commits(commits)
    for commit in commit_objects:

        filechange = []
        for file in commit.file_changes:
            result,high_entropy_line = detect_secrets_from_string(file.code_diff)
            if result:
                filechange.append(file.code_diff)
                # print('有高熵字符串')
            # else:
                # print("没有高熵字符串")
                # print(file.code_diff)
        if len(filechange) > 0:
            tmp = ''.join(filechange)
            # print(tmp)
            content.append(tmp)
        # print('---'*100)
    return content

if __name__ == "__main__":
    # content = read_file("F:/download_space/2022-03/Ralfouzan_YAQEN/app.py")
    # content = read_commitInfo("F:/download_space/2022-03/rajesh1729_live-twitter-sentiment-analysis")
    content = read_commitInfo("F:/download_space/2022-03/Ralfouzan_YAQEN")

