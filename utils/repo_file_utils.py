import csv
import json
import os
from config import fine_tuned_bert_folder, dataset as dataset_name
from main.fine_tune import read_dataset
def read_relevant_files(repo_path):
    all_files = []
    for root, dir, fs in os.walk(repo_path):
        for f in fs:
            if not f.endswith('.java') or 'test' in root or 'Test' in root:
                continue
            file_path = os.path.join(root, f)
            try:
                all_files.append(file_path)  
            except: 
                pass
    return all_files




def read_filtered_funcs(choice='filter_first'):
    if choice == 'filter_first':
        if dataset_name == 'benchmark':
            with open('with_patch_results/target_funcs_from_patch_benchmark.json', 'r') as f:
                targets = json.load(f)
            with open('with_patch_results/original_patch_funcs_benchmark.json', 'r') as f:
                original = json.load(f)
            ret = {}
            ds = read_dataset('data/xxx data - filtered_cve_with_link.csv')
            for each in ds:
                cve = each['cve']
                ret[cve] = []
                if cve in targets:
                    for e in targets[cve]:
                        ret[cve].extend(e)
                if cve in original:
                    ret[cve].extend(original[cve])
            return ret
        elif dataset_name == 'real_world':
            with open('with_patch_results/target_funcs_from_patch_real_world.json', 'r') as f:
                targets = json.load(f)
            with open('with_patch_results/original_patch_funcs_real_world.json', 'r') as f:
                original = json.load(f)
            ret = {}
            dataset = read_dataset('data/xxx data - real-world.csv')
            for each in dataset:
                cve = each['cve']
                ret[cve] = []
                if cve in targets:
                    for e in targets[cve]:
                        ret[cve].extend(e)
                if cve in original:
                    ret[cve].extend(original[cve])
            return ret
    elif choice == 'filter_first_patch_only':
        return read_patched_funcs_only()
    
    elif choice == 'fine_tuned_bert':
        ret = {}
        for f in os.listdir(fine_tuned_bert_folder):
            if f.endswith('.json'):
                with open(fine_tuned_bert_folder+'/'+f) as fp:
                    cve = f.replace('top000_', '').replace('.json', '')
                    ret[cve] = json.load(fp)['funcs'][:100]
        return ret
    else:
        return {}

def read_filtered_files(choice='filter_first'):
    if choice == 'filter_first':
        with open('with_patch_results/target_files_from_patch_benchmark.json', 'r') as f:
            targets = json.load(f)
        with open('with_patch_results/original_patch_results_benchmark.json', 'r') as f:
            original = json.load(f)
        ret = {}
        dataset = read_dataset('data/xxx data - filtered_cve_with_link.csv')
        for each in dataset:
            cve = each['cve']
            ret[cve] = []
            if cve in targets:
                ret[cve].extend(targets[cve])
            if cve in original:
                ret[cve].extend(original[cve])
            # if len(ret[cve]) == 0:
            #     print('no files for:', cve) 
            a=1
        return ret
    elif choice == 'filter_first_patch_only':
        return read_patched_files_only()
    else:
        return {}
    
    
def read_patched_funcs_only():
    with open('with_patch_results/original_patch_funcs_benchmark.json', 'r') as f:
        original = json.load(f)
    ret = {}
    dataset = read_dataset('data/xxx data - filtered_cve_with_link.csv')
    for each in dataset:
        cve = each['cve']
        ret[cve] = []
        if cve not in original:
            break
        ret[cve].extend(original[cve])
    return ret

def read_patched_files_only():
    with open('with_patch_results/original_patch_results_benchmark.json', 'r') as f:
        original = json.load(f)
    ret = {}
    dataset = read_dataset('data/xxx data - filtered_cve_with_link.csv')
    for each in dataset:
        cve = each['cve']
        ret[cve] = []
        if cve not in original:
            break
        ret[cve].extend(original[cve])
    return ret

