import json
import datetime

from bs4 import BeautifulSoup
from flask import   render_template, url_for, request, jsonify, session, \
    redirect, g, flash, make_response, abort
from flask_login import login_user, logout_user, current_user, login_required
from authomatic.adapters import WerkzeugAdapter

from chessquick import app, db, login_manager, authomatic
from chessquick.models import Rounds, Users, Matches, Posts
from chessquick.forms import UserPassEmailForm 
from chessquick.viewmodel import OptionToggler
from .utils import security, emails

@login_manager.user_loader
def load_user(id):
    """User loader"""
    return Users.query.get(int(id))

@app.before_request
def before_request():
    """Before request"""
    g.user = current_user

@app.route('/_save')
@login_required
def toggle_options():
    """Toggle save/notify options based on requested action"""

    # requested action parameters
    data = {k:v for k,v in request.args.items()}

    match = Matches.get_match_by_url(data['match_url'])

    if not match:
        flash('{} is not a valid match url'.format(match_url))
        return redirect(url_for('index')) 

    options = OptionToggler(g.user, data['current_player'], match)   

    action_dict = {'save': options.save_game,
                   'unsave': options.unsave_game,
                   'notify': options.notify,
                   'unnotify': options.unnotify}

    resp = action_dict[data['action']]()
    if not resp == 'need confirmation':
        options.commit_to_db()

    white_player_name = match.white_player.username if match.white_player else 'Guest'
    black_player_name = match.black_player.username if match.black_player else 'Guest'

    return jsonify(white_player_name=white_player_name, 
                   black_player_name=black_player_name,
                   resp=resp)

@login_required
@app.route('/history')
def history():
    """Game history view function"""
    return render_template('history.html')


@app.route('/_submit_move')
def submit_move():
    """Add new move to database. Notify opponent"""

    data = {k:v for k,v in request.args.items()}
   
    time_of_turn = datetime.datetime.utcnow()
    post = Posts.add_post(data['message'], g.user)
    match_url = Rounds.add_turn_to_game(data['match_url'].strip('/'), 
                                        data['fen_move'], 
                                        time_of_turn,
                                        post)

    current_match = Matches.get_match_by_url(match_url)
    emails.process_email(data['current_player'], 
                         current_match, 
                         request.url_root + match_url, 
                         g.user,
                         post)

    # Now add current player ('w' or 'b') to session to keep players the same
    session[match_url] = data['current_player']
    return jsonify(match_url=match_url)

@app.route('/confirm/<token>')
def confirm_email(token):
    """View function called on successful email verification"""

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
    """Sign up view function"""

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

        # Send new user email verification instrux with unique url
        token = security.ts.dumps(user.email, salt='email-confirm-key')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        emails.verify_email(user.email, confirm_url)

        login_user(user)

        flash('Please check your email for verification link.')

        return redirect(url_for('index'))

    if form.errors:
        for field, error in form.errors.items():
            flash(error[0])

    return render_template('signup.html', form=form)

@app.route('/profile/<confirm_email_request>', methods=['GET', 'POST'])
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile(confirm_email_request = False):
    """Profile view function"""

    # All changing of username, so remove other fields from form
    form = UserPassEmailForm()
    del form.password
    del form.email
    del form.remember_me

    if form.validate_on_submit():
        g.user.username = form.username.data
        db.session.add(g.user)
        db.session.commit()

    if form.errors:
        for field, error in form.errors.items():
            flash(error[0])

    if confirm_email_request:
        token = security.ts.dumps(g.user.email, salt='email-confirm-key')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        emails.verify_email(g.user.email, confirm_url)
   
    return render_template('profile.html', form=form)



@app.route('/_set_match_url')
def set_match_url():
    """
    Add current game url to session
    
    This allows successful redirect to in progress game after login w/ Google OAuth 2
    """
    session['match_url'] = request.args.get('match_url')
    return jsonify(match_url=session['match_url'])


@app.route('/login/<provider_name>')
def login_with_oauth(provider_name):
    """Login with Oauth (Google only right now) via authomatic"""

    response = make_response()
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    if result:
        if result.user:
            result.user.update()

            user = Users.query.filter(Users.email == result.user.email).first() 
         
            if not user:
                
                if not result.user.username and result.user.email:
                    # If result.user doesn't have username attribute, use email handle
                    result.user.username = result.user.email.split('@')[0]

                user = Users.add_user(username=result.user.username, 
                                      auth_id=result.user.id,
                                      email=result.user.email,
                                      email_confirmed = True, 
                                      login_type='google')
            login_user(user)

        if 'match_url' not in session.keys():
            session['match_url'] = '/'

        return redirect(url_for('index', match_url=session['match_url']))
    return response

@app.route('/login')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login view function"""

    # Get match_url from request to prepare to redirect back to in-progress game"""
    match_url = request.args.get('match_url')
    if not match_url: 
        match_url = '/'

    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index', match_url=match_url))

    form = UserPassEmailForm()
    del form.username # Don't need username to login in; just email/pass

    if form.validate_on_submit():

        user = Users.query.filter(Users.email == form.email.data).first() 
        if (user and user.is_correct_password(form.password.data)) and user.login_type == 'local':

            login_user(user, remember = form.remember_me.data)
            
            next_url = request.args.get('next')
            if next_url and not security.next_is_valid(next_url.strip('/')):
                next_url = None

            return redirect(next_url or url_for('index', match_url=match_url))

        else:
            flash('Incorrect password or username')
            return redirect(url_for('login', match_url=match_url))

    return render_template('login.html', form=form, match_url=match_url)


@app.route('/logout')
@login_required
def logout():
    """Logout"""

    logout_user()
    return redirect(url_for('index'))

def assign_current_player(player, match_url):

    if not player:
        if match_url in session.keys():
            player = session[match_url]
        else:
            player = ''
    return player

@app.route('/')
@app.route('/<match_url>')
def index(match_url='/'):
    """Main game view function"""

    match_url = match_url.strip('/')
    existing_game = Matches.get_match_by_url(match_url) if match_url else None
    if not existing_game and len(match_url) > 1:
        flash('Unable to locate game the game "{}"'.format(match_url))
        return redirect(url_for('index'))

    # Returns either values for existing game state or initialization values
    state = Matches.get_state(existing_game)

    # We assume that current user has not played this particular match before
    # and update state['current_player'] if assumption is wrong
    player = False
    if g.user.is_authenticated:
        player, state['notify'] = g.user.get_color_and_notify(existing_game)
    
    state['current_player'] = assign_current_player(player, match_url)

    return render_template('index.html', root_path=request.url_root, **state)
