from fastapi import FastAPI
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import time
from typing import List
from pydantic import BaseModel
app = FastAPI()


# 全局缓存
llm = None

# Lazy Load
def get_llm():
    global llm
    if llm is None:
        print('create')
        llm = ChatOpenAI(
            temperature=0.95,
            model="glm-4-plus",
            openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
        )
    return llm


# template for commit history
template_commit = '''
           你的名字是小联。首先，当人问问题的时候,你都会在开头加上'你好，我是智能机器人'。
           其次，你是一位计算机网络安全专家，你需要检查用户的这个代码仓库中的commit历史信息中是否含Secret泄露（APIToken，Credential,keys等），文件内容如下：{question}？
           需要注意的是，这些commit可能有一个或者多个(用大量的_分割开了)
           0.需要注意的是下载文件ID，下载链接等信息都不算，不用记作泄露
           1.在上述条件下，如果包含，帮我提取出所有的Secret泄露，并告诉我出现了几次(给出所有出现的字符串的上下文，打印出出那个完整的泄露)。如果不包含,直接退出.
           3.之后根据上下文判断，这个泄露属于哪个真实的平台或者公司的？（不需要展示上下文）
           4.之后根据上下文判断，这个Secret调用的具体是什么功能？（不需要展示上下文）

       '''

prompt_commit = PromptTemplate(
    template=template_commit,
    input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
)

class Query(BaseModel):
    question: List[str]  # 接收一个字符串列表

@app.post("/query_commit/")
def query(query: Query):
    start_time = time.time()  # 记录函数开始时间
    # 初始化模型
    llm = get_llm()
    llm_init_time = time.time()  # 记录 llm 初始化的时间
    print(f"LLM 初始化耗时: {llm_init_time - start_time} 秒")

    chain = LLMChain(llm=llm, prompt=prompt_commit)
    chain_init_time = time.time()  # 记录 chain 初始化的时间
    print(f"LLMChain 初始化耗时: {chain_init_time - llm_init_time} 秒")

    question_str = ("-" * 100 + '\n').join(query.question)

    # 运行链并计算推理时间
    inference_start_time = time.time()  # 记录推理开始时间
    res = chain.invoke(question_str, verbose=True)  # 运行
    inference_end_time = time.time()  # 记录推理结束时间
    print(f"推理耗时: {inference_end_time - inference_start_time} 秒")

    print(res['text'])
    return {"answer": res['text']}
