from typing import final, Optional
from pymongo import MongoClient


DB_NAME: final = "TrainTickets"
COLLECTION_NAME: final = "Tickets"
CONNECTION_STRING: final = "mongodb+srv://Attornado:andrea22@cluster0.t3es8fi.mongodb.net/?retryWrites=true&w=majority"


def get_db_connection(connection_string: str, name: Optional[str] = None, collection: Optional[str] = None):
    """
    Gets connection to given db.

    :param connection_string: connection string to mongodb cluster/organization.
    :param name: database name to connect to (None by default).
    :param collection: collection name to extract from the database (None by default).
    :return: a cluster connection object if name and collection are not provided, a db connection object if name is
        specified or a collection object if collection name is given.
    :raises ValueError: if database name is not given while collection name is specified.
    """
    if name is None and collection is not None:
        raise ValueError("Collection name cannot be specified if no database name is specified.")

    # Create connection
    client = MongoClient(connection_string)

    if name is not None:
        db = client[name]
    else:
        return client

    if collection is not None:
        collection_connection = db[collection]
        collection_connection.find()
    else:
        return db

    return collection_connection

