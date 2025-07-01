import openai
import requests
from openai import OpenAI
import sys
import os
import re

# ANSI color codes
RED = "\033[91m"  # Bright Red
GREEN = "\033[92m"  # Bright Green
YELLOW = "\033[93m"  # Bright Yellow
RESET = "\033[0m"  # Reset color
CHECK_MARK = "✓"  # Unicode check mark


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def verify_api_key(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    try:
        response = requests.get('https://api.openai.com/v1/me', headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"{GREEN}{CHECK_MARK} API key is valid{RESET}")
            print(f"User ID: {user_info.get('id')}")
            print(f"Organization: {user_info.get('organization_id')}")
            print(f"User email: {user_info.get('email')}")
            return True, user_info
        else:
            print(f"{RED}Invalid API key. Status code: {response.status_code}{RESET}")
            print(response.json())
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error verifying API key: {str(e)}{RESET}")
        return False, None


def print_file_info(client):
    red_marker = "⚠️"

    print(f"\n>>> File operations")
    try:
        # List files
        print("\tFiles:")
        files = client.files.list()
        if not files.data:
            print("\t\tNo files found")
        else:
            for file in files.data:
                status = f"{red_marker} {red_marker} {red_marker}" if file.status != "uploaded" else ""
                print(f"\t\tID: {file.id}")
                print(f"\t\tFilename: {file.filename}")
                print(f"\t\tSize: {file.bytes} bytes")
                print(f"\t\tStatus: {file.status} {status}")
                print(f"\t\tPurpose: {file.purpose}")
                print("\t\t" + "-" * 20)
        return True

    except Exception as e:
        print(f"\tError listing files: {str(e)}")
        return False


def uploading_files(client):
    try:
        # Attempt to upload the file 'icse2026.jsonl' to OpenAI with purpose 'evals'
        file = client.files.create(
            file=open("icse2026.jsonl", "rb"),  # Open file in binary read mode
            purpose="evals"  # Specify the purpose of the file (e.g., for evaluations)
        )
        print(f"{GREEN}File upload successful{RESET}")
    except openai.AuthenticationError as e:
        # Handle authentication errors (e.g., invalid or insufficient permissions)
        print(f"You have insufficient permissions for this operation")
    except FileNotFoundError:
        # Handle case where the specified file is not found
        print("Error: icse2026.jsonl not found in the current directory")
    except Exception as e:
        # Catch any other unexpected errors during file upload
        print(f"An error occurred: {e}")


def down_files(client):
    try:
        # Retrieve the list of files from OpenAI
        files = client.files.list()
        # Check if the list of files is empty
        if not files.data:
            print('No files found.')
            exit(0)  # Exit the function if no files are available
        # Get the ID of the most recent file (first in the list)
        file_id = files.data[0].id
        # Retrieve the content of the file using its ID
        response = client.files.content(file_id)

        # Check if the response contains valid content
        if response is None:
            print(f"No content found for file ID: {file_id}")
            return None

        # Read the content of the file (assuming it's text-based like JSONL)
        content = response.read()  # Returns bytes or text depending on file type

        # Save the content to a local file with a name based on the file ID
        output_filename = f"downloaded_{file_id}.jsonl"  # File extension matches input
        with open(output_filename, "wb") as f:
            f.write(content)  # Write content to the file in binary mode
        print(f"File content saved to {output_filename}")
    except openai.AuthenticationError as e:
        # Handle authentication errors (e.g., invalid API key or permissions)
        print(f"Authentication error: {e}")
        return None
    except openai.APIError as e:
        # Handle API-specific errors (e.g., server issues or invalid requests)
        print(f"API error: {e}")
        return None
    except FileNotFoundError:
        # Handle errors related to saving the file locally
        print(f"Error: Could not save file locally.")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return None


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python mock_openai.py <api_key>")
        sys.exit(1)

    api_key = sys.argv[1]
    output_filename = f"{api_key}.txt"

    print(f"{YELLOW}Step 1: Validating API key...{RESET}")

    # Step 1: Verify API key
    is_valid, user_info = verify_api_key(api_key)

    if not is_valid:
        # Create the file and rename it to indicate invalid key
        with open(output_filename, "w") as f:
            f.write("Invalid API key\n")
        os.rename(output_filename, f"{api_key}_invalid.txt")
        return

    # Write valid key info to file
    with open(output_filename, "w") as f:
        f.write(f"API key is valid\n")
        f.write(f"User ID: {user_info.get('id')}\n")
        f.write(f"Organization: {user_info.get('organization_id')}\n")

    # Wait for user to press Enter to continue
    input(f"{YELLOW}Press Enter to continue to Step 2 (file operations)...{RESET}")

    print(f"{YELLOW}Step 2: Initializing OpenAI client and checking files...{RESET}")

    try:
        client = OpenAI(api_key=api_key)

        # Step 2: File operations
        if print_file_info(client):
            input(f"{YELLOW}Press Enter to continue to Step 3 (upload file)...{RESET}")
            uploading_files(client)
            input(f"{YELLOW}Press Enter to continue to Step 4 (down file)...{RESET}")
            down_files(client)

        # Rename the output file
        user_id = user_info.get('id', 'unknown')
        new_filename = f"{api_key}_{user_id}.txt"
        os.rename(output_filename, new_filename)

        print(f"{GREEN}{CHECK_MARK} File operations completed{RESET}")

    except Exception as e:
        print(f"{RED}Error during file operations: {str(e)}{RESET}")
        os.rename(output_filename, f"{api_key}_error.txt")


if __name__ == "__main__":
    main()
