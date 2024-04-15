import gensim.downloader as api
from config import mongo_db, query_expansion_choice, re_rank_approach_choice, final_results_coll, retrieval_approach_choice
from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine
import numpy as np
from utils.knowledge_graph import process_corpus
from utils.miscellaneous import get_body, get_func_hash, get_func_id

def sentence_vector(sentence, model):
    """Generate a sentence vector by averaging the Word2Vec vectors of all words in the sentence."""
    vectors = [model[word] for word in sentence.lower().split() if word in model]
    if len(vectors) == 0:
        return np.zeros(model.vector_size)
    sentence_vector = np.mean(vectors, axis=0)
    return sentence_vector

def calculate_similarity(sentence1, sentence2, model):
    """Calculate the cosine similarity between two sentences."""
    vec1 = sentence_vector(sentence1, model)
    vec2 = sentence_vector(sentence2, model)
    similarity = 1 - cosine(vec1, vec2)  # cosine() function returns the cosine distance, so we subtract from 1
    return similarity

def get_w2v_sim(item):
    description, filtered_func, model = item
    description = process_corpus(description)
    func_body = get_body(filtered_func)
    func_body = process_corpus(func_body)
    # Get the Word2Vec vector for the description
    description_vector = sentence_vector(description, model)
    # Get the Word2Vec vector for the function
    func_vector = sentence_vector(func_body, model)
    # Calculate the cosine similarity between the description and the function
    similarity = 1 - cosine(description_vector, func_vector)
    return filtered_func, filtered_func['file'], similarity


def word_2_vec_sim(description, cve, c, filtered_funcs):
    model = api.load('glove-wiki-gigaword-100')
    coll = c[mongo_db][final_results_coll]
    # skip if already exists
    # if coll.find_one({'cve': cve}):
    #     return
    
    coll.create_index('cve')
    list_to_do = list()
    for filtered_func in filtered_funcs:
        list_to_do.append((description, filtered_func, model))
    print('list to do for', cve+':', len(list_to_do))
    predicted_funcs_path_score = {}

    for item in list_to_do:
        func, file, score = get_w2v_sim(item)
        predicted_funcs_path_score[get_func_hash(func)] = {'name': func['name'], 'score': score, 'file': file}
    # Sort the predicted functions by score
    predicted_funcs = sorted(predicted_funcs_path_score.items(), key=lambda x: x[1]['score'], reverse=True)


    if retrieval_approach_choice!='no_filter':
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
    # print(get_sim(c2v, "db", "database"))
    # print(get_sim(c2v, "db", "database"))

if __name__=='__main__':
    # Example usage
    # Load your Word2Vec model (make sure to replace 'path/to/your/model' with the actual path to your Word2Vec model)
    # This will list available models
    print(api.info()['models'].keys())

    # For example, to load the 'glove-wiki-gigaword-100' model
    model = api.load('glove-wiki-gigaword-100')
    # Adjust depending on your model format

    sentence1 = "This is the first sentence."
    sentence2 = "This is the second sentence."

    similarity = calculate_similarity(sentence1, sentence2, model)
    print(f"Similarity: {similarity}")
