import string
import random
from flask import Flask, render_template, url_for, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.static_folder = 'static'


# Config
app.config['SECRET_KEY'] = 'quiet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Games(db.Model):
    #Games model
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.String(8))
    turn_number = db.Column(db.Integer)
    fen_string = db.Column(db.String(80))


def make_new_game():

    while True:
        new_url = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) \
                    for _ in range(8))     
        url_exists = Games.query.filter_by(game_id=new_url).first()
        if not url_exists:
            break

    new_game = Games(game_id=new_url, turn_number=0, fen_string='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    db.session.add(new_game)
    db.session.commit()

    return new_url

def add_turn_to_game(game_id, fen):

    game_rounds = Games.query.filter_by(game_id=game_id).all()
    if not game_rounds:
        return False
    num_rounds = len(game_rounds) - 1 # because starting position is turn number 0
    turn_number = num_rounds + 1

    turn_entry = Games(game_id=game_id, turn_number=turn_number, fen_string=fen)
    db.session.add(turn_entry)
    db.session.commit()


@app.route('/_get_fen')
def get_fen():
    fen = request.args.get('fen_move')
    game_url = request.args.get('game_id')
    current_player = request.args.get('current_player')
    game_id = game_url.strip('/')

    if not game_id:
        game_url = make_new_game()
        session[game_url] = 'w'
        add_turn_to_game(game_url, fen)
    else:
        if game_id not in session.keys():
            session[game_id] = current_player

        add_turn_to_game(game_id, fen)

    game_url = game_url.strip('/')
    return jsonify(game_url=game_url)

@app.route('/')
@app.route('/<game_url>')
def index(game_url='/'):

    game_id = game_url.strip('/')
    existing_game = Games.query.filter_by(game_id=game_id).all() if game_id else None

    if not existing_game:
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        current_player = 'w'
    else:
        most_recent_round = existing_game[-1]
        fen = most_recent_round.fen_string
        current_player = session[game_id] if game_id in session.keys() else ''

    return render_template('index.html', 
                            fen=fen, 
                            current_player=current_player,
                            root_path = request.url_root,
                            game_url=game_url)                          



if __name__ == '__main__':
    app.run(debug=True)