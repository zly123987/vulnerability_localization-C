import json
import csv
import os
import pymongo
import torch
from config import mongodb_host, mongodb_port, repo_dir, black_list, mongo_db, data_file
from tqdm import tqdm
from transformers import pipeline
from utils.dissect_description import dissect_description


ret = {}
cves = ['CVE-2014-2058', 'CVE-2014-2059', 'CVE-2014-2062', 'CVE-2014-2063', 'CVE-2014-2064', 'CVE-2014-2065', 'CVE-2014-2066', 'CVE-2014-2067', 'CVE-2014-2068', 'CVE-2014-3661', 'CVE-2014-3662', 'CVE-2014-3663', 'CVE-2014-3664', 'CVE-2014-3666', 'CVE-2014-3667', 'CVE-2014-3680', 'CVE-2014-3681', 'CVE-2014-9634', 'CVE-2014-9635', 'CVE-2015-1806', 'CVE-2015-1807', 'CVE-2015-1808', 'CVE-2015-1810', 'CVE-2015-1812', 'CVE-2015-1813', 'CVE-2015-1814', 'CVE-2015-5317', 'CVE-2015-5318', 'CVE-2015-5319', 'CVE-2015-5322', 'CVE-2015-5323', 'CVE-2015-5324', 'CVE-2015-5325', 'CVE-2015-5326', 'CVE-2015-7536', 'CVE-2015-7538', 'CVE-2015-7539', 'CVE-2016-0788', 'CVE-2016-0789', 'CVE-2016-0790', 'CVE-2016-0791', 'CVE-2016-0792', 'CVE-2016-3721', 'CVE-2016-3722', 'CVE-2016-3723', 'CVE-2016-3724', 'CVE-2016-3725', 'CVE-2016-3726', 'CVE-2016-3727', 'CVE-2016-9299', 'CVE-2017-1000353', 'CVE-2017-1000354', 'CVE-2017-1000391', 'CVE-2017-1000392', 'CVE-2017-1000393', 'CVE-2017-1000395', 'CVE-2017-1000398', 'CVE-2017-1000399', 'CVE-2017-1000400', 'CVE-2017-1000401', 'CVE-2017-1000503', 'CVE-2017-1000504', 'CVE-2017-2598', 'CVE-2017-2600', 'CVE-2017-2601', 'CVE-2017-2602', 'CVE-2017-2603', 'CVE-2017-2604', 'CVE-2017-2606', 'CVE-2017-2608', 'CVE-2017-2609', 'CVE-2017-2610', 'CVE-2017-2611', 'CVE-2017-2612', 'CVE-2017-2613', 'CVE-2018-1000067', 'CVE-2018-1000193', 'CVE-2018-1000194', 'CVE-2018-1000195', 'CVE-2018-1000406', 'CVE-2018-1000407', 'CVE-2018-1000408', 'CVE-2018-1000409', 'CVE-2018-1000410', 'CVE-2018-1000861', 'CVE-2018-1000862', 'CVE-2018-1000863', 'CVE-2018-1000864', 'CVE-2018-1000997', 'CVE-2018-1999001', 'CVE-2018-1999002', 'CVE-2018-1999003', 'CVE-2018-1999004', 'CVE-2018-1999005', 'CVE-2018-1999006', 'CVE-2018-1999042', 'CVE-2018-1999044', 'CVE-2018-1999045', 'CVE-2018-1999046', 'CVE-2018-6356', 'CVE-2019-1003003', 'CVE-2019-10352', 'CVE-2019-10353', 'CVE-2019-10354', 'CVE-2020-2161', 'CVE-2020-2221', 'CVE-2020-2222', 'CVE-2020-2223']
cves = ['CVE-2024-23078' , 'CVE-2024-23079' , 'CVE-2024-22949' , 'CVE-2024-23081' , 'CVE-2024-23082' , 'CVE-2024-3366' , 'CVE-2024-2700' , 'CVE-2024-29834' , 'CVE-2024-27609' , 'CVE-2024-31033' , 'CVE-2024-28109' , 'CVE-2024-25420' , 'CVE-2024-25421' , 'CVE-2024-3046' , 'CVE-2024-31863' , 'CVE-2024-23085' , 'CVE-2023-44487' , 'CVE-2024-23084' , 'CVE-2024-24683' , 'CVE-2024-27439' , 'CVE-2024-22258' , 'CVE-2024-22258' , 'CVE-2024-28851' , 'CVE-2024-28847' , 'CVE-2024-28128' , 'CVE-2024-28254' , 'CVE-2024-28125' , 'CVE-2024-28039' , 'CVE-2024-23604' , 'CVE-2024-23086' , 'CVE-2024-28098' , 'CVE-2024-27135' , 'CVE-2024-27317' , 'CVE-2024-27894' , 'CVE-2024-28213' , 'CVE-2024-25710' , 'CVE-2024-28154' , 'CVE-2023-50740' , 'CVE-2024-26580' , 'CVE-2024-1979' , 'CVE-2024-26308' , 'CVE-2024-26467' , 'CVE-2024-27138' , 'CVE-2024-27139' , 'CVE-2024-27140' , 'CVE-2024-22871' , 'CVE-2024-23114' , 'CVE-2024-1726' , 'CVE-2024-22369' , 'CVE-2024-23320']
def get_info_by_cves():
    with open('materials/cve.csv', 'w') as fw:
        writer = csv.writer(fw, quoting=csv.QUOTE_ALL)

        for cve in cves:
            _, year, _ = cve.split('-')
            if not os.path.exists(f'materials/nvdcve-1.1-{year}.json'):
                ret[cve] = {
                        'cwe': '',
                        'cpes': '',
                        'description': ''
                    }
                continue
            with open(f'materials/nvdcve-1.1-{year}.json') as f:
                content = json.load(f)
                for item in content['CVE_Items']:
                    cve_id = item['cve']['CVE_data_meta']['ID']
                    if cve_id !=cve:
                        continue
                    desc = item['cve']['description']['description_data'][0]['value']

                    cwe = ''
                    for value in item['cve']['problemtype']['problemtype_data'][0]['description']:
                        cwe = value.get('value', '')
                    cpes = []
                    for node in item['configurations']['nodes']:
                        for cpe in node['cpe_match']:
                            if cpe['cpe23Uri'] not in cpes:
                                cpes.append(cpe['cpe23Uri'])
                    ret[cve] = {
                        'cwe': cwe,
                        'cpes': cpes,
                        'description': desc
                    }
        for each in cves:
            if each not in ret:
                writer.writerow([each, '', '', ''])
            else:
                writer.writerow([each, ret[each]['description'], ret[each]['cwe'], '|'.join(ret[each]['cpes'])])
                # print(ret[each]['description']+','+ret[each]['cwe']+','+'|'.join(ret[each]['cpes']))

