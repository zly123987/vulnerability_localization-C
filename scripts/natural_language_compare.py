import ast
import os
import pandas as pd
from scripts.Lmethod import find_elbow_Lmethod
from utils.tf_idf_similarity import camel_case_split
from utils.wordNet_similarity import max_similarity, word_net_similarity

def nl_compare(coll, nl_result_coll, ids, repo, cve, description):
    if not os.path.exists(f'data/nl/{cve}_{repo}_nl.csv') or len(pd.read_csv(f'data/nl/{cve}_{repo}_nl.csv'))==0:

        df = pd.DataFrame([], columns=['id', 'sim'])
        count = len(ids)
        for i, id in enumerate(ids):
            doc = coll.find_one({'id': id})
            if not doc:
                continue
            sums = []
            for clss in doc['meta']['classes']:
                if 'sum' not in clss:
                    continue
                clss_sum = clss['name']+' '+clss.get('sum', '')
                for met in clss['methods']:
                    if 'sum' in met:
                        met_sum = met['name']+' '+met['sum']
                    elif met['comment'] != '':
                        met_sum = met['name']+' '+met['comment']
                    else:
                        met_sum = met['name']+' '+' '.join(camel_case_split(met['name']))
                    sums.append(clss_sum+' '+met_sum)
            sums = list(set(sums))
            print(i+1, '/', count, 'NL sim', repo ,'\r', end='', flush=True)
            if len(sums):
                sim = max_similarity(description, sums)    
                df = pd.concat([df, pd.DataFrame({'id': [id], 'sim': [sim]})], ignore_index=True)
            
        df = df.sort_values('sim', ascending=False)
        df.to_csv(f'data/nl/{cve}_{repo}_nl.csv')
    df = pd.read_csv(f'data/nl/{cve}_{repo}_nl.csv')
    

    scores = [float(e.split(', ')[0].strip(' (')) for e in df["sim"]]

    elbow_point = find_elbow_Lmethod(scores)
    if elbow_point <10:
        elbow_point = 10
    print("Elbow point:", elbow_point, '/', len(scores))
    nl_result_coll.update_one({'cve': cve}, {'$set':{
        'repo': repo,
        'cve': cve,
        'top-k': list(df["id"][:elbow_point])
        }}, upsert=True)