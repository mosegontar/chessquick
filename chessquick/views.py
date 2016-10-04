import datetime

from flask import   render_template, url_for, request, jsonify, session, redirect
from flask_login import login_user

from chessquick import app, db, login_manager
from chessquick.models import Games, Users
from chessquick.forms import EmailPasswordForm

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route('/_get_fen')
def get_fen():

    fen = request.args.get('fen_move')
    game_url = request.args.get('game_id')
    current_player = request.args.get('current_player')
    _game_id = game_url.strip('/')
    time_of_turn = datetime.datetime.utcnow()

    game_id = Games.add_turn_to_game(_game_id, fen, time_of_turn)
    session[game_id] = current_player

    return jsonify(game_url=game_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = EmailPasswordForm()
    if form.validate_on_submit():
        user = Users(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
#@app.route('/login/<game_url>')
def login():#(game_url=None):
    form = EmailPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first_or_404()
        if user.is_correct_password(form.password.data):
            login_user(user)
            print(user.email, "LOGIN SUCCESSFUL :)")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/')
@app.route('/<game_url>')
def index(game_url='/'):
    users = Users.query.all()
    for u in users:
        print('========')
        print(u.email)
        print('========')
    game_id = game_url.strip('/')
    existing_game = Games.query.filter_by(game_id=game_id).all() if game_id else None

    if not existing_game:
        fen = app.config['STARTING_FEN_STRING']
        current_player = 'w'
        date_of_turn = None
    else:
        most_recent_round = existing_game[-1]
        date_of_turn = most_recent_round.date_of_turn
        fen = most_recent_round.fen_string
        current_player = session[game_id] if game_id in session.keys() else ''

    return render_template('index.html', 
                           fen=fen, 
                           current_player=current_player,
                           root_path = request.url_root,
                           game_url=game_url,
                           round_date=date_of_turn)                          
