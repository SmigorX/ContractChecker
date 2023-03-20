from flask import Flask, request, redirect
import requests
import secrets
from urllib.parse import urlencode
import json


app = Flask(__name__)


class UrlBuilder:
    def __init__(self, ):
        self.code_challenge = secrets.token_urlsafe(100)[:128]
        self.base_url = "login.eveonline.com/oauth/authorize"
        self.client_id = 'd40c1a23ee8a433ab3e161b46c105e9c'
        self.callback_url = 'http://localhost:5000/callback'
        self.scopes = 'esi-contracts.read_corporation_contracts.v1 esi-contracts.read_character_contracts.v1'

        self.args = {
            'code_challenge': self.code_challenge,
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': self.scopes,
        }


url_builder = UrlBuilder()


@app.route('/')
def hello_world():
    auth_url = 'https://%s?%s' % (url_builder.base_url, urlencode(url_builder.args))
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
        'code_verifier': f"{url_builder.code_challenge}",
        'client_id': f"{url_builder.client_id}",
    }

    global token
    request_url = "https://login.eveonline.com/oauth/token"
    response = requests.post(request_url, headers=headers, data=body)
    token = response.json()['access_token']

    if response.content:
        return token and redirect("http://localhost:5000/get_character_id", code=302)
    else:
        return {'message': 'Error, could not get the access token ' + str(token.status_code)}


@app.route('/get_character_id')
def get_character_id():
    headers = {
        'Authorization': f"Bearer {token}",
    }

    response = requests.get('https://esi.evetech.net/verify', headers=headers)

    global character_id
    if response.status_code == 200:
        character_id = str(response.json()['CharacterID'])
        return character_id and redirect("http://localhost:5000/get_corporation_id", code=302)
    else:
        return {'message': 'Error while getting the character ID ' + str(response.status_code)}

@app.route('/get_corporation_id')
def get_corp_id():
    headers = {
        'accept': 'application/json',
        'Cache-Control': 'no-cache',
    }

    params = {
        'datasource': 'tranquility',
    }

    response = requests.get(f'https://esi.evetech.net/latest/characters/{character_id}/', params=params, headers=headers)

    global corporation_id

    corporation_id = response.json()
    corporation_id = str(corporation_id["corporation_id"])

    if response.status_code == 200:
        return corporation_id and redirect("http://localhost:5000/contracts", code=302)
    else:
        return {'message': 'Error while getting the corp ID ' + str(response.status_code)}


@app.route('/contracts')
def contract():
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Cache-Control": "no-cache",
    }

    params = {
        "datasource": "tranquility"
    }

    returned_contracts = requests.get(f"https://esi.evetech.net/latest/corporations/{corporation_id}/contracts/",
                                      headers=headers,
                                      params=params)

    returned_contracts = returned_contracts.json()

    with open("contracts.json", "w") as f:
        json.dump(returned_contracts, f)

    return returned_contracts