def get_info_all():
    # Initialize the QA model
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2", device=0 if torch.cuda.is_available() else -1)

    c = pymongo.MongoClient(mongodb_host,
                port=mongodb_port)
    coll = c[mongo_db]['dissected_description']
    coll.create_index('cve_id', unique=True)
    description_dict = {}
    with open('data/description_all.csv', 'w', encoding='utf-8') as fw, open('data/description_all.json', 'w', encoding='utf-8') as fw2:
        writer = csv.writer(fw, quoting=csv.QUOTE_ALL)

        for year in range(2022,2025):
            # if year <= 2019:
            #     continue
            with open(f'materials/nvdcve-1.1-{year}.json', encoding='utf-8') as f:
                content = json.load(f)
                for item in tqdm(content['CVE_Items']):
                    cve_id = item['cve']['CVE_data_meta']['ID']
                    if coll.find_one({'cve_id': cve_id}):  # Skip if already in the database
                        continue
                    desc = item['cve']['description']['description_data'][0]['value']

                    cwe = ''
                    for value in item['cve']['problemtype']['problemtype_data'][0]['description']:
                        cwe = value.get('value', '')
                    cpes = []
                    for node in item['configurations']['nodes']:
                        for cpe in node['cpe_match']:
                            if cpe['cpe23Uri'] not in cpes:
                                cpes.append(cpe['cpe23Uri'])
                    # writer.writerow([cve_id, desc, cwe, cpes])
                    # print(cve_id, desc, cwe, cpes)
                    dissected = dissect_description(qa_model, desc)
                    description_dict[cve_id] = {'description': desc, 'cwe': cwe, 'cpes': cpes, **dissected}
                    # print(cpes)
                    coll.update_one({'cve_id': cve_id}, {'$set': {'cve_id': cve_id, 'description': desc, 'cwe': cwe, 'cpes': cpes, 'cpe_product': [cpe.split(':')[4] for cpe in cpes], **dissected}}, upsert=True)
        # json.dump(description_dict, fw2, indent=4)
    c.close()

