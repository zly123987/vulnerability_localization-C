from config import repo_dir, mongo_db, query_expansion_choice, retrieval_approach_choice, final_results_coll



def skip_rerank(description, cve, c, filtered_funcs_cve):
    coll = c[mongo_db][final_results_coll]
    all_docs = []#get_cve_documents(description, filtered_funcs)
    coll.create_index('cve')
    coll.update_one({'cve': cve}, {'$set':{
            'top-k': [each['name'] for each in filtered_funcs_cve],
            # 'path': [each['file'] for each in res],
            # 'scores': [each['similarity_score'] for each in res],
            'all_file_count': len(filtered_funcs_cve)
            }}, upsert=True)