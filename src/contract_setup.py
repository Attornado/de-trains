from web3 import Web3, HTTPProvider
import json


# Truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'

# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))

# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
set_account_flag = False

# Load contract address
with open("src/configurations.json") as file:
    deployed_contract_address = json.load(file)['contract_address']  # load contract address

# Path to the compiled contract JSON file
compiled_contract_path = 'build/contracts/TicketStore.json'

# Enable unaudited features
web3.eth.account.enable_unaudited_hdwallet_features()

# Load smart contract
with open(compiled_contract_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)  # ignore this warning
