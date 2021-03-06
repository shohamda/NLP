# -*- coding: utf-8 -*-
"""NLP HW 1 - Gili

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NWx-_yDe8bZOoXvLMMUYBDNsQZSW-zBy

# Assignment 1
In this assignment you will be creating tools for learning and testing language models.
The corpora that you will be working with are lists of tweets in 8 different languages that use the Latin script. The data is provided either formatted as CSV or as JSON, for your convenience. The end goal is to write a set of tools that can detect the language of a given tweet.

*As a preparation for this task, download the data files from the course git repository.

The relevant files are under **lm-languages-data-new**:


*   en.csv (or the equivalent JSON file)
*   es.csv (or the equivalent JSON file)
*   fr.csv (or the equivalent JSON file)
*   in.csv (or the equivalent JSON file)
*   it.csv (or the equivalent JSON file)
*   nl.csv (or the equivalent JSON file)
*   pt.csv (or the equivalent JSON file)
*   tl.csv (or the equivalent JSON file)
*   test.csv (or the equivalent JSON file)
"""

!git clone https://github.com/kfirbar/nlp-course.git

"""

---



**Important note: please use only the files under lm-languages-data-new and NOT under lm-languages-data**


---

"""

!ls nlp-course/lm-languages-data-new

"""**Part 1**

Write a function *preprocess* that iterates over all the data files and creates a single vocabulary, containing all the tokens in the data. **Our token definition is a single UTF-8 encoded character**. So, the vocabulary list is a simple Python list of all the characters that you see at least once in the data.
"""

import pandas as pd
import numpy as np
import os

def preprocess_tweet(tweet):
    tokens = []
    for c in tweet:
        tokens.append(c)
    return tokens

def unique_values_from_list(lst):
    unique_set = set(lst)
    unique_lst = list(unique_set)
    return unique_lst

def add_unique_symbols(text, n):
    prefix = 'א' * (n-1) 
    suffix = 'ת' * (n-1)
    return prefix + text + suffix

def preprocess_file(file_name):
    data_file_pd = pd.read_csv(f'/content/nlp-course/lm-languages-data-new/{file_name}')
    tweets = data_file_pd['tweet_text']
    tweets_tokens = []
    for tweet in tweets:
        tweet = add_unique_symbols(tweet, 2)
        tweet_tokens = preprocess_tweet(tweet)
        tweets_tokens = tweets_tokens + unique_values_from_list(tweet_tokens)
    return unique_values_from_list(tweets_tokens)

directory = os.fsencode('/content/nlp-course/lm-languages-data-new')
files_tokens = []
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".csv") and (filename not in ['test.csv', 'tests.csv']): 
         print(filename)
         files_tokens = files_tokens + preprocess_file(filename)
vocabulary = unique_values_from_list(files_tokens)

"""**Part 2**

Write a function lm that generates a language model from a textual corpus. The function should return a dictionary (representing a model) where the keys are all the relevant n-1 sequences, and the values are dictionaries with the n_th tokens and their corresponding probabilities to occur. For example, for a trigram model (tokens are characters), it should look something like:

{
  "ab":{"c":0.5, "b":0.25, "d":0.25},
  "ca":{"a":0.2, "b":0.7, "d":0.1}
}

which means for example that after the sequence "ab", there is a 0.5 chance that "c" will appear, 0.25 for "b" to appear and 0.25 for "d" to appear.

Note - You should think how to add the add_one smoothing information to the dictionary and implement it.
"""

def calculate_probas(model, vocabulary, add_one):
    for _, counts in model.items():
        if add_one:
            total_counts = len(vocabulary) + sum(counts.values())
        else:
            total_counts = sum(counts.values())
        for token, count in counts.items():
            counts.update({token : count / total_counts})
    return model

def add_default_zero(model):
    for _, counts in model.items():
        counts.update({'default' : 0})
    return model

def add_one_func(model):
    for _, counts in model.items():
        for token in list(counts.items()):
            counts.update({token[0] : token[1] + 1})
        counts.update({'default' : 1})
    return model

def lm(n, vocabulary, data_file_path, add_one):
    # n - the n-gram to use (e.g., 1 - unigram, 2 - bigram, etc.)
    # vocabulary - the vocabulary list (which you should use for calculating add_one smoothing)
    # data_file_path - the data_file from which we record probabilities for our model
    # add_one - True/False (use add_one smoothing or not)
    data = pd.read_csv(data_file_path)
    model = {}
    for tweet in data['tweet_text']:
        tweet = add_unique_symbols(tweet, n)
        for i in range(len(tweet) - n + 1):
            ngram = tweet[i:i+n]
            if ngram[0:n-1] not in model.keys():
                model.update({ngram[0:n-1] : {}})
            counts = model[ngram[0:n-1]]
            if ngram[n-1:n] in counts.keys():
                current_val = counts.get(ngram[n-1:n]) + 1
            else:
                current_val = 1
            counts.update({ngram[n-1:n] : current_val})
    if add_one:
        model = add_one_func(model)
    else:
        model = add_default_zero(model)
    model = calculate_probas(model, vocabulary, add_one)
    return model

