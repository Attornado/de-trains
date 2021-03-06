from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.contract_setup import web3, contract
from src.tickets.tickets_api import TICKETS_API
from src.admin.admin_api import ADMIN_API


# Instantiate the flask app
app = Flask(__name__)
CORS(app)

# Get APIs from other files
app.register_blueprint(TICKETS_API)
app.register_blueprint(ADMIN_API)


def check_account_exist(address: str) -> bool:
    for account in web3.eth.accounts:
        if address == account:
            return True
    return False


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('./index.html')


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
    is_admin = contract.functions.isAdmin(account=web3.eth.defaultAccount).call()
    app.config['is_admin'] = is_admin

    return render_template('./index.html')


@app.route("/login_mnemonic", methods=["POST"])
def login_mnemonic():
    params = request.form
    mnemonic = params['mnemonic']
    account = web3.eth.account.from_mnemonic(mnemonic)
    if not check_account_exist(account.address):
        return jsonify({"message": "Account login failed!"}), 400

    web3.eth.defaultAccount = account.address
    is_admin = contract.functions.isAdmin(account=web3.eth.defaultAccount).call()
    app.config['is_admin'] = is_admin

    return jsonify({"message": "Login successful!"}), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
