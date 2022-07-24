from flask import jsonify, request, render_template
from web3 import exceptions
import web3
from src.contract_setup import web3, contract
from flask import Blueprint


ADMIN_API = Blueprint('ADMIN_API', __name__)


@ADMIN_API.route("/admin", methods=["GET"])
def show_admin_page():
    # if not set_account_flag:
    #    return jsonify({"message": "You are not logged in!"}), 400
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        return render_template('./admin.html')
    else:
        return jsonify({"message": "You are not an admin!"}), 400


@ADMIN_API.route("/admin/register_admin", methods=["GET"])
def register_admin():
    # if not set_account_flag:
    #    return jsonify({"message": "You are not logged in!"}), 400
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


@ADMIN_API.route("/admin/register_ticket_usage_setter", methods=["GET"])
def register_ticket_usage_setter():
    # if not set_account_flag:
    #    return jsonify({"message": "You are not logged in!"}), 400
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


@ADMIN_API.route("/admin/withdraw", methods=["GET"])
def withdraw():
    # if not set_account_flag:
    #    return jsonify({"message": "You are not logged in!"}), 400
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


'''
@ADMIN_API.route("/admin/remove_admin", methods=["GET"])
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


@ADMIN_API.route("/admin/remove_ticket_usage_setter", methods=["GET"])
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


@ADMIN_API.route("/admin/transfer_founds", methods=["GET"])
def transfer_founds():
    address = request.args.get('transfer_address')
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()

        try:
            contract.functions.removeUsageSetterRole(to=address).call()
            contract.functions.removeUsageSetterRole(to=address).transact()  # Notarization
        except exceptions.SolidityError as e:
            return jsonify({"message": "Usage setter role assignation failed: " + str(e)}), 400

    else:
        return jsonify({
            "message": "Usage setter role renounce failed: you are not an admin nor a usage setter!"
        }), 400
'''
