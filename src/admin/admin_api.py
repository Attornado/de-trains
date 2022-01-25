from flask import jsonify, request, render_template
from web3 import exceptions

from src.main_app import app, web3, contract


@app.route("/show_admin_page", methods=["GET"])
def show_admin_page():
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        return render_template('./admin.html')
    else:
        return jsonify({"message": "You are not an admin!"}), 400


@app.route("/admin/register_admin", methods=["GET"])
def register_admin():
    address = request.args.get('admin_address')
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
    address = request.args.get('usage_setter_address')
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


@app.route("/admin/remove_admin", methods=["GET"])
def register_admin():
    address = request.args.get('admin_address')
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
def register_ticket_usage_setter():
    address = request.args.get('usage_setter_address')
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
