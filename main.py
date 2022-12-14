import tweepy
import pandas as pd
import re

import matplotlib.pyplot as plt
from wordcloud import WordCloud

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

consumer_key = '78F6GWmlPoJX4CtW8E5A4dQYf'
consumer_secret = 'Uj3ZCkYe47HOLG0OOyXUly3wyvwhFAG8GLuQqZHVqse6VipfwJ'
access_token = '1310463220281495552-D8AOegt4AcMXgiC738DgD6STjQbaVi'
access_token_secret = 'PrcCzW7N4LmEcLIKnxv7VcX8ytwwCsAIdal2EWXROhKAh'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

key_word = 'bitcoin'
limit = 500

def TextClean(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r'@[a-z0-9_]\S+', '', tweet)
    tweet = re.sub(r'#[a-z0-9_]\S+', '', tweet)
    tweet = re.sub(r'&[a-z0-9_]\S+', '', tweet)
    tweet = re.sub(r'[?!.+,;$%&"]+', '', tweet)
    tweet = re.sub(r'rt[\s]+', '', tweet)
    tweet = re.sub(r'\d+', '', tweet)
    tweet = re.sub(r'\$', '', tweet)
    tweet = re.sub(r'rt+', '', tweet)
    tweet = re.sub(r'https?:?\/\/\S+', '', tweet)

    return tweet

def tweet_search(key_word):
    i = 0
    tweets_df = pd.DataFrame(columns = ['Datetime', 'Tweet', 'Username', 'Retweets', 'Followers'])
    for tweet in tweepy.Cursor(api.search_tweets, q = key_word, count = 100, lang = 'en', tweet_mode = 'extended').items():
        print('Tweets downloaded:', i, '/', limit, end = '\r')
        if tweet.user.followers_count > 500:
            tweets_df = tweets_df.append({'Datetime': tweet.created_at,
                                          'Tweet': tweet.full_text,
                                          'Username': tweet.user.screen_name,
                                          'Retweets': tweet.retweet_count,
                                          'Followers': tweet.user.followers_count,}, ignore_index = True)
            i += 1
        if i >= limit:
            break
        else:
            pass

    tweets_df['Datetime'] = pd.to_datetime(tweets_df['Datetime'], format = '%Y.%m.%d %H:%M:%S')
    tweets_df.set_index('Datetime', inplace = True)
    tweets_df['CleanTweet'] = tweets_df['Tweet'].apply(TextClean)
    tweets_df.to_csv(key_word + '.csv', encoding = 'utf-8')
    return tweets_df

tweets_df = tweet_search(key_word)

tweets_df

all_tweets = ' '.join(tweet for tweet in tweets_df['CleanTweet'])
all_tweets

WordCloud = WordCloud(width = 800, height = 400, random_state = 21, max_font_size = 100, collocations = False).generate(all_tweets)

plt.figure(figsize = (20, 10))
plt.imshow(WordCloud, interpolation = 'bilinear')
plt.axis('off')

plt.style.use('ggplot')
word_frequency = pd.DataFrame.from_dict(data = WordCloud.words_, orient = 'index')
word_frequency = word_frequency.head(20)
plt.figure(figsize = (20, 10))
plt.bar(word_frequency.index, word_frequency[0])
plt.xticks(rotation = 90)

tokens = word_tokenize(all_tweets)
tokens

lemmatizer = WordNetLemmatizer()
lemma = [lemmatizer.lemmatize(tweet, pos = 'v') for tweet in tokens]
print(tokens[:20])
print(lemma[:20])

porter_stemmer = PorterStemmer()
stemm = [porter_stemmer.stem(tweet) for tweet in tokens]
print(tokens[:20])
print(stemm[:20])

print('Number of word in tweets:', len(all_tweets))
print('Number of tokens:', len(tokens))
print('Number of lemmas:', len(lemma))
print('Number of stemms:', len(stemm))

df = pd.DataFrame(columns = ['Tokens', 'Stemm', 'Lemma'])
df['Tokens'] = tokens[:50]
df['Stemm'] = stemm[:50]
df['Lemma'] = lemma[:50]
df

def vader_compound_score(tweet):
    vader = SentimentIntensityAnalyzer()
    if vader.polarity_scores(tweet)['compound'] >= 0.05:
        return 'Positive'
    elif vader.polarity_scores(tweet)['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def textblob_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

vader = SentimentIntensityAnalyzer()

print(vader.polarity_scores('This is good'))
print(vader.polarity_scores('This is really good'))
print(vader.polarity_scores('This is great'))
print(vader.polarity_scores('This is terrible'))
print(vader.polarity_scores('How are you? :)'))
print(vader.polarity_scores('How are you? :('))
print(vader.polarity_scores('This is fine'))
print(vader.polarity_scores('This is fine!'))
print(vader.polarity_scores('This is FINE'))
print(vader.polarity_scores('I used to like him, but now I see he is jerk'))

from textblob import TextBlob

print(TextBlob('This is good').sentiment)
print(TextBlob('This is really good').sentiment)
print(TextBlob('This is great').sentiment)
print(TextBlob('This is terrible').sentiment)
print(TextBlob('How are you?').sentiment)
print(TextBlob('How are you? :)').sentiment)
print(TextBlob('How are you? :(').sentiment)
print(TextBlob('This is fine').sentiment)
print(TextBlob('This is fine!').sentiment)
print(TextBlob('This is FINE').sentiment)
print(TextBlob('I used to love him, but now I see he is jerk').sentiment)

tweets_df['Vader_sent'] = tweets_df['CleanTweet'].apply(vader_compound_score)
tweets_df['TextBlob_sent'] = tweets_df['CleanTweet'].apply(textblob_sentiment)
tweets_df

vader_pie = [len(tweets_df[tweets_df['Vader_sent'] == 'Positive']),
             len(tweets_df[tweets_df['Vader_sent'] == 'Negative']),
             len(tweets_df[tweets_df['Vader_sent'] == 'Neutral'])]
blob_pie = [len(tweets_df[tweets_df['TextBlob_sent'] == 'Positive']),
            len(tweets_df[tweets_df['TextBlob_sent'] == 'Negative']),
            len(tweets_df[tweets_df['TextBlob_sent'] == 'Neutral'])]
labels = ['Positive', 'Negative', 'Neutral']
colors = ['aquamarine', 'tomato', 'skyblue']

plt.style.use('ggplot')
plt.figure(figsize = (20, 10))
plt.subplot(1, 2, 1)
plt.pie(vader_pie, labels = labels, colors = colors, autopct = '%1.1f%%')
plt.title('Vader')

plt.subplot(1, 2, 2)
plt.pie(blob_pie, labels = labels, colors = colors, autopct = '%1.1f%%')
plt.title('TextBlob')