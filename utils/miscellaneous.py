import csv
import os
import re
import subprocess
import json
from config import repo_dir, mongo_db
from utils.save_github_commit import save_commit_diff_as_file


def get_all_documents():
    with open('data/all_docs_incomplete.json') as f:
        data = list(json.load(f).values())
        data = [item for sublist in data for item in sublist]
    return data

def get_func_hash(func):
    return hash(func['body'])

def get_func_id(func):
    if 'file' in func:
        return func['name']+'@'+func['file'].split('/maven_repos/')[-1]
    if 'file_path' in func:
        return func['name']+'@'+func['file_path'].split('/maven_repos/')[-1]

def get_body(func):
    if func['comment']:
        return func['comment']+'\n'+func['body']
    else:
        return func['body']

def get_cwe_dict():
    cwe_dict = {}
    with open('materials/1000.csv') as f:
        for line in csv.reader(f):
            cwe_dict[line[0]] = line[1]
    return cwe_dict


def git_clone(repo, url):
    # if repo =='jetty.project':
    #     os.system('rm -rf '+repo_dir+'jetty.project')
    cwd = os.getcwd()
    os.chdir(repo_dir)
    command = ['git', 'clone', url, repo]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully cloned '{url}' to '{repo}'")
    except subprocess.CalledProcessError:
        print(f"Failed to clone '{url}' to '{repo}'. Command: {' '.join(command)}")
    os.system('git config --global --add safe.directory /data/ubuntu/maven_repos/'+repo)
    os.chdir(cwd)

def get_parent_commit(commit_hash, repo):
    cwd = os.getcwd()
    os.chdir(repo)
    # Command to get the parent commit of the given commit hash
    command = ["git", "rev-parse", "{}^".format(commit_hash)]
    
    try:
        # Execute the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # The parent commit hash is in the stdout attribute
        parent_commit_hash = result.stdout.strip()
        os.chdir(cwd)
        return parent_commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        os.chdir(cwd)
        return None

def get_parent_commit_of_file(output_file_path, commit_url, repo):
    version = None
    if not os.path.exists(output_file_path):
        save_commit_diff_as_file(commit_url, output_file_path)
    if os.path.exists(output_file_path):
        # Example patch file content as a string
        # Regular expression to match the commit hash
        commit_hash_pattern = re.compile(r'^From (\w+) ')

        # Search for the commit hash
        match = commit_hash_pattern.search(open(output_file_path).read())
        if match:
            commit_hash = match.group(1)
            next_commit  = get_parent_commit(commit_hash, repo)
            version = next_commit
    return version

def get_fix_commit(output_file_path, commit_url):
    version = None
    if not os.path.exists(output_file_path):
        save_commit_diff_as_file(commit_url, output_file_path)
    if os.path.exists(output_file_path):
        # Example patch file content as a string
        # Regular expression to match the commit hash
        commit_hash_pattern = re.compile(r'^From (\w+) ')

        # Search for the commit hash
        match = commit_hash_pattern.search(open(output_file_path).read())
        if match:
            commit_hash = match.group(1)
            version = commit_hash
    return version

def get_vulnerable_commit(output_file_path, commit_url, repo, default_version):
    version = default_version
    parent_commmit = get_parent_commit_of_file(output_file_path, commit_url, repo)
    if parent_commmit:
        version = parent_commmit
    return version

def checkout_version(repo, version, cve):
    cwd = os.getcwd()
    os.chdir(repo)
    command = ['git', 'checkout', '-f', version]
    try:
        subprocess.run(command, check=True)
        print(f"Successfully checked out branch '{version}'")
    except subprocess.CalledProcessError:
        print(f"Failed to checkout branch '{version}'. Command: {' '.join(version)}")
        # os.chdir(cwd)
        # with open('with_patch_results/results.csv', 'a') as f:
        #     f.write(cve+',Failed to checkout branch\n')
    os.chdir(cwd)

def extract_semver(text):
    # Regex pattern to match the numeric part of the version number
    pattern = r'[0-9]+\.[0-9]+\.[0-9]+'

    # Search for the pattern in the text
    match = re.search(pattern, text)

    if match:
        version_number = match.group(0)
        return version_number

    else:
        # Regex pattern to match the numeric part of the version number
        pattern = r'[0-9]+\.[0-9]+'

        # Search for the pattern in the text
        match = re.search(pattern, text)
        if match:
            version_number = match.group(0)
            return version_number
        else:
            print("No version number found", text)
            return text

def read_mongodb_file_properties(repo, cve, versions, c):
    coll = c[mongo_db]['repo_vectors']
    tf_idf_coll = c[mongo_db]['tf-idf']
    tf_idf_doc = tf_idf_coll.find_one({'cve': cve})
    class_names = {each.split('@')[-1] for each in tf_idf_doc['top-k']}
    res = []
    added_set = set()
    versions = [extract_semver(each) for each in versions]
    coll.create_index('repo')

    for doc in coll.find({'repo': repo}):
        # ensure class is not filtered out by tf-idf
        if doc['class'] in added_set:
            continue
        if doc['class'] not in class_names:
            continue
        if extract_semver(doc['version']) in versions or extract_semver(doc['version']) in '|'.join(versions).replace('_', '.'):
            res.append(doc)
            added_set.add(doc['class'])


    return res


def get_next_version(repo_path, version, output_file_path, commit_url):
    fix_commit = get_fix_commit(output_file_path, commit_url)
    if fix_commit:
        version = fix_commit
        return version
    tags = subprocess.check_output(['git', 'tag'], cwd=repo_path).decode().strip().split('\n')
    if version in tags and tags.index(version) < len(tags) - 1:
        return tags[tags.index(version)+1]
    else:
        print('Next version not found, back to', version)
        return version
    
def normalize_file_path(file_path):
    return file_path.split('maven_repos/')[-1]