"""**Part 3**

Write a function *eval* that returns the perplexity of a model (dictionary) running over a given data file.
"""

def evaluate(n, model, data_file):
    # n - the n-gram that you used to build your model (must be the same number)
    # model - the dictionary (model) to use for calculating perplexity
    # data_file - the tweets file that you wish to claculate a perplexity score for
    tweets = data_file['tweet_text']
    total_entropy = []
    for tweet in tweets:
        tweet = add_unique_symbols(tweet, n)
        entropy = []
        for i in range(len(tweet) - n + 1):
            ngram = tweet[i:i+n]
            proba = model.get(ngram[0:n-1],{}).get(ngram[n-1:], model.get(ngram[0:n-1],{}).get('default',0))
            if proba != 0:
                entropy.append(-1 * np.log2(proba))
        tweet_entropy = sum(entropy)
        total_entropy.append(tweet_entropy / (len(tweet) - n + 1))
    H = sum(total_entropy) / len(tweets)
    perplexity = 2 ** H
    return perplexity

"""**Part 4**

Write a function *match* that creates a model for every relevant language, using a specific value of *n* and *add_one*. Then, calculate the perplexity of all possible pairs (e.g., en model applied on the data files en ,es, fr, in, it, nl, pt, tl; es model applied on the data files en, es...). This function should return a pandas DataFrame with columns [en ,es, fr, in, it, nl, pt, tl] and every row should be labeled with one of the languages. Then, the values are the relevant perplexity values.
"""

def match(n, add_one):
    # n - the n-gram to use for creating n-gram models
    # add_one - use add_one smoothing or not
    languages = ['en','es', 'fr', 'in', 'it', 'nl', 'pt', 'tl']
    file_path = '/content/nlp-course/lm-languages-data-new/'
    perplexity = []
    for model_lang in languages:
        model = lm(n, vocabulary, f'{file_path}{model_lang}.csv', add_one)
        values = []
        for value_lang in languages:
            data_file = pd.read_csv(f'{file_path}{value_lang}.csv')
            values.append(float('%.2f' % evaluate(n, model, data_file)))
        perplexity.append(values)
    return pd.DataFrame(perplexity, index = languages, columns = languages)

"""**Part 5**

Run match with *n* values 1-4, once with add_one and once without, and print the 8 tables to this notebook, one after another.
"""

for n in range(1,5):
    for add_one in [True, False]:
        print(f'n = {n}, add_one = {add_one}:')
        print(match(n, add_one))

"""**Part 6**

Each line in the file test.csv contains a sentence and the language it belongs to. Write a function that uses your language models to classify the correct language of each sentence.

Important note regarding the grading of this section: this is an open question, where a different solution will yield different accuracy scores. any solution that is not trivial (e.g. returning 'en' in all cases) will be excepted. We do reserve the right to give bonus points to exceptionally good/creative solutions.
"""

def evaluate_tweet(n, model, tweet):
    # n - the n-gram that you used to build your model (must be the same number)
    # model - the dictionary (model) to use for calculating perplexity
    # tweet - the tweetthat you wish to claculate a perplexity score for
    tweet_text = tweet['tweet_text']
    tweet_text = add_unique_symbols(tweet_text, n)
    entropy = []
    for i in range(len(tweet_text) - n + 1):
        ngram = tweet_text[i:i+n]
        proba = model.get(ngram[0:n-1],{}).get(ngram[n-1:], model.get(ngram[0:n-1],{}).get('default',0))
        if proba != 0:
            entropy.append(-1 * np.log2(proba))
    tweet_entropy = sum(entropy) / (len(tweet_text) - n + 1)
    tweet_perplexity = 2 ** tweet_entropy
    return tweet_perplexity

# create all models for classification

languages = ['en','es', 'fr', 'in', 'it', 'nl', 'pt', 'tl']
file_path = '/content/nlp-course/lm-languages-data-new/'
models = {}

for lang in languages:
    for n in range(1,6):
        for add_one in [True, False]:
            model = lm(n, vocabulary, f'{file_path}{lang}.csv', add_one)
            if lang in models:
                if n in models[lang]:
                    models[lang][n].update({add_one : model})
                else:
                    models[lang].update({n : {add_one : model}})
            else:
                models.update({lang: {n : {add_one:model}}})

