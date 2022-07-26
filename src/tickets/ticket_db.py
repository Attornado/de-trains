from typing import Optional

import pymongo

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
                    fare: Optional[str] = None, max_price: Optional[float] = None, db_id: Optional[int] = None,
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
    :param max_price: maximum price of the ticket.
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
    if origin is not None and origin != "":
        query['origin'] = origin
    if destination is not None and destination != "":
        query['destination'] = destination
    if start_date is not None and start_date != "":
        query['start_date'] = start_date
    if end_date is not None and start_date != "":
        query['end_date'] = end_date
    if train_type is not None and train_type != "":
        query['train_type'] = train_type
    if train_class is not None and train_class != "":
        query['train_class'] = train_class
    if fare is not None and fare != "":
        query['fare'] = fare
    if max_price is not None and max_price != "":
        query['price'] = {"$lte": max_price}  # price must be less than or equal to max_price
    if db_id is not None:
        query['db_id'] = db_id

    # Get results
    if offset is not None and limit is not None:
        results = collection.find(query).skip(offset).limit(limit)
    elif offset is not None and limit is None:
        results = collection.find(query).skip(offset)
    elif offset is None and limit is not None:
        results = collection.find(query).limit(limit)
    else:
        results = collection.find(query)

    # For each result, create a Ticket containing retrieved ticket parameters, and add it to the return list
    for result in results:
        origin_res = result.get('origin')
        destination_res = result.get('destination')
        start_date_res = result.get('start_date')
        end_date_res = result.get('end_date')
        train_type_res = result.get('train_type')
        train_class_res = result.get('train_class')
        fare_res = result.get('fare')
        price_res = result.get('price')
        db_id_res = int(result.get('id'))

        ticket = Ticket(
            origin=origin_res,
            destination=destination_res,
            start_date=start_date_res,
            end_date=end_date_res,
            train_type=train_type_res,
            train_class=train_class_res,
            fare=fare_res,
            price=price_res,
            db_id=db_id_res
        )
        tickets.append(ticket)

    return tickets


def insert_ticket(origin: str, destination: str, start_date: str, end_date: str,
                  train_type: str, train_class: str, fare: str, price: float) -> Optional[Ticket]:
    """
    Inserts a ticket with given fields into the database.

    :param origin: start station of the ticket.
    :param destination: destination station of the ticket.
    :param start_date: start of the train ride.
    :param end_date: end of the train ride.
    :param train_type: train type of the ride.
    :param train_class: train class of the ride.
    :param fare: fare of the train ride.
    :param price: price of the ticket.
    :return: the ticket having the given parameters retrieved from the database.
    """

    collection = get_db_connection(CONNECTION_STRING, DB_NAME, COLLECTION_NAME)

    try:
        # Get ticket max id
        result = collection.find().sort("id", pymongo.DESCENDING).limit(1).next()  # should return only 1 element
        max_id = int(result["id"])
        db_id = max_id + 1

    except StopIteration:
        # DB is empty and don't contain any tickets
        db_id = 1

    collection.insert_one(document={
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "train_type": train_type,
        "train_class": train_class,
        "fare": fare,
        "price": price,
        "id": db_id
    })

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


def update_ticket(db_id: int, origin: Optional[str] = None, destination: Optional[str] = None,
                  start_date: Optional[str] = None, end_date: Optional[str] = None, train_type: Optional[str] = None,
                  train_class: Optional[str] = None, fare: Optional[str] = None, price: Optional[float] = None) -> \
        Optional[Ticket]:
    """
    Updated the ticket with given fields into the database.

    :param db_id: database id of the ticket to update.
    :param origin: start station of the ticket.
    :param destination: destination station of the ticket.
    :param start_date: start of the train ride.
    :param end_date: end of the train ride.
    :param train_type: train type of the ride.
    :param train_class: train class of the ride.
    :param fare: fare of the train ride.
    :param price: price of the ticket.
    :return: the updated ticket having the given parameters retrieved from the database, None if it doesn't exist.
    """

    update_query = {}

    # Set update query parameters according to given parameters
    if origin is not None and origin != "":
        update_query['origin'] = origin
    if destination is not None and destination != "":
        update_query['destination'] = destination
    if start_date is not None and start_date != "":
        update_query['start_date'] = start_date
    if end_date is not None and end_date != "":
        update_query['end_date'] = end_date
    if train_type is not None and train_type != "":
        update_query['train_type'] = train_type
    if train_class is not None and train_class != "":
        update_query['train_class'] = train_class
    if fare is not None and fare != "":
        update_query['fare'] = fare
    if price is not None and price != "":
        update_query['price'] = price  # price must be less than or equal to max_price

    # Get db connection object
    collection = get_db_connection(CONNECTION_STRING, DB_NAME, COLLECTION_NAME)

    # Update value
    n_updated = collection.update_one(
        filter={"id": db_id}, update={"$set": update_query}
    ).modified_count

    if n_updated > 0:
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
    else:
        return None


def delete_ticket(db_id: int) -> bool:
    """
    Deletes the ticket with given database id from the database.

    :param db_id: database id of the ticket to update.
    :return: True if the ticket was successfully deleted, False otherwise.
    """

    # Get db connection object
    collection = get_db_connection(CONNECTION_STRING, DB_NAME, COLLECTION_NAME)

    query = {
        "id": db_id
    }
    n_deleted = collection.delete_one(query).deleted_count

    if n_deleted > 0:
        return True
    else:
        return False
