

#Let's start with importing libraries
 
import numpy as np  #linear Algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.model_selection import train_test_split # function for splitting data to train and test sets

import nltk #he Natural Language Toolkit 
from nltk.corpus import stopwords #remove the low-level information from our text in order to give more focus to the important information.
from nltk.classify import SklearnClassifier

from wordcloud import WordCloud,STOPWORDS # Word Clouds display the most prominent or frequent words in a body of text 
import matplotlib.pyplot as plt # Data Visualization

data = pd.read_csv("/content/Sentiment.csv") #importing data sets using pandas

data.head() #This is for printing starting 5-6 lines of data sets

data.info() #Print a concise summary of a DataFrame.

# Keeping only the neccessary columns
data = data[['text','sentiment']]

"""Splitting the dataset into train and test set"""

train, test = train_test_split(data,test_size = 0.1) #splitting the data set into a training and a testing set. The test set is the 10% of the original data set.

# Removing neutral sentiments
train = train[train.sentiment != "Neutral"] #For this particular analysis I dropped the neutral tweets, as my goal was to only differentiate positive and negative tweets.

#As a next step I separated the Positive and Negative tweets of the training set in order to easily visualize their contained words.
train_pos = train[ train['sentiment'] == 'Positive']
train_pos = train_pos['text']
train_neg = train[ train['sentiment'] == 'Negative']
train_neg = train_neg['text']

# In this step I cleaned the text from hashtags, mentions and links.
# And using wordcloud visualizing only the most emphatic words of the Positive and Negative tweets
def wordcloud_draw(data, color = 'black'):
    words = ' '.join(data)
    cleaned_word = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and not word.startswith('#')
                                and word != 'RT'
                            ])
    wordcloud = WordCloud(stopwords=STOPWORDS,
                      background_color=color,
                      width=2500,
                      height=2000
                     ).generate(cleaned_word)
    plt.figure(1,figsize=(13, 13))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()
    
print("Positive words")
wordcloud_draw(train_pos,'white')
print("Negative words")
wordcloud_draw(train_neg)

# Downloading Packages from nltk for stopwords
nltk.download('stopwords')

tweets = []
stopwords_set = set(stopwords.words("english")) # Stop Words are words which do not contain important significance to be used in Search Queries.
# Usually these words are filtered out from search queries because they return vast amount of unnecessary information. ( the, for, this etc. )

# Next following steps I removed the hashtags, mentions, links and stopwords from the test set.

for index, row in train.iterrows():
    words_filtered = [e.lower() for e in row.text.split() if len(e) >= 3]
    words_cleaned = [word for word in words_filtered
        if 'http' not in word
        and not word.startswith('@')
        and not word.startswith('#')
        and word != 'RT']
    words_without_stopwords = [word for word in words_cleaned if not word in stopwords_set]
    tweets.append((words_without_stopwords, row.sentiment))

test_pos = test[ test['sentiment'] == 'Positive'] # here I seperated positive messages from test data sets.
test_pos = test_pos['text'] # I need only Positive messages so I stored messages in test_pos 
test_neg = test[ test['sentiment'] == 'Negative'] # here I seperated negative messages from test data sets.
test_neg = test_neg['text'] # I need only Negative messages so I stored messages in test_neg.

"""As a next step I extracted the so called features with nltk lib, first by measuring a frequent distribution and by selecting the resulting keys."""

# Extracting word features
def get_words_in_tweets(tweets):
    all = []
    for (words, sentiment) in tweets:
        all.extend(words)
    return all

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    features = wordlist.keys()
    return features
w_features = get_word_features(get_words_in_tweets(tweets))

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in w_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

# Hereby I plotted the most frequently distributed words. The most words are centered around debate nights.
wordcloud_draw(w_features)

# Using the nltk NaiveBayes Classifier I classified the extracted tweet word features.
# Training the Naive Bayes classifier
training_set = nltk.classify.apply_features(extract_features,tweets)
classifier = nltk.NaiveBayesClassifier.train(training_set)

# Finally, with not-so-intelligent metrics, I tried to measure how the classifier algorithm scored
neg_cnt = 0
pos_cnt = 0
for obj in test_neg: 
    res =  classifier.classify(extract_features(obj.split()))
    if(res == 'Negative'): 
        neg_cnt = neg_cnt + 1
for obj in test_pos: 
    res =  classifier.classify(extract_features(obj.split()))
    if(res == 'Positive'): 
        pos_cnt = pos_cnt + 1
        
print('[Negative]: Out of %s test Negative tweet %s is negative tweet are predicted'  % (len(test_neg),neg_cnt))        
print('[Positive]: Out of %s test Positive tweet %s is positive tweet are predicted'  % (len(test_pos),pos_cnt))

labels='Negative tweets','Positive tweets'
sizes=[neg_cnt,pos_cnt]
fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
ax1.axis('equal')

