import concurrent.futures
import re
import numpy as np
import logging
from config import repo_dir, mongo_db, retrieval_approach_choice, re_rank_approach_choice, final_results_coll
from utils.bert_similarity import lemmatize_sentence
from gensim.models import KeyedVectors
from spiral import ronin
from tqdm import tqdm
from utils.miscellaneous import get_body, get_func_hash, get_func_id, get_all_documents
from utils.nltk_utils import sanitize_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
# Set the logging level to WARNING specifically for gensim
logging.getLogger('gensim').setLevel(logging.WARNING)
def get_weighted_vector(tf_idf_scores, emb, words, desc_weights={}):
    # Initialize an empty vector
    weighted_vec = np.zeros(emb.vector_size)
    for word, value in zip(words, tf_idf_scores):
        if word in desc_weights and word in emb:
            weighted_vec += emb.get_vector(word, norm=True) * desc_weights[word]
        elif word in emb:
            weighted_vec += emb.get_vector(word, norm=True) * value
    return weighted_vec/len(words)

def get_tfidf_scores_for_document(doc_index, tfidf_matrix, vocabulary, doc_terms):
    """Retrieve TF-IDF scores for the terms in a specific document.

    Args:
        doc_index (int): Index of the document in the TF-IDF matrix.
        tfidf_matrix (scipy.sparse.csr.csr_matrix): The TF-IDF matrix.
        vocabulary (dict): The vocabulary mapping terms to their indices in the TF-IDF matrix.
        doc_terms (list of str): The terms (words) in the document.

    Returns:
        list of float: The list of TF-IDF scores corresponding to each term in the document.
    """
    # Convert the specific row of the TF-IDF matrix to a dense array
    doc_vector = tfidf_matrix[doc_index].toarray().flatten()
    
    # Initialize a list to store TF-IDF scores for terms in the document
    tfidf_scores = []
    
    # Iterate over each term in the document
    for term in doc_terms:
        # Check if the term is in the vocabulary
        if term in vocabulary:
            # Retrieve the TF-IDF score using the column index from the vocabulary
            score = doc_vector[vocabulary[term]]
        else:
            # If the term is not in the vocabulary, its score is 0
            score = 0
        tfidf_scores.append(score)
    # Apply L2 normalization (Euclidean norm) to the TF-IDF scores
    norm = np.sqrt(sum([score ** 2 for score in tfidf_scores]))
    normalized_scores = [score / norm if norm > 0 else 0 for score in tfidf_scores]
    return normalized_scores

def get_sim_weighted_optimized(emb, description, source_codes, documents, desc_weights ={}):
    # Prepend the description and source codes to the documents
    all_texts = [description] + source_codes + documents
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    vocabulary = vectorizer.vocabulary_
    description_tfidf_scores = get_tfidf_scores_for_document(0, tfidf_matrix, vocabulary, all_texts[0].split(' '))
    # Extract TF-IDF vector for the description, which is now the first document
    # description_vector = description_vector.toarray().flatten()
    # Calculate the weighted vector for the description
    desc_weighted_vec = get_weighted_vector(description_tfidf_scores, emb, all_texts[0].split(' '), desc_weights)
    
    similarities = []
    # Iterate over each source code file, which are now the documents immediately following the description
    for i, source_code in tqdm(enumerate(source_codes, start=1), desc="Calculating similarities"):
        # Calculate the weighted vector for the source code
        source_code_scores = get_tfidf_scores_for_document(i, tfidf_matrix, vocabulary, all_texts[i].split(' '))
        source_code_weighted_vec = get_weighted_vector(source_code_scores, emb, all_texts[i].split(' '))
        
        # Compute cosine similarity
        norm_desc = np.linalg.norm(desc_weighted_vec)
        norm_source_code = np.linalg.norm(source_code_weighted_vec)
        if norm_desc > 0 and norm_source_code > 0:  # Avoid division by zero
            cos_sim = np.dot(desc_weighted_vec, source_code_weighted_vec) / (norm_desc * norm_source_code)
        else:
            cos_sim = 0  # Handle case where vectors are zero or one of them is
        similarities.append(cos_sim)
    
    return similarities


