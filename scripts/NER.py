import os
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

# Set the classpath to the directory where Stanford NER is installed
# Replace 'path_to_stanford_ner_folder' with the actual path on your machine
os.environ['CLASSPATH'] = 'stanford-ner-2020-11-17'

# Set the Stanford models to the path where the models are located
# Replace 'path_to_stanford_ner_models' with the actual path on your machine
os.environ['STANFORD_MODELS'] = 'stanford-ner-2020-11-17/classifiers/'

# Replace 'english.muc.7class.distsim.crf.ser.gz' with the model you wish to use
# This model is suitable for identifying elements like Location, Person, Organization, etc.
# For CVE descriptions, you might need a custom-trained model or use the 7-class model to see if it fits your needs
stanford_ner_model = 'english.muc.7class.distsim.crf.ser.gz'

# Initialize the NER tagger
st = StanfordNERTagger(stanford_ner_model)

# Your sample CVE description text
text = 'Apache Log4j2 2.0-beta9 through 2.15.0 (excluding security releases 2.12.2, 2.12.3, and 2.3.1) JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints. An attacker who can control log messages or log message parameters can execute arbitrary code loaded from LDAP servers when message lookup substitution is enabled. From log4j 2.15.0, this behavior has been disabled by default. From version 2.16.0 (along with 2.12.2, 2.12.3, and 2.3.1), this functionality has been completely removed. Note that this vulnerability is specific to log4j-core and does not affect log4net, log4cxx, or other Apache Logging Services projects.'

# Tokenize the text
tokenized_text = word_tokenize(text)

# Tag the text and print it
classified_text = st.tag(tokenized_text)

print(classified_text)
