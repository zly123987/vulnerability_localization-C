import os
import requests
import re


def save_commit_diff_as_file(commit_url, output_file_path):
    """
    Fetches the .diff for a given GitHub commit URL and saves it to a file.

    Args:
    - commit_url (str): The URL of the GitHub commit.
    - output_file_path (str): The path where the .diff file should be saved.

    Returns:
    None
    """
    # Append .diff to the commit URL to get the diff format
    diff_url = commit_url + '.patch'
    
    try:
        # Send a GET request to the diff URL
        response = requests.get(diff_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the response content to a file
            with open(output_file_path, 'w') as file:
                file.write(response.text)
            print(f"Commit diff saved to {output_file_path}")
        else:
            print(f"Failed to fetch commit diff. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")



def parse_diff(diff_text):
    file_changes = []
    file_parts = re.split(r'diff --git a/', diff_text)[1:]  # Split diff by file

    for part in file_parts:
        file_change = {
            'old_file_path': '',
            'new_file_path': '',
            'diffs': []  # This will store multiple diff blocks per file
        }

        # Extract file paths
        # Improved regex to extract file paths
        pattern = re.compile(r'--- a/(.*?)\n\+\+\+ b/(.*?)\n', re.DOTALL)

        # Search for matches
        matches = pattern.findall(part)

        # Extract file paths if matches are found
        if matches:
            file_change['old_file_path'], file_change['new_file_path'] = matches[0]

        # Skip non-Java files and test files
        if not file_change['old_file_path'].endswith('.java') and not file_change['new_file_path'].endswith('.java'):
            continue
        if '/test/' in file_change['old_file_path'].lower() or '/test/' in file_change['new_file_path'].lower() or 'Test.java' in file_change['new_file_path']:
            continue

        # Split into diff blocks
        diff_blocks = re.split(r'@@ -\d+,\d+ \+\d+,\d+ @@', part)[1:]

        for block in diff_blocks:
            diff_change = {
                'removed_lines': [],
                'added_lines': [],
                'context_lines': []
            }

            lines = block.strip().split('\n')

            for line in lines:
                if line.startswith('-'):
                    diff_change['removed_lines'].append(line[1:])
                elif line.startswith('+'):
                    diff_change['added_lines'].append(line[1:])
                else:
                    # End current change if there's context (non-added/removed) line
                    if diff_change['added_lines'] or diff_change['removed_lines']:
                        file_change['diffs'].append(diff_change)
                        diff_change = {'removed_lines': [], 'added_lines': [], 'context_lines': []}
                    diff_change['context_lines'].append(line)

            # Append last change if it has any added or removed lines
            if diff_change['added_lines'] or diff_change['removed_lines'] or diff_change['context_lines']:
                file_change['diffs'].append(diff_change)

        file_changes.append(file_change)

    return file_changes




if __name__ == '__main__':
    # Example usage
    commit_url = 'https://github.com/x-stream/xstream/commit/0fec095d534126931c99fd38e9c6d41f5c685c'

    output_file_path = 'patches/CVE-2020-5229.patch'
    save_commit_diff_as_file(commit_url, output_file_path)
    with open(output_file_path, 'r') as file:
        changes = parse_diff(file.read())
    for file_change in changes:
        print("---------------------------------------------------")
        print("---------------------------------------------------")
        print(f"File: {file_change['old_file_path']} -> {file_change['new_file_path']}")
        for diff in file_change['diffs']:
            print("Added Lines:", diff['added_lines'])
            print("Removed Lines:", diff['removed_lines'])
            print("Context Lines:", diff['context_lines'])
            print("---------------------------------------------------")