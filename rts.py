import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, wait

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, help="The text to search for")
    parser.add_argument("directory", type=str, help="Directory to search in")
    return parser.parse_args()

def process_file(file_path: str, query: str) -> None:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_number, line in enumerate(f, start=1):
                if query in line:
                    line = line.rstrip("\n")
                    print(f"{file_path}:{line_number}: {line}")
    except (OSError, IOError) as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)

def search_in_directory(directory: str, query: str) -> None:
    with ThreadPoolExecutor() as executor:
        futures = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if not filename.lower().endswith((".txt", ".log")):
                    continue
                file_path = os.path.join(root, filename)
                futures.append(executor.submit(process_file, file_path, query))
                
            wait(futures)

def main():
    args = parse_arguments()
    print("Query:", args.query)
    print("Directory:", args.directory)
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory or does not exist.", file=sys.stderr)
        sys.exit(1)
    search_in_directory(args.directory, args.query)

if __name__ == "__main__":
    main()
