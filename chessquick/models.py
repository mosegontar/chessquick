import string
import random

from chessquick import app, db

class Games(db.Model):
    """Games model"""

    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.String(8))
    turn_number = db.Column(db.Integer)
    date_of_turn = db.Column(db.DateTime)
    fen_string = db.Column(db.String(80))


def make_new_game(date_of_turn):

    while True:
        game_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) \
                    for _ in range(8))     
        url_exists = Games.query.filter_by(game_id=game_id).first()
        if not url_exists:
            break

    new_game = Games(game_id=game_id, turn_number=0, date_of_turn=date_of_turn, fen_string='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    db.session.add(new_game)
    db.session.commit()

    return game_id

def add_turn_to_game(game_id, fen, date_of_turn):

    game_rounds = Games.query.filter_by(game_id=game_id).all()
    if not game_rounds:
        game_id = make_new_game(date_of_turn)
    num_rounds = len(game_rounds) - 1 # because starting position is turn number 0
    turn_number = num_rounds + 1

    turn_entry = Games(game_id=game_id, turn_number=turn_number, date_of_turn=date_of_turn, fen_string=fen)
    db.session.add(turn_entry)
    db.session.commit()

    return game_id
