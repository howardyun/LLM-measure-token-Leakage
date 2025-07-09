import requests
import sys
import os
import re
import json
from datetime import datetime
from openai import OpenAI
from modelscope import HubApi, snapshot_download
from modelscope.msdatasets import MsDataset

# ANSI color codes
RED = "\033[91m"  # Bright Red
GREEN = "\033[92m"  # Bright Green
YELLOW = "\033[93m"  # Bright Yellow
RESET = "\033[0m"  # Reset color
CHECK_MARK = "✓"  # Unicode check mark


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def validate_token(token):
    # Attempt to validate token by making a simple API call
    url = "https://api-inference.modelscope.cn/v1/models"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200, response.text
    except requests.RequestException as e:
        return False, str(e)


def list_models(token):
    # Fetch models available on ModelScope
    url = "https://api-inference.modelscope.cn/v1/models"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('models', [])
        return []
    except requests.RequestException:
        return []


def list_datasets(token):
    # Fetch datasets; assuming ModelScope has a datasets endpoint
    url = "https://api-inference.modelscope.cn/v1/datasets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('datasets', [])
        return []
    except requests.RequestException:
        return []


def test_api_inference(token, filename):
    # Test API inference with Qwen model
    print(f"{YELLOW}Step 3: Testing API inference with Qwen model...{RESET}")
    print(f">>> Running API inference test with Qwen/Qwen2.5-Coder-32B-Instruct")

    with open(filename, "a") as f:
        f.write("\nAPI Inference Test:\n")

    try:
        client = OpenAI(
            api_key=token,
            base_url="https://api-inference.modelscope.cn/v1/"
        )

        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant.'
                },
                {
                    'role': 'user',
                    'content': 'who are you'
                }
            ],
            stream=True
        )

        print("\tQuicksort Response:")
        with open(filename, "a") as f:
            f.write("\tQuicksort Response:\n")

        response_text = ""
        for chunk in response:
            content = chunk.choices[0].delta.content or ""
            print(content, end='', flush=True)
            response_text += content

        with open(filename, "a") as f:
            f.write(response_text + "\n")

        print(f"\n{GREEN}{CHECK_MARK} API inference test successful{RESET}")
        with open(filename, "a") as f:
            f.write("API inference test successful\n")

        return True
    except Exception as e:
        error_message = f"API inference test failed: {str(e)}"
        print(f"\n{RED}{error_message}{RESET}")
        with open(filename, "a") as f:
            f.write(f"{error_message}\n")
        return False


def test_model_download(token, filename, model_id="icse2026/aaa"):
    # Test downloading a private model
    print(f"{YELLOW}Step 4: Testing private model download...{RESET}")
    print(f">>> Attempting to download model: {model_id}")

    with open(filename, "a") as f:
        f.write("\nPrivate Model Download Test:\n")
        f.write(f"Attempting to download model: {model_id}\n")

    try:
        api = HubApi()
        api.login(token)

        model_path = snapshot_download(model_id=model_id)

        print(f"\tModel downloaded successfully to: {model_path}")
        with open(filename, "a") as f:
            f.write(f"Model downloaded successfully to: {model_path}\n")

        print(f"{GREEN}{CHECK_MARK} Model download test successful{RESET}")
        with open(filename, "a") as f:
            f.write("Model download test successful\n")

        return True
    except Exception as e:
        error_message = f"Model download test failed: {str(e)}"
        print(f"\n{RED}{error_message}{RESET}")
        with open(filename, "a") as f:
            f.write(f"{error_message}\n")
        return False


def test_dataset_download(token, filename, dataset_id="icse2026/aaa"):
    # Test downloading a dataset
    print(f"{YELLOW}Step 5: Testing dataset download...{RESET}")
    print(f">>> Attempting to download dataset: {dataset_id} (train split)")

    with open(filename, "a") as f:
        f.write("\nDataset Download Test:\n")
        f.write(f"Attempting to download dataset: {dataset_id} (train split)\n")

    try:
        # Ensure token is set for dataset access
        ds = MsDataset.load(dataset_id)

        # Log basic information about the dataset
        dataset_info = f"Dataset {dataset_id}  loaded successfully. Sample count: {len(ds)}"
        print(f"\t{dataset_info}")
        with open(filename, "a") as f:
            f.write(f"{dataset_info}\n")

        print(f"{GREEN}{CHECK_MARK} Dataset download test successful{RESET}")
        with open(filename, "a") as f:
            f.write("Dataset download test successful\n")

        return True
    except Exception as e:
        error_message = f"Dataset download test failed: {str(e)}"
        print(f"\n{RED}{error_message}{RESET}")
        with open(filename, "a") as f:
            f.write(f"{error_message}\n")
        return False


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python mock_modelscope.py <token>")
        sys.exit(1)

    token = sys.argv[1]
    output_filename = f"{token}.txt"

    print(f"{YELLOW}Step 1: Validating token...{RESET}")
    print(f">>> Attempting to validate ModelScope SDK Token")

    # Step 1: Validate token
    is_valid, response_text = validate_token(token)

    # Write initial output to file
    with open(output_filename, "w") as f:
        f.write(f"Token validation attempt at {datetime.now()}\n")
        f.write(f"Response: {response_text}\n")

    if is_valid:
        print(f"{GREEN}{CHECK_MARK} Token is valid{RESET}")
        with open(output_filename, "a") as f:
            f.write("Token is valid\n")

        # Wait for user to press Enter to continue
        input(f"{YELLOW}Press Enter to continue to Step 2 (API inference test)...{RESET}")

        # Step 3: Test API inference
        inference_success = test_api_inference(token, output_filename)

        # Wait for user to press Enter to continue
        input(f"{YELLOW}Press Enter to continue to Step 3 (private model download test)...{RESET}")

        # Step 4: Test private model download
        model_download_success = test_model_download(token, output_filename)

        # Wait for user to press Enter to continue
        input(f"{YELLOW}Press Enter to continue to Step 4 (dataset download test)...{RESET}")

        # Step 5: Test dataset download
        dataset_download_success = test_dataset_download(token, output_filename)

        # Rename the file
        status = "_success" if inference_success and model_download_success and dataset_download_success else "_failed"
        new_filename = f"{token}_modelscope{status}.txt"
        os.rename(output_filename, new_filename)
    else:
        print(f"{RED}Token is invalid{RESET}")
        with open(output_filename, "a") as f:
            f.write("Token is invalid\n")
        os.rename(output_filename, f"{token}_invalid.txt")


if __name__ == "__main__":
    main()
