from flask import Flask, request, redirect
import requests
import secrets
from urllib.parse import urlencode

app = Flask(__name__)


code_challenge = secrets.token_urlsafe(100)[:128]
base_url = "login.eveonline.org/oauth/authorize"
client_id = 'd40c1a23ee8a433ab3e161b46c105e9c'
callback_url = 'http://localhost:5000/callback'
scopes = 'esi-contracts.read_corporation_contracts.v1 esi-contracts.read_character_contracts.v1'


args = {
  'code_challenge': code_challenge,
  'response_type': 'code',
  'client_id': client_id,
  'redirect_uri': callback_url,
  'scope': scopes,
  }


@app.route('/')
def hello_world():
    auth_url = 'https://%s?%s' % (base_url, urlencode(args))
    return '<a href="' + auth_url + '">Click here to authorize the application</a>'


@app.route('/callback')  # Gets one time use OAuth code
def callback():
    global auth_code
    auth_code = request.args.get('code')
    return auth_code and redirect("http://localhost:5000/exchange", code=302)


@app.route('/exchange')  # Exchanges OAuth code for access token
def exchange():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    body = {
        'grant_type': "authorization_code",
        'code': f"{auth_code}",
        'code_verifier': f"{code_challenge}",
        'client_id': f"{client_id}",
    }

    request_url = "https://login.eveonline.com/oauth/token"
    response = requests.post(request_url, headers=headers, data=body)

    if response.content:
        return response.json()
    else:
        return {'message': 'Error'}


@app.route('/test')
def test():
    return "it works"


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
