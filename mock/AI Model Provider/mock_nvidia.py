import requests
import sys
import os
import re
from typing import Optional, Dict, Any

# ANSI color codes
RED = "\033[91m"  # Bright Red
GREEN = "\033[92m"  # Bright Green
YELLOW = "\033[93m"  # Bright Yellow
RESET = "\033[0m"  # Reset color
CHECK_MARK = "✓"  # Unicode check mark


def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def verify_api_key(api_key: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    try:
        # Test endpoint - this might need to be adjusted based on actual NVIDIA API
        response = requests.get('https://integrate.api.nvidia.com/v1/models', headers=headers)
        if response.status_code == 200:
            models_info = response.json()
            print(f"{GREEN}{CHECK_MARK} API key is valid{RESET}")
            print(f"Available models: {', '.join(model['id'] for model in models_info.get('data', []))}")
            return True, models_info
        else:
            print(f"{RED}Invalid API key. Status code: {response.status_code}{RESET}")
            print(response.json())
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error verifying API key: {str(e)}{RESET}")
        return False, None


def chat_completion(client: Any, model: str = "meta/llama3-70b", prompt: str = "Hello, world!") -> None:
    try:
        print(f"\n>>> Chat completion with model: {model}")

        headers = {
            'Authorization': f'Bearer {client.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1024
        }

        response = requests.post(
            'https://integrate.api.nvidia.com/v1/chat/completions',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            completion = response.json()
            print(f"{GREEN}{CHECK_MARK} Chat completion successful{RESET}")
            print(f"Response: {completion['choices'][0]['message']['content']}")
            print(f"Usage: {completion['usage']}")
            return completion
        else:
            print(f"{RED}Error in chat completion: {response.status_code}{RESET}")
            print(response.json())
            return None

    except Exception as e:
        print(f"{RED}Error during chat completion: {str(e)}{RESET}")
        return None


class NvidiaClient:
    def __init__(self, api_key: str):
        self.api_key = api_key


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python mock_nvidia.py <api_key>")
        sys.exit(1)

    api_key = sys.argv[1]
    output_filename = f"{api_key}.txt"

    print(f"{YELLOW}Step 1: Validating API key...{RESET}")

    # Step 1: Verify API key
    is_valid, models_info = verify_api_key(api_key)

    if not is_valid:
        # Create the file and rename it to indicate invalid key
        with open(output_filename, "w") as f:
            f.write("Invalid API key\n")
        os.rename(output_filename, f"{api_key}_invalid.txt")
        return

    # Write valid key info to file
    with open(output_filename, "w") as f:
        f.write(f"API key is valid\n")
        if models_info and 'data' in models_info:
            f.write(f"Available models: {', '.join(model['id'] for model in models_info['data'])}\n")

    # Wait for user to press Enter to continue
    input(f"{YELLOW}Press Enter to continue to Step 2 (chat completion)...{RESET}")

    print(f"{YELLOW}Step 2: Initializing NVIDIA client and testing chat completion...{RESET}")

    try:
        client = NvidiaClient(api_key=api_key)

        # Step 2: Chat completion
        default_model = "meta/llama3-70b" if models_info and any(
            'llama3-70b' in m['id'] for m in models_info.get('data', [])) else "gpt-3.5-turbo"
        prompt = "Explain quantum computing in simple terms"

        completion_result = chat_completion(client, model=default_model, prompt=prompt)

        # Rename the output file
        new_filename = f"{api_key}_completed.txt"
        os.rename(output_filename, new_filename)

        print(f"{GREEN}{CHECK_MARK} Chat completion test completed{RESET}")

    except Exception as e:
        print(f"{RED}Error during chat completion: {str(e)}{RESET}")
        os.rename(output_filename, f"{api_key}_error.txt")


if __name__ == "__main__":
    main()