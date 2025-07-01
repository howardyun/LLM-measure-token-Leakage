import pymongo
import sys
import os
from urllib.parse import quote_plus
from bson import ObjectId
from datetime import datetime

# ANSI color codes
RED = "\033[91m"  # Bright Red
GREEN = "\033[92m"  # Bright Green
YELLOW = "\033[93m"  # Bright Yellow
RESET = "\033[0m"  # Reset color
CHECK_MARK = "✓"  # Unicode check mark
WARNING_MARKER = "⚠️"  # Warning marker


def print_mongo_content(uri, filename):
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(uri)

        print(f"{GREEN}{CHECK_MARK} Successfully connected to MongoDB{RESET}")
        with open(filename, "a", encoding='utf-8') as f:
            f.write("Successfully connected to MongoDB\n")

        # Get server info
        server_info = client.server_info()
        print(f"\n>>> MongoDB Server Info:")
        print(f"\tVersion: {server_info.get('version', 'N/A')}")
        print(f"\tStorage Engine: {server_info.get('storageEngine', {}).get('name', 'N/A')}")

        with open(filename, "a", encoding='utf-8') as f:
            f.write("\n>>> MongoDB Server Info:\n")
            f.write(f"\tVersion: {server_info.get('version', 'N/A')}\n")
            f.write(f"\tStorage Engine: {server_info.get('storageEngine', {}).get('name', 'N/A')}\n")

        # List all databases
        print("\n>>> Databases:")
        with open(filename, "a", encoding='utf-8') as f:
            f.write("\n>>> Databases:\n")

        for db_name in client.list_database_names():
            db = client[db_name]
            print(f"\tDatabase: {db_name}")

            # Get stats for each database
            try:
                stats = db.command('dbstats')
                size_mb = stats.get('dataSize', 0) / (1024 * 1024)
                print(f"\t  Size: {size_mb:.2f} MB | Collections: {stats.get('collections', 0)}")

                with open(filename, "a", encoding='utf-8') as f:
                    f.write(f"\tDatabase: {db_name}\n")
                    f.write(f"\t  Size: {size_mb:.2f} MB | Collections: {stats.get('collections', 0)}\n")

                # List collections in each database
                print("\t  Collections:")
                with open(filename, "a", encoding='utf-8') as f:
                    f.write("\t  Collections:\n")

                for col_name in db.list_collection_names():
                    collection = db[col_name]
                    count = collection.estimated_document_count()

                    # Get sample document to show structure
                    sample = collection.find_one()
                    sample_info = "No documents" if sample is None else f"Sample fields: {list(sample.keys())}"

                    print(f"\t    {col_name} (Documents: {count}) - {sample_info}")
                    with open(filename, "a", encoding='utf-8') as f:
                        f.write(f"\t    {col_name} (Documents: {count}) - {sample_info}\n")

                print()  # Add empty line between databases
                with open(filename, "a", encoding='utf-8') as f:
                    f.write("\n")

            except Exception as db_error:
                error_msg = f"\t  Error accessing database {db_name}: {str(db_error)}"
                print(f"{RED}{error_msg}{RESET}")
                with open(filename, "a", encoding='utf-8') as f:
                    f.write(f"{error_msg}\n")

        client.close()

    except pymongo.errors.ConnectionFailure as e:
        error_msg = f"{RED}Failed to connect to MongoDB: {str(e)}{RESET}"
        print(error_msg)
        with open(filename, "a", encoding='utf-8') as f:
            f.write(f"Failed to connect to MongoDB: {str(e)}\n")
        return False
    except Exception as e:
        error_msg = f"{RED}Unexpected error: {str(e)}{RESET}"
        print(error_msg)
        with open(filename, "a", encoding='utf-8') as f:
            f.write(f"Unexpected error: {str(e)}\n")
        return False

    return True


def main():
    # Check if connection string is provided
    if len(sys.argv) != 2:
        print("Usage: python mongo_test.py <connection_string>")
        print("Example: python mongo_test.py 'mongodb://username:password@host:port'")
        sys.exit(1)

    uri = sys.argv[1]

    # Create a safe filename (replace special characters)
    safe_uri = quote_plus(uri)
    output_filename = f"mongo_{safe_uri[:50]}.txt"  # Limit filename length

    print(f"{YELLOW}Testing MongoDB connection...{RESET}")
    print(f">>> Connection string: {uri}")

    # Write initial info to file
    with open(output_filename, "w", encoding='utf-8') as f:
        f.write(f"MongoDB Connection Test\n")
        f.write(f"Connection string: {uri}\n")
        f.write(f"Test time: {datetime.now().isoformat()}\n\n")

    # Test connection and print content
    success = print_mongo_content(uri, output_filename)

    if success:
        print(f"{GREEN}{CHECK_MARK} MongoDB test completed successfully{RESET}")
        print(f"{GREEN}Results saved to: {output_filename}{RESET}")
    else:
        os.rename(output_filename, f"mongo_error_{safe_uri[:50]}.txt")
        print(f"{RED}MongoDB test failed{RESET}")


if __name__ == "__main__":
    main()