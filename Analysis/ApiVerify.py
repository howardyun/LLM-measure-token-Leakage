import csv
import os
import time
import psycopg2

import requests
from pymongo import MongoClient
import boto3
from pymongo.errors import ConnectionFailure, PyMongoError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'



def verify_cohere_api_key(api_key: str,files: dict):
    """
    检查 Cohere API 密钥是否有效
    :param api_key: Cohere API 密钥
    :return: 如果 API 密钥有效，返回 True,否则返回 False
    """
    # 设置请求头，包含 API 密钥
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    files["organization"]="cohere"

    # 请求 URL，用于检查密钥有效性（这里请求模型列表作为测试）
    url = "https://api.cohere.ai/models"

    # 发起请求
    response = requests.get(url, headers=headers)

    # 检查响应状态
    if response.status_code == 200:
        files["valid"]=1
        files["available"]=1
    else:
        files["valid"]=0
        files["available"]=0


def verify_github_token(token,files):
    """
    验证 GitHub Personal Access Token 是否有效。

    参数:
    token (str): GitHub Personal Access Token。

    返回:
    None: 直接打印验证结果。
    """
    # GitHub API URL for the authenticated user
    url = "https://api.github.com/user"

    files["organization"]="github"

    # 设置请求头，包括 Authorization
    headers = {
        "Authorization": f"token {token}"
    }

    # 发起请求
    response = requests.get(url, headers=headers)

    # 检查响应状态并输出中文信息
    if response.status_code == 200:
        files["valid"]=1
        files["available"]=1
        files["userinfo"] = response.json()
        
    else:
        files["valid"]=0
        files["available"]=0
    
        

def test_openai(openai_api,files):
    """
    测试 OpenAI API 是否有效，并测试聊天补全功能。

    参数:
    openai_api (str): OpenAI API 密钥。

    返回:
    None: 直接打印测试结果。
    """

    # 测试 OpenAI API 密钥是否有效
    def test_api_key():
        files["organization"]="openai"
        headers = {
            'Authorization': f'Bearer {openai_api}',
        }
        try:
            response = requests.get('https://api.openai.com/v1/me', headers=headers)
            if response.status_code == 200:
                files["valid"]=1
                files["userinfo"]=response.json()

            elif response.status_code == 429:
                print("Rate limit reached for requests")
                time.sleep(10)
                response = requests.get('https://api.openai.com/v1/me', headers=headers)
                if response.status_code == 200:
                    files["valid"]=1
                    files["userinfo"]=response.json()
                else:
                    files["valid"]=0
            else:
                files["valid"]=0
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
                files["available"]=1
            else:
                files["available"]=0
                files["balance"]=0
        except requests.exceptions.RequestException as e:
            print(f"测试聊天补全功能时发生错误: {e}")

    # 执行测试
    print("开始测试 OpenAI API 密钥...")
    test_api_key()

    print("\n开始测试聊天补全功能...")
    test_chat_completion()


def test_huggingface_api(huggingface_api,files):
    headers = {
        'Authorization': 'Bearer ' + huggingface_api,
    }
    files["organization"]="huggingface"

    response = requests.get('https://huggingface.co/api/whoami-v2', headers=headers)
    if 'error' in response.json():
        files["valid"]=0
        files["available"]=0
        files["balance"]=None
        files["context"]=None
        files["permissions"]=None
        files["userinfo"]=None
        return
    files["valid"]=1
    files["available"]=1
    files["balance"]=None
    files["userinfo"]="name: " + response.json().get("name", "N/A") + " email: " + response.json().get("email", "N/A")
    files["permissions"]=response.json()["auth"]["accessToken"]["role"]
    files["context"]=None
    response2 = requests.get(f"https://huggingface.co/api/models?author={response.json()['name']}", headers=headers)
    if response2.status_code == 200:
        models = response2.json()
        files["models"]=models
    else:
        files["models"]=None

    response3 = requests.get(f"https://huggingface.co/api/datasets?author={response.json()['name']}", headers=headers)
    if response3.status_code == 200:
        datasets = response3.json()
        files["datasets"]=datasets
    else:
        files["datasets"]=None

    response3 = requests.get(f"https://huggingface.co/api/spaces?author={response.json()['name']}", headers=headers)
    if response3.status_code == 200:
        spaces = response3.json()
        files["spaces"]=spaces
    else:
        files["spaces"]=None


