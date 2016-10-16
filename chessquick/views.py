import datetime

from flask import   render_template, url_for, request, jsonify, session, \
    redirect, g, flash, make_response, abort
from flask_login import login_user, logout_user, current_user, login_required
from authomatic.adapters import WerkzeugAdapter

from chessquick import app, db, login_manager, authomatic
from chessquick.models import Rounds, Users, Matches
from chessquick.forms import UserPassEmailForm 
from .utils import security, emails

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user


def save_game(current_player, match):

    game_closed = (match.white_player and match.black_player)
    if not game_closed and (current_player != g.user.is_color(match) and not g.user.is_color(match)):
        g.user.save_match(current_player, match)

    return match

def unsave_game(current_player, match):

    if g.user.is_color(match) == 'w':
        match.white_player = None
    if g.user.is_color(match) == 'b':
        match.black_player = None

    match = unnotify(current_player, match)
    return match

def notify(current_player, match):
    print('notifying')
    if g.user.is_color(match) == 'w':
        match.white_notify = True
    if g.user.is_color(match) == 'b':
        match.black_notify = True
   
    return match

def unnotify(current_player, match):
    print(g.user.username)
    if g.user.is_color(match) == 'w':
        match.white_notify = False
    if g.user.is_color(match) == 'b':
        match.black_notify = False

    return match

@app.route('/_save')
@login_required
def toggle_options():

    current_player = request.args.get('current_player')
    action = request.args.get('action')
    match_url = request.args.get('match_url')

    match = Matches.get_match_by_url(match_url)

    if not match:
        flash('{} is not a valid match url'.format(match_url))
        return redirect(url_for('index'))    

    action_dict = {'save': save_game,
                   'unsave': unsave_game,
                   'notify': notify,
                   'unnotify': unnotify}

    match = action_dict[action](current_player, match)

    db.session.add(match)
    db.session.commit()

    white_player_name = match.white_player.username if match.white_player else 'Guest'
    black_player_name = match.black_player.username if match.black_player else 'Guest'

    if match.white_notify and g.user.is_color(match) == 'w':
        notify_on = True
    elif match.black_notify and g.user.is_color(match) == 'b':
        notify_on = True
    else:
        notify_on = False

    return jsonify(white_player_name=white_player_name, 
                   black_player_name=black_player_name,
                   notify_on=notify_on)

@login_required
@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/_get_fen')
def get_fen():

    fen = request.args.get('fen_move')
    game_url = request.args.get('match_url')
    current_player = request.args.get('current_player')
    _match_url = game_url.strip('/')
    time_of_turn = datetime.datetime.utcnow()

    match_url = Rounds.add_turn_to_game(_match_url, fen, time_of_turn)
    current_match = Matches.get_match_by_url(match_url)

    session[match_url] = current_player 

    return jsonify(game_url=match_url)

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = security.ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = Users.query.filter_by(email=email).first_or_404()

    user.email_confirmed = True

    db.session.add(user)
    db.session.commit()

    flash('Email confirmed :)')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserPassEmailForm()
    if form.validate_on_submit():

        email_exists = Users.query.filter(Users.email==form.email.data).first()

        if email_exists:
            flash('A user with the email has already registered')
            return render_template('signup.html', form=form)

        user = Users.add_user(username=form.username.data, 
                              email=form.email.data, 
                              password=form.password.data, 
                              login_type='local')

        token = security.ts.dumps(user.email, salt='email-confirm-key')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        emails.verify_email(user.email, confirm_url)

        login_user(user)
        return redirect(url_for('index'))

    if form.errors:
        for field, error in form.errors.items():
            flash(error[0])

    return render_template('signup.html', form=form)

@app.route('/profile/<confirm_email_request>', methods=['GET', 'POST'])
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile(confirm_email_request = False):

    form = UserPassEmailForm()
    del form.password
    del form.email
    if form.validate_on_submit():
        g.user.username = form.username.data
        db.session.add(g.user)
        db.session.commit()

    if form.errors:
        for field, error in form.errors.items():
            flash(error[0])
    print(confirm_email_request)

    if confirm_email_request:
        token = security.ts.dumps(g.user.email, salt='email-confirm-key')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        emails.verify_email(g.user.email, confirm_url)
   
    return render_template('profile.html', form=form)


def next_is_valid(endpoint):
    return endpoint in app.view_functions

@app.route('/_set_game_url')
def set_game_url():
    session['game_url'] = request.args.get('match_url')
    return jsonify(game_url=session['game_url'])


@app.route('/login/<provider_name>')
def login_with_oauth(provider_name):

    response = make_response()
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    if result:
        if result.user:
            result.user.update()

            user = Users.query.filter(Users.email == result.user.email).first() 
         
            if not user:
                
                if not result.user.username and result.user.email:
                    result.user.username = result.user.email.split('@')[0]

                user = Users.add_user(username=result.user.username, 
                                      auth_id=result.user.id,
                                      email=result.user.email,
                                      email_confirmed = True, 
                                      login_type='google')
            login_user(user)

        if 'game_url' not in session.keys():
            session['game_url'] = '/'

        return redirect(url_for('index', game_url=session['game_url']))
    return response

@app.route('/login')
@app.route('/login', methods=['GET', 'POST'])
def login():

    game_url = request.args.get('game_url')
    if not game_url: game_url = '/'

    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index', game_url=game_url))

    form = UserPassEmailForm()
    del form.username

    if form.validate_on_submit():

        user = Users.query.filter(Users.email == form.email.data).first() 
        if (user and user.is_correct_password(form.password.data)) and user.login_type == 'local':

            login_user(user)
            
            next_url = request.args.get('next')
            if next_url and not next_is_valid(next_url.strip('/')):
                next_url = None

            return redirect(next_url or url_for('index', game_url=game_url))

        else:
            flash('Incorrect password or username')
            return redirect(url_for('login', game_url=game_url))

    return render_template('login.html', form=form, game_url=game_url)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@app.route('/<game_url>')
def index(game_url='/'):

    users = Users.query.all()

    match_url = game_url.strip('/')
    existing_game = Matches.get_match_by_url(match_url) if match_url else None
    if not existing_game and len(match_url) > 1:
        flash("Couldn't locate game at the address {}".format(match_url))
        match_url = ''

    taken_players = {'w': 'Guest', 'b': 'Guest'}
    if not existing_game:
        fen = app.config['STARTING_FEN_STRING']
        current_player = 'w'
        date_of_turn = None
    else:
        taken_players['w'] = existing_game.white_player.username if existing_game.white_player else 'Guest'
        taken_players['b'] = existing_game.black_player.username if existing_game.black_player else 'Guest'
        if g.user == existing_game.white_player:
            session[match_url] = 'w'
        elif g.user == existing_game.black_player:
            session[match_url] = 'b'

        game_rounds = existing_game.rounds.all()
        most_recent_round = game_rounds[-1]
        date_of_turn = most_recent_round.date_of_turn
        fen = most_recent_round.fen_string

        current_player = session[match_url] if match_url in session.keys() else ''

    return render_template('index.html', 
                           fen=fen, 
                           current_player=current_player,
                           root_path = request.url_root,
                           game_url=match_url,
                           round_date=date_of_turn,
                           taken_players=taken_players,
                           current_match=existing_game)                          
