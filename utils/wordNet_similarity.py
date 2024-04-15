from nltk.corpus import wordnet
import nltk
from nltk import word_tokenize
from itertools import product
import concurrent.futures




from utils.bert_similarity import bert_embedding_similarity
nltk.download('punkt', quiet=True)



def score_pair(args):
    sentence, s = args
    # return (word_net_similarity(sentence, s), s)
    return (sentence_bert_similarity(sentence, s), s)


# Below are wordNet
def max_similarity(sentence, sentence_list):
    # create a list of arguments for score_pair
    # args_list = [(sentence, s) for s in sentence_list]
    
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     # pass args_list to executor.map
    #     results = list(executor.map(score_pair, args_list))
    results = [score_pair((sentence, s)) for s in sentence_list]
    return max(results)


def word_net_similarity(sentence1, sentence2):

    # Tokenize and tag
    words1 = word_tokenize(sentence1)
    words2 = word_tokenize(sentence2)

    overall_score = 0.0
    count = 0
    
    # For each word in the first sentence
    for word1 in words1:
        max_sim = -1.0
        # Get the synsets for this word
        synsets1 = wordnet.synsets(word1)
        # For each word in the second sentence
        for word2 in words2:
            # Get the synsets for this word
            synsets2 = wordnet.synsets(word2)
            # For each combination of synsets
            for synset1, synset2 in product(synsets1, synsets2):
                # Find the similarity value of these two synsets
                sim = wordnet.wup_similarity(synset1, synset2)
                # Ignore this pair if no similarity value
                if sim is not None and sim > max_sim:
                    max_sim = sim
        # Ignore this word if no synsets were found
        if max_sim != -1:
            overall_score += max_sim
            count += 1
            
    # Calculate average score
    sentence_similarity = overall_score / count

    return sentence_similarity