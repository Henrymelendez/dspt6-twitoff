from os import getenv
from flask import Flask, render_template, request, jsonify, redirect
from dotenv import load_dotenv
from .model import db, User
from .twitter import add_user_tweepy, update_all_users
from .predict import predict_user

load_dotenv()

def create_app():
    ''' Create and configure an instance of the flask application'''

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/')
    def root():
        return render_template('base.html',title='Home',users= User.query.all())
    
    @app.route('/user',methods=['POST'])
    @app.route('/user/<name>',methods=['GET'])
    def user(name=None,message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_user_tweepy(name)
                message = "User {} successfully added!".format(name)
            tweets = User.query.filter(User.username == name).one().tweet
        except Exception as e:
            message = "Error adding {}: {}".format(name,e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,message=message)
    
    
    
    @app.route('/compare',methods=['POST'])        
    def compare(message=''):
        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']

        if user1 == user2:
            message = 'Cannot compare to self'
        else:
            prediction = predict_user(user1, user2, message)
            message = '"{}"is more likely to be said by {} than {}'.format(tweet_text, user1 if prediction else user2, user2 if prediction else user1)
        
            return render_template('prediction.html',title='Prediction', message=message)
    @app.route('/update', methods=['GET'])
    def update():
        update_all_users()
        return render_template('base.html', title='All tweets updated', users=User.query.all())
    
    @app.route('/reset')
    def reset():
        db.drop_all()
        db.create_all()
        return render_template('base.html', title='Reset DataBase!', users=User.query.all())
        
    return app
    
if __name__ == 'main':
    app.run(debug=True)