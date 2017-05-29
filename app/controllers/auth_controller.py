import json
import random
import string

import httplib2
import requests
from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    url_for
)
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

auth_ctrl = Blueprint('auth', __name__, static_folder='static', template_folder='templates')


# Create a state token to prevent request
# Store it in the login_session for later validation
@auth_ctrl.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('_main.html', view='login', STATE=state)


@auth_ctrl.route('/gconnect', methods=['POST'])
def gconnect():
    # Check if request was sent from the right user
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter', 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match give user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content_Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    store_gplus_id = login_session.get('gplus_id')
    if (stored_credentials is not None) and (gplus_id == store_gplus_id):
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<div> Welcome, <span class="title-bold">' + login_session['username'] + '</span></div>'
    output += '<img src= "' + login_session['picture'] \
              + '" alt="..." ' \
                'style="width: 150px; height:150px; border-radius: 75px; border: 3px solid #000; margin: 15px;">'
    output += '<div>' + login_session['email'] + '</div>'
    return output


@auth_ctrl.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET to disconnect current token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # Reset the user's session.
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['credentials']
    del login_session['gplus_id']
    if result['status'] == '200':
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('category.get_all_categories'))
    else:
        response = make_response(json.dumps("Fail to disconnect."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
