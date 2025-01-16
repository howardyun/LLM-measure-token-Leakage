import csv
import os
import time

import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
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
    headers = {
        'Authorization': 'Bearer ' + openai_api,
    }

    response = requests.get('https://api.openai.com/v1/me', headers=headers)
    print(openai_api, response.text)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + openai_api,
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

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
    print(response.text)


def test_huggingface_api(huggingface_api):
    headers = {
        'Authorization': 'Bearer ' + huggingface_api,
    }

    response = requests.get('https://huggingface.co/api/whoami-v2', headers=headers)
    print(huggingface_api, response.text)


def groq_api(groq_api_key):
    headers = {
        'Authorization': 'Bearer ' + groq_api_key,
    }

    response = requests.get('https://api.groq.com/openai/v1/models', headers=headers)
    print(groq_api_key, response.text)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + groq_api_key,
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

    response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=json_data)
    print(groq_api_key, response.text)


def aws_api():
    ACCESS_KEY = "AKIAZPNYOGSLLAIPOMM2"
    SECRET_KEY = "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"
    REGION_NAME = "eu-west-2"
    BUCKET_NAME = "ogtl-analytics"
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION_NAME,
    )
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    for item in response.get('Contents', []):
        print(item['Key'])


def mongdb_test(uri):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 设置超时时间为5000毫秒
        # 尝试一个简单的操作来测试连接
        # 这将引发异常，如果没有连接到服务器
        client.admin.command('ping')
        print("连接成功")
    except ConnectionFailure:
        print("连接失败")
    # 关闭连接
    client.close()


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

