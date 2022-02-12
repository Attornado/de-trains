import datetime
import json

import ipfsApi
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from web3 import Web3, HTTPProvider, exceptions

from tickets.ticket import Ticket

IPFS_ADDRESS = "127.0.0.1"
IPFS_PORT = 5001

# Instantiate the flask app
app = Flask(__name__)
CORS(app)
# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
set_account_flag = False

# Path to the compiled contract JSON file
compiled_contract_path = '../build/contracts/TicketStore.json'
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = "0xFad328e049a0a6492A1e0b9204F36aD3C3e63970"
# Enable unaudited features
web3.eth.account.enable_unaudited_hdwallet_features()

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


@app.route("/admin", methods=["GET"])
def show_admin_page():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        return render_template('./admin.html')
    else:
        return jsonify({"message": "You are not an admin!"}), 400


@app.route("/admin/register_admin", methods=["GET"])
def register_admin():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    address = request.args.get('address')
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization

        try:
            contract.functions.addAdminRole(to=address).call()
            contract.functions.addAdminRole(to=address).transact()  # Notarization
        except exceptions.SolidityError as e:
            return jsonify({"message": "Admin role assignation failed: " + str(e)}), 400

        return jsonify({"message": "Admin role added successfully to address: " + str(address)}), 200
    else:
        return jsonify({"message": "Admin role assignation failed: you are not an admin!"}), 400


@app.route("/admin/register_ticket_usage_setter", methods=["GET"])
def register_ticket_usage_setter():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    address = request.args.get('address')
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization

        try:
            contract.functions.addUsageSetterRole(to=address).call()
            contract.functions.addUsageSetterRole(to=address).transact()  # Notarization
        except exceptions.SolidityError as e:
            return jsonify({"message": "Usage setter role assignation failed: " + str(e)}), 400

        return jsonify({"message": "Usage setter role added successfully to address: " + str(address)}), 200
    else:
        return jsonify({"message": "Usage setter role assignation failed: you are not an admin!"}), 400

'''
@app.route("/admin/remove_admin", methods=["GET"])
def remove_admin():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    address = request.args.get('address')
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization

        try:
            contract.functions.removeAdminRole(to=address).call()
            contract.functions.removeAdminRole(to=address).transact()  # Notarization
        except exceptions.SolidityError as e:
            return jsonify({"message": "Admin role assignation failed: " + str(e)}), 400

        return jsonify({"message": "Admin role remove successfully to address: " + str(address)}), 200
    else:
        return jsonify({"message": "Admin role renounce failed: you are not an admin!"}), 400


@app.route("/admin/remove_ticket_usage_setter", methods=["GET"])
def remove_ticket_usage_setter():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    address = request.args.get('address')
    if contract.functions.isUsageSetter(account=web3.eth.defaultAccount).call():
        contract.functions.isUsageSetter(account=web3.eth.defaultAccount).transact()  # Notarization

        try:
            contract.functions.removeUsageSetterRole(to=address).call()
            contract.functions.removeUsageSetterRole(to=address).transact()  # Notarization
        except exceptions.SolidityError as e:
            return jsonify({"message": "Usage setter role assignation failed: " + str(e)}), 400

        return jsonify({"message": "Usage setter role removed successfully to address: " + str(address)}), 200
    else:
        return jsonify({
            "message": "Usage setter role renounce failed: you are not an admin nor a usage setter!"
        }), 400
'''


@app.route("/admin/withdraw", methods=["GET"])
def withdraw():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    address = request.args.get('address')
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization

        try:
            contract.functions.transfer(addressToTransfer=address).call()
            contract.functions.transfer(addressToTransfer=address).transact()  # Notarization
        except exceptions.SolidityError as e:
            return jsonify({
                "message": "Founds transfer to address" + str(address) + " withdrawal failed: " + str(e)
            }), 400

        return jsonify({"message": "Founds successfully transfered to address: " + str(address) + "!"}), 200
    else:
        return jsonify({
            "message": "Founds transfer to address" + str(address) + " withdrawal failed: you are not an admin!"
        }), 400


