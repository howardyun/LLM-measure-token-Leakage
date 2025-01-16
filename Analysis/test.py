import git


def get_file_history(repo_path, file_path):
    # 打开 Git 仓库
    repo = git.Repo(repo_path)

    # 获取文件的所有提交历史
    file_history = list(repo.iter_commits(paths=file_path))

    history = []
    for commit in file_history:
        # 获取每个提交的哈希和提交信息
        commit_info = {
            "commit_hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_datetime,
            "message": commit.message
        }

        # 获取文件在该提交时的内容
        file_content = commit.tree / file_path
        try:
            content = file_content.data_stream.read().decode('utf-8', errors='ignore')  # 跳过解码错误的字符
        except UnicodeDecodeError:
            content = "<Unable to decode file content>"

        history.append({
            "commit_info": commit_info,
            "file_content": content
        })

    return history


def get_file_diff_history(repo_path, file_path):
    # 打开 Git 仓库
    repo = git.Repo(repo_path)

    # 获取文件的所有提交历史
    file_history = list(repo.iter_commits(paths=file_path))

    diffs = []
    for commit in file_history:
        # 获取每个提交的哈希和提交信息
        commit_info = {
            "commit_hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_datetime,
            "message": commit.message
        }

        # 获取该提交的 diff 内容
        diff = commit.diff(commit.parents or None, paths=file_path)

        # 将 diff 格式化成一个字符串
        diff_content = ""
        for change in diff:
            diff_content += change.diff  # 将二进制 diff 转为文本

        diffs.append({
            "commit_info": commit_info,
            "diff_content": diff_content
        })

    return diffs

# 用法
repo_path = 'C:/Users/ShaoxuanYun\Desktop\workspace\LMMeasure'  # Git 仓库路径
file_path = 'Spacehub/DetectScecret/scan'  # 目标文件路径

file_diff_history = get_file_diff_history(repo_path, file_path)

# 打印文件的历史版本信息
for entry in file_diff_history:
    print(f"Commit: {entry['commit_info']['commit_hash']}")
    print(f"Author: {entry['commit_info']['author']}")
    print(f"Date: {entry['commit_info']['date']}")
    print(f"Message: {entry['commit_info']['message']}")
    print(f"Diff Content:\n{entry['diff_content']}")
    print('-' * 80)
