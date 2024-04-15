from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from nltk.corpus import wordnet as wn


# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load English stopwords
stop_words = set(stopwords.words('english'))

def find_synonyms_hypernyms(word):
    synonyms = set()
    hypernyms = set()

    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())  # Add synonyms
        for hyper in syn.hypernyms():  # Access hypernyms
            for lemma in hyper.lemmas():
                hypernyms.add(lemma.name())  # Add hypernyms

    return synonyms, hypernyms

def sanitize_text(text):
    """
    Function to sanitize text by lemmatizing, removing stopwords, and punctuation.
    
    Parameters:
    - text (str): The input text to be sanitized.
    
    Returns:
    - str: The sanitized text.
    """
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Lemmatize, remove stopwords and punctuation
    sanitized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.lower() not in stop_words and token not in string.punctuation]
    
    # Join the tokens back into a string
    sanitized_text = ' '.join(sanitized_tokens)
    
    return sanitized_text


from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


def remove_common_words(corpus, top_n=10):
    """
    Remove the top_n most common words from the corpus.

    Parameters:
    - corpus: list of documents (strings)
    - top_n: number of most common words to remove

    Returns:
    - updated_corpus: list of documents with common words removed
    - removed_words: list of words that have been removed
    """
    # Vectorize the corpus to get word counts
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(corpus)
    sum_words = X.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)

    # Identify top_n common words to remove
    removed_words = [word for word, _ in words_freq[:top_n]]

    # Remove these words from the corpus
    updated_corpus = []
    for document in corpus:
        for word in removed_words:
            document = document.replace(f" {word} ", " ")
        updated_corpus.append(document)

    return updated_corpus, removed_words


# Example usage
corpus = [
    "This is a sample document with some common words",
    "Another document that might have common and frequent words",
    "More text to analyze with common words and phrases",
    "This corpus will be used to identify common words"
]



if __name__ == "__main__":
    # Example usage

    # Remove top 5 most common words for demonstration

    example_text = "This is an example sentence to demonstrate the sanitization process, including lemmatization and the removal of stopwords and punctuation."
    sanitized_text = sanitize_text(example_text)
    print(sanitized_text)
