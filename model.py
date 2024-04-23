import gensim
import pandas as pd
import numpy as np

lda_model = gensim.models.LdaModel.load(r'C:\Users\scxrp\Downloads\sem_6\nlp\project\model\model3_path\model3')

dictionary = gensim.corpora.Dictionary.load(r'C:\Users\scxrp\Downloads\sem_6\nlp\project\model\model3_path\model3.id2word')

topic_labels = {
    0: "NATION",
    1: "FINANCE",
    2: "WORLD",
    3: "SCIENCE",
    4: "HEALTH",
    5: "BUSINESS",
    6: "TECHNOLOGY",
    7: "SPORTS"
}
user_input = input("Enter your input: ")

# Tokenize user input
tokenized_input = user_input.lower().split()

# Convert input to bag-of-words representation
bow_input = dictionary.doc2bow(tokenized_input)

# Infer the topic distribution for the input
topic_distribution = lda_model.get_document_topics(bow_input)

# Find the topic with the highest probability for the input
most_probable_topic = max(topic_distribution, key=lambda x: x[1])

# Assign the topic label to the input
topic_label = topic_labels[most_probable_topic[0]]

print(f"The input belongs to topic: {topic_label}")
