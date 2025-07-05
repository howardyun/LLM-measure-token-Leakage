import json

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from OurTools.utils import read_commitInfo
from concurrent.futures import ThreadPoolExecutor, as_completed


def LLM_analysis_file(question):
    # 初始化语言模型
    # 初始化语言模型
    llm = ChatOpenAI(
        temperature=0,
        # model="glm-4-air-250414",
        model="glm-4-plus",
        openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model_kwargs={
            "response_format": {"type": "json_object"}  # 确保输出JSON格式
        }
    )

    template = '''
            你的名字是小联。首先，当人问问题的时候,你都会在开头加上'你好，我是智能机器人'。
            其次，你是一位计算机网络安全专家，你需要检查用户的这个代码文件中是否含Secret泄露（APIToken，Credential,keys等），文件内容如下：{question}？
            0.需要注意的是下载文件ID，下载、广告展示链接等信息都不算，针对确切出现的密钥字符串（随机字符所组成的字符串），一些对于密钥的描述以及你可以忽略网页代码中的内容（eg.src），不用记作泄露
            1.在上述条件下，如果包含，帮我提取出所有的Secret泄露，并告诉我出现了几次(给出所有出现的字符串的上下文，打印出出那个完整的泄露)。如果不包含,直接退出.
            3.之后根据上下文判断，这个泄露属于哪个真实的平台或者公司的？（不需要展示上下文）
            4.之后根据上下文判断，这个Secret调用的具体是什么功能？（不需要展示上下文）
            
            请用以下JSON格式输出：
            {{
                "leaked_tokens": [
            {{
                "token": "具体的token值",
                "context": "出现上下文",
                "times": 出现次数,
                "platform": "平台名称",
                "function": "功能描述"
            }}
            ]
            }}

        '''
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
    )

    ## 创建了一个chain
    chain = LLMChain(llm=llm, prompt=prompt)
    res = chain.invoke(question, verbose=True)  # 运行
    # 结果处理
    result = json.loads(res['text'])
    return result


def LLM_analysis_commmit(question):

    # 初始化语言模型
    llm = ChatOpenAI(
        temperature=0,
        # model="glm-4-air-250414",
        model="glm-4-plus",
        openai_api_key="b39529e090954a2496d240535200e2d3.x93fykyPxeiRroto",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model_kwargs={
            "response_format": {"type": "json_object"}  # 确保输出JSON格式
        }
    )

    template = '''
            你的名字是小联。首先，当人问问题的时候,你都会在开头加上'你好，我是智能机器人'。
            其次，你是一位计算机网络安全专家，你需要检查用户的这个代码仓库中的commit历史信息中是否含Secret泄露（APIToken，Credential,keys等），文件内容如下：{question}？
            需要注意的是，这些commit可能有一个或者多个(用大量的_分割开了)
            0.需要注意的是下载文件ID，下载、广告展示链接等信息都不算，针对确切出现的密钥字符串（随机字符所组成的字符串），一些对于密钥的描述以及你可以忽略网页代码中的内容（eg.src），不用记作泄露
            1.在上述条件下，如果包含，帮我提取出所有的Secret泄露，并告诉我出现了几次(给出所有出现的字符串的上下文，打印出出那个完整的泄露)。如果不包含,直接退出.
            3.之后根据上下文判断，这个泄露属于哪个真实的平台或者公司的？（不需要展示上下文）
            4.之后根据上下文判断，这个Secret调用的具体是什么功能？（不需要展示上下文）
            
            请用以下JSON格式输出：
            {{
                "leaked_tokens": [
            {{
                "token": "具体的token值",
                "context": "出现上下文",
                "times": 出现次数,
                "platform": "平台名称",
                "function": "功能描述"
            }}
            ]
            }}

        '''
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
    )
    ## 创建了一个chain
    chain = LLMChain(llm=llm, prompt=prompt)

    res = chain.invoke(question, verbose=True)  # 运行
    result = json.loads(res['text'])
    return result



# 包装成线程池可调用的形式
def analyze_commit_wrapper(commit_lines):
    try:
        result = LLM_analysis_commmit(commit_lines)
        return result
    except Exception as e:
        return {"error": str(e), "input": commit_lines}

# 并发执行
def run_parallel_analysis(all_commits, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyze_commit_wrapper, c) for c in all_commits]
        for future in as_completed(futures):
            results.append(future.result())
    return results




if __name__ == "__main__":
    # content = read_file("F:/download_space/2022-03/Prathap_sql_quries/GPT_SECRET_KEY.json")
    # print(content)
    # content = read_commitInfo("F:/download_space/2022-03/Prathap_sql_quries")
    content = read_commitInfo(r"Z:\MiniDataset\ABAO77_TriVenture-BE")
    # abidlabs / speech - translation
    for c in content:
        print('#'*100)
        print(c)



    final_results  = run_parallel_analysis(content, max_workers=6)
    print(final_results)

