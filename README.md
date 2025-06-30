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
