import json
from web3 import Web3
import requests


def get_creds():
    """
        read in the login details from secret file
    """
    file_data = open('pass.txt', 'r+').strip()
    creds = json.loads(file_data)
    API_KEY = creds['API_KEY']
    URL = creds['URL']
    return data_clean


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
        return data.json()
    else:
        print(f'Error finding the smart contract, exiting with code {data.status_code}')
        sys.exit()


def create_transaction(IPC_FILE, contract_add, abi, quantity, price):
    """
    create the transaction to send to the blockchain
    """
    #TODO: Do we need to extract and call only the relevant mint function?
    # How can this logic be added in a generic way?
    # contract_obj.functions.function_name().transact()
    # NOTE: Use .transact() for write functions and .call() for read functions
    w3 = Web3(Web3.IPCProvider(IPC_FILE))
    #NOTE: this may need to be updated everytime
    # the local eth node is restarted
    address = w3.toChecksumAddress(contract_add)
    contract = w3.eth.contract(address=address, abi=abi)
    trans_id = contract.functions.mint(price * quantity, quantity).transact()
    return trans_id


def estimate_gas():
    """
    estimate the optimal gas fee in order to increase chance of being accepted
    in the next block
    """
    #TODO: Can we check for arb opportunities between marketplace and the
    # initial mint cost?
    pass


def send_transaction(transaction):
    """
    send the transaction to the mem pool ?? sign first with private key?
    """
    #TODO: package the transaction and sign with private key. 
    # then send the transaction to th eth mem pool
    pass


def main():
    """
    Main function that takes in the ether address of the smart contract.
    1) Use input ether address to programatically extract the abi from
    etherscan API
    2) Create a transaction to send to the blockchain that will purchase x
    amount of NFT - dynamically adjust gas based on the current gas estimates
    3) Send the transaction to the ethereum blockchain -> using local get node
    """
    API_KEY, URL = get_creds()
    contract_add = input('Please enter the smart contract id: ')
    abi = extract_abi(contract_add, API_KEY)
    print(f'ABI for contract {contract_add} is {abi}')
    #TODO: Programmatically set the quantity and price
    create_transaction(IPC_FILE, contract_add, abi, quantity, price)


if __name__ == "__main__":
    main()
