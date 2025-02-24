from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
import requests
from langchain_community.chat_models import ChatOpenAI

# 设置OpenAI API Key
openai_api_key = "your_openai_api_key"

# 创建LLM实例
llm = ChatOpenAI(
    temperature=0.95,
    model="glm-4-plus",
    openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 定义验证API Key的Prompt模板
verify_prompt = PromptTemplate(
    input_variables=["api_key"],
    template="请验证以下API Key是否有效：{api_key}。如果有效，返回'有效'，否则返回'无效'。"
)

# 定义评估API Key危害的Prompt模板
evaluate_prompt = PromptTemplate(
    input_variables=["api_key"],
    template="请评估以下API Key的潜在危害：{api_key}。可能的危害包括仓库泄漏、用户Credit损失等。"
)

# 创建LLMChain实例
verify_chain = LLMChain(llm=llm, prompt=verify_prompt)
evaluate_chain = LLMChain(llm=llm, prompt=evaluate_prompt)

# 验证API Key的函数
def verify_api_key(api_key):
    response = verify_chain.run(api_key=api_key,verbose=True)
    print(response)
    return response.strip() == "有效"

# 评估API Key危害的函数
def evaluate_api_key(api_key):
    response = evaluate_chain.run(api_key=api_key,verbose=True)
    print(response)
    return response

# 示例API Key列表
api_keys = ["b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto"]

# 验证并评估每个API Key
for api_key in api_keys:
    is_valid = verify_api_key(api_key)
    if is_valid:
        print(f"API Key {api_key} 是有效的。")
        evaluation = evaluate_api_key(api_key)
        print(f"评估结果：{evaluation}")
    else:
        print(f"API Key {api_key} 是无效的。")