from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

from OurTools.utils import read_commitInfo


def LLM_analysis_file(question):
    # 初始化语言模型
    llm = ChatOpenAI(
        temperature=0.95,
        model="glm-4-plus",
        openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )

    template = '''
            你的名字是小联。首先，当人问问题的时候,你都会在开头加上'你好，我是智能机器人'。
            其次，你是一位计算机网络安全专家，你需要检查用户的这个文件中包不包含APitoken，或者Secret泄露，文件内容：{question}？
            如果包含，帮我提取出这个API泄露。
            之后根据上下文判断，这个APItoken泄露属于哪个真实的平台或者公司的？
            之后根据上下文判断，这个APItoken调用的具体是什么功能？
            
        '''
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
    )
    ## 创建了一个chain

    chain = LLMChain(llm=llm, prompt=prompt)
    key = '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'
    key2 = 'b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto'


    res = chain.invoke(question, verbose=True)  # 运行

    print(res['text'])  # 打印结果


def LLM_analysis_commmit(question):
    # 初始化语言模型
    llm = ChatOpenAI(
        temperature=0.95,
        model="glm-4-plus",
        openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )

    template = '''
            你的名字是小联。首先，当人问问题的时候,你都会在开头加上'你好，我是智能机器人'。
            其次，你是一位计算机网络安全专家，你需要检查用户的这个代码仓库中的信息包不包含APitoken，或者Secret泄露，文件内容：{question}？
            如果包含，帮我提取出这个API泄露。如果不包含,直接退出.
            之后根据上下文判断，这个APItoken泄露属于哪个真实的平台或者公司的？
            之后根据上下文判断，这个APItoken调用的具体是什么功能？

        '''
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
    )
    ## 创建了一个chain

    chain = LLMChain(llm=llm, prompt=prompt)
    key = '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'
    key2 = 'b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto'

    res = chain.invoke(question, verbose=True)  # 运行

    print(res['text'])  # 打印结果
if __name__ == "__main__":
    # content = read_file("F:/download_space/2022-03/Ralfouzan_YAQEN/app.py")
    content = read_commitInfo("F:/download_space/2022-03/Prathap_sql_quries")
    LLM_analysis_commmit(content)
