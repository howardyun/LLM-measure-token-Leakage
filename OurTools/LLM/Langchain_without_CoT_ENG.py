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
        model="glm-4-plus",
        openai_api_key="",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model_kwargs={
            "response_format": {"type": "json_object"}  # 确保输出JSON格式
        }
    )

    template = '''
            You are a computer network security expert. You are required to inspect the following code file provided by the user to determine whether it contains any secret leaks (such as API tokens, credentials, keys, etc.). The content of the file is as follows:
            {question}

            Please output your findings in the following JSON format:
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
        model="glm-4-plus",
        openai_api_key="",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model_kwargs={
            "response_format": {"type": "json_object"}  # 确保输出JSON格式
        }
    )

    template = '''
        You are a computer network security expert. You are required to inspect the following code file provided by the user to determine whether it contains any secret leaks (such as API tokens, credentials, keys, etc.). The content of the file is as follows:
            {question}

            Please output your findings in the following JSON format:
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
    print(res['text'])
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
    content = read_commitInfo(r"")
    # abidlabs / speech - translation
    for c in content:
        print('#' * 100)
        print(c)

    final_results = run_parallel_analysis(content, max_workers=6)
    print(final_results)

