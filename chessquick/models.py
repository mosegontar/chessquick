import string
import random

from sqlalchemy.ext.hybrid import hybrid_property

from chessquick import app, db, bcrypt

class Users(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True)
    _password = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        # encoding/decoding utf-8: 
        # http://stackoverflow.com/questions/34548846/flask-bcrypt-valueerror-invalid-salt
        self._password = bcrypt.generate_password_hash(plaintext.encode('utf-8')).decode('utf-8')

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)


    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
    
"""
class Matches(db.Model):

    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    player_id = db.Column(db.Integer)
    player_color = db.Column()
"""

class Games(db.Model):
    """Games model"""

    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.String(8))
    turn_number = db.Column(db.Integer)
    date_of_turn = db.Column(db.DateTime)
    fen_string = db.Column(db.String(80))

    @staticmethod
    def make_new_game(date_of_turn):

        while True:
            game_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) \
                        for _ in range(8))     
            url_exists = Games.query.filter_by(game_id=game_id).first()
            if not url_exists:
                break

        new_game = Games(game_id=game_id, 
                         turn_number=0, 
                         date_of_turn=date_of_turn, 
                         fen_string=app.config['STARTING_FEN_STRING'])
        
        db.session.add(new_game)
        db.session.commit()

        return game_id

    @staticmethod
    def add_turn_to_game(game_id, fen, date_of_turn):

        game_rounds = Games.query.filter_by(game_id=game_id).all()
        if not game_rounds:
            game_id = Games.make_new_game(date_of_turn)
        num_rounds = len(game_rounds) - 1 # because starting position is turn number 0
        turn_number = num_rounds + 1

        turn_entry = Games(game_id=game_id, turn_number=turn_number, date_of_turn=date_of_turn, fen_string=fen)
        db.session.add(turn_entry)
        db.session.commit()

        return game_id
