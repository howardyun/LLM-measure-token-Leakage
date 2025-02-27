from langchain.chains import SimpleSequentialChain
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
import json

def read_file(file_path):
    # 判断文件类型
    file_extension = file_path.split('.')[-1]

    content = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_extension == 'py':
                # 读取Python文件，将内容按行存储到数组
                content = f.readlines()

            elif file_extension == 'json':
                # 读取JSON文件，将内容解析为Python对象（通常是字典或列表）
                content = json.load(f)

            elif file_extension == 'env':
                # 读取.env文件，按行处理每一行并去除空行和注释
                for line in f.readlines():
                    line = line.strip()
                    if line and not line.startswith('#'):  # 忽略空行和注释
                        content.append(line)
            else:
                print(f"Unsupported file type: {file_extension}")

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    return ''.join(content)



def LLM_analysis(question):
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


if __name__ == "__main__":
    content = read_file("F:/download_space/2022-03/Ralfouzan_YAQEN/app.py")
    LLM_analysis(content)
