import os
import json
import subprocess
from datetime import datetime
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['GIT_LFS_SKIP_SMUDGE'] = "1"
my_env = os.environ.copy()


def read_monthly_models(output_dir, start_month=None, end_month=None):
    """读取存储目录中的每个 JSON 文件及其内容，并根据月份范围筛选。"""
    monthly_models = {}

    if not os.path.exists(output_dir):
        print(f"目录 {output_dir} 不存在！")
        return monthly_models

    for file_name in os.listdir(output_dir):
        if file_name.endswith(".json"):
            month_key = file_name.replace(".json", "")

            # 如果指定了月份范围，进行过滤
            if start_month or end_month:
                try:
                    month_date = datetime.strptime(month_key, "%Y-%m")
                    if start_month and month_date < datetime.strptime(start_month, "%Y-%m"):
                        continue
                    if end_month and month_date > datetime.strptime(end_month, "%Y-%m"):
                        continue
                except ValueError:
                    print(f"文件名 {file_name} 的月份格式不正确，跳过。")
                    continue

            file_path = os.path.join(output_dir, file_name)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    monthly_models[month_key] = json.load(f)
                    print(f"已读取 {month_key} 的模型文件: {file_path}")
            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {e}")

    return monthly_models

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
        repo_url = f"https://huggingface.co/spaces/{model_id}"
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
    OUTPUT_DIR = "monthly_spaceId_files"  # 存储模型文件的目录
    START_MONTH = "2025-01"  # 起始月份，例如 "2024-01"
    END_MONTH = "2025-05"  # 结束月份，例如 "2024-06"

    models_by_month = read_monthly_models(OUTPUT_DIR, start_month=START_MONTH, end_month=END_MONTH)

    # 打印读取的模型数据
    for month, models in models_by_month.items():
        print(f"月份: {month}, 模型数量: {len(models)}")
        download_parallel('Z:/download_space/'+month,models)