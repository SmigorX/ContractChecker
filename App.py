import PySimpleGUIWx as sg
import json, webbrowser, os, threading
import ContractFetcher


def run_contract_fetcher():
    ContractFetcher.app.run()


def fetch_contracts():
    webbrowser.open('http://localhost:5000/')
    contract_fetcher_thread = threading.Thread(target=run_contract_fetcher)
    contract_fetcher_thread.start()


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
    stock_table = []
    for key, value in stock_numbers.items():
        stock_table.append([key, value])
    return stock_table


stock_table = create_contract_table()

sg.theme('Dark')


if check_for_contracts_json() == False:
    layout = [sg.Text('No contracts imported')]
else:
    layout = [
        [sg.Button('Import Contracts', key='-BUTTON-'),
         sg.Button('Refresh', key='-REFRESH-')],
        [sg.Multiline('\n'.join(str(x) for x in stock_table), size=(100, 20), font=('Helvetica', 14), key='-MULTILINE-')],
        ]


window = sg.Window('Stock Checker', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    elif event == '-BUTTON-':
        fetch_contracts()
    elif event == '-REFRESH-':
        stock_table = create_contract_table()
        window['-MULTILINE-'].update('\n'.join(str(x) for x in stock_table))
    window_size = window.size
    window['-MULTILINE-'].size = (int(window_size[0]*0.9), int(window_size[1]*0.9))

window.close()
