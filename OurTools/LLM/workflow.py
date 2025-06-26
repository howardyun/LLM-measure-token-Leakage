import os

from OurTools.LLM.Langchain_test import LLM_analysis_file, LLM_analysis_commmit, run_parallel_analysis
from OurTools.utils import detect_secrets_from_string, read_file_to_string, read_commitInfo, \
    detect_secrets_from_string_file, extract_merged_context

TARGET_EXTENSIONS = [
    '.txt', '.md', '.csv', '.json', '.xml', '.yaml', '.yml','.csv','.jsonl'
     '.js', '.ts', '.py', '.c', '.cpp', '.h', '.hpp', '.java', '.sh',
    '.bash', '.conf', '.cfg', '.ini', '.log', '.sql', '.toml',
    '.jsx', '.tsx', '.vue', '.rb', '.pl', '.php', '.go', '.rs', '.scala', '.dart',
    '.proto', '.diff', '.patch', '.rst', '.tex', '.bib', '.markdown', '.gitignore',
    '.properties', '.gradle', '.bat', '.ps1', '.vbs', '.cs', '.csproj', '.sln'
]

def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))

def walk_repo_files(repo_path):
    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            if ext in TARGET_EXTENSIONS:
                yield file_path

def SecretReviwer(repo_path):
    print(f"\n--- Git 仓库: {repo_path} ---")
    file_leak = []
    commit_leak = []
    # 对于文件内容的扫描
    for file_path in walk_repo_files(repo_path):
        file_content = read_file_to_string(f'{file_path}')
        re,high_entropy_lines =detect_secrets_from_string(file_content)
        if re:
            context_string = extract_merged_context(file_content, high_entropy_lines, 5)
            try:
                leak_json = LLM_analysis_file(context_string)
            except Exception as e:
                print(f"发生了未知异常：{e}")
                continue
            file_leak.append(leak_json)

    commit_contents = read_commitInfo(repo_path)

    if len(commit_contents) > 0:
        commit_leak = run_parallel_analysis(commit_contents, max_workers=6)

    return file_leak + commit_leak

def traverse_all_repos(base_dir):
    for entry in os.listdir(base_dir):
        repo_path = os.path.join(base_dir, entry)
        if os.path.isdir(repo_path) and is_git_repo(repo_path):
            result = SecretReviwer(repo_path)
            print(repo_path)
            print(result)
            print('#'*100)

if __name__ == "__main__":
    # 使用示例
    base_directory = r"Z:\MiniDataset"  # 修改为你的路径
    traverse_all_repos(base_directory)
