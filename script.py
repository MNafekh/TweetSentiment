import datetime
from textblob import TextBlob
from twitter.search import search
import pandas as pd
import yfinance as yf

# Define function to check if a given stock ticker exists on Yahoo Finance
def check_ticker_exists(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    if 'quoteType' in info:
        return True
    return False

# Define function to get sentiment polarity of a tweet
def get_tweet_sentiment(tweet):
    analysis = TextBlob(tweet)
    return analysis.sentiment.polarity

# Define function to get weighted sentiment of all tweets for a given stock ticker
def get_weighted_sentiment(ticker):
    if not check_ticker_exists(ticker):
        return 0
    untildate = datetime.datetime.today()
    sincedate = untildate - datetime.timedelta(days=1)
    searchstring = f"{ticker} until:{untildate.strftime('%Y-%m-%d')} since:{sincedate.strftime('%Y-%m-%d')}"
    search_result = search(searchstring, limit=100)
    df = pd.DataFrame(columns=['text', 'followers'])
    search_result = search_result[0]
    for tweetset in search_result: # need to further decompose tweet object content
        gObj = tweetset["globalObjects"]
        tweets: dict = gObj["tweets"]
        users: dict = gObj["users"]
        for _, tweet in tweets.items():
            row = {'text': tweet["full_text"], 'followers': users.get(tweet["user_id_str"])["followers_count"]}
            df_new = pd.DataFrame(row, index=[0])
            df = pd.concat([df, df_new], ignore_index=True)
    df['sentiment'] = df['text'].apply(get_tweet_sentiment)
    df['weighted_sentiment'] = df['sentiment'] * df['followers']
    weighted_sentiment = df['weighted_sentiment'].sum() / df['followers'].sum()
    return weighted_sentiment

# Example usage
ticker = 'AAPL'
weighted_sentiment = get_weighted_sentiment(ticker)
print(f"Weighted sentiment for {ticker} is {weighted_sentiment}")
