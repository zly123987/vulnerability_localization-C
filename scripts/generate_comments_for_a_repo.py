import pymongo
from utils.tf_idf_similarity import calculate_tfidf_cosine_similarity
from config import repo_dir, mongodb_host, mongodb_port, mongo_db
import os
import concurrent.futures
from utils.gen_comment import get_summary_codeTransT5, summarize_parsed
from utils.parse_java import parse_java
from utils.parse_pom_gav import parse_pom
import pandas as pd

def gen_comments_4_repo(repo, c):
    coll = c[mongo_db]['repo_summary']
    coll.create_index('id')
    gav_dict = {}
    list_to_do = list()
    for root, dir, fs in os.walk(os.path.join(repo_dir, repo)):
        if os.path.exists(os.path.join(root, 'pom.xml')):
            file_path = os.path.join(root, 'pom.xml')
            data = parse_pom(file_path)
            gav = data.get('groupId')+'|'+data.get('artifactId')+'|'+data.get('version')
            gav_dict[root] = gav
          
        for f in fs:
            if not f.endswith('.java') or not '/src/main/java/' in root:
                continue
            file_path = os.path.join(root, f)
            # get gav
            if root.split('/src/main/java/')[0] in gav_dict:
                gav = gav_dict.get(root.split('/src/main/java/')[0])

            # get class
            clazz = f.replace('.java', '')

            # get id, skip visited
            id = gav+'@'+clazz
            if coll.find_one({'id':id}):
                continue
            
            file_sig = id+'&&'+file_path + '&&'+gav+'&&'+repo
            list_to_do.append(file_sig)
    print('list to do', len(list_to_do))
    with concurrent.futures.ProcessPoolExecutor(1) as executor:
        executor.map(one_file, list_to_do)



def one_file(args):
    try:
        current_doc_num, all_count, sig = args
        c = pymongo.MongoClient(mongodb_host,
                                port=mongodb_port)
        coll = c[mongo_db]['repo_summary_nl_filter']

        id, file_path, gav, repo, cve = sig.split('&&')

        # g, a, _ = gav.split('|')
        if not os.path.exists(file_path):
            return
        parsed = parse_java(file_path, id.split('@')[-1])
        parsed = summarize_parsed(parsed)
        doc = {
            'id': id,
            'repo': repo,
            'gav': gav,
            'cve': cve,
            # 'class': clazz,
            # 'sum': sum,
            'meta': parsed,
            # "group": g,
            # 'artifact': a,
            # 'ga': g+'|'+a,
            'repo': repo
        }

        coll.update_one({'id': id}, {'$set': doc}, upsert=True)
        print(coll.count_documents({})- current_doc_num, '/', all_count , id)
    except Exception as e:
        print('Exception:', e)
    c.close()



        
        