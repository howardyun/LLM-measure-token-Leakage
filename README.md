# SecretReviewr

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://travis-ci.org/username/repo.svg?branch=master)](https://travis-ci.org/username/repo)

本项目主要用于检测Hugging Face Space代码仓库以及ModelScope Space中的密钥泄露。



## 功能特性

### Step1.数据收集
使用[DataCollection](DataCollection)文件中的文件在本地收集所有的Huggingface以及ModelScope的代码。 
- 对于Huggingface来说，您先需要通过运行文件[getSpaceID.py](DataCollection%2FHF%2FgetSpaceID.py)获得所有的在HF Space中公开的代码仓库，
在获得每个月创建的Space仓库列表之后，您可以使用文件[DownloadFromFile_space.py](DataCollection%2FHF%2FDownloadFromFile_space.py)对所有的Space代码进行下载。

- 对于Huggingface来说，您先需要通过运行文件[CollectSpaceList.py](DataCollection%2FModelScope%2FCollectSpaceList.py)获得所有的在ModelScope中公开的Space代码仓库，
在获得所有列表之后（需要注意的是，由于ModelScope不提供相关API，在这里我们使用的是爬虫方法进行的实现），
- 您可以使用文件[DownloadFromFile_space_modelscope.py](DataCollection%2FModelScope%2FDownloadFromFile_space_modelscope.py)对所有的Space代码进行下载。


考虑到下载数据过大，我们分别在两个平台的数据集中提取出了1000个代码仓库便于您进行测试:

Hugging Face:
https://zenodo.org/records/15752077

Model Scope:
https://zenodo.org/records/15752627


- 功能2
- 功能3

## Dataset


## 快速开始

```bash

```

## [mock](mock)文件夹说明

`mock` 文件夹用于模拟不同平台和服务的密钥泄露攻击，帮助用户直观了解密钥泄露后可能造成的安全风险。每个子文件夹和脚本都对应一种常见的密钥类型和攻击方式。

### 结构说明

- `AI Model Provider/`  
  包含针对主流 AI 服务商（如 OpenAI、Replicate、Groq）的密钥攻击模拟脚本：
  - `mock_openai.py`：模拟 OpenAI API Key 泄露后的攻击流程，包括验证密钥有效性、文件操作等。
  - `mock_replicate.py`：模拟 Replicate API Key 泄露后的攻击流程，包括模型推理等。
  - `mock_groq.py`：模拟 Groq API Key 泄露后的攻击流程，包括模型调用等。

- `Storage Service/`  
  包含针对云数据库服务的密钥攻击模拟脚本：
  - `mock_mongdb.py`：模拟 MongoDB 连接密钥泄露后的攻击流程，包括数据库连接、数据遍历等。

- `Code Hosting Platforms/`  
  包含针对代码托管平台（如 Hugging Face、GitHub）的密钥攻击模拟脚本：
  - `mock_hf.py`：模拟 Hugging Face Token 泄露后的攻击流程，包括账户信息、模型、数据集、空间等资源的访问。
  - `mock_github.py`：模拟 GitHub Token 泄露后的攻击流程，包括用户信息、仓库、Gist 等资源的访问。
  - `icse2026.jsonl`：用于部分脚本（如 OpenAI 文件上传）测试的数据文件。

- `key.txt`  
  示例密钥文件，包含 Hugging Face、OpenAI、MongoDB 等服务的模拟密钥，供各脚本测试使用。

### 使用方法

1. 进入 `mock` 目录，根据需要选择对应的脚本。
2. 运行脚本时，将 `key.xtx` 中的密钥作为参数传入。例如：
   ```bash
   python mock_openai.py <OpenAI_API_Key>
   python mock_groq.py <API_Key>
   python mock_nvidia.py <API_Key>
   python mock_replicate <API_Key>
   python mock_mongdb.py <MongoDB_Connection_String>
   python mock_hf.py <HuggingFace_Token>
   python mock_github.py <GitHub_Token>
   ```
3. 脚本会模拟攻击者利用泄露密钥进行的操作，并输出相关信息，帮助理解风险。


