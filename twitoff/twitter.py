from os import getenv
import basilica
import tweepy
from dotenv import load_dotenv
from .model import db,User,Tweet

load_dotenv()

TWITTER_AUTH = tweepy.OAuthHandler(getenv('TWITTER_CONSUMER_API_KEY'),
                                  getenv('TWITTER_CONSUMER_API_SECRET'))
TWITTER_AUTH.set_access_token(getenv('TWITTER_ACCESS_TOKEN'),
                              getenv('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(getenv('BASILICA_KEY'))

def add_user_tweepy(username):
    '''Add a user and their tweets to database'''
    try:
        # Get user info from tweepy
        twitter_user = TWITTER.get_user(username)

        # Add to User table (or check if existing)
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id,
                        username=username,
                        followers=twitter_user.followers_count))
        db.session.add(db_user)

        # Get tweets ignoring re-tweets and replies
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)
        oldest_max_id = tweets[-1].id -1
        tweet_history = []
        tweet_history += tweets
    
    
        # Add newest_tweet_id to the User table
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        
        # Continue to collect tweets using_max_id and update until 3200 tweet max
        while True:
            tweets = twitter_user.timeline(count=200,
                                           exclude_replies=True,
                                           include_rts=False,
                                           tweet_mode='extended',
                                           max_id = oldest_max_id)
            if len(tweets) == 0:
                break
            oldest_max_id = tweets[-1].id -1
            tweet_history = []
            tweet_history += tweets
        
        print(f'Total Tweets collected for {username}: {len(tweet_history)}')
    
    
        # Loop over tweets, get embedding and add to Tweet table
        for tweet in tweet_history:

            # Get an examble basilica embedding for first tweet
            embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')

            # Add tweet info to Tweet table
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             embedding=embedding)
            db_user.tweet.append(db_tweet)
            db.session.add(db_tweet)

    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e

    else:
        # If no errors happend than commit the records
        db.session.commit()

def add_user_history(username):
    '''Add a user and their tweets to database'''
    try:
        # Get user info from tweepy
        twitter_user = TWITTER.get_user(username)
        # Add to User table (or check if existing)
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id,
                        username=username,
                        follower_count=twitter_user.followers_count))
        db.session.add(db_user)
        # Get tweets ignoring re-tweets and replies
        tweets = twitter_user.timeline(count=200, 
                                       exclude_replies=True, 
                                       include_rts=False, 
                                       tweet_mode='extended')
        oldest_max_id = tweets[-1].id - 1
        tweet_history = []
        tweet_history += tweets
        # Add newest_tweet_id to the User table
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        # Continue to collect tweets using max_id and update until 3200 tweet max
        while True:
            tweets = twitter_user.timeline(count=200,
                                        exclude_replies=True,
                                        include_rts=False,
                                        tweet_mode='extended',
                                        max_id=oldest_max_id)
            if len(tweets) == 0:
                break
            oldest_max_id = tweets[-1].id - 1
            tweet_history += tweets 
        print(f'Total Tweets collected for {username}: {len(tweet_history)}')
        # Loop over tweets, get embedding and add to Tweet table
        for tweet in tweet_history:
            # Get an examble basilica embedding for first tweet
            embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
            # Add tweet info to Tweet table
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             embedding=embedding)
            db_user.tweet.append(db_tweet)
            db.session.add(db_tweet)
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    else:
        # If no errors happend than commit the records
        db.session.commit()
        print('Successfully saved tweets to DB!')
    
    
    def update_all_users():
        ''''Update all tweets for all users in the user table'''
        for user in User.query.all():
            add_user_tweepy()