from rank_bm25 import BM25Okapi
from config import mongo_db, final_results_coll, retrieval_approach_choice
from utils.knowledge_graph import process_corpus
from utils.miscellaneous import get_body


from rank_bm25 import BM25Okapi

def rank_java_methods_bm25(processed_methods, description, all_docs):
    """
    Rank Java methods based on their relevance to a description using BM25,
    structured for updating MongoDB with method names, file paths, and scores.
    
    Args:
        processed_methods (list of dicts): A list of dictionaries, each representing a processed Java method.
        description (str): The processed description text to compare against the Java methods.
        all_docs (list of str): All additional documents to consider for the BM25 corpus.

    Returns:
        list of dicts: A list of dictionaries, each containing 'name', 'file', and 'similarity_score'
                       for a method, sorted by relevance (highest scores first).
    """
    # Combine the bodies of processed methods and all_docs to form the corpus
    corpus = [method['body'] for method in processed_methods] + all_docs
    # Tokenize the corpus
    tokenized_corpus = [doc.split() for doc in corpus]
    
    # Initialize BM25 model
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Tokenize the description
    tokenized_description = description.split()
    
    # Compute BM25 scores for each document in the corpus relative to the description
    scores = bm25.get_scores(tokenized_description)
    
    # Prepare method info and scores in the expected dictionary format
    method_scores = [
        {
            'name': method['name'],
            'file': method['file'],
            'similarity_score': scores[i]
        } for i, method in enumerate(processed_methods)
    ]
    
    # Sort the methods based on their BM25 scores in descending order
    sorted_methods = sorted(method_scores, key=lambda x: x['similarity_score'], reverse=True)
    
    return sorted_methods


def re_rank_bm25(repo, description, cve, c, filtered_funcs=[]):
    coll = c[mongo_db][final_results_coll]
    all_docs = []#get_cve_documents(description, filtered_funcs)
    coll.create_index('cve')

    # for filtered_func in filtered_funs:
    #     dict_of_java_files[filtered_func['name']] = {'path': filtered_func['file']}
     
    print('list to do BM25', len(filtered_funcs))
    
    description = process_corpus(description)
    processed_methods = [
        {
            'body': process_corpus(get_body(f)),
            'file': f['file'],
            'name': f['name']
         } for f in filtered_funcs
        ]
    res = rank_java_methods_bm25(processed_methods, description, all_docs)
    if retrieval_approach_choice!='no_filter':
        coll.update_one({'cve': cve}, {'$set':{
            'repo': repo,
            'top-k': [each['name'] for each in res],
            'path': [each['file'] for each in res],
            'scores': [each['similarity_score'] for each in res],
            'all_file_count': len(filtered_funcs)
            }}, upsert=True)
    else:
        coll.update_one({'cve': cve}, {'$set':{
            'repo': repo,
            'top-k': [each['name'] for each in res],
            'all_file_count': len(filtered_funcs)
            }}, upsert=True)