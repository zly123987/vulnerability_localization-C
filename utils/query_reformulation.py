import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
from scipy.spatial.distance import cosine
import numpy as np

from utils.nltk_utils import sanitize_text

def get_all_cwe_description():
    ret = {}
    with open("materials/cwe1000.csv") as f:
        for l in csv.reader(f):
            ret[l[0]] = l[4] +'. ' + l[5]

    return ret

def LSA(corpus, query, expanded_terms):
    expanded_terms = list(set(expanded_terms))
    # Step 1: Preprocess and Vectorize the Corpus with TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    X_corpus = vectorizer.fit_transform(corpus)

    # Step 2: Apply LSA on TF-IDF Vectors
    svd = TruncatedSVD(n_components=100)  # Adjust n_components for optimal semantic space representation
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)

    X_corpus_lsa = lsa.fit_transform(X_corpus)

    # Step 3: Vectorize Query and Expanded Terms with the same TF-IDF Vectorizer
    query_vector = vectorizer.transform([query])
    expanded_terms_vectors = vectorizer.transform(expanded_terms)

    # Project Query and Expanded Terms into LSA Space
    query_lsa = lsa.transform(query_vector)
    expanded_terms_lsa = lsa.transform(expanded_terms_vectors)

    # Define Cosine Similarity Function
    def cosine_similarity(v1, v2):
        return 1 - cosine(v1.flatten(), v2.flatten())

    # Calculate Similarities
    similarities = [cosine_similarity(query_lsa, term_vector.reshape(1, -1)) for term_vector in expanded_terms_lsa]

    # Step 5: Convert Similarities to Probabilities
    probabilities = softmax(similarities)

    # Pair each term with its probability and sort
    terms_with_probs = sorted(zip(expanded_terms, probabilities), key=lambda x: x[1], reverse=True)

    # Display Sorted Terms with Probabilities
    ret = {}
    for term, prob in terms_with_probs:
        # print(f"{term}: {prob:.4f}")
        ret[term] = prob
    return ret

# Helper function: Softmax
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def reformulate_query(query, expanded):
    all_cwe_description = get_all_cwe_description()
    # Example corpus and query
    corpus = list(all_cwe_description.values())
    # cve_description = get_all_description(c)
    # corpus.extend(cve_description)
    query = sanitize_text(query)
    expanded_terms = sanitize_text(expanded).split(' ')
    weights = LSA(corpus, query, expanded_terms)
    for term in expanded_terms:
        if term not in weights:
            weights[term] = 0
    return weights, expanded_terms