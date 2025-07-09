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
WARNING = "⚠️"  # Unicode warning sign


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def verify_api_key(api_key: str) -> tuple[bool, Dict[str, Any]]:
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    try:
        response = requests.get('https://api.replicate.com/v1/account', headers=headers)
        if response.status_code == 200:
            account_info = response.json()
            print(f"{GREEN}{CHECK_MARK} API key is valid{RESET}")
            print(f"Account Type: {account_info.get('type', 'unknown')}")
            print(f"Username: {account_info.get('username', 'unknown')}")
            print(f"Organization: {account_info.get('organization', {}).get('name', 'none')}")
            return True, account_info
        else:
            print(f"{RED}Invalid API key. Status code: {response.status_code}{RESET}")
            print(response.json())
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error verifying API key: {str(e)}{RESET}")
        return False, None


def test_model_prediction(api_key: str, model: str = "black-forest-labs/flux-schnell") -> bool:
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Prefer': 'wait',
    }

    json_data = {
        'input': {
            'prompt': 'an illustration of a dog jumping',
        },
    }

    print(f"\n>>> Testing model prediction with: {model}")
    try:
        response = requests.post(
            f'https://api.replicate.com/v1/models/{model}/predictions',
            headers=headers,
            json=json_data,
        )

        if response.status_code == 200:
            prediction = response.json()
            print(f"{GREEN}{CHECK_MARK} Prediction created successfully{RESET}")
            print(f"Prediction ID: {prediction.get('id')}")
            print(f"Status: {prediction.get('status')}")
            print(f"Model: {prediction.get('version')}")
            return True
        else:
            print(f"{RED}Error creating prediction. Status code: {response.status_code}{RESET}")
            print(response.json())
            return False
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error testing model prediction: {str(e)}{RESET}")
        return False


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python mock_replicate.py <api_key>")
        sys.exit(1)

    api_key = sys.argv[1]
    output_filename = f"{api_key}.txt"

    print(f"{YELLOW}Step 1: Validating API key...{RESET}")

    # Step 1: Verify API key
    is_valid, account_info = verify_api_key(api_key)

    if not is_valid:
        # Create the file and rename it to indicate invalid key
        with open(output_filename, "w") as f:
            f.write("Invalid API key\n")
        os.rename(output_filename, f"{api_key}_invalid.txt")
        return

    # Write valid key info to file
    with open(output_filename, "w") as f:
        f.write(f"API key is valid\n")
        f.write(f"Account Type: {account_info.get('type', 'unknown')}\n")
        f.write(f"Username: {account_info.get('username', 'unknown')}\n")
        f.write(f"Organization: {account_info.get('organization', {}).get('name', 'none')}\n")

    # Wait for user to press Enter to continue
    input(f"{YELLOW}Press Enter to continue to Step 2 (model prediction test)...{RESET}")

    print(f"{YELLOW}Step 2: Testing model prediction...{RESET}")

    try:
        # Step 2: Test model prediction
        if test_model_prediction(api_key):
            # Rename the output file
            username = account_info.get('username', 'unknown')
            new_filename = f"{api_key}_{username}_success.txt"
            os.rename(output_filename, new_filename)
            print(f"{GREEN}{CHECK_MARK} All tests completed successfully{RESET}")
        else:
            os.rename(output_filename, f"{api_key}_error.txt")

    except Exception as e:
        print(f"{RED}Error during model prediction test: {str(e)}{RESET}")
        os.rename(output_filename, f"{api_key}_error.txt")


if __name__ == "__main__":
    main()
