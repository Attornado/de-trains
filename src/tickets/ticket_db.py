from typing import Optional
from src.db_utils import get_db_connection, CONNECTION_STRING, DB_NAME, COLLECTION_NAME
from src.tickets.ticket import Ticket


def retrieve_and_check_ticket_by_id(origin: str, destination: str, start_date: str, end_date: str,
                                    train_type: str, train_class: str, fare: str, price: float, db_id: int) -> \
        Optional[Ticket]:
    """
    Retrieves ticket by database, checking if it exists a ticket with the given parameters and returning it.

    :param origin: start station of the ticket.
    :param destination: destination station of the ticket.
    :param start_date: start of the train ride.
    :param end_date: end of the train ride.
    :param train_type: train type of the ride.
    :param train_class: train class of the ride.
    :param fare: fare of the train ride.
    :param price: price of the ticket.
    :param db_id: database id of the ticket.
    :return: the ticket having the given parameters retrieved from the database, if it exists, None otherwise.
    """
    collection = get_db_connection(CONNECTION_STRING, DB_NAME, COLLECTION_NAME)
    query = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "train_type": train_type,
        "train_class": train_class,
        "fare": fare,
        "price": price,
        "id": db_id
    }

    try:
        result = collection.find(query).next()  # should return only 1 element
    except StopIteration:
        return None

    return Ticket(
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


def retrieve_filter(origin: Optional[str] = None, destination: Optional[str] = None, start_date: Optional[str] = None,
                    end_date: Optional[str] = None, train_type: Optional[str] = None, train_class: Optional[str] = None,
                    fare: Optional[str] = None, price: Optional[float] = None, db_id: Optional[int] = None,
                    offset: Optional[int] = None, limit: Optional[int] = None) -> list[Ticket]:
    """
    Retrieves tickets by database based on given parameters.

    :param origin: start station of the ticket.
    :param destination: destination station of the ticket.
    :param start_date: start of the train ride.
    :param end_date: end of the train ride.
    :param train_type: train type of the ride.
    :param train_class: train class of the ride.
    :param fare: fare of the train ride.
    :param price: price of the ticket.
    :param db_id: database id of the ticket.
    :param offset: offset index of the query result.
    :param limit: limit index of the query result.
    :return: a list containing the tickets having the given parameters retrieved from the database, if they exists, or
        an empty list otherwise.
    """
    collection = get_db_connection(CONNECTION_STRING, DB_NAME, COLLECTION_NAME)
    query = {}
    tickets: list[Ticket] = []

    # Set query parameters according to given parameters
    if origin is not None:
        query['origin'] = origin
    if destination is not None:
        query['destination'] = destination
    if start_date is not None:
        query['start_date'] = start_date
    if end_date is not None:
        query['end_date'] = end_date
    if train_type is not None:
        query['train_type'] = train_type
    if train_class is not None:
        query['train_class'] = train_class
    if fare is not None:
        query['fare'] = fare
    if price is not None:
        query['price'] = price
    if db_id is not None:
        query['db_id'] = db_id

    # Get results
    results = collection.find(query).skip(offset).limit(limit)  # should return only 1 element

    # For each result, create a Ticket containing retrieved ticket parameters, and add it to the return list
    for result in results:
        origin = result.get('origin')
        destination = result.get('destination')
        start_date = result.get('start_date')
        end_date = result.get('end_date')
        train_type = result.get('train_type')
        train_class = result.get('train_class')
        fare = result.get('fare')
        price = result.get('price')
        db_id = result.get('id')

        ticket = Ticket(
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
        tickets.append(ticket)

    return tickets
