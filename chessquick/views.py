import datetime

from flask import   render_template, url_for, request, jsonify, session, \
    redirect, g
from flask_login import login_user, logout_user, current_user, login_required

from chessquick import app, db, login_manager
from chessquick.models import Rounds, Users, Matches
from chessquick.forms import EmailPasswordForm


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user

@app.route('/_bookmark')
@login_required
def bookmark():
    
    current_player = request.args.get('current_player')
    action = request.args.get('action')
    match_url = request.args.get('match_url')

    match = Matches.get_match_by_url(match_url)

    if action == 'bookmark':

        if not match or (match.white_player and match.black_player):
            return redirect(url_for('index'))
        elif current_player == 'w' and not match.white_player:
            match.white_player = current_user
        elif current_player == 'b' and not match.black_player:
            match.black_player = current_user
        else:
            pass

    elif action == 'unbookmark':

        if not match or (not match.white_player and not match.black_player): 
            return redirect(url_for('index'))
        elif current_user == match.white_player:
            match.white_player = None
        elif current_user == match.black_player:
            match.black_player = None
        else:
            pass
    else:
        pass


    db.session.add(match)
    db.session.commit()
    white_player_name = match.white_player.email if match.white_player else 'Guest'
    black_player_name = match.black_player.email if match.black_player else 'Guest'

    return jsonify(white_player_name=white_player_name, black_player_name=black_player_name)


@app.route('/_get_fen')
def get_fen():

    fen = request.args.get('fen_move')
    game_url = request.args.get('match_url')
    current_player = request.args.get('current_player')
    _match_url = game_url.strip('/')
    time_of_turn = datetime.datetime.utcnow()

    match_url = Rounds.add_turn_to_game(_match_url, fen, time_of_turn)
    session[match_url] = current_player

    return jsonify(game_url=match_url)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = EmailPasswordForm()
    if form.validate_on_submit():
        user = Users(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)

def next_is_valid(endpoint):
    return endpoint in app.viewfunctions

@app.route('/login', methods=['GET', 'POST'])
def login():

    game_url = request.args.get('game_url')
    if not game_url: game_url = '/'

    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index', game_url=game_url))

    form = EmailPasswordForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        
        if user and user.is_correct_password(form.password.data):
            login_user(user)
            next_url = request.args.get('next')

            if next_url and not next_is_valid(next_url.strip('/')):
                next_url = None

            return redirect(next_url or url_for('index', game_url=game_url))
        else:
            return redirect(url_for('login', game_url=game_url))

    return render_template('login.html', form=form, game_url=game_url)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/')
@app.route('/<game_url>')
def index(game_url='/'):

    users = Users.query.all()

    match_url = game_url.strip('/')
    existing_game = Matches.get_match_by_url(match_url) if match_url else None

    taken_players = {'w': False, 'b': False}
    if not existing_game:
        fen = app.config['STARTING_FEN_STRING']
        current_player = 'w'
        date_of_turn = None
    else:
        taken_players['w'] = existing_game.white_player.email if existing_game.white_player else False
        taken_players['b'] = existing_game.black_player.email if existing_game.black_player else False

        game_rounds = existing_game.rounds.all()
        most_recent_round = game_rounds[-1]
        date_of_turn = most_recent_round.date_of_turn
        fen = most_recent_round.fen_string
        current_player = session[match_url] if match_url in session.keys() else ''

    return render_template('index.html', 
                           fen=fen, 
                           current_player=current_player,
                           root_path = request.url_root,
                           game_url=game_url,
                           round_date=date_of_turn,
                           taken_players=taken_players)                          
