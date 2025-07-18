# SecretReviewr

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Build Status](https://travis-ci.org/username/repo.svg?branch=master)](https://travis-ci.org/username/repo)

This project is primarily designed to detect secret key leaks in code repositories from Hugging Face Spaces and ModelScope Spaces.

## Features

### Step 1. Data Collection  
Use the scripts in the [DataCollection](DataCollection) directory to locally collect all Hugging Face and ModelScope code repositories.  
- For Hugging Face: First, run [getSpaceID.py](DataCollection%2FHF%2FgetSpaceID.py) to obtain all public Spaces.  
  After retrieving the list of Spaces created each month, use [DownloadFromFile_space.py](DataCollection%2FHF%2FDownloadFromFile_space.py) to download the corresponding code repositories.

- For ModelScope: Run [CollectSpaceList.py](DataCollection%2FModelScope%2FCollectSpaceList.py) to gather all public Spaces.  
  *(Note: Since ModelScope does not provide an official API, this step is implemented via web scraping.)*  
  You can then use [DownloadFromFile_space_modelscope.py](DataCollection%2FModelScope%2FDownloadFromFile_space_modelscope.py) to download the Space code.

Due to the large volume of data, we have extracted 1,000 code repositories from each platform for easier testing:

- Hugging Face: https://zenodo.org/records/15752077  
- ModelScope: https://zenodo.org/records/15752627  

### Step 2. LLM-Based Extraction  
You can find the relevant implementation in the [OurTools](OurTools) directory.  
- Use [filterRepo.py](OurTools%2FStaticAnalysis%2FfilterRepo.py) to perform static analysis and extract candidate files and relevant commit history.  
- Use [LLM_main.py](OurTools%2FLLM%2FLLM_main.py) to run secret leakage detection using a combination of static analysis and large language models.

### Step 3. Secret Key Verification  
Use [ApiVerify.py](Analysis%2FApiVerify.py) to verify the validity of the detected secrets. It supports the following services:
- AI model service providers
- Cloud storage services
- Code hosting platforms  

The results will be saved in a CSV file with the following fields:  
`Repository`, `api`, `organization`, `valid`, `available`, `userinfo`, `permissions`, `balance`, `models`, `datasets`, `spaces`, `context`.

## Real-World Threat Simulation

### Overview of the [mock](mock) Directory

The `mock` directory is designed to simulate attacks resulting from secret key leakage across various platforms and services, helping researchers understand the real-world risks of such incidents. Each subfolder or script corresponds to a common type of key and its exploitation method.

### Directory Structure

- **AI Model Provider/**  
  Simulates secret key leakage for popular AI platforms (e.g., OpenAI, Replicate, Groq):  
  - `mock_openai.py`: Simulates exploitation of OpenAI API keys, including key validation, file operations, etc.  
  - `mock_replicate.py`: Simulates Replicate API key misuse, including model inference.  
  - `mock_groq.py`: Simulates Groq API key leakage and model invocation.  
  - `mock_nvidia.py`: Simulates Nvidia API key leakage and model invocation.

- **Storage Service/**  
  Simulates leakage scenarios for cloud databases:  
  - `mock_mongdb.py`: Simulates attacks using leaked MongoDB connection strings, including connection and data access.

- **Code Hosting Platforms/**  
  Simulates exploitation of credentials for code hosting services (e.g., Hugging Face, GitHub):  
  - `mock_hf.py`: Simulates Hugging Face token leakage, including access to user info, models, datasets, and Spaces.  
  - `mock_modelscope.py`: Simulates ModelScope token leakage, including access to models, datasets, and APIs.  
  - `mock_github.py`: Simulates GitHub token leakage, including access to user info, repositories, Gists, etc.  
  - `icse2026.jsonl`: Sample data file used for specific scripts (e.g., OpenAI upload test).

- **key.zip**  
  Example key file containing simulated API keys for Hugging Face, OpenAI, MongoDB, etc., used for testing purposes.

> 🚨 **Note**: These test keys may become invalid over time. If needed, please submit an issue to request updates.

### How to Use

1. Navigate to the `mock` directory and choose the relevant script for the platform or service you wish to test.
2. When running a script, pass the key from `key.txt` as a parameter. Example usage:

```bash
python mock_openai.py <OpenAI_API_Key>
python mock_groq.py <API_Key>
python mock_nvidia.py <API_Key>
python mock_replicate.py <API_Key>
```

```bash
python mock_mongdb.py <MongoDB_Connection_String>
```

```bash
python mock_hf.py <HuggingFace_Token>
python mock_github.py <GitHub_Token>
python mock_modelscope.py <ModelScope_Token>
```

3. The script will simulate an attacker using the leaked secret key and output relevant information to help illustrate the risk.