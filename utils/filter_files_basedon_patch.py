import csv
import concurrent
import json
import os
import re

from tqdm import tqdm

from main.fine_tune import get_all_files, read_dataset
from config import repo_dir
from config import dataset_name as dataset_file_name
from utils.miscellaneous import checkout_version, get_vulnerable_commit, git_clone
from utils.parse_java import parse_java, parse_java_for_variable
from utils.save_github_commit import parse_diff, save_commit_diff_as_file

def check_funcs_from_each_method(methods, file_path):
    parsed = parse_java(file_path, file_path.split('/')[-1].replace('.java', ''))
    for method in methods:
        # if method starts with a big letter, means it is a class
        if method[0].isupper():
            for clazz in parsed['classes']:
                if clazz['name'] == method or method == clazz['name']:
                    ret = []
                    for real_method in clazz['methods']:
                        ret.append({
                            'name': real_method['name'],
                            'body': real_method['body'],
                            'comment': real_method['comment'],
                            'class': clazz['name'],
                            'file': file_path
                            
                        })
                    return ret
        else:
            for clazz in parsed['classes']:
                for m in clazz['methods']:
                    if m['name'] == method:
                        return [{
                            'name': m['name'],
                            'body': m['body'],
                            'comment': m['comment'],
                            'class': clazz['name'],
                            'file': file_path
                        }]

def check_each_method(methods, file_path):
    parsed = parse_java(file_path, file_path.split('/')[-1].replace('.java', ''))
    
    if 'Yaml'in file_path:
        print(file_path)
    for method in methods:
        # if method starts with a big letter, means it is a class
        if method[0].isupper():
            for clazz in parsed['classes']:
                if clazz['name'] == method or method == clazz['name']:
                    return file_path
        else:
            for clazz in parsed['classes']:
                for m in clazz['methods']:
                    if m['name'] == method:
                        return file_path


def get_repo_files(repo):
    list_to_do = list()
    for root, dir, fs in os.walk(os.path.join(repo_dir, repo)):         
        for f in fs:
            if not f.endswith('.java'):
                continue
            if 'test' in f.lower() or '/mock/' in f.lower():
                continue
            file_path = os.path.join(root, f)
            list_to_do.append(file_path)

    print('list to do', len(list_to_do))
    return list_to_do

def search_funcs_from_method_or_class(repo, methods):
    target_funcs = []
    list_to_do = get_all_files(repo)
    # Using ThreadPoolExecutor to execute the function concurrently
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Using a list to store futures
        futures = []
        
        for item in list_to_do:
            # Submitting the function to be executed with fixed arguments and an element from the list
            future = executor.submit(check_funcs_from_each_method, methods, item)
            futures.append(future)
        
        # Gathering results (if needed)
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc='Processing Files: '):
            try:
                result = future.result()
                if result:
                    target_funcs.append(result) 
            except Exception as exc:
                print(f"Generated an exception: {exc}")
    return target_funcs

def search_method_or_class(repo, methods):
    target_files = []
    list_to_do = get_all_files(repo)
    # Using ThreadPoolExecutor to execute the function concurrently
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Using a list to store futures
        futures = []
        
        for item in list_to_do:
            # Submitting the function to be executed with fixed arguments and an element from the list
            future = executor.submit(check_each_method, methods, item)
            futures.append(future)
        
        # Gathering results (if needed)
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc='Processing Files: '):
            try:
                result = future.result()
                if result:
                    target_files.append(result) 
            except Exception as exc:
                print(f"Generated an exception: {exc}")
    return target_files


def check_funcs_from_each_variable(variables, file_path):
    funcs = []
    parsed = parse_java_for_variable(file_path, file_path.split('/')[-1].replace('.java', ''))
    for clazz in parsed['classes']:
        for method in clazz['methods']:
            for v  in variables:
                if v in method['varRef'] or v in method['varDef']:
                    funcs.append({
                        'name': method['name'],
                        'body': method['body'],
                        'comment': method.get('comment', ''),
                        'class': clazz['name'],
                        'file': file_path
                    })
    if len(funcs) > 0:
        return funcs
    else:
        for clazz in parsed['classes']:
            for v  in variables:
                if v in clazz['varRef'] or v in clazz['varDef']:
                    for method in clazz['methods']:
                        funcs.append({
                            'name': method['name'],
                            'body': method['body'],
                            'comment': method.get('comment', ''),
                            'class': clazz['name'],
                            'file': file_path
                        })
                    
    return funcs


