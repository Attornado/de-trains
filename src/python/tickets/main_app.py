import json

from flask import Flask, render_template
from flask_cors import CORS
from web3 import Web3, HTTPProvider

# Instantiate the flask app
app = Flask(__name__)
CORS(app)
# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]

# Path to the compiled contract JSON file
compiled_contract_path = 'build/contracts/TicketStore.json'
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = "0x4337D217370eAd2C847E9Cc260d68f5023418dA5"

with open(compiled_contract_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)  # ignore this warning


@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/index_truffle')
def index_truffle():
    return render_template('./indexDiTruffle.html')


@app.route('/about')
def about():
    return render_template('./about.html')


@app.route('/buy_product')
def buy_product():
    return render_template('./buyProduct.html')


@app.route('/products')
def products():
    return render_template('./products.html')


@app.route('/refund')
def refund():
    return render_template('./refund.html')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)