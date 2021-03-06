import json
from flask import jsonify, request, render_template
import ipfshttpclient
from web3 import exceptions
from src.contract_setup import web3, contract
from typing import final
from flask import Blueprint
from src.tickets.ticket_db import retrieve_and_check_ticket_by_id, retrieve_filter


TICKETS_API = Blueprint('TICKETS_API', __name__)
IPFS_ADDRESS: final = "127.0.0.1:5001"
IPFS_PORT: final = 5001
_N_TICKETS_PER_PAGE: final = 5


def generate_ticket_uri(ticket_json):
    """
    Generates NFT URI pointing to given ticket json.

    :param ticket_json: the json to generate NFT URI for.
    :return: an URI string pointing to the NFT URI of the ticket.
    """
    tk_id = json.loads(ticket_json)['id']
    filename = 'ticket' + str(tk_id) + '.json'
    with open(filename, 'w') as outfile:
        outfile.write(ticket_json)
    api = ipfshttpclient.connect() #"/dns/ipfs.infura.io/tcp/5001/https"
    res = api.add(filename)
    return 'https://ipfs.io/ipfs/' + res['Hash']


def generate_code_url(tk_id: int, origin: str, destination: str, start_date: str, end_date: str,
                      train_type: str, train_class: str, fare: str, price: float, db_id: int) -> str:
    """
    Generates a QR code URL for the ticket with given parameters.

    :param tk_id: NFT id of the ticket.
    :param origin: start station of the ticket.
    :param destination: destination station of the ticket.
    :param start_date: start of the train ride.
    :param end_date: end of the train ride.
    :param train_type: train type of the ride.
    :param train_class: train class of the ride.
    :param fare: fare of the train ride.
    :param price: price of the ticket.
    :param db_id: database id of the ticket.
    :return: the URL of the generated ticket QR code.
    """
    # Dummy file
    filename = "src/static/assets/qr/qrcode.txt"
    api = ipfshttpclient.connect() #"/dns/ipfs.infura.io/tcp/5001/https"
    res = api.add(filename)
    return 'https://ipfs.io/ipfs/' + res['Hash']


@TICKETS_API.route("/buy_ticket", methods=['GET'])
def buy_ticket():
    # These parameters can be taken from the front-end safely, since ticket validator will eventually check them
    # comparing the purchased ticket stored in smart contract with the database one
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    train_type = request.args.get("train_type")
    train_class = request.args.get("train_class")
    fare = request.args.get("fare")
    price = float(request.args.get("price"))
    db_id = int(request.args.get('db_id'))

    # Check if it exists a ticket matching the given parameters
    '''
    ticket = retrieve_and_check_ticket_by_id(
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
    '''
    try:
        ticket = retrieve_filter(db_id=db_id)[0]
    except IndexError:
        ticket = None

    if ticket is None:
        return jsonify({
            "message": f"Ticket buy failed:  ticket with given parameters "
                       f"origin: {origin}, destination: {destination}, start_date: {start_date}, end_date: {end_date},"
                       f" train_type: {train_type}, train_class: {train_class}, fare: {fare}, price: {price}, "
                       f"db_id: {db_id} doesn't exist."
        }), 400

    # Generate QR code URL for ticket
    estimate_tk_id = contract.functions.nextId().call()
    contract.functions.nextId().transact()  # notarization
    url = generate_code_url(
        tk_id=estimate_tk_id,
        origin=ticket.origin,
        destination=ticket.destination,
        start_date=ticket.start_date,
        end_date=ticket.end_date,
        train_type=ticket.train_type,
        train_class=ticket.train_class,
        fare=ticket.fare,
        price=ticket.price,
        db_id=ticket.db_id
    )
    ticket.url = url

    # Generate ticket URI
    ticket_json_light = ticket.jsonify_light()
    ticket_uri = generate_ticket_uri(ticket_json_light)

    # Simulate the buyTicket() function call to obtain the ticket id and check it
    try:
        tk_id = contract.functions.buyTicket(
            buyer=web3.eth.defaultAccount,
            origin=ticket.origin,
            destination=ticket.destination,
            trainType=ticket.train_type,
            trainClass=ticket.train_class,
            fare=ticket.fare,
            startDate=ticket.start_date_as_int,
            endDate=ticket.end_date_as_int,
            dbId=ticket.db_id,
            ticketURI=ticket_uri
        ).call({'value': ticket.price_wei})
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket buy failed: " + str(e)}), 400
    if tk_id == 0:
        return jsonify({"message": "Ticket buy failed!"}), 400
    if tk_id != estimate_tk_id:
        return jsonify({"message": "Ticket buy failed for a race condition!"}), 400

    # Notarize the ticket purchase
    contract.functions.buyTicket(
        buyer=web3.eth.defaultAccount,
        origin=ticket.origin,
        destination=ticket.destination,
        trainType=ticket.train_type,
        trainClass=ticket.train_class,
        fare=ticket.fare,
        startDate=ticket.start_date_as_int,
        endDate=ticket.end_date_as_int,
        dbId=ticket.db_id,
        ticketURI=ticket_uri
    ).transact({'value': ticket.price_wei})

    ticket.id = tk_id
    ticket_json = ticket.jsonify_full()
    response = {"ticket": ticket_json, "ticket_uri": ticket_uri, "message": "Ticket bought successfully!"}
    return jsonify(response), 200


