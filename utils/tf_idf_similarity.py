import json
import os
import re
import pandas as pd
import numpy as np
from config import repo_dir, mongo_db, query_expansion_choice, retrieval_approach_choice, final_results_coll
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertModel, BertTokenizer
from matplotlib import pyplot as plt
from scripts.Lmethod import find_elbow_Lmethod
from utils.knowledge_graph import get_cve_documents, process_corpus
from utils.miscellaneous import get_body, normalize_file_path, get_all_documents
from utils.parse_pom_gav import parse_pom

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def split_camel_case(sentence):
    # Check for 'IDs' and replace it with a placeholder
    sentence = sentence.replace('IDs', '[*Placeholder*]')
    # Split lower and upper camel words into multiple words
    # while keeping consecutive uppercase letters together
    words = re.sub(r'([a-z0-9])([A-Z])|([A-Z])([A-Z][a-z])', r'\1\3 \2\4', sentence).split(' ')
    ret = []
    tmp = ''
    for word in words:
        if tmp:
            if len(word) == 1 and re.match(r'^[A-Z]$', word):
                tmp += word
            else:
                ret.append(tmp)
                ret.append(word)
        else:
            ret.append(word)
    ret = ' '.join(ret)
    ret = ret.replace('[*Placeholder*]', 'IDs')
    return ret

def dot_split(identifier):
    return identifier.replace('.', ' ').replace('#', ' ')
    # return re.sub(r'\w+\.\w+', '\w+ \w+', identifier, flags=re.MULTILINE)

def remove_imports(java_code):
    # Removes all lines that start with 'import'
    java_code = re.sub(r'^import.*\n?', '', java_code, flags=re.MULTILINE)
    java_code = re.sub(r'^package.*\n?', '', java_code, flags=re.MULTILINE)
    return java_code

def tokenize_description(desc):
    desc = dot_split(desc)
    desc = split_camel_case(desc)
    tokens = re.split(r'\W+', desc)  # split on non-word characters
    # Handle CamelCase
    # tokens = [camel_case_split(token) for token in tokens]
    # Flatten list and convert to lower case
    tokens = [token.lower() for token in tokens]
    return ' '.join(tokens)

def tokenize_java_code(code):
    code = remove_imports(code)
    code = split_camel_case(code)
    tokens = re.split(r'\W+', code)  # split on non-word characters
    # Handle CamelCase
    # tokens = [camel_case_split(token) for token in tokens]
    # Flatten list and convert to lower case
    tokens = [token.lower() for token in tokens]
    return ' '.join(tokens)

def skip_interface_abstract(dict_of_java_files):
    # comment it out for now
    files = []
    # skip interface and abstract
    for key in dict_of_java_files:
        path = dict_of_java_files[key]['path']
        try:
            with open(path, 'r') as f:
                code = f.read()
                # if 'public interface ' in code:
                #     continue
                files.append(code)
        except:
            pass
    return files

def rank_java_methods_by_vulnerability(java_methods, vulnerability_desc, all_docs):
    """
    Ranks Java method code snippets based on their TF-IDF similarity to a vulnerability description, 
    considering a broader set of documents for TF-IDF calculation.
    
    :param java_methods: A list of dictionaries, each containing 'name', 'body', and 'file' for each Java method.
    :param vulnerability_desc: A string describing the vulnerability.
    :param all_docs: A list of additional documents to consider for the TF-IDF calculations.
    :return: A list of dictionaries with 'file', 'name', and 'similarity_score', ranked by descending similarity.
    """
    # Combine the vulnerability description, Java method bodies, and all additional documents
    documents = [vulnerability_desc] + [f['body'] for f in java_methods] + all_docs
    
    # Compute TF-IDF vectors, considering all documents
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Compute similarity scores between the vulnerability description and each Java method
    # Note: The first document is the vulnerability description, and the following documents are Java methods.
    # The rest are the additional documents from all_docs, which contribute to the TF-IDF calculations but are not compared directly.
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:len(java_methods)+1])
    
    # Flatten the similarity scores to a 1D array for easier indexing
    similarity_scores_flattened = similarity_scores.flatten()
    
    # Rank the Java methods based on similarity scores
    ranked_indices = np.argsort(similarity_scores_flattened)[::-1]
    
    # Prepare the ranked list of Java methods with their file paths, names, and similarity scores
    ranked_methods = [
        {
            'file': java_methods[idx]['file'],
            'name': java_methods[idx]['name'],
            'similarity_score': similarity_scores_flattened[idx]
        } for idx in ranked_indices
    ]
    
    return ranked_methods


def calculate_tfidf_cosine_similarity(dict_of_java_files, vulnerability_description):

    codes = skip_interface_abstract(dict_of_java_files)

    # Each Java file is tokenized into a single string with tokens separated by spaces
    tokenized_java_files = [tokenize_java_code(code) for code in codes]
    # for key in dict_of_java_files:
    #      if 'NettyDecoder.java' in dict_of_java_files[key]['path']:
    #         code = tokenize_java_code(dict_of_java_files[key]['path'])

    
    vulnerability_description = dot_split(vulnerability_description)
    vulnerability_description = tokenize_description(vulnerability_description)

    # Combine Java files and vulnerability description
    all_documents = tokenized_java_files + [vulnerability_description]

    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_documents)
    
    # Compute cosine similarity
    vulnerability_vector = tfidf_matrix[-1]
    similarities = cosine_similarity(vulnerability_vector, tfidf_matrix[:-1])
    df = pd.DataFrame([], columns=['id', 'sim', 'path'])
    for i, each in enumerate(similarities[0]):
        # dict_of_java_files[list(dict_of_java_files.keys())[i]]['sim'] = each
        df = pd.concat([df, pd.DataFrame({'id': [list(dict_of_java_files.keys())[i]], 'sim': [each], 'path': [dict_of_java_files[list(dict_of_java_files.keys())[i]]['path']]})], ignore_index=True)
    df = df.sort_values('sim', ascending=False)
    return df


