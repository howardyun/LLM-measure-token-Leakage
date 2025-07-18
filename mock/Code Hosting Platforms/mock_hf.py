from huggingface_hub import HfApi
import sys
import subprocess
import os
import re

# ANSI color codes
RED = "\033[91m"        # Bright Red
GREEN = "\033[92m"      # Bright Green
YELLOW = "\033[93m"     # Bright Yellow
RESET = "\033[0m"       # Reset color
CHECK_MARK = "✓"        # Unicode check mark


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def print_content(api, user_name, org_list, filename):
    red_marker = "⚠️"

    print(f">>> {user_name}: ")
    with open(filename, "a") as f:
        f.write(f">>> {user_name}: \n")

    models = api.list_models(author=user_name)
    print("\tModels:")
    with open(filename, "a") as f:
        f.write("\tModels:\n")

    for m in models:
        if m.private:
            print(f"\t\t{m.id} Private={m.private} {red_marker} {red_marker} {red_marker}")
        else:
            print(f"\t\t{m.id} Private={m.private}")
        with open(filename, "a") as f:
            f.write(f"\t\t{m.id} Private={m.private}\n")

    datasets = api.list_datasets(author=user_name)
    print("\tDatasets:")
    with open(filename, "a") as f:
        f.write("\tDatasets:\n")

    for m in datasets:
        if m.private:
            print(f"\t\t{m.id} Private={m.private} {red_marker} {red_marker} {red_marker}")
        else:
            print(f"\t\t{m.id} Private={m.private}")
        with open(filename, "a") as f:
            f.write(f"\t\t{m.id} Private={m.private}\n")

    spaces = api.list_spaces(author=user_name)
    print("\tSpaces:")
    with open(filename, "a") as f:
        f.write("\tSpaces:\n")

    for m in spaces:
        if m.private:
            print(f"\t\t{m.id} Private={m.private} {red_marker} {red_marker} {red_marker}")
        else:
            print(f"\t\t{m.id} Private={m.private}")
        with open(filename, "a") as f:
            f.write(f"\t\t{m.id} Private={m.private}\n")

    colls = api.list_collections(owner=user_name)
    print("\tCollections:")
    with open(filename, "a") as f:
        f.write("\tCollections:\n")

    for m in colls:
        if m.private:
            print(f"\t\t{m.slug} Private={m.private} {red_marker} {red_marker} {red_marker}")
        else:
            print(f"\t\t{m.slug} Private={m.private}")
        with open(filename, "a") as f:
            f.write(f"\t\t{m.slug} Private={m.private}\n")

    # for org_name in org_list:
    #     org_members = api.list_organization_members(org_name)
    #     print(f"\tOrg {org_name} members: ")
    #     with open(filename, "a") as f:
    #         f.write(f"\tOrg {org_name} members: \n")
    #
    #     for m in org_members:
    #         print(f"\t\t{m.fullname}")
    #         with open(filename, "a") as f:
    #             f.write(f"\t\t{m.fullname}\n")


def main():
    # Check if token is provided
    if len(sys.argv) != 2:
        print("Usage: python mock_hf.py <token>")
        sys.exit(1)

    token = sys.argv[1]
    output_filename = f"{token}.txt"

    print(f"{YELLOW}Step 1: Validating token...{RESET}")
    print(f">>> Command: huggingface-cli login --token {token}")

    # Step 1: Execute huggingface-cli login
    login_result = subprocess.run(
        ["huggingface-cli", "login", "--token", token],
        capture_output=True,
        text=True
    )

    # Print the output to stdout
    print(login_result.stdout)
    if login_result.stderr:
        print(login_result.stderr)

    combined_output = login_result.stdout + login_result.stderr

    # Check if login was successful
    if "Token is valid" in combined_output:
        # Extract the "Token is valid" line
        print(f"{GREEN}{CHECK_MARK} Token is valid{RESET}")
        valid_line = ""
        for line in combined_output.splitlines():
            if "Token is valid" in line:
                valid_line = line
                break

        # Write to output file
        with open(output_filename, "w") as f:
            f.write(valid_line + "\n")

        # Wait for user to press Enter to continue
        input(f"{YELLOW}Press Enter to continue to Step 2 (whoami)...{RESET}")

        print(f"{YELLOW}Step 2: Running whoami command...{RESET}")
        print(f">>> Command: huggingface-cli whoami")

        # Proceed to step 2
        whoami_result = subprocess.run(
            ["huggingface-cli", "whoami"],
            capture_output=True,
            text=True
        )

        # Print the output to stdout
        print(whoami_result.stdout)
        if login_result.stderr:
            print(whoami_result.stderr)

        combined_output = whoami_result.stdout + whoami_result.stderr
        lines = [strip_ansi(line.strip()) for line in combined_output.strip().split('\n') if strip_ansi(line.strip())]

        if not lines:
            print("Error: Unable to get username information")
            # Also write to file
            with open(output_filename, "a") as f:
                f.write("Error: Unable to get username information\n")
            os.rename(output_filename, f"{token}_error.txt")
            return

        username = lines[0].strip()
        orgs = []

        # Look for the line starting with "orgs:"
        for line in lines[1:]:
            if line.strip().startswith("orgs:"):
                orgs_line = line.replace("orgs:", "").strip()
                orgs = [org.strip() for org in orgs_line.split(',')]
                break

        # Append to output file
        with open(output_filename, "a") as f:
            f.write(f"username: {username}\n")
            if orgs:
                f.write(f"orgs: {', '.join(orgs)}\n")

        print(f"{GREEN}Identified username: {username}{RESET}")
        print(f"{GREEN}Identified orgs: {orgs}{RESET}")

        print(f"{GREEN}{CHECK_MARK} Running whoami command success{RESET}")

        # Step 3: Use the HfApi to get more information
        # Wait for user to press Enter to continue
        input(f"{YELLOW}Press Enter to continue to Step 3 (fetching account details)...{RESET}")

        print(f"{YELLOW}Step 3: Fetching account details for {username}...{RESET}")

        api = HfApi(token=token)

        # Execute the function with output filename
        print_content(api, username, orgs, output_filename)
        if orgs:
            for org in orgs:
                print_content(api, org, [], output_filename)

        # Rename the file
        new_filename = f"{token}_{username}"
        if orgs:
            new_filename += "_" + "_".join(orgs)
        new_filename += ".txt"

        os.rename(output_filename, new_filename)
    else:
        # Create the file and rename it to indicate invalid token
        with open(output_filename, "w") as f:
            pass
        os.rename(output_filename, f"{token}_invalid.txt")


if __name__ == "__main__":
    main()


