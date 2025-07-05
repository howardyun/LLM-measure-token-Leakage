import requests
import sys
import os
import re
from typing import Dict, Any

# ANSI color codes
RED = "\033[91m"  # Bright Red
GREEN = "\033[92m"  # Bright Green
YELLOW = "\033[93m"  # Bright Yellow
RESET = "\033[0m"  # Reset color
CHECK_MARK = "✓"  # Unicode check mark


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def verify_api_key(api_key: str) -> tuple[bool, Dict[str, Any]]:
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    try:
        response = requests.get('https://api.groq.com/openai/v1/models', headers=headers)
        if response.status_code == 200:
            models = response.json().get('data', [])
            print(f"{GREEN}{CHECK_MARK} API key is valid{RESET}")
            print(f"Available models: {', '.join([m['id'] for m in models])}")
            return True, {'models': models}
        else:
            print(f"{RED}Invalid API key. Status code: {response.status_code}{RESET}")
            print(response.json())
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error verifying API key: {str(e)}{RESET}")
        return False, None


def test_chat_completion(client, model: str = "llama3-8b-8192") -> bool:
    print(f"\n>>> Testing chat completion with model: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Explain the importance of fast language models"
                }
            ]
        )

        print(f"{GREEN}{CHECK_MARK} Chat completion successful{RESET}")
        print(f"Model: {response.model}")
        print(f"Completion: {response.choices[0].message.content[:100]}...")
        return True
    except Exception as e:
        print(f"{RED}Error testing chat completion: {str(e)}{RESET}")
        return False


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python mock_groq.py <api_key>")
        sys.exit(1)

    api_key = sys.argv[1]
    output_filename = f"{api_key}.txt"

    print(f"{YELLOW}Step 1: Validating API key...{RESET}")

    # Step 1: Verify API key
    is_valid, api_info = verify_api_key(api_key)

    if not is_valid:
        # Create the file and rename it to indicate invalid key
        with open(output_filename, "w") as f:
            f.write("Invalid API key\n")
        os.rename(output_filename, f"{api_key}_invalid.txt")
        return

    # Write valid key info to file
    with open(output_filename, "w") as f:
        f.write(f"API key is valid\n")
        if api_info and 'models' in api_info:
            f.write(f"Available models: {', '.join([m['id'] for m in api_info['models']])}\n")

    # Wait for user to press Enter to continue
    input(f"{YELLOW}Press Enter to continue to Step 2 (chat completion test)...{RESET}")

    print(f"{YELLOW}Step 2: Testing chat completion...{RESET}")

    try:
        # In a real implementation, we would use the Groq client
        # For this mock, we'll simulate it with a simple dict
        client = {"chat": {"completions": {"create": lambda **kwargs: {
            "model": kwargs.get("model"),
            "choices": [{"message": {"content": "Fast language models are important because..."}}]
        }}}}

        # Step 2: Test chat completion
        if test_chat_completion(client):
            # Rename the output file
            new_filename = f"{api_key}_success.txt"
            os.rename(output_filename, new_filename)
            print(f"{GREEN}{CHECK_MARK} All tests completed successfully{RESET}")
        else:
            os.rename(output_filename, f"{api_key}_error.txt")

    except Exception as e:
        print(f"{RED}Error during chat completion test: {str(e)}{RESET}")
        os.rename(output_filename, f"{api_key}_error.txt")


if __name__ == "__main__":
    main()