import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

# Manual domain dictionary for terms that might not have synsets in WordNet
domain_dict = {
    "deserialization": ["serialization", "object", "data conversion", "input sanitization"]
}


def enhance_with_wordnet(description):
    tokens = nltk.word_tokenize(description)

    # Prioritize the domain-specific terms
    keywords = [token for token in tokens if token in domain_dict]

    new_terms = set()

    for keyword in keywords:
        # Use domain dictionary if keyword is present
        if keyword in domain_dict:
            new_terms.update(domain_dict[keyword])
            continue

        synsets = wn.synsets(keyword)

        # Only fetch one related term (synonym, hypernym, or hyponym)
        if synsets:
            syn = synsets[0]
            related_terms = [lemma.name() for lemma in syn.lemmas()] + \
                            [lemma.name() for hyper in syn.hypernyms() for lemma in hyper.lemmas()] + \
                            [lemma.name() for hypo in syn.hyponyms() for lemma in hypo.lemmas()]
            new_terms.add(related_terms[0])

    # Convert underscore-separated terms to spaces
    new_terms = " ".join([term.replace("_", " ") for term in new_terms])

    enhanced_description = description + " " + new_terms
    return enhanced_description


# Use the function
print(enhance_with_wordnet("Solon before 2.3.3 allows Deserialization of Untrusted Data."))