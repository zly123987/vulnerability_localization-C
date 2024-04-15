import concurrent.futures
import re
from concurrent.futures import ProcessPoolExecutor
import torch
from transformers import PLBartForConditionalGeneration, PLBartTokenizer
from transformers import AutoTokenizer, AutoModelWithLMHead, SummarizationPipeline, AutoModelForCausalLM
import os
from multiprocessing import Pool


# os.environ['KMP_DUPLICATE_LIB_OK']='True'
# os.environ['PYTORCH_CUDA_ALLOC_CONF']='max_split_size_mb:512' 
pipeline = SummarizationPipeline(
    model=AutoModelWithLMHead.from_pretrained("SEBIS/code_trans_t5_small_code_documentation_generation_java_multitask_finetune"),
    tokenizer=AutoTokenizer.from_pretrained("SEBIS/code_trans_t5_small_code_documentation_generation_java_multitask_finetune", skip_special_tokens=True),
    device=-1
    )

def summarize(text):
        
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    return get_summary_codeTransT5(text)
    # return get_summary_PLBart(text)

def get_summary_codeTransT5(text):
    res = pipeline([text])
    return res[0]['summary_text']

def sum_one(met):
    met['sum'] = get_summary_PLBart(met['body'])
    return met['sum']

def summarize_parsed(parsed):
    # if parsed['comment']=='':
        # parsed['sum'] = summarize(parsed['body'])
    for cls in parsed['classes']:
        if cls['isInterface']==True or 'abstract' in cls['modifiers']:
            continue
        # if cls['comment']=='':
        cls['sum'] = summarize(cls['body'])
        for met in cls['methods']:
            if met['name'].startswith('get') or met['name'].startswith('set') or met['name'].startswith('is'):
                continue
            met['sum'] = summarize(met['body'])
        # with Pool(processes=10) as pool:  # Choose the number of processes based on your CPU's cores
            # results = pool.map(sum_one, cls['methods'])
        # for each in results:
        #     name, sum = each.split('!@#$%^&*()')
        #     for each_met in cls['methods']:
        #         if each_met['name']==name:
        #             each_met['sum'] = sum
        #             break
        # print(cls['methods'])
        # exit()
    return parsed

def get_summary_PLBart(text):
    max_length = 10240
    chunk_size = 1500  # Adjust this value as per your needs
    tokenizer = PLBartTokenizer.from_pretrained("uclanlp/plbart-java-en_XX", src_lang="java", tgt_lang="en_XX")
    model = PLBartForConditionalGeneration.from_pretrained("uclanlp/plbart-java-en_XX")
    # Split the text into smaller chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    summaries = []

    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", max_length=max_length, truncation=True)
        translated_tokens = model.generate(
            **inputs,
            decoder_start_token_id=tokenizer.lang_code_to_id["__en_XX__"],
            max_length=max_length,
            no_repeat_ngram_size=3,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        summary = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        summaries.append(summary)

    return '|'.join(summaries)

# import logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# mongo='mongodb://155.69.147.181:28888/'
# db=pymongo.MongoClient(mongo)
# collection1=db['bugs']['false_warnings']
# collection2=db['bugs']['tempwarning']
# negwarning=collection1.find({'return_comment':None},{'bug_code':1})
# negwarning=list(negwarning)
# for warning in tqdm(negwarning):
#     # logging.info('Processing %s'%warning['_id'])
#     if 'bug_code' not in warning.keys():
#         continue
#     text = warning['bug_code']
#     inputs = tokenizer(text, return_tensors="pt",max_length=512,truncation=True)
#     translated_tokens = model.generate(**inputs, decoder_start_token_id=tokenizer.lang_code_to_id["__en_XX__"],max_length=32)
#     summary = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
#     collection1.update_one({'_id':warning['_id']},{'$set':{'return_comment':summary,'is_gen':True}})


# poswarning=collection2.find({'return_comment':None},{'bug_code':1})
# poswarning=list(poswarning)
# for warning in tqdm(poswarning):
#     # logging.info('Processing %s'%warning['_id'])
#     if 'bug_code' not in warning.keys():
#         continue
#     text = warning['bug_code']
#     inputs = tokenizer(text, return_tensors="pt",max_length=512,truncation=True)
#     translated_tokens = model.generate(**inputs, decoder_start_token_id=tokenizer.lang_code_to_id["__en_XX__"],max_length=32)
#     summary = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
#     collection2.update_one({'_id':warning['_id']},{'$set':{'return_comment':summary,'is_gen':True}})
