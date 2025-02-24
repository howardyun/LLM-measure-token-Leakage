import os
import re
import json
import subprocess
import tempfile
from git import Repo
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.document_loaders import TextLoader, PythonLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import Tool, initialize_agent, AgentExecutor

# 初始化LLM
llm = ChatOpenAI(
    temperature=0.95,
    model="glm-4-plus",
    openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 正则表达式模式库
SECRET_PATTERNS = {
    "AWS_KEY": r"AKIA[0-9A-Z]{16}",
    "API_KEY": r"(?i)(?:api|secret)[_-]?key\s*=\s*['\"][a-z0-9]{32,}['\"]",
    "JWT": r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"
}


# ------------------------------
# 数据获取模块
# ------------------------------
def clone_repo(repo_url):
    """克隆GitHub仓库到本地临时目录"""
    local_dir = tempfile.mkdtemp()
    print(f"Cloning repository {repo_url} to {local_dir}...")
    Repo.clone_from(repo_url, local_dir)
    return local_dir


# ------------------------------
# 数据处理模块
# ------------------------------
def load_files(repo_path):
    """加载仓库中的文件"""
    loaders = {
        '.py': PythonLoader,
        '.env': TextLoader,
        '.txt': TextLoader,
        '.json': lambda file_path: JSONLoader(file_path, jq_schema=".", text_content=False)
    }
    documents = []
    for root, _, files in os.walk(repo_path):
        if '.git' in root.split(os.sep):
            continue
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in loaders:
                try:
                    loader = loaders[ext](os.path.join(root, file))
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    return documents


def split_documents(documents):
    """分割文档为小块"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(documents)


# ------------------------------
# 敏感信息检测模块
# ------------------------------
def regex_scan(text):
    """使用正则表达式检测敏感信息"""
    secrets_found = []
    for name, pattern in SECRET_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            secrets_found.append({
                "type": name,
                "matches": matches
            })
    return secrets_found


def ai_detect_secret(text):
    """使用AI模型检测敏感信息"""
    prompt = f"""Analyze if this code contains sensitive information:
    {text[:2000]}

    Consider:
    1. Credential patterns
    2. Hardcoded passwords
    3. Internal URLs
    4. Unusual entropy

    Respond in JSON format: {{"risk": "high/medium/low", "reason": "..."}}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    print(response)
    return json.loads(response.content)


# ------------------------------
# Git历史记录扫描模块
# ------------------------------


# def scan_git_history(repo_path):
#     """扫描.git历史记录中的敏感信息"""
#     repo = Repo(repo_path)
#     secrets_found = []
#
#     for commit in repo.iter_commits('--all'):
#         for blob in commit.tree.blobs:
#             try:
#                 content = blob.data_stream.read().decode('utf-8', errors='replace')
#                 secrets = regex_scan(content)
#                 if secrets:
#                     secrets_found.append({
#                         "commit": commit.hexsha,
#                         "file": blob.path,
#                         "secrets": secrets
#                     })
#             except Exception as e:
#                 print(f"Error reading blob {blob.path}: {e}")
#     return secrets_found
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


def scan_git_history(repo_path):
    """
    扫描 Git 历史记录中的敏感信息。
    :param repo_path: Git 仓库路径
    :param sensitive_patterns: 敏感信息的正则表达式列表
    """
    print("提取提交历史...")
    commits = run_git_command(repo_path, ["rev-list", "--all"]).splitlines()

    print(f"发现 {len(commits)} 个提交，开始扫描...")
    secrets_found = []
    for commit_hash in commits:
        try:
            # 获取提交的变更内容
            diff_output = run_git_command(repo_path, ["show", commit_hash])
            secrets = regex_scan(diff_output)
            if secrets:
                secrets_found.append({
                    "commit": commit_hash,
                    "secrets": secrets
                })
        except Exception as e:
            print(f"[!] 无法扫描提交 {commit_hash}：{e}")
    return secrets_found


# ------------------------------
# Agent核心模块
# ------------------------------
def initialize_secret_agent():
    """初始化AI Agent"""
    tools = [
        Tool(
            name="history_scanner",
            func=scan_git_history,
            description="扫描git历史提交记录中的敏感信息"
        ),
        Tool(
            name="pattern_matcher",
            func=regex_scan,
            description="使用正则表达式匹配已知密钥模式"
        ),
        Tool(
            name="ai_detector",
            func=ai_detect_secret,
            description="AI模型进行上下文敏感分析"
        )
    ]
    return initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=True
    )


# ------------------------------
# 主工作流
# ------------------------------
def full_scan_workflow(repo_url):
    """完整扫描工作流"""
    # 克隆仓库
    # local_repo = clone_repo(repo_url)
    local_repo = repo_url

    # 加载并分割文件
    documents = load_files(local_repo)
    split_docs = split_documents(documents)

    # 初始化Agent
    agent = initialize_secret_agent()

    # 扫描当前文件
    current_secrets = []
    for doc in split_docs:
        result = agent.run(f"分析以下内容是否存在敏感信息:\n{doc.page_content}")
        if "high" in result.lower() or "medium" in result.lower():
            current_secrets.append({
                "content": doc.page_content[:500],  # 截取部分内容
                "analysis": result
            })

    # 扫描历史记录
    history_secrets = scan_git_history(local_repo)

    # 生成报告
    report = {
        "repo_url": repo_url,
        "stats": {
            "current_files_scanned": len(split_docs),
            "historical_commits_scanned": len(history_secrets),
            "secrets_found": len(current_secrets) + len(history_secrets)
        },
        "current_secrets": current_secrets,
        "historical_secrets": history_secrets
    }

    return report


# ------------------------------
# 多仓库扫描
# ------------------------------
def scan_multiple_repos(repo_urls):
    """扫描多个仓库"""
    reports = []
    for repo_url in repo_urls:
        print(f"Scanning repository: {repo_url}")
        report = full_scan_workflow(repo_url)
        reports.append(report)
        print(f"Scan completed for {repo_url}. Secrets found: {report['stats']['secrets_found']}")
    return reports


# ------------------------------
# 主函数
# ------------------------------
if __name__ == "__main__":
    # 示例仓库列表
    repo_urls = [
        "/Volumes/My Passport/download_space/2024-03/a958909457_Tavern_HF_Chathistory2",
        # "E:\\download_space\\2024-03\\a958909457_Tavern_HF_Chathistory2",
    ]

    # 扫描所有仓库
    reports = scan_multiple_repos(repo_urls)

    # 保存报告
    with open("scan_reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    print("扫描完成！报告已保存到 scan_reports.json")
