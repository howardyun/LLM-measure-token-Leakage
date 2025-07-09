import math
import os
import re
import subprocess
import json

import chardet
from bs4 import BeautifulSoup

from RQ.RQ6.CommitInfoClass import Commit, FileChange

HTML_LIKE_PREFIXES = [
    "<!DOCTYPE",   # HTML文档声明
    "<html",       # HTML根标签
    "<head", "<body", "<title", "<meta", "<link", "<style", "<script",
    "<div", "<span", "<section", "<article", "<footer", "<header",
    "<img", "<a", "<p", "<br", "<input", "<form", "<button", "<label",
    "<ul", "<li", "<ol", "<table", "<tr", "<td", "<th", "<tbody", "<thead",
    "<h1", "<h2", "<h3", "<h4", "<h5", "<h6",
    "</html", "</head", "</body", "</div", "</span", "</script", "</style",
    "<svg", "<canvas", "<iframe", "<object",
    "<Component", "</Component",  # React JSX
    "<template", "<slot", "<router-view", "<nuxt-link", "<v-",  # Vue 模板语言
]


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



def remove_html_tags_safe(html_str):
    """使用BeautifulSoup安全移除HTML标签"""
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


# # 获取密钥正则
# with open(os.path.join(os.path.dirname(__file__), "../regexes_v2.json"), 'r') as f:
#     regexes = json.loads(f.read())
# # 定义敏感信息的正则表达式
# sensitive_patterns = regexes
def is_html_advanced(input_str):
    # 常见HTML标签列表
    common_tags = ['<html', '<body', '<div', '<p', '<a', '<img', '<script', '<style']
    input_lower = input_str.lower()
    return any(tag in input_lower for tag in common_tags)

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


# def detect_secrets_from_string(file_content: str, entropy_threshold=5.1):
#     # if is_html_advanced(file_content):
#     #     file_content = remove_html_tags_safe(file_content)
#     # 按行拆分
#     lines = file_content.split("\n")
#     high_entropy_line = []
#     for line_number, line in enumerate(lines, start=1):
#         entropy = shannon_entropy(line.strip())
#
#         # 如果熵值高于阈值，记录该行
#         if entropy > entropy_threshold:
#             high_entropy_line.append(line.strip())
#     if len(high_entropy_line) > 0:
#         return True,high_entropy_line
#     return False,high_entropy_line


def has_structured_subsequence(s, window=4):
    """
    判断字符串中是否存在结构化子串（长度为4的滑动窗口）：
    - AAAA 类型：相同字符
    - ABCD 类型：连续递增
    - DCBA 类型：连续递减
    """
    s = s.lower().strip()
    if len(s) < window:
        return False

    for i in range(len(s) - window + 1):
        sub = s[i:i+window]
        if len(set(sub)) == 1:
            return True  # 重复字符
        if all(ord(sub[j+1]) - ord(sub[j]) == 1 for j in range(window - 1)):
            return True  # 递增
        if all(ord(sub[j+1]) - ord(sub[j]) == -1 for j in range(window - 1)):
            return True  # 递减
    return False

def starts_with_html_prefix(line: str) -> bool:
    line = line.strip().lower()
    return any(line.startswith(prefix.lower()) for prefix in HTML_LIKE_PREFIXES)

def detect_secrets_from_string(file_content: str, entropy_threshold=5.0):
    lines = file_content.split("\n")
    high_entropy_line = []
    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        entropy = shannon_entropy(stripped_line)
        if entropy > entropy_threshold:
            if not has_structured_subsequence(stripped_line):  # 加入结构序列排除
                high_entropy_line.append(stripped_line)
            if not starts_with_html_prefix(stripped_line):
                high_entropy_line.append(stripped_line)

    if high_entropy_line:
        return True, high_entropy_line
    return False, high_entropy_line



