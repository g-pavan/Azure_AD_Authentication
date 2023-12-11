from flask import Blueprint, Flask, redirect, url_for, session, request, render_template
import msal
import requests
from config import AzureADConfig

auth_bp = Blueprint('auth', __name__)

# Azure AD app configurations
scope = ["user.read"]

msal_app = msal.ConfidentialClientApplication(
    AzureADConfig.CLIENT_ID,
    authority=AzureADConfig.AUTHORITY,
    client_credential=AzureADConfig.CLIENT_SECRET
)

def get_user_profile(access_token):
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(AzureADConfig.GRAPH_API_ENDPOINT, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get('displayName', 'User')
    else:
        return 'User'

@auth_bp.route('/')
def home():
    username = 'User'
    if 'access_token' in session:
        access_token = session['access_token']
        username = get_user_profile(access_token)
    return render_template('home.html', logged_in='access_token' in session, username=username)

@auth_bp.route('/login')
def login():
    # Redirect to Azure AD for login
    auth_url = msal_app.get_authorization_request_url(
        scopes = scope,
        redirect_uri = AzureADConfig.REDIRECT_URI,
    )
    return redirect(auth_url)

@auth_bp.route('/get_token')
def get_token():
    if 'code' in request.args:
        # Exchange authorization code for access token
        token_response = msal_app.acquire_token_by_authorization_code(
            request.args['code'],
            scopes = scope,
            redirect_uri = AzureADConfig.REDIRECT_URI,
        )
        
        if 'access_token' in token_response:
            # Store the token in session (you may want to store it securely)
            session['access_token'] = token_response['access_token']
            return redirect(url_for('auth.home'))
        else:
            return 'Failed to retrieve access token'
    else:
        return 'Authorization code not found in the request'

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.home'))