def compute_tfidf(word, document, documents):
    tf = document.count(word) / len(document.split())
    idf = np.log(len(documents) / (1 + sum(word in d.split() for d in documents)))
    return tf * idf

def get_sim_weighted(emb: KeyedVectors, phrase1, phrase2, documents):
    documents = documents+[phrase1, phrase2]
    words1, words2 = phrase1.split(), phrase2.split()
    tfidf_weights1 = [compute_tfidf(w, phrase1, documents) for w in words1]
    tfidf_weights2 = [compute_tfidf(w, phrase2, documents) for w in words2]

    vec1 = sum(emb.get_vector(w, norm=True) * weight for w, weight in zip(words1, tfidf_weights1)) / len(words1)
    vec2 = sum(emb.get_vector(w, norm=True) * weight for w, weight in zip(words2, tfidf_weights2)) / len(words2)

    cos = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return cos

def filter_out_absent_term(phrase, c2v):
    ret = []
    missing_terms = []
    terms = phrase.split(' ')
    for term in terms:
        if term in c2v:
            ret.append(term)
        else:
            missing_terms.append(term)
    missing_terms = list(set(missing_terms))
    # print missing rate in percentage
    # print('missing rate:', str(int((len(terms) - len(ret)) / len(terms) * 100))+'%')
    if len(missing_terms) > 0:
        with open('data/kg_missing_token.csv', 'a') as f:
            f.write(','.join(missing_terms)+','+ str(len(missing_terms))+','+str(len(terms))+'\n')
    return ret

def remove_java_symbols(code):
    # Remove Java symbols except for underscores and dollar signs
    code = re.sub(r'[^\w]', ' ', code)
    code = code.replace('-', ' ')
    code = code.replace('\'s', '')
    code = code.replace('`', '')
    code = code.replace('(', '').replace(')', '')
    code = code.replace('[', '').replace(']', '')
    code = code.replace('{', '').replace('}', '')
    code = code.replace(',', '')
    return code

def split_camel_case(code):
    # Remove Java symbols except for underscores and dollar signs
    code_no_symbols = re.sub(r'[^\w$_]', ' ', code)
    
    # Split camelCase and PascalCase
    split_camel = re.sub('([a-z])([A-Z])', r'\1 \2', code_no_symbols)
    split_pascal = re.sub('([A-Z]+)([A-Z][a-z])', r'\1 \2', split_camel)
    
    # Optionally, remove extra spaces
    cleaned_code = re.sub(r'\s+', ' ', split_pascal).strip()
    
    return cleaned_code

def get_sim(emb: KeyedVectors, phrase1, phrase2):
    words1, words2 = phrase1.split(), phrase2.split()
    vec1 = sum(emb.get_vector(w, norm=True) for w in words1) / len(words1)
    vec2 = sum(emb.get_vector(w, norm=True) for w in words2) / len(words2)
    cos = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return cos


def process_corpus(copurs):
    description = sanitize_text(copurs)
    description = remove_java_symbols(description)
    description = ronin.split(description)
    # lower
    description = [word.lower() for word in description if word!='']
    return ' '.join(description)


def get_kg_sim(args):
    description, func, c2v = args
    
    source_code = get_body(func)


    # preprocess
    description = process_corpus(description)
    description = filter_out_absent_term(description, c2v)

    source_code = process_corpus(source_code)
    source_code = filter_out_absent_term(source_code, c2v)


    # deduplicate
    # description = ' '.join(list(set(description)))
    # source_code = ' '.join(list(set(source_code)))
    description = ' '.join(description)
    source_code = ' '.join(source_code)

    return func, func['file'], get_sim(c2v, description, source_code)

