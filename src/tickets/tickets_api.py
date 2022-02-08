import json

import ipfsApi
from flask import jsonify, request
from web3 import exceptions

from src.main_app import app, web3, contract
from ticket import Ticket

IPFS_ADDRESS = "127.0.0.1"
IPFS_PORT = 5001


def generate_ticket_uri(ticket_json):
    tk_id = json.loads(ticket_json)['id']
    filename = 'ticket' + tk_id + '.json'
    with open(filename, 'w') as outfile:
        outfile.write(ticket_json)
    api = ipfsApi.Client(IPFS_ADDRESS, IPFS_PORT)
    res = api.add(filename)
    return 'https://ipfs.io/ipfs/' + res['Hash']


def generate_code_url(tk_id: int, start_station: str, end_station: str, station_num: int, date: str) -> str:
    filename = "static/assets/qr/qrcode.txt"
    api = ipfsApi.Client(IPFS_ADDRESS, IPFS_PORT)
    res = api.add(filename)
    return 'https://ipfs.io/ipfs/' + res['Hash']


@app.route("/buy_ticket", methods=['GET'])
def buy_ticket():
    date = request.args.get("date")
    start_station = request.args.get('start_station')
    end_station = request.args.get('end_station')
    station_num: int = int(request.args.get('station_num'))


    # generate QR code for ticket
    estimate_tk_id = contract.functions.nextId().call()
    contract.functions.nextId().transact()  # Notarization

    url = generate_code_url(estimate_tk_id, start_station, end_station, station_num, date)
    ticket = Ticket(start_station, end_station, station_num, date, url)
    ticket_json = ticket.jsonify_light()

    ticket_uri = generate_ticket_uri(ticket_json)

    try:
        tk_id = contract.functions.buyTicket(
            buyer=web3.eth.defaultAccount,
            stationNum=station_num,
            startStation=start_station,
            endStation=end_station,
            date=date,
            ticketURI=ticket_uri
        ).call()
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
        date=date,
        ticketURI=ticket_uri
    ).transact()

    ticket.id = tk_id
    ticket_json = ticket.jsonify_full()
    response = {"ticket": ticket_json, "ticket_uri": ticket_uri, "message": "Ticket buyed successfully!"}
    return jsonify(response), 200


@app.route("/refund", methods=['GET'])
def refund_ticket():
    ticket_id = request.args.get('ticket_id')

    try:
        contract.functions.refund(ticketId=ticket_id).call()
        contract.functions.refund(ticketId=ticket_id).transact()  # Notarization
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket refund failed : " + str(e)}), 400

    response = {"message": "Ticket refunded successfully!"}
    return jsonify(response), 200


@app.route("/usage_setter/use_ticket", methods=["GET"])
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
