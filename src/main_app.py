import datetime
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from web3 import Web3, HTTPProvider, exceptions

from tickets.tickets_api import retrieve_and_check_ticket_by_id, buy_ticket, generate_code_url, generate_ticket_uri, \
    refund_ticket, use_ticket, IPFS_PORT, IPFS_ADDRESS
from tickets.ticket import Ticket
from admin.admin_api import register_admin, show_admin_page, register_ticket_usage_setter, withdraw


# Instantiate the flask app
app = Flask(__name__)
CORS(app)

# Truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'

# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))

# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
set_account_flag = False

# Path to the compiled contract JSON file
compiled_contract_path = '../build/contracts/TicketStore.json'

# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = "0xF00723b667FeAf4b6a85c208f05e3c771FE3d15D"

# Enable unaudited features
web3.eth.account.enable_unaudited_hdwallet_features()

# Load smart contract
with open(compiled_contract_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)  # ignore this warning


def check_account_exist(address: str) -> bool:
    for account in web3.eth.accounts:
        if address == account:
            return True
    return False


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('./index.html')


@app.route('/index_truffle')
@app.route('/indexDiTruffle.html')
def index_truffle():
    return render_template('./indexDiTruffle.html')


@app.route('/about')
@app.route('/about.html')
def about():
    return render_template('./about.html')


@app.route('/buy_product')
@app.route('/buyProduct.html')
def buy_product():
    return render_template('./buyProduct.html')


@app.route('/products')
@app.route('/products.html')
def products():
    return render_template('./products.html')


@app.route('/refund')
@app.route('/refund.html')
def refund():
    return render_template('./refund.html')


@app.route('/login')
def login_page():
    return render_template('./login.html')


@app.route("/login_private_key", methods=["POST"])
def login_private_key():
    params = request.form
    sk = "0x" + params['private_key']
    account = web3.eth.account.from_key(sk)
    if not check_account_exist(account.address):
        return jsonify({"message": "Account login failed!"}), 400

    web3.eth.defaultAccount = account.address
    global set_account_flag
    set_account_flag = True
    return render_template('./index.html')


@app.route("/login_mnemonic", methods=["POST"])
def login_mnemonic():
    params = request.form
    mnemonic = params['mnemonic']
    account = web3.eth.account.from_mnemonic(mnemonic)
    if not check_account_exist(account.address):
        return jsonify({"message": "Account login failed!"}), 400

    web3.eth.defaultAccount = account.address
    global set_account_flag
    set_account_flag = True
    return jsonify({"message": "Login successful!"}), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)