import json
from web3 import Web3
import requests


def get_creds():
    """
        read in the login details from secret file
    """
    with open('pass.txt', 'r') as f:
        file_data = f.readlines()
    creds = json.loads(file_data[0].strip())
    API_KEY = creds['API_KEY']
    IPC_FILE = creds['URL']
    PUB_KEY = creds['PUB_KEY']
    PRIVATE_KEY = creds['PRIVATE_KEY']
    return API_KEY, IPC_FILE, PUB_KEY, PRIVATE_KEY


def extract_abi(contract_add: str, API_KEY: str) -> json:
    """
    connect to the the etherscan api and extract the ABI details for the smart
    contract
    NOTE: the abi is a json object that returns all smart contract functions
    """
    url = 'https://api.etherscan.io/api'
    payload = {'module': 'contract', 'action': 'getabi', 'address':
               contract_add, 'apikey': API_KEY}
    data = requests.get(url, payload)
    if data.status_code == 200:
        return json.loads(data.json()['result'])
    else:
        print(f'Error finding the smart contract, exiting with code {data.status_code}')
        sys.exit()


def create_transaction(IPC_FILE, PUB_KEY, contract_add, abi, quantity, price):
    """
    create the transaction to send to the blockchain
    """
    w3 = Web3(Web3.IPCProvider(IPC_FILE))
    price_wei = w3.toWei(price, 'ether')
    address = w3.toChecksumAddress(contract_add)
    contract = w3.eth.contract(address=address, abi=abi)
    nonce = w3.eth.getTransactionCount(PUB_KEY)
    account = w3.toChecksumAddress(PUB_KEY)
    gas_wei = estimate_gas(w3)
    gas_wei = 61444436997
    transact_payload = {'nonce': nonce,
                        'from': account
                        'value': price_wei * quantity,
                        'gasPrice': gas_wei}
    func_call = contract.functions.mint(quantity)
    txn = func_call.buildTransaction(transact_payload)
    print(w3.eth.estimateGas(txn))
    input()
    return txn


def sign_txn(transaction, PRIVATE_KEY):
    """
    sign the transaction with the PRIVATE_KEY
    """
    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    return signed_txn


def estimate_gas(w3):
    """
    estimate the optimal gas fee in order to increase chance of being accepted
    in the next block

    uses built in API call to return the max fee for a prority transaction
    """
    gas_wei = w3.eth.max_priority_fee
    return gas_wei


def send_transaction(signed_transaction):
    """
    send the transaction to the mem pool ?? sign first with private key?
    """
    #TODO: package the transaction and sign with private key. 
    # then send the transaction to th eth mem pool
    result = w3.eth.send_raw_transaction(signed_transaction)
    return result


def main():
    """
    Main function that takes in the ether address of the smart contract.
    1) Use input ether address to programatically extract the abi from
    etherscan API
    2) Create a transaction to send to the blockchain that will purchase x
    amount of NFT - dynamically adjust gas based on the current gas estimates
    3) Send the transaction to the ethereum blockchain -> using local get node
    """
    API_KEY, IPC_FILE, PUB_KEY, PRIVATE_KEY = get_creds()
    contract_add = input('Please enter the smart contract id: ')
    price = int(input('Please enter the price per nft: '))
    quantity = int(input('Please enter the total number of NFTs to mint: '))
    abi = extract_abi(contract_add, API_KEY)
    #TODO: Programmatically set the quantity and price
    txn = create_transaction(IPC_FILE, PUB_KEY, contract_add, abi, quantity, price)
    signed_txn = sign_txn(txn)
    result = send_transaction(signed_txn)
    print(result)


if __name__ == "__main__":
    main()
