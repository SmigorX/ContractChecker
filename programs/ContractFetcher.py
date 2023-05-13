import threading

import requests
import secrets
import webbrowser

from flask import Flask, request

from urllib.parse import urlencode


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


class APICalls:
    def __init__(self):
        self.url_builder = UrlBuilder()
        self.eve_auth_code = None
        self.auth_url = 'https://%s?%s' % (self.url_builder.base_url, urlencode(self.url_builder.args))
        self.character_id = None
        self.corporation_id = None
        self.token = None
        self.stock = None
    def exchange(self):  # Exchanges OAuth code for access token
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        body = {
            'grant_type': "authorization_code",
            'code': f"{self.eve_auth_code}",
            'code_verifier': f"{self.url_builder.code_challenge}",
            'client_id': f"{self.url_builder.client_id}",
        }

        request_url = "https://login.eveonline.com/oauth/token"
        response = requests.post(request_url, headers=headers, data=body)
        self.token = response.json()['access_token']

        if response.content:
            return self.token and self.get_character_id()
        else:
            return {'message': 'Error, could not get the access token ' + str(self.token.status_code)}

    def get_character_id(self):
        headers = {
            'Authorization': f"Bearer {self.token}",
        }

        response = requests.get('https://esi.evetech.net/verify', headers=headers)
        if response.status_code == 200:
            self.character_id = str(response.json()['CharacterID'])

            return self.character_id and self.get_character_name()
        else:
            return {'message': 'Error while getting the character ID ' + str(response.status_code)}

    def get_character_name(self):
        url = f'https://esi.evetech.net/latest/characters/{self.character_id}/?datasource=tranquility'

        response = requests.get(url)

        character_name = response.json()
        character_name = str(character_name["name"])

        with open("./name.txt", "w") as f:
            f.truncate()
            f.write(character_name)

        return self.get_corp_id()

    def get_corp_id(self):
        headers = {
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
        }

        params = {
            'datasource': 'tranquility',
        }

        response = requests.get(f'https://esi.evetech.net/latest/characters/{self.character_id}/',
                                params=params, headers=headers)

        self.corporation_id = response.json()
        self.corporation_id = str(self.corporation_id["corporation_id"])

        if response.status_code == 200:
            return self.corporation_id and self.contract()
        else:
            return {'message': 'Error while getting the corp ID ' + str(response.status_code)}

    def contract(self):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Cache-Control": "no-cache",
        }

        params = {
            "datasource": "tranquility"
        }

        self.returned_contracts = requests.get(
            f"https://esi.evetech.net/latest/corporations/{self.corporation_id}/contracts/",
            headers=headers,
            params=params)


        self.stock = DataHandling.outstanding_contract_filter(self.returned_contracts.json())
        self.stock = str(DataHandling.merge_contracts(self.stock))[1:-1]

        with open("./stock.txt", "w") as stock_file:
            self.stock = self.stock.split(", '")
            self.stock = [i.replace("'", "") for i in self.stock]
            stock_file.truncate()
            for i in range(len(self.stock)):
                stock_file.write(str(self.stock[i])+"\n")

        return "You can now close this tab"


class DataHandling:
    def outstanding_contract_filter(returned_contracts):
        contracts_list = returned_contracts

        outstanding_contracts = []
        for i in range(len(contracts_list)):
            if contracts_list[i]['type'] == "item_exchange" and contracts_list[i]['status'] == "outstanding":
                outstanding_contracts.append(contracts_list[i])

        return outstanding_contracts

    def merge_contracts(outstanding_contracts):

        contract_dictionary = {}
        for i in range(len(outstanding_contracts)):
            if not outstanding_contracts[i]['title'] == '':
                if outstanding_contracts[i]['title'] in contract_dictionary:
                    contract_dictionary[outstanding_contracts[i]['title']] += 1
                else:
                    contract_dictionary.update({outstanding_contracts[i]['title']: 1})

        return contract_dictionary


def browser_opener():
    url_builder = UrlBuilder()
    auth_url = 'https://%s?%s' % (url_builder.base_url, urlencode(url_builder.args))
    return webbrowser.open(auth_url)


class App(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.caller = APICalls()
        self.thread: threading.Thread = None
        browser_opener()


app = App(__name__)


@app.route('/callback')
def callback():
    app.caller.eve_auth_code = request.args.get('code')
    app.caller.exchange()
    return "You can now close your browser"


if __name__ == "__main__":
    app.run()
