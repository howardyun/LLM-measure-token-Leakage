import csv
import os
import time

import requests
from pymongo import MongoClient
import boto3
from pymongo.errors import ConnectionFailure, PyMongoError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'



def verify_cohere_api_key(api_key: str) -> bool:
    """
    检查 Cohere API 密钥是否有效
    :param api_key: Cohere API 密钥
    :return: 如果 API 密钥有效，返回 True，否则返回 False
    """
    # 设置请求头，包含 API 密钥
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 请求 URL，用于检查密钥有效性（这里请求模型列表作为测试）
    url = "https://api.cohere.ai/models"

    # 发起请求
    response = requests.get(url, headers=headers)

    # 检查响应状态
    if response.status_code == 200:
        print("API 密钥有效！")
        return True
    else:
        print("API 密钥无效或请求失败。状态码:", response.status_code)
        return False


def verify_github_token(token):
    """
    验证 GitHub Personal Access Token 是否有效。

    参数:
    token (str): GitHub Personal Access Token。

    返回:
    None: 直接打印验证结果。
    """
    # GitHub API URL for the authenticated user
    url = "https://api.github.com/user"

    # 设置请求头，包括 Authorization
    headers = {
        "Authorization": f"token {token}"
    }

    # 发起请求
    response = requests.get(url, headers=headers)

    # 检查响应状态并输出中文信息
    if response.status_code == 200:
        print("Token 是有效的！")
        user_data = response.json()
        print(f"已验证用户: {user_data['login']}")
    elif response.status_code == 401:
        print("Token 无效。")
    else:
        print(f"请求失败，状态码: {response.status_code}")

