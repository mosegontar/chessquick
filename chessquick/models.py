import string
import random

from chessquick import app, db

class Games(db.Model):
    """Games model"""

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