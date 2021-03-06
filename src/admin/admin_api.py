from flask import jsonify, request, render_template, redirect
from web3 import exceptions
import web3
from src.contract_setup import web3, contract
from src.tickets.ticket_db import insert_ticket, update_ticket, delete_ticket
from flask import Blueprint


ADMIN_API = Blueprint('ADMIN_API', __name__)


@ADMIN_API.route("/admin", methods=["GET"])
def show_admin_page():
    # if not set_account_flag:
    # return jsonify({"message": "You are not logged in!"}), 400
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        return render_template('./admin.html')
    else:
        return jsonify({"message": "You are not an admin!"}), 400


@ADMIN_API.route("/admin/update_page")
@ADMIN_API.route("/admin/insert_page")
def show_product_form():
    modify = request.args.get('modify')
    insert = request.args.get('insert')
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        if modify is not None:

            return render_template(
                './product_form.html',
                insert=insert,
                modify=modify,
                origin=request.args.get('origin'),
                destination=request.args.get('destination'),
                start_date=request.args.get("start_date"),
                end_date=request.args.get("end_date"),
                train_type=request.args.get("train_type"),
                train_class=request.args.get("train_class"),
                fare=request.args.get("fare"),
                price=float(request.args.get("price")),
                db_id=int(request.args.get('db_id'))
            )
        else:
            return render_template('./product_form.html', insert=insert, modify=modify)


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


@ADMIN_API.route("/admin/insert_ticket", methods=["GET"])
def insert_ticket_api():
    origin = request.args.get('origin').upper()
    destination = request.args.get('destination').upper()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    train_type = request.args.get("train_type")
    train_class = request.args.get("train_class")
    fare = request.args.get("fare")
    price = float(request.args.get("price"))

    if start_date is not None and start_date != "":
        start_date = start_date.replace("T", " ")

    if end_date is not None and end_date != "":
        end_date = end_date.replace("T", " ")

    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        try:
            new_ticket = insert_ticket(
                origin=origin,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                train_type=train_type,
                train_class=train_class,
                fare=fare,
                price=price
            )
            response = {"message": f"Datebase ticket with id: {new_ticket.db_id} created successfully!"}
            return jsonify(response), 200
        except BaseException as e:
            return jsonify({
                "message": f"Database ticket creation failed: {e}"
            }), 400
    else:
        return jsonify({"message": "Ticket insertion failed: you are not an admin!"}), 400


@ADMIN_API.route("/admin/update_ticket", methods=["GET"])
def update_ticket_api():
    origin = request.args.get('origin').upper()
    destination = request.args.get('destination').upper()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    train_type = request.args.get("train_type")
    train_class = request.args.get("train_class")
    fare = request.args.get("fare")
    db_id = int(request.args.get('db_id'))

    if start_date is not None and start_date != "":
        start_date = start_date.replace("T", " ")

    if end_date is not None and end_date != "":
        end_date = end_date.replace("T", " ")

    price = request.args.get("price")
    if price is not None and price != "":
        price = float(price)

    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        updated_ticket = update_ticket(
            origin=origin,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            train_type=train_type,
            train_class=train_class,
            fare=fare,
            price=price,
            db_id=db_id
        )

        if updated_ticket is not None:
            return jsonify({"message": f"Ticket with id: {db_id} updated successfully!"}), 200
        else:
            return jsonify({"message": f"Ticket with id {db_id} not updated because it doesn't exist!"}), 400
    else:
        return jsonify({"message": "Ticket update failed: you are not an admin!"}), 400


@ADMIN_API.route("/admin/delete_ticket", methods=["GET"])
def delete_ticket_api():
    db_id = int(request.args.get('db_id'))
    reload = request.args.get('reload')

    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        if delete_ticket(db_id):
            if reload is not None and reload != "":
                return redirect("/products", code=302)
            else:
                return jsonify({"message": f"Ticket with id: {db_id} deleted successfully!"}), 200
        else:
            return jsonify({"message": f"Ticket with id {db_id} not deleted because it doesn't exist!"}), 400
    else:
        return jsonify({"message": "Ticket delete failed: you are not an admin!"}), 400