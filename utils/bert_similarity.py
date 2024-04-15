import os
import multiprocessing
from config import mongo_db, repo_dir, retrieval_approach_choice, re_rank_approach_choice, final_results_coll
from transformers import BertModel, BertTokenizer
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel, RobertaTokenizer
import torch
from torch.nn.functional import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import re
import concurrent.futures
from utils.miscellaneous import get_body, get_func_hash, get_func_id
# from sentence_transformers import SentenceTransformer, util


lemmatizer = WordNetLemmatizer()
# Check if CUDA (GPU support) is available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"Using device: {device}")


def remove_comments(java_code):
    # Remove all types of comments (//, /* */)
    cleaned_code = re.sub(r'//.*?\n|/\*.*?\*/', '', java_code, flags=re.DOTALL)
    return cleaned_code

def normalize_whitespace(java_code):
    # Replace multiple spaces/tabs with a single space
    java_code = re.sub(r'\s+', ' ', java_code)
    # Optionally, remove leading/trailing whitespace
    java_code = java_code.strip()
    return java_code


# Lemmatize then bert embedding
def lemmatize_sentence(sentence):
    tokenized_words = word_tokenize(sentence)
    lemmatized_sentence = ' '.join([lemmatizer.lemmatize(word) for word in tokenized_words])
    return lemmatized_sentence


# def bert_encode(sentence, tokenizer, model):
#     # Prepare inputs
#     inputs = tokenizer(lemmatize_sentence(sentence), return_tensors='pt', truncation=True, padding=True)

#     # Move inputs to the same device as the model
#     inputs = {k: v.to(device) for k, v in inputs.items()}

#     # Compute embeddings
#     with torch.no_grad():
#         outputs = model(**inputs).last_hidden_state[:, 0, :]

#     # Move embeddings back to CPU for further processing or return
#     embeddings = outputs.cpu()

#     return embeddings




def calculate_bert(description, cve, model, device, c, filtered_funs):
    if re_rank_approach_choice == 'bert':
        calculate_func = bert_embedding_similarity
    else:
        calculate_func = bert_embedding_similarity_seperate
    coll = c[mongo_db][final_results_coll]

    coll.create_index('cve')

    list_to_do = list()
    for filtered_func in filtered_funs:
        list_to_do.append((filtered_func, description, device, model))
    print('list to do for', cve+':', len(list_to_do))
    predicted_funcs_path_score = {}
    # initialize_model()
    with concurrent.futures.ProcessPoolExecutor(4) as executor:
        # Using a list to store futures
        futures = []
        
        for item in list_to_do:
            # Submitting the function to be executed with fixed arguments and an element from the list
            future = executor.submit(calculate_func, item)
            futures.append(future)
        
        # Gathering results (if needed)
        for future in concurrent.futures.as_completed(futures):
            try:
                result, score = future.result()

                func, file = result['name'], result['file']
                predicted_funcs_path_score[get_func_hash(result)] = {'name': func, 'score': score, 'file': file}
            except Exception as exc:
                print(f"Generated an exception: {exc}")
    # Sort the predicted functions by score
    predicted_funcs = sorted(predicted_funcs_path_score.items(), key=lambda x: x[1]['score'], reverse=True)
    if retrieval_approach_choice != 'no_filter':
        coll.update_one({'cve': cve}, {'$set': {
            'all_file_count': len(filtered_funs),
            'path': [each[1]['file'] for each in predicted_funcs],
            'top-k': [each[1]['name'] for each in predicted_funcs],
            'scores': [each[1]['score'] for each in predicted_funcs]

        }}, upsert=True)
    else:
        coll.update_one({'cve': cve}, {'$set': {
            'all_file_count': len(filtered_funs),
            'top-k': [each[1]['name'] for each in predicted_funcs],
        }}, upsert=True)


def bert_embedding_similarity(args):
    func, description, device, model = args
    body = get_body(func)
    # source = remove_comments(source)
    # source = normalize_whitespace(source)
    model_name = "microsoft/codebert-base"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    # inputs1 = tokenizer(lemmatize_sentence(body), return_tensors='pt', truncation=True, padding=True)
    # inputs2 = tokenizer(lemmatize_sentence(description), return_tensors='pt', truncation=True, padding=True)
    inputs = tokenizer.encode_plus(
        description + tokenizer.sep_token + body,  # You might need a separator depending on your data
        return_tensors="pt",
        max_length=512,  # Ensure this matches your training setup
        truncation=True,
        padding="max_length"
    )

    # Move tensors to the same device as the model
    inputs = {k: v.to(device) for k, v in inputs.items()}


    with torch.no_grad():  # Disable gradient calculation
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)  # Convert logits to probabilities

        # Since it's binary classification, assuming the positive class is the second one
        # Adjust the index if your positive class is at a different position
        positive_class_probabilities = probabilities[:, 1]
    # print('Predicted:', func['name'], func['file'], positive_class_probabilities.item())
    return func, positive_class_probabilities.item()



# def sentence_bert_similarity(sentence1, sentence2):
#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     # Encode the sentences
#     embedding1 = model.encode(lemmatize_sentence(sentence1), convert_to_tensor=True)
#     embedding2 = model.encode(lemmatize_sentence(sentence2), convert_to_tensor=True)
#
#     # Compute similarity scores of two embeddings
#     cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)
#     # print(cosine_scores)
#     return cosine_scores.item()
    
def bert_embedding_similarity_seperate(args):
    '''
    Calculate the cosine similarity between two sentences using BERT embeddings
    '''
    func, description, device, model = args
    body = get_body(func)
    model_name = "microsoft/codebert-base"
    # model_name = "bert-base-uncased"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    # Tokenize inputs
    inputs1 = tokenizer(body, return_tensors='pt', truncation=True, padding=True).to(device)
    inputs2 = tokenizer(description, return_tensors='pt', truncation=True, padding=True).to(device)

    # Perform model inference and extract the [CLS] token embeddings
    with torch.no_grad():
        outputs1 = model(**inputs1)
        outputs2 = model(**inputs2)
        # Extract [CLS] token's embeddings
        embeddings1 = outputs1.last_hidden_state[:, 0, :]  # [CLS] is the first token
        embeddings2 = outputs2.last_hidden_state[:, 0, :]

    cosine_similarity = torch.nn.functional.cosine_similarity(embeddings1, embeddings2).item()
    # print('Predicted:', func['name'], func['file'], cosine_similarity)
    return func, cosine_similarity