def test_openai(openai_api):
    """
    测试 OpenAI API 是否有效，并测试聊天补全功能。

    参数:
    openai_api (str): OpenAI API 密钥。

    返回:
    None: 直接打印测试结果。
    """

    # 测试 OpenAI API 密钥是否有效
    def test_api_key():
        headers = {
            'Authorization': f'Bearer {openai_api}',
        }
        try:
            response = requests.get('https://api.openai.com/v1/me', headers=headers)
            if response.status_code == 200:
                print("OpenAI API 密钥有效！")
                print(f"API 响应: {response.text}")
            else:
                print(f"OpenAI API 密钥无效，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"测试 API 密钥时发生错误: {e}")

    # 测试聊天补全功能
    def test_chat_completion():
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_api}',
        }
        json_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user',
                    'content': 'Say this is a test!',
                },
            ],
        }
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
            if response.status_code == 200:
                print("聊天补全功能测试成功！")
                print(f"API 响应: {response.text}")
            else:
                print(f"聊天补全功能测试失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"测试聊天补全功能时发生错误: {e}")

    # 执行测试
    print("开始测试 OpenAI API 密钥...")
    test_api_key()

    print("\n开始测试聊天补全功能...")
    test_chat_completion()


def test_huggingface_api(huggingface_api):
    headers = {
        'Authorization': 'Bearer ' + huggingface_api,
    }

    response = requests.get('https://huggingface.co/api/whoami-v2', headers=headers)
    if 'error' in response.json():
        print("api is error")
        return
    print("name: " + response.json()["name"] + " email: " + response.json()["email"] + " token permissions: " +
          response.json()["auth"]["accessToken"]["role"])
    response2 = requests.get(f"https://huggingface.co/api/models?author={response.json()['name']}", headers=headers)
    if response2.status_code == 200:
        models = response2.json()
        print("models:")
        for model in models:
            print(model)
    else:
        print("Failed to fetch repositories")

    response3 = requests.get(f"https://huggingface.co/api/datasets?author={response.json()['name']}", headers=headers)
    if response3.status_code == 200:
        datasets = response3.json()
        print("datasets:")
        for dataset in datasets:
            print(datasets)
    else:
        print("Failed to fetch datasets")

    response3 = requests.get(f"https://huggingface.co/api/spaces?author={response.json()['name']}", headers=headers)
    if response3.status_code == 200:
        spaces = response3.json()
        print("spaces:")
        for space in spaces:
            print(space)
    else:
        print("Failed to fetch spaces")


def groq_api(groq_api_key):
    """
    测试 Groq API 是否有效，并测试聊天补全功能。

    参数:
    groq_api_key (str): Groq API 密钥。

    返回:
    None: 直接打印测试结果。
    """
    # 测试 Groq API 密钥是否有效
    def test_api_key():
        headers = {
            'Authorization': f'Bearer {groq_api_key}',
        }
        try:
            response = requests.get('https://api.groq.com/openai/v1/models', headers=headers)
            if response.status_code == 200:
                print("Groq API 密钥有效！")
                print(f"API 响应: {response.text}")
            else:
                print(f"Groq API 密钥无效，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"测试 API 密钥时发生错误: {e}")

    # 测试聊天补全功能
    def test_chat_completion():
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {groq_api_key}',
        }
        json_data = {
            'model': 'llama3-8b-8192',
            'messages': [
                {
                    'role': 'user',
                    'content': 'Explain the importance of fast language models',
                },
            ],
        }
        try:
            response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=json_data)
            if response.status_code == 200:
                print("聊天补全功能测试成功！")
                print(f"API 响应: {response.text}")
            else:
                print(f"聊天补全功能测试失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"测试聊天补全功能时发生错误: {e}")

    # 执行测试
    print("开始测试 Groq API 密钥...")
    test_api_key()

    print("\n开始测试聊天补全功能...")
    test_chat_completion()


def aws_api(ACCESS_KEY,SECRET_KEY,REGION_NAME,BUCKET_NAME):
    """
    列出 AWS S3 存储桶中的所有对象。

    返回:
    None: 直接打印存储桶中的对象键。
    """
    # AWS 凭证和配置

    try:
        # 创建 S3 客户端
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )

        # 列出存储桶中的对象
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

        # 检查是否有内容
        if 'Contents' in response:
            print(f"存储桶 '{BUCKET_NAME}' 中的对象列表：")
            for item in response['Contents']:
                print(item['Key'])
        else:
            print(f"存储桶 '{BUCKET_NAME}' 为空。")

    except NoCredentialsError:
        print("错误：未提供 AWS 凭证。")
    except PartialCredentialsError:
        print("错误：凭证不完整。")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"错误：存储桶 '{BUCKET_NAME}' 不存在。")
        else:
            print(f"AWS 客户端错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


def mongodb_test(uri):
    """
    测试 MongoDB 连接是否成功。

    参数:
    uri (str): MongoDB 连接字符串。

    返回:
    None: 直接打印连接测试结果。
    """
    client = None
    try:
        # 创建 MongoDB 客户端，设置超时时间为5000毫秒
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # 尝试执行一个简单的操作（如 ping）来测试连接
        client.admin.command('ping')
        print("MongoDB 连接成功！")

    except ConnectionFailure:
        # 捕获连接失败异常
        print("MongoDB 连接失败：无法连接到服务器。")
    except PyMongoError as e:
        # 捕获其他 PyMongo 异常
        print(f"MongoDB 连接失败：发生错误 - {e}")
    finally:
        # 确保关闭客户端连接
        if client:
            client.close()
            print("MongoDB 连接已关闭。")

def test_anthropic(anthropic_api):
    """
    测试 Anthropic API 是否有效，并发送一条消息。

    参数:
    anthropic_api (str): Anthropic API 密钥。

    返回:
    None: 直接打印 API 响应结果。
    """
    # 设置请求头
    headers = {
        'x-api-key': anthropic_api,  
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    }

    # 设置请求体
    json_data = {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 1024,
        'messages': [
            {
                'role': 'user',
                'content': 'Hello, world',
            },
        ],
    }

    try:
        # 发送 POST 请求
        response = requests.post('https://api.anthropic.com/v1/messages', headers=headers, json=json_data)

        # 检查响应状态码
        if response.status_code == 200:
            print("Anthropic API 请求成功！")
            print(f"API 响应: {response.text}")
        else:
            print(f"Anthropic API 请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")

    except requests.exceptions.RequestException as e:
        # 捕获请求过程中可能出现的异常
        print(f"请求过程中发生错误: {e}")

def test_deepseek(deepseek_api):
    """
    测试 Deepseek API 是否有效，并获取用户余额信息。

    参数:
    deepseek_api (str): Deepseek API 密钥。

    返回:
    None: 直接打印 API 响应结果。
    """
    # 设置请求头
    headers = {
        'Accept': 'application/json',
        'Authorization': "Bearer "+deepseek_api, 
    }

    try:
        # 发送 GET 请求
        response = requests.get('https://api.deepseek.com/user/balance', headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("Deepseek API 请求成功！")
            print(f"用户余额信息: {response.text}")
        else:
            print(f"Deepseek API 请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")

    except requests.exceptions.RequestException as e:
        # 捕获请求过程中可能出现的异常
        print(f"请求过程中发生错误: {e}")

def test_Gemini(Gemini_api):
    """
    测试 Gemini API 是否有效，并获取模型信息。

    参数:
    Gemini_api (str): Gemini API 密钥。

    返回:
    None: 直接打印 API 响应结果。
    """
    # 设置请求参数
    params = {
        'key': Gemini_api,
    }

    try:
        # 发送 GET 请求
        response = requests.get('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash',
                                params=params)

        # 检查响应状态码
        if response.status_code == 200:
            print("Gemini API 请求成功！")
            print(f"模型信息: {response.text}")
        else:
            print(f"Gemini API 请求失败，状态码: {response.status_code}")
            print("api is not valid")

    except requests.exceptions.RequestException as e:
        # 捕获请求过程中可能出现的异常
        print(f"请求过程中发生错误: {e}")

# if __name__ == '__main__':
    # return 1
    # with open(r"./output_with_raw_array.csv", 'r', encoding='utf-8-sig') as f:
    #     reader = csv.reader(f)
    #     for _ in range(48):
    #         next(reader)
    #     j = 1
    #     for row in reader:
    #         api = eval(row[2])
    #         j = j + 1
    #         k = set()
    #         for i in api:
    #             k.add(i)
    #         for m in k:
    #             if m.startswith('hf_'):
    #                 huggingface_api = m
    #                 test_huggingface_api(huggingface_api)
    #             if m.startswith('sk-'):
    #                 test_openai(m)
    #             if m.startswith('gsk-'):
    #                 groq_api(m)
    #
    #         if j == 51:
    #             exit(0)
    #         if j % 10 == 0:
    #             time.sleep(10)

