'''Prediction of Users based on tweet Embeddings'''
import numpy as np
from sklearn.linear_model import LogisticRegression
from .model import User
from .twitter import BASILICA

def predict_user(user1,user2,tweet_text):
    ''' Determine and retun which user is more likely to say a given tweet

    #Argument:
     user1: str, twitter username for user 1 in comparison from web form
     user2: str, twitter username for user 2 in comparison from web form
     tweet_text: str, tweet text to evalute

    
    # Returns:
      prediction from logistic regression model
    '''
    user1 = User.query.filter(User.username == user1).one()
    user2 = User.query.filter(User.username == user2).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.tweet])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.tweet])
    # combine embeddings and reate labels
    embeddings = np.vstack([user1_embeddings,user2_embeddings])
    labels = np.concatenate([np.ones(len(user1_embeddings)),
                             np.zeros(len(user2_embeddings))])
    
    # train model and convert input to embeddings 
    lr = LogisticRegression().fit(embeddings,labels)
    tweet_embedding = BASILICA.embed_sentence(tweet_text,model='twitter')
    return lr.predict(np.array(tweet_embedding).reshape(1,-1))

