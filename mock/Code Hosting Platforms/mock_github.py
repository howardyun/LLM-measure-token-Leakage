import requests
import sys
import os
import re

# ANSI color codes
RED = "\033[91m"  # Bright Red
GREEN = "\033[92m"  # Bright Green
YELLOW = "\033[93m"  # Bright Yellow
RESET = "\033[0m"  # Reset color
CHECK_MARK = "✓"  # Unicode check mark
WARNING_MARKER = "⚠️"  # Warning marker for private items


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def make_github_request(token, endpoint):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com{endpoint}"
    response = requests.get(url, headers=headers)
    return response


def print_content(token, user_info, filename):
    # Print user info
    print(f">>> User Information:")
    with open(filename, "a", encoding='utf-8') as f:  # Added encoding='utf-8'
        f.write(f">>> User Information:\n")

    print(f"\tUsername: {user_info['login']}")
    print(f"\tName: {user_info.get('name', 'Not provided')}")
    print(f"\tEmail: {user_info.get('email', 'Not provided')}")
    print(f"\tPublic Repos: {user_info['public_repos']}")
    print(f"\tPrivate Repos: {user_info.get('total_private_repos', 'Not available')}")

    with open(filename, "a", encoding='utf-8') as f:  # Added encoding='utf-8'
        f.write(f"\tUsername: {user_info['login']}\n")
        f.write(f"\tName: {user_info.get('name', 'Not provided')}\n")
        f.write(f"\tEmail: {user_info.get('email', 'Not provided')}\n")
        f.write(f"\tPublic Repos: {user_info['public_repos']}\n")
        f.write(f"\tPrivate Repos: {user_info.get('total_private_repos', 'Not available')}\n")

    # Get repositories
    print("\n\tRepositories:")
    with open(filename, "a", encoding='utf-8') as f:  # Added encoding='utf-8'
        f.write("\n\tRepositories:\n")

    repos_response = make_github_request(token, "/user/repos?per_page=100")
    if repos_response.status_code == 200:
        repos = repos_response.json()
        for repo in repos:
            if repo['private']:
                # Add warning markers for private repos
                print(f"\t\t{repo['full_name']} {RED}Private{WARNING_MARKER * 3}{RESET}")
                with open(filename, "a", encoding='utf-8') as f:
                    f.write(f"\t\t{repo['full_name']} Private{WARNING_MARKER * 3}\n")
            else:
                print(f"\t\t{repo['full_name']} Public")
                with open(filename, "a", encoding='utf-8') as f:
                    f.write(f"\t\t{repo['full_name']} Public\n")
    else:
        error_msg = f"\t\tError fetching repositories: {repos_response.status_code}"
        print(f"{RED}{error_msg}{RESET}")
        with open(filename, "a", encoding='utf-8') as f:
            f.write(f"{error_msg}\n")

    # Get gists
    print("\n\tGists:")
    with open(filename, "a", encoding='utf-8') as f:  # Added encoding='utf-8'
        f.write("\n\tGists:\n")

    gists_response = make_github_request(token, "/gists?per_page=100")
    if gists_response.status_code == 200:
        gists = gists_response.json()
        for gist in gists:
            if not gist['public']:
                # Add warning markers for private gists
                print(
                    f"\t\t{gist['id']} {RED}Private{WARNING_MARKER * 3}{RESET} - {gist['description'] or 'No description'}")
                with open(filename, "a", encoding='utf-8') as f:
                    f.write(
                        f"\t\t{gist['id']} Private{WARNING_MARKER * 3} - {gist['description'] or 'No description'}\n")
            else:
                print(f"\t\t{gist['id']} Public - {gist['description'] or 'No description'}")
                with open(filename, "a", encoding='utf-8') as f:
                    f.write(f"\t\t{gist['id']} Public - {gist['description'] or 'No description'}\n")
    else:
        error_msg = f"\t\tError fetching gists: {gists_response.status_code}"
        print(f"{RED}{error_msg}{RESET}")
        with open(filename, "a", encoding='utf-8') as f:
            f.write(f"{error_msg}\n")


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python github_token_test.py <token>")
        sys.exit(1)

    token = sys.argv[1]
    output_filename = f"{token}.txt"

    print(f"{YELLOW}Step 1: Validating token...{RESET}")
    print(f">>> API Request: GET https://api.github.com/user")

    # Step 1: Validate token by getting user info
    user_response = make_github_request(token, "/user")

    if user_response.status_code == 200:
        user_info = user_response.json()
        print(f"{GREEN}{CHECK_MARK} Token is valid{RESET}")
        print(f"\tAuthenticated as: {user_info['login']}")

        # Write to output file with UTF-8 encoding
        with open(output_filename, "w", encoding='utf-8') as f:  # Added encoding='utf-8'
            f.write(f"Token is valid\n")
            f.write(f"Authenticated as: {user_info['login']}\n")

        # Step 2: Get additional account details
        input(f"{YELLOW}Press Enter to continue to Step 2 (fetching account details)...{RESET}")
        print(f"{YELLOW}Step 2: Fetching account details for {user_info['login']}...{RESET}")

        print_content(token, user_info, output_filename)

        # Rename the file
        new_filename = f"{token}_{user_info['login']}.txt"
        os.rename(output_filename, new_filename)

        print(f"{GREEN}{CHECK_MARK} Account details fetched successfully{RESET}")
        print(f"{GREEN}Results saved to: {new_filename}{RESET}")
    else:
        error_msg = f"Invalid token (HTTP {user_response.status_code})"
        if user_response.status_code == 401:
            error_msg += ": Unauthorized - Bad credentials"
        print(f"{RED}{error_msg}{RESET}")

        # Create the file with UTF-8 encoding
        with open(output_filename, "w", encoding='utf-8') as f:
            f.write(f"{error_msg}\n")
        os.rename(output_filename, f"{token}_invalid.txt")


if __name__ == "__main__":
    main()