from flask import jsonify, request
from web3 import exceptions

from main_app import app, web3, contract
from ticket import Ticket, generate_code_url, generate_ticket_uri


@app.route("/buy_ticket", methods=['GET'])
def buy_ticket():
    start_station = request.args.get('start_station')
    end_station = request.args.get('end_station')
    station_num: int = int(request.args.get('station_num'))
    date = request.args.get("date")

    # generate QR code for ticket
    url = generate_code_url(start_station, end_station, station_num, date)
    ticket = Ticket(start_station, end_station, station_num, date, url)
    ticket_uri = generate_ticket_uri(start_station, end_station, station_num, date, url)

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

    contract.functions.buyTicket(
        buyer=web3.eth.defaultAccount,
        stationNum=station_num,
        startStation=start_station,
        endStation=end_station,
        date=date,
        ticketURI=ticket_uri
    ).transact()

    ticket.id = tk_id
    ticket_json = ticket.jsonify()
    response = {"ticket": ticket_json, "message": "Ticket buyed successfully!"}
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
        contract.functions.isAdmin(account=web3.eth.defaultAccount).transact() # Notarization
        contract.functions.useTicket(ticketId=ticket_id).call()
        contract.functions.useTicket(ticketId=ticket_id).transact()  # Notarization
    except exceptions.SolidityError as e:
        return jsonify({"message": "Ticket usage setting failed : " + str(e)}), 400

    response = {"message": "Ticket usage setted successfully!"}
    return jsonify(response), 200