def generate_ticket_uri(ticket_json):
    tk_id = json.loads(ticket_json)['id']
    filename = 'ticket' + str(tk_id) + '.json'
    with open(filename, 'w') as outfile:
        outfile.write(ticket_json)
    api = ipfsApi.Client(IPFS_ADDRESS, IPFS_PORT)
    res = api.add(filename)
    return 'https://ipfs.io/ipfs/' + res['Hash']


def generate_code_url(tk_id: int, start_station: str, end_station: str, station_num: int, date: str) -> str:
    filename = "static/assets/qr/qrcode.txt"
    api = ipfsApi.Client(IPFS_ADDRESS, IPFS_PORT)
    res = api.add(filename)[0] # will create an ipfs file for all directories
    return 'https://ipfs.io/ipfs/' + res['Hash'] # localhost:8086 o


@app.route("/buy_ticket", methods=['GET'])
def buy_ticket():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    start_station = request.args.get('start_station')
    end_station = request.args.get('end_station')
    station_num: int = int(request.args.get('station_num'))
    date = request.args.get("date")
    timestamp = int(datetime.datetime.timestamp(datetime.datetime.strptime(date, "%d/%m/%Y")))

    # generate QR code for ticket
    estimate_tk_id = contract.functions.nextId().call()
    contract.functions.nextId().transact()  # Notarization

    url = generate_code_url(
        tk_id=estimate_tk_id, start_station=start_station, end_station=end_station, station_num=station_num, date=date
    )
    ticket = Ticket(
        tk_id=estimate_tk_id, start_station=start_station, end_station=end_station,
        station_num=station_num, date=date, url=url
    )
    ticket_json = ticket.jsonify_light()

    ticket_uri = generate_ticket_uri(ticket_json)

    try:
        tk_id = contract.functions.buyTicket(
            buyer=web3.eth.defaultAccount,
            stationNum=station_num,
            startStation=start_station,
            endStation=end_station,
            date=timestamp,
            ticketURI=ticket_uri
        ).call({"value": ticket.price_wei()})
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket buy failed: " + str(e)}), 400
    if tk_id == 0:
        return jsonify({"message": "Ticket buy failed!"}), 400
    if tk_id != estimate_tk_id:
        return jsonify({"message": "Ticket buy failed for a race condition!"}), 400

    contract.functions.buyTicket(
        buyer=web3.eth.defaultAccount,
        stationNum=station_num,
        startStation=start_station,
        endStation=end_station,
        date=timestamp,
        ticketURI=ticket_uri
    ).transact({"value": ticket.price_wei()})

    ticket.id = tk_id
    ticket_json = ticket.jsonify_full()
    response = {"ticket": ticket_json, "ticket_uri": ticket_uri, "message": "Ticket buyed successfully!"}
    return jsonify(response), 200


@app.route("/refund_ticket", methods=['GET'])
def refund_ticket():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    ticket_id = int(request.args.get('ticket_id'))

    try:
        contract.functions.refund(ticketId=ticket_id).call()
        contract.functions.refund(ticketId=ticket_id).transact()  # Notarization
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket " + str(ticket_id) + " refund failed : " + str(e)}), 400

    response = {"message": "Ticket " + str(ticket_id) + " refunded successfully!"}
    return jsonify(response), 200


@app.route("/usage_setter/use_ticket", methods=["GET"])
def use_ticket():
    if not set_account_flag:
        return jsonify({"message": "You are not logged in!"}), 400
    ticket_id = request.args.get('ticket_id')
    if not contract.functions.isAdmin(account=web3.eth.defaultAccount).call() and not contract.functions.isUsageSetter(account=web3.eth.defaultAccount):
        return jsonify({"message": "Ticket usage setting failed: you are not an admin or a usage setter!"}), 400
    try:
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        contract.functions.useTicket(ticketId=ticket_id).call()
        contract.functions.useTicket(ticketId=ticket_id).transact()  # Notarization
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket usage setting failed : " + str(e)}), 400

    response = {"message": "Ticket usage setted successfully!"}
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)