from transformers import pipeline
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def parse_output_to_dict(output_text):
    # Define a dictionary to hold the extracted information
    info_dict = {}
    
    # Regular expression patterns for extracting the information
    patterns = {
        "Vulnerability Type": r"Vulnerability Type: \[(.*?)\]",
        "Product": r"Product: \[(.*?)\]",
        "Vendor": r"Vendor: \[(.*?)\]",
        "Affected Versions": r"Affected Versions: \[(.*?)\]",
        "Attacker/Source": r"Attacker/Source: \[(.*?)\]",
        "Impact": r"Impact: \[(.*?)\]",
        "Attack Vector": r"Attack Vector: \[(.*?)\]",
        "Root Cause": r"Root Cause: \[(.*?)\]",
        "Affected Class": r"Affected Class: \[(.*?)\]",
        "Affected Method": r"Affected Method: \[(.*?)\]",
        "Recommended Upgrade": r"Recommended Upgrade: \[(.*?)\]",
    }
    
    # Iterate over the patterns and extract information
    for key, pattern in patterns.items():
        match = re.search(pattern, output_text)
        if match:
            info_dict[key] = match.group(1).strip()
        else:
            info_dict[key] = None  # Use None or an appropriate placeholder if the pattern is not found
    
    return info_dict

def dissect_description_llama2(model=None, description = """The REST Plugin in Apache Struts 2.1.1 through 2.3.x before 2.3.34 and 2.5.x before 2.5.13 uses an XStreamHandler with an instance of XStream for deserialization without any type filtering, which can lead to Remote Code Execution when deserializing XML payloads."""):
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Crafting a comprehensive prompt for detailed analysis
    prompt = f"""Given the CVE description, provide a detailed analysis including the following aspects:
    - Type of vulnerability (vulnerability_type)
    - Product with the vulnerability (library)
    - Vendor of the affected component (vendor)
    - Versions of the library affected (version)
    - Attacker or source of the attack (attacker)
    - Impact of the vulnerability (impact)
    - Attack vector (attack vector)
    - Root cause of the vulnerability (root cause)
    - Affected class (affected class)
    - Affected method (affected method)
    - Recommended upgrade (upgrade)

    Please structure your response as follows: "Vulnerability Type: [type], Product: [library], Vendor: [vendor], Affected Versions: [version], Attacker/Source: [attacker], Impact: [impact], Attack Vector: [attack vector], Root Cause: [root cause], Affected Class: [affected class], Affected Method: [affected method], Recommended Upgrade: [upgrade]."

    Example CVE description:
    {description}
    """

    # Encode the prompt
    input_ids = tokenizer.encode(prompt, return_tensors='pt')

    # Generate the response
    output = model.generate(input_ids, max_length=1024, num_return_sequences=1)

    # Decode and print the output
    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
    print(decoded_output)



def dissect_description(qa_model=None, description = """The REST Plugin in Apache Struts 2.1.1 through 2.3.x before 2.3.34 and 2.5.x before 2.5.13 uses an XStreamHandler with an instance of XStream for deserialization without any type filtering, which can lead to Remote Code Execution when deserializing XML payloads."""):
    if qa_model is None:
        # Initialize the QA model
        qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2", device=0 if torch.cuda.is_available() else -1)


    # Define your questions
    questions = {
        "vulnerability_type": "What is the type of vulnerability?",
        "library": "Which product has the vulnerability?",
        "vendor": "Who is the vendor of the affected component?",
        "version": "Which version of the library is affected?",
        "attacker": "Who is the attacker or what is the source of the attack?",
        "impact": "What is the impact of the vulnerability?",
        "attack vector": "What is the attack vector?",
        "root cause": "What is the root cause of the vulnerability?",
        "affected class": "What is the affected class?",
        "affected method": "What is the affected method?",
        "upgrade": "What is the recommended upgrade?", 
    }
    ret = {}
    # Extract answers
    for key, question in questions.items():
        result = qa_model(question=question, context=description)
        ret[key] = result['answer']
    return ret
    

