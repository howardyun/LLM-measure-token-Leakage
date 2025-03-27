from OurTools.LLM.Langchain_test import LLM_analysis_commmit
from OurTools.utils import read_commitInfo
import requests




# content = read_commitInfo("F:/download_space/2022-03/abidlabs_speech-translation")
content = read_commitInfo("F:/download_space/2022-03/abby711_FaceRestoration")



# 设置 API 地址和端口
url = "http://127.0.0.1:8000/query_commit/"

# 构造请求数据，传递给 API
data = {
    "question": content
}

# 发送 POST 请求
response = requests.post(url, json=data)



# 检查返回状态码和响应内容
if response.status_code == 200:
    print("API 返回成功：")
    res = response.json()
    print(res.keys())
    print(res['answer'])
    print(response.json())  # 输出 API 返回的 JSON 数据
else:
    print("请求失败，状态码：", response.status_code)





# # content = read_commitInfo("F:/download_space/2022-03/asgaardlab_CLIPxGamePhysics")
#
# LLM_analysis_commmit(content)








