from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask, redirect, url_for, session, request, jsonify, render_template, abort
from flask_oauthlib.client import OAuth

import logging

from connection import Connection

########################################################################
#                                                                      #
#                              CONSTANTS                               #
#                                                                      #
########################################################################

DEBUG = True
SECRET_KEY = 'secret key for development'
API_URL = 'http://localhost'
API_PORT = 9001
API_SITE = '/singin'
ADMIN_URL = 'http://localhost:8001'
CLIENT_URL = 'http://localhost:8001'

########################################################################
#                                                                      #
#                                 INIT                                 #
#                                                                      #
########################################################################

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
api = Connection(API_URL, API_PORT)

########################################################################
#                                                                      #
#                              FUNCTIONS                               #
#                                                                      #
########################################################################

def get_token(data):
    response = api.send(API_SITE, data)
    if(response):
        if(response.get('token')):
            return response['token']
    
    return None

########################################################################
#                                                                      #
#                              OAUTH DATA                              #
#                                                                      #
########################################################################
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='909295073138-t5qbc8gj430biacdij444ntn3vda24im.apps.googleusercontent.com',
    consumer_secret='40kNL1xZThaVkwvk4omRFnqD',
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

########################################################################
#                                                                      #
#                             ERROR HANDLER                            #
#                                                                      #
########################################################################

@app.errorhandler(400)
def pageBadRequest(error):
    return render_template('error.html', error='400 Bad Request'), 400

@app.errorhandler(401)
def pageUnauthorizedAccess(error):
    return render_template('error.html', error='401 Unauthorized Access'), 401

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('error.html', error='404 Not Found'), 404

@app.errorhandler(405)
def pageMethodNotAllowed(error):
    return render_template('error.html', error='405 Method Not Allowed'), 405

@app.errorhandler(500)
def pageInternalServerError(error):
    return render_template('error.html', error='500 Internal Server Error'), 500

########################################################################
#                                                                      #
#                                ROUTES                                #
#                                                                      #
########################################################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/google/login')
def login_with_google():
    #return google.authorize(ADMIN_URL)
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
@google.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    
    data = resp
    data['service'] = 'google'

    #Send data to API to receive token
    token = get_token(data)

    #Redirect to admin site with token
    if(token):
        url = ADMIN_URL + '/?token=' + token
        return redirect(url)
        #return redirect(url_for('index', token=token))
    else:
        abort(401)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')