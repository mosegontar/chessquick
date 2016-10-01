
from flask import   render_template, url_for, request, jsonify, session

from chessquick import app
from chessquick.models import Games, make_new_game, add_turn_to_game


@app.route('/_get_fen')
def get_fen():
    fen = request.args.get('fen_move')
    game_url = request.args.get('game_id')
    current_player = request.args.get('current_player')
    game_id = game_url.strip('/')

    if not game_id: 
        game_id = make_new_game()

    session[game_id] = current_player
    add_turn_to_game(game_id, fen)

    return jsonify(game_url=game_id)

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
