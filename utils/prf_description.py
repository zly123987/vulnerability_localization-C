import csv

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def get_prf_cve_descriptions(original_query):
    # Sample CVE descriptions (Replace these with your actual data)
    cve_desciption_mapping = {}
    cve_descriptions = []
    with open('data/dataset - cve data set.csv') as f:
        reader = csv.reader(f)
        next(reader, None)
        for line in reader:
            cve = line[0]
            description = line[2]
            cve_desciption_mapping[description]=cve
    # Adding the original query to the list of descriptions for vectorization
    cve_descriptions = list(cve_desciption_mapping.keys())
    cve_descriptions.append(original_query)

    # Vectorize the descriptions using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cve_descriptions)

    # Compute cosine similarity between the original query and all descriptions
    cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])

    # Get the indices of the top N similar descriptions
    N = 5  # Number of top documents to consider for PRF
    top_indices = np.argsort(cosine_similarities[0])[::-1][:N]

    # Extract top N similar descriptions
    top_descriptions = [cve_descriptions[i] for i in top_indices]
    top_cves = [cve_desciption_mapping[description] for description in top_descriptions]
    # Extract key terms from the top descriptions
    # (For simplicity, we're just taking terms with the highest TF-IDF scores)
    top_terms = set()
    for desc in top_descriptions:
        terms = vectorizer.transform([desc])
        sorted_terms = np.argsort(terms.toarray()).flatten()[::-1]
        top_terms.update([vectorizer.get_feature_names_out()[i] for i in sorted_terms[:10]])  # Top 10 terms per document

    # Expand the original query with top terms from similar descriptions
    expanded_query = original_query + " " + " ".join(top_terms)

    print("Expanded Query:", expanded_query)
    print("Top CVEs:", top_cves)
    return expanded_query