def check_each_variable(variables, file_path):
    parsed = parse_java_for_variable(file_path, file_path.split('/')[-1].replace('.java', ''))
    for clazz in parsed['classes']:
        for v  in variables:
            if v in clazz['varRef'] or v in clazz['varDef']:
                return file_path
    return None


def search_funcs_from_variables(repo, variables):
    list_to_do = get_all_files(repo)
    target_funcs = []
    # Using ThreadPoolExecutor to execute the function concurrently
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Using a list to store futures
        futures = []
        
        for item in list_to_do:
            # Submitting the function to be executed with fixed arguments and an element from the list
            future = executor.submit(check_funcs_from_each_variable, variables, item)
            futures.append(future)
        
        # Gathering results (if needed)
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    target_funcs.append(result) 
            except Exception as exc:
                print(f"Generated an exception: {exc}")
    return target_funcs


def search_variables(repo, variables):
    list_to_do = get_repo_files(repo)
    target_files = []
    # Using ThreadPoolExecutor to execute the function concurrently
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Using a list to store futures
        futures = []
        
        for item in list_to_do:
            # Submitting the function to be executed with fixed arguments and an element from the list
            future = executor.submit(check_each_variable, variables, item)
            futures.append(future)
        
        # Gathering results (if needed)
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    target_files.append(result) 
            except Exception as exc:
                print(f"Generated an exception: {exc}")
    return target_files

def find_cve_in_dataset(cve, dataset):
    for data in dataset:
        if data['cve'] == cve:
            return data
    return None

