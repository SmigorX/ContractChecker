import base64
import json
import os
import requests
import threading
import webbrowser

from urllib.parse import urlencode

import PySimpleGUIWx as sg

import ContractFetcher


def check_for_updates():

    username = "SmigorX"
    repository_name = "test"
    file_path = "version.json"

    url = f"https://api.github.com/repos/{username}/{repository_name}/contents/{file_path}"

    response = requests.get(url)

    if response.status_code == 200:
        newest_version = response.json()
        newest_version = newest_version['content']
        newest_version = base64.b64decode(newest_version)
        newest_version = str(newest_version, 'utf-8')
    else:
        return False

    current_version = open('version.json', 'r').read()

    if newest_version != current_version:
        return True
    else:
        return False


def browser_opener():
    url_builder = ContractFetcher.UrlBuilder()
    auth_url = 'https://%s?%s' % (url_builder.base_url, urlencode(url_builder.args))
    return webbrowser.open(auth_url)


def fetch_contracts():
    flask_thread = threading.Thread(target=ContractFetcher.app.run)
    ContractFetcher.app.thread = flask_thread
    flask_thread.start()
    browser_opener()


def check_for_contracts_json():
    if os.path.isfile("contracts.json"):
        if os.stat("contracts.json").st_size == 0:
            fetch_contracts()
    else:
        json_create = []
        json.dump(json_create, fp=open("contracts.json", "w"))
        fetch_contracts()


check_for_contracts_json()


def open_contracts_json():
    contracts_string = open("contracts.json", "r").read()
    contracts_list = json.loads(contracts_string)
    return contracts_list


def outstanding_contract_filter(contracts_list):
    outstanding_contracts = []
    for i in range(len(contracts_list)):
        if contracts_list[i]['type'] == "item_exchange" and contracts_list[i]['status'] == "outstanding":
            outstanding_contracts.append(contracts_list[i])
    return outstanding_contracts


def merge_contracts():

    contract_list = open_contracts_json()
    outstanding_contracts = outstanding_contract_filter(contract_list)

    contract_dictionary = {}
    for i in range(len(outstanding_contracts)):
        if not outstanding_contracts[i]['title'] == '':
            if outstanding_contracts[i]['title'] in contract_dictionary:
                contract_dictionary[outstanding_contracts[i]['title']] += 1
            else:
                contract_dictionary.update({outstanding_contracts[i]['title']: 1})
    return contract_dictionary


def create_contract_table():
    stock_numbers = merge_contracts()
    current_stock_table = []
    for key, value in stock_numbers.items():
        current_stock_table.append([key, value])
    return current_stock_table


def get_character_name():
    name = open('name.txt', 'r').read()
    name = str(name)
    name = name[1:-1]
    return name


def check_for_character_name_file():
    if os.path.isfile("name.txt"):
        if os.stat("name.txt").st_size == 0:
            with open("name.txt", "w") as f:
                f.write(" Unknown ")
    else:
        with open("name.txt", "w") as f:
            f.write(" Unknown ")


check_for_character_name_file()

stock_table = create_contract_table()

sg.theme('Dark')


class Layouts:
    layout1 = [
        [sg.Button('Import Contracts', key='-BUTTON-'),
         sg.Button('Refresh', key='-REFRESH-')],
        [sg.Text(f'Character: {get_character_name()}', font=('Helvetica', 14), key='-CHARACTER-')],
        [sg.Multiline('\n'.join(str(x) for x in stock_table), size=(120, 30), font=('Helvetica', 14), key='-MULTILINE-',)],
              ]

    layout2 = [
        [sg.Button('Import Contracts', key='-BUTTON-'),
         sg.Button('Refresh', key='-REFRESH-'),
         sg.Text('New Update Available', font=('Helvetica', 14), key='-UPDATE-')],
        [sg.Text(f'Character: {get_character_name()}', font=('Helvetica', 14), key='-CHARACTER-')],
        [sg.Multiline('\n'.join(str(x) for x in stock_table), size=(120, 30), font=('Helvetica', 14), key='-MULTILINE-',)],
              ]


def update_checker():
    if check_for_updates() is True:
        layout = Layouts.layout2
    else:
        layout = Layouts.layout1    
    return layout


window = sg.Window('Stock Checker', update_checker())


while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    elif event == '-BUTTON-':
        fetch_contracts()
    elif event == '-REFRESH-':
        stock_table = create_contract_table()
        window['-MULTILINE-'].update('\n'.join(str(x) for x in stock_table))
        window['-CHARACTER-'].update(f'Character: {get_character_name()}')

window.close()