# list_of_java_files = ["file1.java", "file2.java", "file3.java"]
# vulnerability_description = "The code has a SQL injection vulnerability."
# similarity_scores = calculate_tfidf_cosine_similarity(list_of_java_files, vulnerability_description)

# for i, score in enumerate(similarity_scores[0]):
#     print(f"Similarity between vulnerability description and file {i+1}: {score}")


def calculate_tf_idf_vectors(repo, coll, description, cve, version, filtered_files = []):
    coll.create_index('cve')
    # skip processed, but now reprocess all
    # if coll.find_one({'cve': cve}):
    #     return
    gav_dict = {}
    dict_of_java_files = {}
    all_file_count = 0
    
    for root, dir, fs in os.walk(os.path.join(repo_dir, repo)):
        if os.path.exists(os.path.join(root, 'pom.xml')):
            file_path = os.path.join(root, 'pom.xml')
            data = parse_pom(file_path)
            if data:
                gav = data.get('groupId', 'g')+'|'+data.get('artifactId', repo)+'|'+data.get('version', 'v')
                gav_dict[root] = gav
            else:
                gav = repo+'|'+version
          
        for f in fs:
            if not f.endswith('.java') or 'Test' in root:
                continue
            all_file_count+=1
            file_path = os.path.join(root, f)

            filter_files =[normalize_file_path(f) for f in filtered_files]

            if len(filter_files)>0 and normalize_file_path(file_path) not in filter_files:
                continue
             # get gav
            gav = None
            for each in gav_dict:
                if each in root:
                    gav = gav_dict.get(each)

            # get class
            clazz = f.replace('.java', '')

            # get id, skip visited
            if not gav:
                gav = repo
            id = gav+'@'+clazz


            dict_of_java_files[id] = {'path': file_path}
    print('list to do TF-IDF', len(dict_of_java_files))
    df = calculate_tfidf_cosine_similarity(dict_of_java_files, description)
    os.makedirs('data/tf-idf', exist_ok=True)
    df.to_csv(f'data/tf-idf/{cve}_{repo}_tf-idf_ranking.csv',index=False)

    scores = list(df["sim"])
    elbow_point = find_elbow_Lmethod(scores)
    true_elbow = elbow_point
    plt.figure(figsize=(10, 5))  # create a new figure for each iteration
    plt.plot(scores, 'o-', label='score')
    plt.vlines(x=elbow_point, ymin=min(scores), ymax=max(scores), colors='r', linestyles='dotted')
    # plt.show()
    os.makedirs('figs', exist_ok=True)
    plt.savefig(f'figs/{repo}_elbow.png')
    print("Elbow point:", elbow_point, '/', len(scores))
    if elbow_point< all_file_count*0.1 or elbow_point<100:
        elbow_point = max(round(all_file_count*0.1), 100)
        print('Too few files, trigger lowerlimit', elbow_point)


    coll.update_one({'cve': cve}, {'$set':{
        'true_elbow': true_elbow,
        'repo': repo,
        'cve': cve,
        'top-k': list(df["id"][:elbow_point]),
        'path': list(df["path"][:elbow_point]),
        'all_file_count': all_file_count
        }}, upsert=True)
    # print('Elbow list:', scores[:elbow_point])
    # print("Top k:", list(df['id'])[:elbow_point])

def calculate_tf_idf_vectors_func(repo, description, cve, c, filtered_funs = []):
    coll = c[mongo_db][final_results_coll]
    all_docs = []#get_cve_documents(description, filtered_funcs)
    coll.create_index('cve')

    # for filtered_func in filtered_funs:
    #     dict_of_java_files[filtered_func['name']] = {'path': filtered_func['file']}
     
    print('list to do TF-IDF', len(filtered_funs))
    
    description = process_corpus(description)
    processed_methods = [
        {
            'body': process_corpus(get_body(f)),
            'file': f['file'],
            'name': f['name']
         } for f in filtered_funs
        ]
    res = rank_java_methods_by_vulnerability(processed_methods, description, all_docs)
    if retrieval_approach_choice!='no_filter':
        coll.update_one({'cve': cve}, {'$set':{
            'repo': repo,
            'top-k': [each['name'] for each in res],
            'path': [each['file'] for each in res],
            'scores': [each['similarity_score'] for each in res],
            'all_file_count': len(filtered_funs)
            }}, upsert=True)
    else:
        coll.update_one({'cve': cve}, {'$set':{
            'repo': repo,
            'top-k': [each['name'] for each in res],
            'all_file_count': len(filtered_funs)
            }}, upsert=True)
    # print('Elbow list:', scores[:elbow_point])
    # print("Top k:", list(df['id'])[:elbow_point])



