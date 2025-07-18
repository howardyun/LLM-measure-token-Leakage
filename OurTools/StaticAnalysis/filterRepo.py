import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed  # 或者用 ProcessPoolExecutor

from OurTools.utils import detect_secrets_from_string, read_file_to_string, read_commitInfo, extract_merged_context
def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))

def walk_repo_files(repo_path):
    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            return file_path

def SecretReviwer(repo_path, output_dir):
    print(f"\n--- Git 仓库: {repo_path} ---")
    file_leak = []
    for file_path in walk_repo_files(repo_path):
        file_content = read_file_to_string(file_path)
        re, high_entropy_lines = detect_secrets_from_string(file_content)
        if re:
            context_string = extract_merged_context(file_content, high_entropy_lines, 5)

            file_leak.append({
                "file_path": file_path,
                "context": context_string
            })

    commit_contents = read_commitInfo(repo_path)

    data = {
        "RepoName": repo_path,
        "file": file_leak,
        "commit": commit_contents,
        "is_student": False
    }

    if len(file_leak) > 0 or len(commit_contents) > 0:
        filename = os.path.basename(repo_path).replace("/", "_").replace("\\", "_")
        output_path = os.path.join(output_dir, f"{filename}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[+] {repo_path} → 写入成功")
    else:
        print(f"[-] {repo_path} → 无敏感信息")
    print("#" * 80)

def traverse_all_repos_parallel(base_dir, output_dir, max_workers=6):
    os.makedirs(output_dir, exist_ok=True)
    repo_list = [
        os.path.join(base_dir, entry)
        for entry in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, entry)) and is_git_repo(os.path.join(base_dir, entry))
    ]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(SecretReviwer, repo_path, output_dir)
            for repo_path in repo_list
        ]
        for future in as_completed(futures):
            try:
                future.result()  # 捕捉异常
            except Exception as e:
                print(f"[!] 某个任务执行出错: {e}")

if __name__ == "__main__":
    base_directory = r""  # change to your path
    output_directory = r"Z"
    traverse_all_repos_parallel(base_directory, output_directory, max_workers=8)  # par