def get_kg_sim_weighted(description, funcs, c2v, all_docs, weights={}):
    source_codes = []
    for func in funcs:
        source_code = get_body(func)
        source_code = process_corpus(source_code)
        source_code = filter_out_absent_term(source_code, c2v)
        # deduplicate
        source_code = ' '.join(source_code)
        source_codes.append(source_code)
    # preprocess
    description = process_corpus(description)
    description = filter_out_absent_term(description, c2v)
    description = ' '.join(description)

    predicted_funcs_path_score = {}
    scores = get_sim_weighted_optimized(c2v, description, source_codes, all_docs, weights)
    for i, func in enumerate(funcs):
        predicted_funcs_path_score[get_func_hash(func)] = {'name': func['name'], 'score': scores[i], 'file': func['file']}
    return predicted_funcs_path_score
def kg_sim(description, cve, c, filtered_funcs):
    c2v: KeyedVectors = KeyedVectors.load("libs/knowledge_graph/code_wv.bin")
    coll = c[mongo_db][final_results_coll]
    # skip if already exists
    # if coll.find_one({'cve': cve}):
    #     return
    
    coll.create_index('cve')
    list_to_do = list()
    for filtered_func in filtered_funcs:
        list_to_do.append((description, filtered_func, c2v))
    print('list to do for', cve+':', len(list_to_do))
    predicted_funcs_path_score = {}
    # # initialize_model()
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     # Using a list to store futures
    #     futures = []
        
    #     for item in list_to_do:
    #         # Submitting the function to be executed with fixed arguments and an element from the list
    #         future = executor.submit(get_kg_sim, item)
    #         futures.append(future)
        
    #     # Gathering results (if needed)
    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             func, file, score = future.result()
    #             predicted_funcs_path_score[file] = {'name': func, 'score': score}
    #         except Exception as exc:
    #             print(f"Generated an exception: {exc}")
    for item in list_to_do:
        func, file, score = get_kg_sim(item)
        predicted_funcs_path_score[get_func_hash(func)] = {'name': func['name'], 'score': score, 'file': file}
    # Sort the predicted functions by score
    predicted_funcs = sorted(predicted_funcs_path_score.items(), key=lambda x: x[1]['score'], reverse=True)
    if retrieval_approach_choice != 'no_filter':

        coll.update_one({'cve': cve}, {'$set': {
            'all_file_count': len(filtered_funcs),
            'path': [each[1]['file'] for each in predicted_funcs],
            'top-k': [each[1]['name'] for each in predicted_funcs],
            'scores': [float(each[1]['score']) for each in predicted_funcs]
        }}, upsert=True)
    else:
        coll.update_one({'cve': cve}, {'$set': {
            'all_file_count': len(filtered_funcs),
            'top-k': [each[1]['name'] for each in predicted_funcs],
        }}, upsert=True)


def weighted_kg_sim(description, cve, c, filtered_funcs, weights={}):
    c2v: KeyedVectors = KeyedVectors.load("libs/knowledge_graph/code_wv.bin")
    coll = c[mongo_db][final_results_coll]
    # skip if already exists
    # if coll.find_one({'cve': cve}):
    #     return
    all_docs = get_cve_documents(description, filtered_funcs)
    # all_docs = get_all_documents()
    coll.create_index('cve')
    # list_to_do = list()
    print('list to do for', cve+':', len(filtered_funcs))
    predicted_funcs_path_score = get_kg_sim_weighted(description, filtered_funcs, c2v, all_docs, weights)

    predicted_funcs = sorted(predicted_funcs_path_score.items(), key=lambda x: x[1]['score'], reverse=True)
    if retrieval_approach_choice != 'no_filter':
        coll.update_one({'cve': cve}, {'$set': {
            'all_file_count': len(filtered_funcs),
            'path': [each[1]['file'] for each in predicted_funcs],
            'top-k': [each[1]['name'] for each in predicted_funcs],
            'scores': [float(each[1]['score']) for each in predicted_funcs]
        }}, upsert=True)
    else:
        coll.update_one({'cve': cve}, {'$set': {
            'all_file_count': len(filtered_funcs),
            'top-k': [each[1]['name'] for each in predicted_funcs][:300]
    }}, upsert=True)

def get_cve_documents(description, filtered_funcs):
    ret = [process_corpus(description)]
    for f in filtered_funcs:
        ret.append(process_corpus(get_body(f)))
    return ret