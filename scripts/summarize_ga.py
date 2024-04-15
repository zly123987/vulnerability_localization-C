from config import mongo_db

def get_summaries_for_ga(c):
    coll = c[mongo_db]['repo_summary']

    for doc in coll.find():
        id = doc['id']
        gav = doc['gav']
        g,a,v = gav.split('|')
        ga = doc['ga']
        