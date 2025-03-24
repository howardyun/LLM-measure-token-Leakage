from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
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
            (1) 数据接收与预处理
                首先，请你检查收到的 commit 历史数据，并计算文本总量：
                - 如果数据为空，直接退出。
                - 如果commit数据由多个部分组成，使用 `_` 分隔解析多个 commit 片段。
                思考过程*：
                - Commit 可能包含多个部分，因此我需要正确解析并提取所有有效内容。
                ---
            (2) 确认 Secret 是否真实
                对于识别出的潜在 Secret，请你进一步验证其真实性：
                上下文分析：
                   - 如果 Secret 出现在变量赋值（如 `API_KEY = "sk_live_xxx"`），可能性增加。
                   - Secret中也有可能出现两个字符串对象拼接成一个密钥的情况
                思考过程：
                - 只基于字符串模式可能会产生误报，因此需要结合上下文信息。
                ---
            (3) 判断 Secret 归属的平台
                对于确认的 Secret，请你根据知识库或者根据网络信息推测它的来源：
                - 根据前缀模式（例如 `ghp_` -> GitHub, `hf_` -> Hugging Face）。
                - 根据上下文信息（例如 `AWS_SECRET_ACCESS_KEY` 可能用于 AWS）。
                - 根据使用方式（例如 `curl -H 'Authorization: Bearer xxx'` 表明它是 API 访问凭证）。
                思考过程：
                - 不同平台的 Secret 具有不同的格式和用途。
                - 结合上下文和调用方式可以提高判断的准确性。
                ---
            (4) 推测 Secret 的用途
                最后，请你分析 Secret 可能的用途：
                - 身份验证：如果 Secret 出现在 `Authorization` 头部，它可能用于 OAuth 认证。
                - 数据库访问：如果 Secret 结合 `db_uri` 变量，它可能是数据库连接密钥。
                思考过程：
                - API Key 通常用于身份验证或云端服务。
                - 结合调用方式可以更准确地推测 Secret 的用途。
                ---
            (5)最终结论
                - 回答检测到 X 个 Secret，其中 Y 个属于已知平台，Z 个用途未确定。
                - 这些 Secret 可能用于例如：身份验证/数据库访问/云 API 调用/支付 API等用途。
                ---
        '''
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
    )
    ## 创建了一个chain

    chain = LLMChain(llm=llm, prompt=prompt)



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
            其次，你是一位计算机网络安全专家，你需要检查用户的这个代码仓库中的commit历史信息中包不包含APitoken，或者Secret泄露，
            文件内容：{question}？
            告诉你接收到了多少文本？判断是否是Commit信息？
            需要注意的是，如果是commit信息的和可能有一个或者多个(用大量的_分割开了)？
            根据文本判断是否出现了Secret泄露？如果不包含,直接退出.
            如果包含，帮我提取出所有的Secret泄露，并告诉我出现了几次（密钥中可能会有两个字符串拼接的情况）。
            之后根据上下文判断，这个泄露属于哪个真实的平台或者公司的？（不需要展示上下文）
            之后根据上下文判断，这个Secret调用的具体是什么功能？（不需要展示上下文）
            '''
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]  # 这个question就是用户输入的内容,这行代码不可缺少
    )
    ## 创建了一个chain

    chain = LLMChain(llm=llm, prompt=prompt)
    question_str = ("-"*100+'\n').join(question)

    response_schemas = [
        ResponseSchema(name="leaked_token", description="泄露的 API Token"),
        ResponseSchema(name="Times", description="泄露的 Secret "),
        ResponseSchema(name="platform", description="可能的服务平台"),
        ResponseSchema(name="function", description="Token 的用途"),

    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    res = chain.invoke(question_str, verbose=True)  # 运行
    print(res['text'])
    parsed_output = output_parser.parse(res['text'])
    print(parsed_output)  # 打印结果
if __name__ == "__main__":
    # content = read_file("F:/download_space/2022-03/Ralfouzan_YAQEN/app.py")
    content = read_commitInfo("F:/download_space/2022-03/Prathap_sql_quries")
    LLM_analysis_commmit(content)