def search_files_from_patch_tool(dataset='benchmark'):
    if dataset == 'benchmark':
        if os.path.exists('with_patch_results/target_files_from_patch_benchmark.json'):
            tool_result = json.load(open('with_patch_results/target_files_from_patch_benchmark.json', 'r'))
        else:
            tool_result = {}
        if os.path.exists('with_patch_results/original_patch_results_benchmark.json'):
            original_patch_results = json.load(open('with_patch_results/original_patch_results_benchmark.json', 'r'))
        else:
            original_patch_results = {}
        dataset = read_dataset('data/xxx data - filtered_cve_with_link.csv')
        with open('with_patch_results/results_benchmark.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for i, row in enumerate(reader):

                # skip processed cve
                # if row[0] in tool_result and row[0] in original_patch_results:
                #     continue

                # Prepare the data
                data = find_cve_in_dataset(row[0], dataset)
                if not data:
                    continue
                cve = data['cve']


                # for debug
                if cve !='CVE-2017-5617':
                    continue

                if data['same_location'] == '':
                    continue
                print(i, '########## Current cve:', cve)
                if cve != row[0]:
                    print('cve not match', cve, row[0])
                    exit()
                repo = data['repo']
                version = data['version']
                repo_path = os.path.join(repo_dir,repo)
                output_file_path = 'patches/'+cve+'.patch'
                commit_url = data['commit_url']
                if not os.path.exists(repo_path) or repo=='jetty.project':
                    print('cloning', repo)
                    git_clone(repo, data['repo_link'])

                # clone failed
                if not os.path.exists(repo_path):
                    continue

                version = get_vulnerable_commit(output_file_path, commit_url, repo_path, version)
                checkout_version(repo_path, version, cve)

                # Get directly from patches
                patch_files = get_patch_files(cve, output_file_path, commit_url, repo_path)
                original_patch_results[cve] = patch_files


                # Get from tools
                if row[1] == 'No commit file':
                    continue
                if 'No such file or directory' in row[1]:
                    print(row[0])
                    print(row[1])
                    print('-------------------')
                    continue
                target_files = []
                if 'Final result:' in row[1]:
                    reason = row[2]
                    
                    # the result is a method or class
                    if reason == 'Replaced invocation' or reason == 'Arguments changed' or reason == 'Removed method' or reason == 'Deprecated method':
                        methods = row[1].replace('Final result:', '').strip().split('|')
                        target_files = search_method_or_class(repo, methods)
                        print(row[0], target_files)
                    # the result is a variable
                    elif reason == 'Configuration changed':
                        variables = row[1].replace('Final result:', '').strip().split('|')
                        target_files = search_variables(repo, variables)
                        print(row[0], target_files)
                tool_result[row[0]] = target_files
                with open('with_patch_results/original_patch_results_benchmark.json', 'w') as f:
                    json.dump(original_patch_results, f)
                with open('with_patch_results/target_files_from_patch_benchmark.json', 'w') as f:
                    json.dump(tool_result, f)
    elif dataset == 'real_world':
        if os.path.exists('with_patch_results/target_files_from_patch_real_world.json'):
            tool_result = json.load(open('with_patch_results/target_files_from_patch_real_world.json', 'r'))
        else:
            tool_result = {}
        if os.path.exists('with_patch_results/original_patch_results_real_world.json'):
            original_patch_results = json.load(open('with_patch_results/original_patch_results_real_world.json', 'r'))
        else:
            original_patch_results = {}
        dataset = read_dataset(dataset_name)
        with open('with_patch_results/results.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for i, row in enumerate(reader):

                # skip processed cve
                if row[0] in tool_result and row[0] in original_patch_results:
                    continue

                # Prepare the data
                data = find_cve_in_dataset(row[0], dataset)
                if not data:
                    continue
                # only process CVEs with patches 
                if data['commit_url']== '':
                    continue
                cve = data['cve']
                # if cve !='CVE-2020-1953':
                #     continue
                if data['same_location'] != '':
                    continue
                print(i, '########## Current cve:', cve)
                if cve != row[0]:
                    print('cve not match', cve, row[0])
                    exit()
                repo = data['repo']
                version = data['version']
                repo_path = os.path.join(repo_dir,repo)
                output_file_path = 'patches/'+cve+'.patch'
                commit_url = data['commit_url']
                if not os.path.exists(repo_path):
                    print('cloning', repo)
                    git_clone(repo, data['repo_link'])

                # clone failed
                if not os.path.exists(repo_path):
                    continue

                version = get_vulnerable_commit(output_file_path, commit_url, repo_path, version)
                checkout_version(repo_path, version, cve)

                # Get directly from patches
                patch_files = get_patch_files(cve, output_file_path, commit_url, repo_path)
                original_patch_results[cve] = patch_files


                # Get from tools
                if row[1] == 'No commit file':
                    continue
                if 'No such file or directory' in row[1]:
                    print(row[0])
                    print(row[1])
                    print('-------------------')
                    continue
                target_files = []
                if 'Final result:' in row[1]:
                    reason = row[2]
                    
                    # the result is a method or class
                    if reason == 'Replaced invocation' or reason == 'Arguments changed' or reason == 'Removed method' or reason == 'Deprecated method':
                        methods = row[1].replace('Final result:', '').strip().split('|')
                        target_files = search_method_or_class(repo, methods)
                        print(row[0], target_files)
                    # the result is a variable
                    elif reason == 'Configuration changed':
                        variables = row[1].replace('Final result:', '').strip().split('|')
                        target_files = search_variables(repo, variables)
                        print(row[0], target_files)
                tool_result[row[0]] = target_files
                with open('with_patch_results/original_patch_results_real_world.json', 'w') as f:
                    json.dump(original_patch_results, f)
                with open('with_patch_results/target_files_from_patch_real_world.json', 'w') as f:
                    json.dump(tool_result, f)


    else:
        if os.path.exists('with_patch_results/target_files_from_patch.json'):
            tool_result = json.load(open('with_patch_results/target_files_from_patch.json', 'r'))
        else:
            tool_result = {}
        if os.path.exists('with_patch_results/original_patch_results.json'):
            original_patch_results = json.load(open('with_patch_results/original_patch_results.json', 'r'))
        else:
            original_patch_results = {}
        dataset = read_dataset('data/xxx data - filtered_cve_with_link.csv')
        with open('with_patch_results/results.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for i, row in enumerate(reader):

                # skip processed cve
                if row[0] in tool_result and row[0] in original_patch_results:
                    continue

                # Prepare the data
                data = find_cve_in_dataset(row[0], dataset)
                if not data:
                    continue
                cve = data['cve']
                # if cve !='CVE-2020-1953':
                #     continue
                if data['same_location'] != '':
                    continue
                print(i, '########## Current cve:', cve)
                if cve != row[0]:
                    print('cve not match', cve, row[0])
                    exit()
                repo = data['repo']
                version = data['version']
                repo_path = os.path.join(repo_dir,repo)
                output_file_path = 'patches/'+cve+'.patch'
                commit_url = data['commit_url']
                if not os.path.exists(repo_path) or repo=='jetty.project':
                    print('cloning', repo)
                    git_clone(repo, data['repo_link'])

                # clone failed
                if not os.path.exists(repo_path):
                    continue

                version = get_vulnerable_commit(output_file_path, commit_url, repo_path, version)
                checkout_version(repo_path, version, cve)

                # Get directly from patches
                patch_files = get_patch_files(cve, output_file_path, commit_url, repo_path)
                original_patch_results[cve] = patch_files


                # Get from tools
                if row[1] == 'No commit file':
                    continue
                if 'No such file or directory' in row[1]:
                    print(row[0])
                    print(row[1])
                    print('-------------------')
                    continue
                target_files = []
                if 'Final result:' in row[1]:
                    reason = row[2]
                    
                    # the result is a method or class
                    if reason == 'Replaced invocation' or reason == 'Arguments changed' or reason == 'Removed method' or reason == 'Deprecated method':
                        methods = row[1].replace('Final result:', '').strip().split('|')
                        target_files = search_method_or_class(repo, methods)
                        print(row[0], target_files)
                    # the result is a variable
                    elif reason == 'Configuration changed':
                        variables = row[1].replace('Final result:', '').strip().split('|')
                        target_files = search_variables(repo, variables)
                        print(row[0], target_files)
                tool_result[row[0]] = target_files
                with open('with_patch_results/original_patch_results.json', 'w') as f:
                    json.dump(original_patch_results, f)
                with open('with_patch_results/target_files_from_patch.json', 'w') as f:
                    json.dump(tool_result, f)

def search_func_from_patch_tool(dataset_name='benchmark'):
    # select datasets
    if dataset_name == 'benchmark':
        target_file_name = 'with_patch_results/target_funcs_from_patch_benchmark.json'
        original_file_name = 'with_patch_results/original_patch_funcs_benchmark.json'
        data_file = 'with_patch_results/results_benchmark.csv'

    elif dataset_name == 'real_world':
        target_file_name = 'with_patch_results/target_funcs_from_patch_real_world.json'
        original_file_name = 'with_patch_results/original_patch_funcs_real_world.json'
        data_file = 'with_patch_results/results.csv'
    else:
        target_file_name = 'with_patch_results/target_funcs_from_patch.json'
        original_file_name = 'with_patch_results/original_patch_funcs.json'
        data_file = 'with_patch_results/results.csv'



    if os.path.exists(target_file_name):
        tool_result = json.load(open(target_file_name, 'r'))
    else:
        tool_result = {}
    if os.path.exists(original_file_name):
        original_patch_results = json.load(open(original_file_name, 'r'))
    else:
        original_patch_results = {}
    dataset = read_dataset(dataset_file_name)
    with open(data_file, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for i, row in enumerate(reader):
            # if row[0] !='CVE-2024-28847':
            #     continue
            # skip processed cve

            if row[0] in tool_result and row[0] in original_patch_results:
                continue
            # Prepare the data
            data = find_cve_in_dataset(row[0], dataset)
            if not data:
                continue
            cve = data['cve']
            # for debug

            # if original_patch_results.get(cve):
            #     continue
            if dataset_name == 'benchmark':
                if data['same_location'] == '':
                    continue
            elif dataset_name == 'real_world':
                pass
            else:
                if data['same_location'] != '':
                    continue
            print(i, '########## Current cve:', cve)
            if cve != row[0]:
                print('cve not match', cve, row[0])
                exit()
            repo = data['repo']
            version = data['version']
            repo_path = os.path.join(repo_dir,repo)
            output_file_path = 'patches/'+cve+'.patch'
            commit_url = data['commit_url']
            if not os.path.exists(repo_path):
                print('cloning', repo)
                git_clone(repo, data['repo_link'])

            # clone failed
            if not os.path.exists(repo_path):
                continue

            version = get_vulnerable_commit(output_file_path, commit_url, repo_path, version)
            checkout_version(repo_path, version, cve)

            # Get directly from patches
            original_patch_results[cve] = []
            patch_files = get_patch_funcs(cve, output_file_path, commit_url, repo_path)
            for patch_file, funcs in patch_files.items():
                all_funcs = extract_funcs_from_file(patch_file)
                for func in all_funcs:
                    if func['name'] in funcs:
                        original_patch_results[cve].append(func)
                if len(original_patch_results[cve]) ==0:
                    original_patch_results[cve].extend(all_funcs)




            # Get from tools
            if row[1] == 'No commit file':
                continue
            if 'No such file or directory' in row[1]:
                print(row[0])
                print(row[1])
                print('-------------------')
                continue
            target_methods = []
            if 'Final result:' in row[1]:
                reason = row[2]
                
                # the result is a method or class
                if reason == 'Replaced invocation' or reason == 'Arguments changed' or reason == 'Removed method' or reason == 'Deprecated method':
                    methods = row[1].replace('Final result:', '').strip().split('|')
                    target_funcs = search_funcs_from_method_or_class(repo, methods)
                    target_methods.extend(target_funcs)
                    
                # the result is a variable
                elif reason == 'Configuration changed':
                    variables = row[1].replace('Final result:', '').strip().split('|')
                    target_funcs = search_funcs_from_variables(repo, variables)
                    target_methods.extend(target_funcs)

            print(row[0], len(target_methods))
            tool_result[row[0]] = target_methods
            with open(original_file_name, 'w') as f:
                json.dump(original_patch_results, f)
            with open(target_file_name, 'w') as f:
                json.dump(tool_result, f)


def extract_funcs_from_file(file):
    parsed = parse_java(file, file.split('/')[-1].replace('.java', ''))
    funcs = []
    if not parsed:
        return funcs
    for clazz in parsed['classes']:
        for m in clazz['methods']:
            funcs.append({
                'name': m['name'],
                'body': m['body'],
                'comment': m['comment'],
                'class': clazz['name'],
                'file': file
            })
    return funcs


def get_patch_funcs(cve, output_file_path, commit_url, repo_path):
    funcs = {}
    # Regex pattern to match Java method names
    pattern = r"\b(public|protected|private)?\s*(([\w.]+)\s+)?(\w+)\s*\("
    if not os.path.exists(output_file_path):
        save_commit_diff_as_file(commit_url, output_file_path)
    if not os.path.exists(output_file_path):
        with open('with_patch_results/patch_file_availability.csv', 'a') as f:
            f.write(cve+',No patch file\n')
        return funcs
    with open(output_file_path, 'r') as file:
        changes = parse_diff(file.read())
        # Serialize the parsed changes to JSON
        json_output = json.dumps(changes, indent=4)
        # Save the JSON to a file
        with open(f"patches/{cve}_parsed_diffs.json", "w") as json_file:
            json_file.write(json_output)
        for change in changes:
            old_file = change['old_file_path']

            if os.path.exists(os.path.join(repo_path, old_file)):
                function_names = []
                for diff in change['diffs']:
                    # for removed lines
                    for line in diff['removed_lines']:
                        match = re.search(pattern, line)
                        if match:
                            function_names.append(match.group(4))
                    # for context lines
                    for line in diff['context_lines']:
                        match = re.search(pattern, line)
                        if match:
                            function_names.append(match.group(4))
                funcs[os.path.join(repo_path, old_file)] = list(set(function_names))

            else:
                with open('with_patch_results/patch_file_availability.csv', 'a') as f:
                    f.write(cve+',no such file,'+os.path.join(repo_path, old_file)+'\n')
    return funcs

def get_patch_files(cve, output_file_path, commit_url, repo_path):
    patch_files = []
    if not os.path.exists(output_file_path):
        save_commit_diff_as_file(commit_url, output_file_path)
    if not os.path.exists(output_file_path):
        with open('with_patch_results/patch_file_availability.csv', 'a') as f:
            f.write(cve+',No patch file\n')
        return patch_files
    with open(output_file_path, 'r') as file:
        changes = parse_diff(file.read())
        # Serialize the parsed changes to JSON
        json_output = json.dumps(changes, indent=4)
        # Save the JSON to a file
        with open(f"patches/{cve}_parsed_diffs.json", "w") as json_file:
            json_file.write(json_output)
        for change in changes:
            old_file = change['old_file_path']
            if os.path.exists(os.path.join(repo_path, old_file)):
                patch_files.append(os.path.join(repo_path, old_file))
            else:
                with open('with_patch_results/patch_file_availability.csv', 'a') as f:
                    f.write(cve+',no such file,'+os.path.join(repo_path, old_file)+'\n')
    return patch_files




    