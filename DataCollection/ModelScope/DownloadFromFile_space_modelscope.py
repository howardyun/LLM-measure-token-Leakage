import os
import json
import subprocess
from datetime import datetime
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
# os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['GIT_LFS_SKIP_SMUDGE'] = "1"
my_env = os.environ.copy()


def download(download_dir,modelhub_list):
    """检查下载目录是否存在，如果不存在则创建。"""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)
        print(f"已创建下载目录: {download_dir}")
    else:
        print(f"下载目录已存在: {download_dir}")

    for id in modelhub_list:
        subprocess.run(["git", "clone", "https://huggingface.co/spaces/" + id,
                    f"{download_dir}/" + id.replace("/", "_")],
                   env=my_env, shell=True, )

    return


def download_parallel(download_dir, modelhub_list):
    """检查下载目录是否存在，如果不存在则创建，并并行克隆仓库。"""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)
        print(f"已创建下载目录: {download_dir}")
    else:
        print(f"下载目录已存在: {download_dir}")


    def clone_repo(model_id):
        """克隆单个仓库的逻辑。"""
        repo_url = f"https://www.modelscope.cn/studios/{model_id}.git"
        target_dir = os.path.join(download_dir, model_id.replace("/", "_"))
        try:
            subprocess.run(["git", "clone", repo_url, target_dir], check=True, shell=True)
            print(f"成功克隆仓库: {model_id}")
        except subprocess.CalledProcessError as e:
            print(f"克隆仓库失败: {model_id}, 错误: {e}")

    # 使用线程池并行化克隆操作
    with ThreadPoolExecutor(max_workers=10) as executor:  # 根据需要调整 max_workers
        futures = {executor.submit(clone_repo, model_id): model_id for model_id in modelhub_list}

        for future in as_completed(futures):
            model_id = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"线程任务失败: {model_id}, 错误: {e}")

    print("所有仓库克隆操作已完成。")
    return


# 示例用法
if __name__ == "__main__":
    with open('output/modelscope_studios_links.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    data_list = [s[:s.rfind('/')].rsplit('/', 1)[-1] + '/' + s[s.rfind('/') + 1:] for s in data_list]
    print(data_list)
    download_parallel(r'Z:\download_space_modelscope', data_list)