@TICKETS_API.route("/refund_ticket", methods=['GET'])
def refund_ticket():
    ticket_id = int(request.args.get('ticket_id'))

    try:
        contract.functions.refund(ticketId=ticket_id).call()
        contract.functions.refund(ticketId=ticket_id).transact()  # Notarization
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket refund failed : " + str(e)}), 400

    response = {"message": "Ticket refunded successfully!"}
    return jsonify(response), 200


@TICKETS_API.route("/usage_setter/use_ticket", methods=["GET"])
def use_ticket():
    ticket_id = request.args.get('ticket_id')
    if not contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        return jsonify({"message": "Ticket usage setting failed: you are not an admin or a usage setter!"}), 400
    try:
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization
        contract.functions.useTicket(ticketId=ticket_id).call()
        contract.functions.useTicket(ticketId=ticket_id).transact()  # Notarization
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket usage setting failed : " + str(e)}), 400

    response = {"message": "Ticket usage setted successfully!"}
    return jsonify(response), 200


@TICKETS_API.route("/retrieve_tickets", methods=["GET"])
def retrieve_tickets():
    # Setup parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    train_type = request.args.get("train_type")
    train_class = request.args.get("train_class")
    fare = request.args.get("fare")

    if start_date is not None and start_date != "":
        start_date = start_date.replace("T", " ")

    if end_date is not None and end_date != "":
        end_date = end_date.replace("T", " ")

    max_price = request.args.get("max_price")
    if max_price is not None and max_price != "":
        max_price = float(max_price)
    else:
        max_price = None

    db_id = request.args.get('db_id')
    if db_id is not None and db_id != "":
        db_id = int(db_id)
    else:
        db_id = None

    offset = request.args.get('offset')
    if offset is not None and offset != "":
        offset = int(offset)
    else:
        offset = None

    limit = request.args.get('limit')
    if limit is not None and limit != "":
        limit = int(limit)
    else:
        limit = None

    # Retrieve results
    results = retrieve_filter(
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        train_type=train_type,
        fare=fare,
        max_price=max_price,
        train_class=train_class,
        db_id=db_id,
        offset=offset,
        limit=limit
    )

    # Convert them in json
    results_json = [result.jsonify_full() for result in results]

    # Build and return response
    response = {"tickets": results_json, "message": "Tickets retrieved successfully!"}
    return jsonify(response), 200


@TICKETS_API.route('/products')
@TICKETS_API.route('/products.html')
def show_tickets():
    # Setup parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    train_type = request.args.get("train_type")
    train_class = request.args.get("train_class")
    fare = request.args.get("fare")

    if start_date is not None and start_date != "":
        start_date = start_date.replace("T", " ")

    if end_date is not None and end_date != "":
        end_date = end_date.replace("T", " ")

    max_price = request.args.get("max_price")
    if max_price is not None and max_price != "":
        max_price = float(max_price)
    else:
        max_price = None

    db_id = request.args.get('db_id')
    if db_id is not None and db_id != "":
        db_id = int(db_id)
    else:
        db_id = None

    offset = request.args.get('offset')
    if offset is not None and offset != "":
        offset = int(offset)
    else:
        offset = None

    limit = request.args.get('limit')
    if limit is not None and limit != "":
        limit = int(limit)
    else:
        limit = None

    page = request.args.get('page')
    if page is not None and page != "":
        page = int(page)
        offset = _N_TICKETS_PER_PAGE*page
    else:
        page = 0

    if limit is None:
        limit = _N_TICKETS_PER_PAGE

    # Retrieve results
    results = retrieve_filter(
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        train_type=train_type,
        fare=fare,
        max_price=max_price,
        train_class=train_class,
        db_id=db_id,
        offset=offset,
        limit=limit
    )

    admin_flag = False
    if contract.functions.isAdmin(account=web3.eth.defaultAccount).call():
        admin_flag = True
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact()  # Notarization

    return render_template(
        './products.html',
        tickets=results,
        page=page,
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        train_type=train_type,
        fare=fare,
        max_price=max_price,
        train_class=train_class,
        db_id=db_id,
        admin_flag=admin_flag
    )
