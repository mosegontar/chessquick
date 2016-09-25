import string
import random
from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.static_folder = 'static'


# Config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Games(db.Model):
    #Games model
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(8))
    turn_number = db.Column(db.Integer)
    fen_string = db.Column(db.String(80))



    def __init__(self, url=None, turn_number=None, fen_string='start'):
        if not url:
            self.url = None
            self.turn_number = 0
            self.fen_string = 'start'
        else:
            self.url = url
            self.turn_number = turn_number
            self.fen_string = fen_string

def make_new_game(fen_string):

    while True:
        new_url = ''.join(random.choice(string.ascii_uppercase + stringascii_lowercase + string.digits) \
                    for _ in range(8))     
        url_exists = Games.query.filter_by(url=new_url).first()
        if not url_exists:
            break

    new_game = Games(new_url, 0, 'start')



@app.route('/_get_fen')
def get_fen():
    fen = request.args.get('fen_move')
    game_id = request.args.get('game_id')
    print(game_id)
    return fen

@app.route('/<game_id>')
def index(game_id=None):
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)