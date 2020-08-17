from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(80),unique= True, nullable= False)
    followers = db.Column(db.Integer, nullable= False)
    newest_tweet_id = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key = True)
    embedding = db.Column(db.PickleType,nullable = False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tweet', lazy = True))
    text = db.Column(db.Unicode(300))

    def __repr__(self):
        return '<Tweet %r>' % self.text
