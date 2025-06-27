import os
import shutil
import random
from tqdm import tqdm

# === 配置区域 ===
source_dir = r'Z:\download_space_modelscope'  # 原始文件夹路径（包含很多代码仓库）
target_dir = r'Z:\MiniDataset-ModelScope'  # 目标文件夹路径（用来存放复制的仓库）
sample_size = 1000  # 抽取数量

# === 逻辑开始 ===
# 获取所有子文件夹（假设每个仓库是一个子文件夹）
all_repos = [name for name in os.listdir(source_dir)
             if os.path.isdir(os.path.join(source_dir, name))]

print(f'总共找到 {len(all_repos)} 个仓库')

# 检查是否足够抽样
if len(all_repos) < sample_size:
    raise ValueError(f'可用仓库数不足（仅有 {len(all_repos)} 个）')

# 随机抽取
sampled_repos = random.sample(all_repos, sample_size)

# 创建目标目录
os.makedirs(target_dir, exist_ok=True)

# 使用 tqdm 显示进度条
for repo in tqdm(sampled_repos, desc="复制仓库进度", unit="个"):
    src_path = os.path.join(source_dir, repo)
    dst_path = os.path.join(target_dir, repo)
    shutil.copytree(src_path, dst_path)

print(f'完成：已成功复制 {sample_size} 个仓库到 {target_dir}')
