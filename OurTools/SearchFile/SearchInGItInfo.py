import subprocess
import re

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
            # 获取提交的变更内容
            diff_output = run_git_command(repo_path, ["show", commit_hash])
            print(diff_output)
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
    git_repo_path = r"E:\\download_space\\2024-03\\a958909457_Tavern_HF_Chathistory2"

    # 定义敏感信息的正则表达式
    sensitive_patterns = [
        r"AKIA[0-9A-Z]{16}",  # AWS 密钥
        r"AIza[0-9A-Za-z-_]{35}",  # Google API 密钥
        r"[a-zA-Z0-9-_]{32,64}",  # 通用令牌或密钥
        # r"(?:password|passwd|pwd)["']?\s*[:=]\s*["'][^"']{6,}["']",  # 密码
        # r"PRIVATE KEY-----[\s\S]+?-----END PRIVATE KEY"  # 私钥
    ]

    # 扫描 Git 历史记录
    scan_git_history(git_repo_path, sensitive_patterns)
