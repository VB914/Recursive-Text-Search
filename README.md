# Recursive Text Search
This is a small command-line text search tool I wrote in Python.
It works a bit like a simplified grep (Global Regular Expression Print is a powerful command-line utility in Unix-like systems for searching text in files or input streams for lines matching a specific pattern) that can:

walk through a directory recursively

open each file

search for a given query string

print every line that contains that string

On top of that, it uses threads (ThreadPoolExecutor) so multiple files can be searched at the same time.
1. Overview
The Goal is to Given a search term (query) and a starting directory, search through all files under that directory (including subfolders) and print any matching lines in the below for format:
path/to/file:line_number: matching line text

2. How the program works (high-level)

The main steps are:

Parse command-line arguments using argparse

query: the text to search for

directory: the root directory to search in

Validate the directory

If the directory doesn’t exist or isn’t a directory, the program prints an error to stderr and exits.

Walk the directory tree using os.walk

This visits every subfolder and file under the given directory.

Use a thread pool to process files concurrently

For each file found, a task is submitted to a ThreadPoolExecutor.

Each task runs process_file on a single file.

Search inside each file line by line

For each line in the file, if the query string is found, the program prints

Code structure

The main functions are:

parse_arguments()

Uses argparse.ArgumentParser to define:

query (positional argument, string)

directory (positional argument, string)

Returns an args object with args.query and args.directory.

process_file(file_path, query)

Opens a single file in text mode:

open(file_path, "r", encoding="utf-8", errors="ignore")


Reads it line by line using enumerate(..., start=1) to keep track of line numbers.

If query in line (case-sensitive), it prints:

file_path:line_number: line_text


If the file can’t be opened or read (e.g., permission issues), it catches OSError/IOError and prints an error message to stderr.

search_in_directory(directory, query)

Creates a ThreadPoolExecutor:

with ThreadPoolExecutor() as executor:
    ...


Uses os.walk(directory) to recursively walk through all subdirectories and files.

For each file, builds the full path with os.path.join(root, filename).

Submits a job to the executor:

executor.submit(process_file, file_path, query)


Stores all returned Future objects in a list and calls wait(futures) so the function doesn’t return until all files have been processed.

main()

Calls parse_arguments() to get the query and directory.

Prints them (mainly for clarity while running).

Checks os.path.isdir(args.directory):

If false, prints an error and exits with status code 1.

Calls search_in_directory(args.directory, args.query) to do the actual work.

Entry point

At the bottom, the standard pattern:

if __name__ == "__main__":
    main()


This ensures main() only runs when you execute rts.py directly, not if the file is imported somewhere else.

4. Concurrency model (threads)

For concurrency, I chose to use threads via concurrent.futures.ThreadPoolExecutor.

Why threads?

The work here is mostly I/O-bound (reading from disk), not CPU-heavy.

While one thread is waiting for data from the disk, another thread can work on a different file.

ThreadPoolExecutor has a simple API (submit, wait) and is built into the standard library.

How it works in this program:

A ThreadPoolExecutor is created once inside search_in_directory.

For each file found by os.walk, a new job (process_file) is submitted to the executor.

Each worker thread runs process_file on a different file.

The main thread waits with wait(futures) until all file-processing tasks are done.

So logically:

Main thread: discovers file paths and schedules work.

Worker threads: open files and search lines in parallel.

5. Design choices, limitations, and trade-offs
Design choices

Line-by-line reading

This avoids loading entire files into memory, which matters for large files.

Substring search (query in line)

Simple, readable, and enough for basic exact string matching.

Limitations

Case-sensitive by default

Searching for "danger" will not match "Danger".

This can be changed later by using query.lower() in line.lower().

No filtering by file type

Right now it attempts to open every file it encounters as text.

Binary files may just not produce meaningful matches, but the errors="ignore" prevents crashes.

No regex support

The search is a plain substring search, not a regular expression search.

Symbolic links

I use os.walk(directory) with its default behavior, which does not follow symbolic links to directories.

That means symlinked directory trees are ignored by default (which avoids potential infinite loops).

6. Requirements and setup

Language / Version

Python 3.9 or higher (I tested with Python 3.x on Windows).

No external dependencies
Only uses the Python standard library:

argparse

os

sys

concurrent.futures

7. How to run the program

From the folder where rts.py lives, run:

python rts.py "<query>" <directory>


Examples:

# Search the songs/ folder for the word "danger"
python rts.py "danger" songs

# Search a deeper path
python rts.py "love" "C:\Users\MyName\Documents"

# Search the entire C: drive (can be slow and noisy)
python rts.py "password" C:\


If the directory doesn’t exist, you’ll see an error like:

Error: 'some/path' is not a directory or does not exist.

8. Testing ideas

Right now, the script is easy to test manually:

Basic match test

Create a small folder with a few .txt files.

Put a known word like hello in one of them.

Run python rts.py "hello" test_folder and check that:

the correct file path

the correct line number

and the correct line text
are printed.

No match test

Use a query that doesn’t appear in any files.

The program should run and print nothing (no errors).

Nested folders test

Put files inside subdirectories and run the tool on the top-level folder.

Confirm it finds matches inside nested folders.

Error handling test

Point it to directories that contain system or protected folders.

You should see “Error reading … Permission denied” messages on stderr, but the program should keep going.

Automated tests (using unittest or pytest) can be added later by creating a tests/ folder, generating some temporary files and folders, and asserting on the script’s output.

9. Possible future improvements

Things I could add later:

-i flag for case-insensitive searches.

--ext .txt .log flag to filter by file extensions.

--regex option to enable regular expression searches using the re module.

Summary statistics at the end:

number of files scanned

number of matches found

time taken


