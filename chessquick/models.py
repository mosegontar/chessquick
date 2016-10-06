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
    

class Matches(db.Model):

    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_url = db.Column(db.String(8), unique=True)
    white_player_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    black_player_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    white_player = db.relationship('Users', foreign_keys=[white_player_id])
    black_player = db.relationship('Users', foreign_keys=[black_player_id])


class Rounds(db.Model):
    """Rounds model"""

    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key = True)
    match_url = db.Column(db.String(8))
    turn_number = db.Column(db.Integer)
    date_of_turn = db.Column(db.DateTime)
    fen_string = db.Column(db.String(80))

    @staticmethod
    def make_new_game(date_of_turn):

        while True:
            match_url = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) \
                        for _ in range(8))     
            url_exists = Rounds.query.filter_by(match_url=match_url).first()
            if not url_exists:
                break

        new_game = Rounds(match_url=match_url, 
                          turn_number=0, 
                          date_of_turn=date_of_turn, 
                          fen_string=app.config['STARTING_FEN_STRING'])
        
        db.session.add(new_game)
        db.session.commit()

        return match_url

    @staticmethod
    def add_turn_to_game(match_url, fen, date_of_turn):

        game_rounds = Rounds.query.filter_by(match_url=match_url).all()
        if not game_rounds:
            match_url = Rounds.make_new_game(date_of_turn)
        num_rounds = len(game_rounds) - 1 # because starting position is turn number 0
        turn_number = num_rounds + 1

        turn_entry = Rounds(match_url=match_url, turn_number=turn_number, date_of_turn=date_of_turn, fen_string=fen)
        db.session.add(turn_entry)
        db.session.commit()

        return match_url
