import pymongo
from main.with_patch import parse_patch_locate_root_cause
from utils.dissect_description import dissect_description, dissect_description_llama2
from utils.enrich_description import query_expansion, get_all_cwe_description
from utils.filter_files_basedon_patch import search_files_from_patch_tool, search_func_from_patch_tool
from utils.nltk_utils import remove_common_words
from utils.prf_description import get_prf_cve_descriptions
from config import mongodb_host, mongodb_port, mongo_db, dataset
from utils.query_reformulation import reformulate_query
# description = "Apache Commons Configuration uses a third-party library to parse YAML files which by default allows the instantiation of classes if the YAML includes special statements. Apache Commons Configuration versions 2.2, 2.3, 2.4, 2.5, 2.6 did not change the default settings of this library. So if a YAML file was loaded from an untrusted source, it could therefore load and execute code out of the control of the host application."
# get_prf_cve_descriptions(description)
# c = pymongo.MongoClient(mongodb_host, mongodb_port)
# query_expansion(c)
# print(dissect_description(None, "The Jakarta Multipart parser in Apache Struts 2 2.3.x before 2.3.32 and 2.5.x before 2.5.10.1 has incorrect exception handling and error-message generation during file-upload attempts, which allows remote attackers to execute arbitrary commands via a crafted Content-Type, Content-Disposition, or Content-Length HTTP header, as exploited in the wild in March 2017 with a Content-Type header containing a #cmd= string."))

# search_files_from_patch_tool(dataset)
parse_patch_locate_root_cause()
search_func_from_patch_tool(dataset)
# dissect_description_llama2()
# query = "The REST Plugin in Apache Struts 2.1.1 through 2.3.x before 2.3.34 and 2.5.x before 2.5.13 uses an XStreamHandler with an instance of XStream for deserialization without any type filtering, which can lead to Remote Code Execution when deserializing XML payloads."
# expanded = "The product deserializes untrusted data without sufficiently verifying that the resulting data will be valid.	It is often convenient to serialize objects for communication or to save them for later use. However, deserialized data or code can often be modified without using the provided accessor functions if it does not use cryptography to protect itself. Furthermore, any cryptography would still be client-side security -- which is a dangerous security assumption. Data that is untrusted can not be trusted to be well-formed. When developers place no restrictions on gadget chains, or series of instances and method invocations that can self-execute during the deserialization process (i.e., before the object is returned to the caller), it is sometimes possible for attackers to leverage them to perform unauthorized actions, like generating a shell."
# query_expansion(c)


# corpus = get_all_cwe_description().values()
# updated_corpus, removed_words = remove_common_words(corpus, top_n=10)
#
# print("Updated Corpus:", updated_corpus)
# print("Removed Words:", removed_words)

# c.close()