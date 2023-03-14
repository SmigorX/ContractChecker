from flask import Flask, request, redirect
#import requests

app = Flask(__name__)

callback_url = 'http://localhost:5000/callback'
client_id = '2b063ddd038342d781a9673f72eabce3'
AUTH_URL = f'https://login.eveonline.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={callback_url}&scope=esi-contracts.read_corporation_contracts.v1 esi-contracts.read_character_contracts.v1'


@app.route('/')
def hello_world():
    return '<a href="' + AUTH_URL + '">Click here to authorize the application</a>'

@app.route('/callback') #Get's one time use OAuth code
def callback():
    global auth_code
    auth_code = request.args.get('code')
    return auth_code and redirect("http://localhost:5000/exchange", code=302)
#Tutaj jeszcze działa, ale nie wiem jak dalej

@app.route('/exchange') #Exchanges OAuth code for access token
def exchange_token():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic MmIwNjNkZGQwMzgzNDJkNzgxYTk2NzNmNzJlYWJjZTM6cExyZEVHMkg3dDdZc00yMHdjNEFqOWI5cmtJakFUSFl1ZlpCSVE3cgo=',
    }

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        #'redirect_uri': 'http://localhost:5000/test',
        'scope': 'esi-contracts.read_corporation_contracts.v1, esi-contracts.read_character_contracts.v1',
    }

    response = request.post('https://login.eveonline.com/oauth/token', headers=headers, data=data)

    #if response.status_code == requests.codes.ok:
    #    global access_token
    #    access_token = response.json()['access_token']
    #    return access_token
    #else:
    #    return "error"
    return response

@app.route('/test')
def test():
    return "it works"

if __name__ == '__main__':
    app.run(debug=True)

