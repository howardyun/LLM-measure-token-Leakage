import json
import os
from langchain_community.llms import OpenAI
import subprocess
import re
from git import Repo
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import chromadb
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma




chroma_client = chromadb.Client()




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

def extract_file_and_git_history(repo_path, file_path):
    """
    提取文件内容和 Git 历史记录
    :param repo_path: Git 仓库路径
    :param file_path: 需要分析的文件路径
    :return: 文件内容和历史记录
    """
    # 打开仓库
    repo = Repo(repo_path)
    assert not repo.bare, "The repository is empty."

    # 提取文件内容
    with open(f"{repo_path}/{file_path}", "r",encoding="utf-8") as f:
        file_content = f.read()

    commits = run_git_command(repo_path, ["rev-list", "--all"]).splitlines()

    # 提取 Git 历史记录
    # commits = list(repo.iter_commits(paths=file_path))
    history = []
    for commit_hash in commits:
        # 获取提交的变更内容
        diff_output = run_git_command(repo_path, ["show", commit_hash])
        history.append({
            "commit_info": diff_output,
        })
    return file_content, history

class SecretAnalysisTool(BaseTool):
    """
    LangChain 工具，用于分析 Secrets
    """
    name : str= "SecretAnalysis"
    description: str = "Analyze file contents and git history for secrets, their purposes, risks, and mitigations."

    def _run(self, input: str) -> str:
        """
        分析文件内容和历史记录
        """
        print(input)
        data = json.loads(input)
        file_content = data.get("file_content", "")
        git_history = data.get("git_history", [])
        # 构建分析 Prompt
        prompt = PromptTemplate.from_template("""
        文件内容：
        {file_content}

        Git 历史记录：
        {git_history}

        请分析以下内容：
        1. 文件中是否存在敏感信息（Secrets）。
        2. 每个敏感信息的功能和用途（如所属平台和服务）。
        3. 泄露的潜在危害。
        4. 如何缓解泄露风险。
        """)
        input_text = prompt.format(
            file_content=file_content[:2000],  # 限制内容长度
            git_history=str(git_history[:5])  # 限制历史记录条数
        )

        # 调用大模型
        # llm = ChatOpenAI(model="gpt-4", temperature=0)
        return llm.predict(input_text)



# 定义工具
tools = [SecretAnalysisTool()]

# 初始化 Agent
llm = ChatOpenAI(
    temperature=0.95,
    model="glm-4-plus",
    openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description",verbose=True)

# 提取文件和历史记录
repo_path = r"E:\\download_space\\2024-03\\a958909457_Tavern_HF_Chathistory2"
file_path = "Dockerfile"
file_content, git_history = extract_file_and_git_history(repo_path, file_path)
input_data = json.dumps({
    "file_content": file_content,
    "git_history": git_history[:1]
})

# 调用 Agent 分析
result = agent.invoke(input_data)
print(result)







# prompt = ChatPromptTemplate(
#     messages=[
#         SystemMessagePromptTemplate.from_template(
#             "You are a nice chatbot having a conversation with a human."
#         ),
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template("{question}")
#     ]
# )
#
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# conversation = LLMChain(
#     llm=llm,
#     prompt=prompt,
#     verbose=True,
#     memory=memory
# )
# conversation.invoke({"question": "给我一个好养的孩子的名字"})



