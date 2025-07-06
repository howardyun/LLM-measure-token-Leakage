import glob
import json
import os

import pandas as pd
from selenium.webdriver.common.devtools.v132.debugger import pause

from OurTools.LLM.Langchain_test import LLM_analysis_file, LLM_analysis_commmit, run_parallel_analysis
from OurTools.utils import detect_secrets_from_string, read_file_to_string, read_commitInfo, \
    detect_secrets_from_string_file, extract_merged_context

def collect_all_commit_lines(commit_data):
    all_lines = []
    for item in commit_data:
        content = item.get("commit_content", "")
        all_lines.append(content)
    return all_lines

def extract_file_and_commit_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取文件数据
    file_data = [
        {
            "file_path": f["file_path"],
            "context": f["context"]
        }
        for f in data.get("file", [])
    ]

    # 提取 commit 数据
    commit_data = [
        {
            "commit_index": idx,
            "commit_content": c
        }
        for idx, c in enumerate(data.get("commit", []), 1)
    ]

    return file_data, commit_data

def traverse_all_repos(base_dir,output_dir):
    json_files = glob.glob(os.path.join(base_dir, "*.json"))
    repo_name = []
    final_result = []
    for json_file in json_files:
        file_leak = []
        file_data, commit_data = extract_file_and_commit_data(json_file)
        print(json_file)
        # 先判断文件中的内容
        for item in file_data:
            file_path = item.get("file_path")
            context = item.get("context")
            leak_json = LLM_analysis_file(context)
            try:
                if leak_json.get("leaked_tokens") != []:
                    file_leak.append(leak_json)
            except AttributeError:
                # 处理 leak_json 不是字典或没有 get 方法的情况
                print("Error: leak_json is not a dictionary or doesn't have a get method")
            except Exception as e:
                # 处理其他可能的异常
                print(f"An unexpected error occurred: {e}")

        # 再判断commit信息中的内容
        if commit_data == None:
            print("No commit data found")
        commit_contents = collect_all_commit_lines(commit_data)
        commit_leak = run_parallel_analysis(commit_contents, max_workers=6)
        result = [item for item in commit_leak if item.get('leaked_tokens')]
        final = file_leak+result
        if len(final) == 0:
            print(json_file)
            print("null")
            print('#'*100)
            continue
        else:
            repo_name.append(json_file.split('\\')[-1].split('.')[0])
            final_result.append(final)


        # 创建 DataFrame
    df = pd.DataFrame({
            "repo_name": repo_name,
            "final_result": final_result
        })

    # 保存为 CSV
    df.to_csv(f"{output_dir}/output.csv", index=False, encoding="utf-8")

    print('pause')

if __name__ == '__main__':
    output_dir = r'Z:/Minidataset_output/LLM_result'
    traverse_all_repos('Z:\Minidataset_output\static_result',output_dir)