def groq_api(groq_api_key,files):
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
                files["valid"]=1
            else:
                files["valid"]=0
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
                files["available"]=1
            else:
                files["available"]=0
        except requests.exceptions.RequestException as e:
            print(f"测试聊天补全功能时发生错误: {e}")

    # 执行测试
    print("开始测试 Groq API 密钥...")
    files["organization"]="groq"
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


def mongodb_test(uri,files):
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
        files["organization"]="mongodb"

        # 尝试执行一个简单的操作（如 ping）来测试连接
        client.admin.command('ping')
        print("MongoDB 连接成功！")
        files["valid"]=1
        files["available"]=1
        # 查看已有集合
        database_names = client.list_database_names()
        for collection in database_names:
            files["context"]=files["context"]+' '+collection

    except ConnectionFailure:
        # 捕获连接失败异常
        files["valid"]=0
        files["available"]=0
        print("MongoDB 连接失败：无法连接到服务器。")
    except PyMongoError as e:
        # 捕获其他 PyMongo 异常
        files["valid"]=0
        files["available"]=0
        print(f"MongoDB 连接失败：发生错误 - {e}")
    finally:
        # 确保关闭客户端连接
        if client:
            client.close()
            print("MongoDB 连接已关闭。")

def postgresql_test(conn_string,files):
    """
    测试 PostgreSQL 连接是否成功。

    参数:
    conn_string (str): PostgreSQL 连接字符串。

    返回:
    None: 直接打印连接测试结果。
    """
    conn = None
    try:
        # 创建 psycopg2 连接
        conn = psycopg2.connect(conn_string)
        files["organization"]="postgresql"
        
        # 尝试执行一个简单的查询来测试连接
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        files["valid"]=1
        files["available"]=1
        files["context"]=result
        cursor.close()
        print("PostgreSQL 连接成功！")
        print(result)

    except psycopg2.OperationalError as e:
        # 捕获连接失败异常
        files["valid"]=0
        files["available"]=0
        print(f"PostgreSQL 连接失败：无法连接到服务器 - {e}")
    except psycopg2.Error as e:
        # 捕获其他 psycopg2 异常
        files["valid"]=0
        files["available"]=0
        print(f"PostgreSQL 连接失败：发生错误 - {e}")
    finally:
        # 确保关闭连接
        if conn:
            conn.close()
            print("PostgreSQL 连接已关闭。")




def test_anthropic(anthropic_api,files):
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
    files["organization"]="Anthropic"

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
            files["valid"]=1
            files["available"]=1
        else:
            files["valid"]=0
            files["available"]=0

    except requests.exceptions.RequestException as e:
        # 捕获请求过程中可能出现的异常
        print(f"请求过程中发生错误: {e}")

