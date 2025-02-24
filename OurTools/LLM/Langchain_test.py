from langchain.chains import SimpleSequentialChain
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI

# 初始化语言模型
llm = ChatOpenAI(
    temperature=0.95,
    model="glm-4-plus",
    openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

template = '''
        你的名字是小联。首先，当人问问题的时候,你都会在开头加上'你好，我是智能机器人'。
        其次，你是一位计算机网络安全专家，你需要检查用户给出的{question}，是不是属于api_token？
        如果其属于真实的公司的话，你需要生成出相应的Python代码并运行这段代码来验证这个API_token是否真实？
        如果这个API_token还在有效期，继续生产Python代码来探索这个API_token能带来什么样的泄漏？
    '''
prompt = PromptTemplate(
    template=template,
    input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
)
## 创建了一个chain

chain = LLMChain(llm=llm, prompt=prompt)
key = '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'
key2 = 'b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto'

question = f'帮我判断这个API_key:{key}属于哪个公司？'

res = chain.invoke(question, verbose=True)  # 运行

print(res['text'])

# print(res['text'])  # 打印结果