"""### Classification using majority voting"""

def classify(models):
    languages = ['en','es', 'fr', 'in', 'it', 'nl', 'pt', 'tl']
    file_path = '/content/nlp-course/lm-languages-data-new/'
    data_file  = pd.read_csv(f'{file_path}test.csv')

    final_predictions = []
    for tweet_idx in range(0, len(data_file)):
        tweet_predictions = []
        tweet = data_file.iloc[tweet_idx]
        for n in range(1, 5):
            for add_one in [True, False]:  # [True, False]
                perplexity = {}
                for model_lang in languages:
                    model = models[model_lang][n][add_one]
                    perplexity.update({model_lang : evaluate_tweet(n, model, tweet)})
                tweet_predictions.append(min(perplexity, key=perplexity.get))
        final_predictions.append((tweet['tweet_id'],max(tweet_predictions,key=tweet_predictions.count)))
    return final_predictions

final_predictions = classify(models)
predictions_df = pd.DataFrame(final_predictions)

labels_df = pd.read_csv('/content/nlp-course/lm-languages-data-new/test.csv')

# used macro average for balanced dataset
from sklearn.metrics import f1_score
f1_score(labels_df['label'],predictions_df[1], average='macro')

"""### Classification with predictive model (n-gram predictions as features)"""

def create_dataset(language, models, data_file):
    # data file is a file of specific language
    languages = ['en','es', 'fr', 'in', 'it', 'nl', 'pt', 'tl']
    final_features = []
    for tweet_idx in range(0, len(data_file)):
        tweet_predictions = []
        tweet = data_file.iloc[tweet_idx]
        tweet_predictions.append(tweet['tweet_id'])
        for n in range(1, 6):
            for add_one in [True, False]:  # [True, False]
                perplexity = {}
                for model_lang in languages:
                    model = models[model_lang][n][add_one]
                    perplexity.update({model_lang : evaluate_tweet(n, model, tweet)})
                tweet_predictions.append(min(perplexity, key=perplexity.get))
        tweet_predictions.append(language)
        final_features.append(tweet_predictions)
    df = pd.DataFrame(final_features, columns = ['tweet_id'] + ["feature_"+str(x) for x in range(1, (len(tweet_predictions) - 1))] + ['label'])
    df.set_index(df.columns[0])
    return df

! pip install catboost

file_path = '/content/nlp-course/lm-languages-data-new/'
languages = ['en','es', 'fr', 'in', 'it', 'nl', 'pt', 'tl']

feature_matrix = None
for lang in languages:
    data_file  = pd.read_csv(f'{file_path}{lang}.csv')
    df = create_dataset(lang, models, data_file)
    feature_matrix = df if feature_matrix is None else pd.concat([feature_matrix, df]) 
feature_matrix

feature_matrix2 = feature_matrix.set_index(feature_matrix.columns[0])
feature_matrix2

file_path = '/content/nlp-course/lm-languages-data-new/'

data_file  = pd.read_csv(f'{file_path}test.csv')
test_matrix = create_dataset('test', models, data_file)
test_matrix.merge(data_file, on='tweet_id', how='inner')
test_matrix

test_matrix2 = test_matrix.merge(data_file, on='tweet_id', how='inner').drop(['label_x', 'tweet_text'], axis=1).rename(columns = {'label_y' : 'label'})
test_matrix2 = test_matrix2.set_index(test_matrix2.columns[0])
test_matrix2

from catboost import Pool, CatBoostClassifier

def catboost_classification(feature_matrix, test_matrix):
    train = feature_matrix[feature_matrix.columns[:-1]]
    label = feature_matrix[feature_matrix.columns[-1:]]
    cat_features = range(0,10)
    train_dataset = Pool(data = train, label = label, cat_features=cat_features)

    model = CatBoostClassifier(iterations=100,
                           learning_rate=0.05,
                           loss_function='MultiClass')
    model.fit(train_dataset)

    test = test_matrix[feature_matrix.columns[:-1]]
    label = test_matrix[feature_matrix.columns[-1:]]
    cat_features = range(0,10)
    test_dataset = Pool(data = test, label = label, cat_features=cat_features)
    preds_class = model.predict(test_dataset)
    return preds_class

preds = catboost_classification(feature_matrix2, test_matrix2)

"""**Part 7**

Calculate the F1 score of your output from part 6. (hint: you can use https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html). 

"""

# used macro average for balanced dataset
from sklearn.metrics import f1_score
f1_score(test_matrix2['label'], preds, average='macro')

"""# **Good luck!**"""