def test_deepseek(deepseek_api,files):
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
    files["organization"]="deepseek"

    try:
        # 发送 GET 请求
        response = requests.get('https://api.deepseek.com/user/balance', headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            files["valid"]=1
            if response.json()["is_available"]==False:
                files["available"]=0
                files["balance"]=0
            else:
                files["available"]=1
                files["balance"]=response.json()["balance_infos"]["total_balance"]            
        else:
            files["valid"]=0
            files["available"]=0

    except requests.exceptions.RequestException as e:
        # 捕获请求过程中可能出现的异常
        print(f"请求过程中发生错误: {e}")

def test_Gemini(Gemini_api,files):
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
    files["organization"]="Gemini"

    try:
        # 发送 GET 请求
        response = requests.get('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash',
                                params=params)

        # 检查响应状态码
        if response.status_code == 200:
            files["valid"]=1
            files["available"]=1
        else:
            files["valid"]=0
            files["available"]=0

    except requests.exceptions.RequestException as e:
        # 捕获请求过程中可能出现的异常
        print(f"请求过程中发生错误: {e}")
    
def test_nvidia(api,files):
        files["organization"]="nvidia"
        headers = {
            'accept': 'application/json',
            'authorization': 'Bearer '+api,
            'content-type': 'application/json',
        }

        json_data = {
            'model': '01-ai/yi-large',
            'messages': [
                {
                    'content': 'I am going to Paris, what should I see?',
                    'role': 'user',
                },
            ],
            'temperature': 0.2,
            'top_p': 0.7,
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'max_tokens': 1024,
            'stream': False,
            'stop': [
                'string',
            ],
        }

        response = requests.post('https://integrate.api.nvidia.com/v1/chat/completions', headers=headers, json=json_data)
        if response.status_code == 200:
            files["valid"]=1
            files["available"]=1
            files["balance"]=None
            files["context"]=None
            files["permissions"]=None
            files["userinfo"]=None
        else:
            files["valid"]=0
            files["available"]=0
            files["balance"]=None
            files["context"]=None
            files["permissions"]=None
            files["userinfo"]=None

def test_replicate(api,files):
    headers = {
    'Authorization': 'Bearer ' + api,
        }
    files["organization"]="replicate"

    response = requests.get('https://api.replicate.com/v1/account', headers=headers)
    if response.status_code == 200:
        files["valid"]=1
        files["userinfo"]=response.json()
        headers = {
        'Authorization': 'Bearer ' + os.getenv('REPLICATE_API_TOKEN', ''),
        'Content-Type': 'application/json',
        'Prefer': 'wait',
            }

        json_data = {
            'input': {
                'prompt': 'an illustration of a dog jumping',
            },
        }

        response = requests.post(
            'https://api.replicate.com/v1/models/black-forest-labs/flux-pro/predictions',
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            files["available"]=1
    else:
        files["valid"]=0
        files["available"]=0

if __name__ == '__main__':
    # 指定文件夹的路径
    folder_path = './result/'
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    with open("./result/2024-12_scan_results.csv","a",encoding='utf-8-sig',newline='') as file:
            fields=["Repository","api","organization","valid","available","userinfo","permissions","balance","models","datasets","spaces","context"]
            writer=csv.DictWriter(file,fieldnames=fields)
             # 如果文件是新创建的，则写入表头
            if not file.tell():  # 如果文件指针在文件开始处，则认为是新文件
                writer.writeheader()
            with open(r"./2024-12_scan_results.csv", 'r', encoding='utf-8-sig') as f: 
                reader = csv.reader(f)  
                next(reader)
                j=0
                
                for row in reader:
                    api = eval(row[2])
                    if api[0]==None:
                        continue
                    for m in api:
                        files={'Repository':row[0],"api":m}          
                        if m.startswith('hf_'):                           
                            test_huggingface_api(m,files)
                        elif m.startswith('sk-'):
                            test_deepseek(m,files)
                            if files["valid"]==1:
                                break
                            test_openai(m,files)
                        elif m.startswith('gsk_'):
                            groq_api(m,files)
                        elif m.startswith('nvapi'):
                            test_nvidia(m,files)
                        elif m.startswith("ghp_") or m.startswith("github_"):
                            verify_github_token(m,files)
                        elif m.startswith("r8"):
                            test_replicate(m,files)
                        elif m.startswith("mongodb"):
                            mongodb_test(m,files)
                        elif m.startswith('postgre'):
                            postgresql_test(m,files)
                        else:
                            test_Gemini(m,files)
                            if files["valid"]==1:
                                break
                            verify_cohere_api_key(m,files)
                            if files["valid"]==1:
                                break
                            test_anthropic(m,files)
                            if files["valid"]==1:
                                  break
                            files["organization"]="unknow"
                        if j==100:
                            time.sleep(10)
                            j=0
                        j=j+1
                        writer.writerow(files)

         

