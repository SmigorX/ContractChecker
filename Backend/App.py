import ContractFetcher
import webbrowser
import requests
import base64
import json
import os
import threading

from urllib.parse import urlencode


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


def check_for_contracts_json():
    if os.path.isfile("contracts.json"):
        if os.stat("contracts.json").st_size == 0:
            return False
    else:
        return False


def browser_opener():
    url_builder = ContractFetcher.UrlBuilder()
    auth_url = 'https://%s?%s' % (url_builder.base_url, urlencode(url_builder.args))
    return webbrowser.open(auth_url)


def contract_fetch():
        flask_thread = threading.Thread(target=ContractFetcher.app.run)
        ContractFetcher.app.thread = flask_thread
        flask_thread.start()
        browser_opener()
        while True:
            is_json = check_for_contracts_json()
            if is_json is not False:
                break
        return get_outstanding_and_merge_contracts()


def open_contracts_json():
    contracts_string = open("contracts.json", "r").read()
    contracts_list = json.loads(contracts_string)
    return contracts_list


def outstanding_contract_filter():
    contracts_list = open_contracts_json()

    outstanding_contracts = []
    for i in range(len(contracts_list)):
        if contracts_list[i]['type'] == "item_exchange" and contracts_list[i]['status'] == "outstanding":
            outstanding_contracts.append(contracts_list[i])
    return outstanding_contracts


def get_outstanding_and_merge_contracts():
    outstanding_contracts = outstanding_contract_filter()

    contract_dictionary = {}
    for i in range(len(outstanding_contracts)):
        if not outstanding_contracts[i]['title'] == '':
            if outstanding_contracts[i]['title'] in contract_dictionary:
                contract_dictionary[outstanding_contracts[i]['title']] += 1
            else:
                contract_dictionary.update({outstanding_contracts[i]['title']: 1})
    with open("stock.json", "w") as f:
        json.dump(contract_dictionary, f)


def main():
    check_for_updates()
    contract_fetch()

main()