def detect_secrets_from_string_file(file_content: str, entropy_threshold=5.0):
    # 按行拆分
    lines = file_content.split("\n")
    high_entropy_line = []
    for line_number, line in enumerate(lines, start=1):
        entropy = shannon_entropy(line.strip())
        # 如果熵值高于阈值，记录该行
        if entropy > entropy_threshold:
            high_entropy_line.append(line.strip())
    if len(high_entropy_line) > 0:
        return True,file_content
    return False,file_content
def read_file_to_string(file_path):
    """读取文件内容为字符串，自动处理编码问题

    Args:
        file_path (str): 要读取的文件路径

    Returns:
        str: 文件内容字符串
    """
    # 先尝试用UTF-8读取（大多数现代文本文件使用UTF-8）
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果UTF-8失败，检测实际编码并重试
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)  # 读取前1024字节用于编码检测
                encoding = chardet.detect(raw_data)['encoding']
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"无法读取文件 {file_path}: {str(e)}")
    except Exception as e:
        raise ValueError(f"读取文件 {file_path} 时出错: {str(e)}")

def extract_merged_context(code_diff: str, high_entropy_lines: list[str], context_window: int = 10) -> str:
    lines = code_diff.splitlines()
    entropy_indices = []

    # 1. 找出所有高熵行的索引
    for target_line in high_entropy_lines:
        for idx, content in enumerate(lines):
            if target_line.strip() in content.strip():
                entropy_indices.append(idx)

    if not entropy_indices:
        return ""

    # 2. 每个高熵索引扩展为一个上下文区间 [start, end]
    ranges = []
    for idx in entropy_indices:
        start = max(0, idx - context_window)
        end = min(len(lines), idx + context_window + 1)
        ranges.append((start, end))

    # 3. 合并重叠区间
    merged = []
    ranges.sort()
    cur_start, cur_end = ranges[0]

    for start, end in ranges[1:]:
        if start <= cur_end:  # 有重叠
            cur_end = max(cur_end, end)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
    merged.append((cur_start, cur_end))  # 别忘了最后一段

    # 4. 提取合并后的片段
    result_snippets = []
    for start, end in merged:
        snippet = "\n".join(lines[start:end])
        result_snippets.append(snippet)

    # 5. 用一行多个 '#' 分隔不同片段
    separator = "\n" + "#" * 20 + "\n"
    return separator.join(result_snippets)

# def read_file(file_path):
#     # 判断文件类型
#     file_extension = file_path.split('.')[-1]
#
#     content = []
#
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             if file_extension == 'py':
#                 # 读取Python文件，将内容按行存储到数组
#                 content = f.readlines()
#
#             elif file_extension == 'json':
#                 # 读取JSON文件，将内容解析为Python对象（通常是字典或列表）
#                 content = f.read()
#
#             elif file_extension == 'env':
#                 # 读取.env文件，按行处理每一行并去除空行和注释
#                 for line in f.readlines():
#                     line = line.strip()
#                     if line and not line.startswith('#'):  # 忽略空行和注释
#                         content.append(line)
#             else:
#                 print(f"Unsupported file type: {file_extension}")
#                 for line in f.readlines():
#                     line = line.strip()
#                     if line and not line.startswith('#'):  # 忽略空行和注释
#                         content.append(line)
#
#     except Exception as e:
#         print(f"Error reading file {file_path}: {e}")
#
#     return ''.join(content)
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
            # print(file.code_diff)
            # print('xxx'*100)
            result,high_entropy_line = detect_secrets_from_string(file.code_diff)
            if result:
                context_string = extract_merged_context(file.code_diff,high_entropy_line,5)
                filechange.append(context_string)
                # print('有高熵字符串')
            # else:
            #     print("没有高熵字符串")
            #     print(file.code_diff)
        if len(filechange) > 0:
            tmp = ('#'*20).join(filechange)
            # print(tmp)
            content.append(tmp)
        # print('---'*100)
    return content




if __name__ == "__main__":
    # content = read_file("F:/download_space/2022-03/Ralfouzan_YAQEN/app.py")
    # content = read_commitInfo("F:/download_space/2022-03/rajesh1729_live-twitter-sentiment-analysis")
    content = read_commitInfo("F:/download_space/2022-03/Ralfouzan_YAQEN")



