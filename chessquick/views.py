import datetime

from flask import   render_template, url_for, request, jsonify, session

from chessquick import app
from chessquick.models import Games, add_turn_to_game


@app.route('/_get_fen')
def get_fen():

    fen = request.args.get('fen_move')
    game_url = request.args.get('game_id')
    current_player = request.args.get('current_player')
    _game_id = game_url.strip('/')
    time_of_turn = datetime.datetime.utcnow()

    game_id = add_turn_to_game(_game_id, fen, time_of_turn)
    session[game_id] = current_player

    return jsonify(game_url=game_id)

@app.route('/login')
@app.route('/login/<game_url>')
def login(game_url=None):    
    print('game-url is ', game_url)
    return render_template('login.html')

@app.route('/')
@app.route('/<game_url>')
def index(game_url='/'):

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
