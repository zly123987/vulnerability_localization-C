import json
import os
import concurrent.futures
import pymongo
from tqdm import tqdm

from utils.knowledge_graph import process_corpus
from utils.miscellaneous import get_body
from config import mongodb_host, mongodb_port, mongo_db

def for_one(args):
    cve, i = args
    # print(i, cve)
    

    with open('funcs/'+cve+'/saved_funcs.json') as f:
        list_of_funcs = json.load(f)
        docs = [process_corpus(get_body(each)) for each in list_of_funcs]

    return cve, docs
def organize_all_docs_for_tf_idf():
    c = pymongo.MongoClient(mongodb_host, mongodb_port)
    desc_coll = c[mongo_db]['dissected_description']
    if os.path.exists('data/all_docs.json'):
        with open('data/all_docs.json') as f:
            all_docs = json.load(f)
    else:
        all_docs = {}

    list_to_do = []
    for i, cve in enumerate(os.listdir('funcs')):
        if cve in all_docs:
            continue
        list_to_do.append((cve, i))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Using a list to store futures
        futures = []
        
        for item in list_to_do:
            # Submitting the function to be executed with fixed arguments and an element from the list
            future = executor.submit(for_one, item)
            futures.append(future)
        
        # Gathering results (if needed)
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            try:
                cve, docs = future.result()
                
                dissected_description = desc_coll.find_one({'cve_id': cve})
                if not dissected_description:
                    with open('data/all_docs.json', 'w') as fw:
                        fw.write(json.dumps(all_docs))
                    continue

                original_description = dissected_description['description']
                docs.append(process_corpus(original_description))
                all_docs[cve] = docs
            except Exception as exc:
                print(f"Generated an exception: {exc}")

            with open('data/all_docs.json', 'w') as fw:
                fw.write(json.dumps(all_docs))

    # for cve, docs in all_docs.items():

    # with open('data/all_docs.json', 'w') as fw:
    #     fw.write(json.dumps(all_docs))
# organize_all_docs_for_tf_idf()