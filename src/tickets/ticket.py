import json
from datetime import datetime
from typing import final


EURO_WEI: final = 370816960785710  # this has to be replaced with dynamic one querying an oracle setting correct price
TICKET_PRICE_SHORT: final = EURO_WEI
TICKET_PRICE_MEDIUM: final = 2 * EURO_WEI
TICKET_PRICE_LONG: final = 3 * EURO_WEI
MIN_STATION_MEDIUM: final = 5
MIN_STATION_LONG: final = 13


class Ticket:
    def __init__(self, origin: str, destination: str, start_date: str, end_date: str, train_type: str, train_class: str,
                 fare: str, price: float, db_id: int, url: str = None, tk_id: int = 0, used: bool = False,
                 refunded: bool = False):
        self.__id = tk_id
        self.__origin = origin
        self.__destination = destination
        self.__start_date = start_date
        self.__end_date = end_date
        self.__train_type = train_type
        self.__train_class = train_class
        self.__fare = fare
        self.__price = price
        self.__db_id = db_id
        self.__url = url
        self.__used = used
        self.__refunded = refunded

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, tk_id: int):
        self.__id = tk_id

    @property
    def origin(self) -> str:
        return self.__origin

    @property
    def destination(self) -> str:
        return self.__destination

    @property
    def start_date(self) -> str:
        return self.__start_date

    @property
    def end_date(self) -> str:
        return self.__end_date

    @property
    def start_date_as_int(self) -> int:
        # Format '%d/%m/%y %H:%M:%S.%f'
        try:
            a = datetime.strptime(self.__start_date, '%d/%m/%Y')
        except ValueError:
            a = datetime.strptime(self.__start_date, '%d/%m/%Y %H:%M:%S.%f')
        return int(a.timestamp())

    @property
    def end_date_as_int(self) -> int:
        # Format '%d/%m/%y %H:%M:%S.%f'
        try:
            a = datetime.strptime(self.__end_date, '%d/%m/%Y')
        except ValueError:
            a = datetime.strptime(self.__end_date, '%d/%m/%Y %H:%M:%S.%f')
        return int(a.timestamp())

    @property
    def train_type(self) -> str:
        return self.__train_type

    @property
    def train_class(self) -> str:
        return self.__train_class

    @property
    def fare(self) -> str:
        return self.__fare

    @property
    def price(self) -> float:
        return self.__price

    @property
    def price_wei(self) -> int:
        return int(self.price*EURO_WEI)

    @property
    def db_id(self) -> int:
        return self.__db_id

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    @property
    def used(self):
        return self.__used

    def use(self):
        self.__used = True

    @property
    def refunded(self):
        return self.__refunded

    def refund(self):
        self.__refunded = True

    def jsonify_light(self):
        return json.dumps({
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "train_type": self.train_type,
            "train_class": self.train_class,
            "fare": self.fare,
            "price": self.price,
            "db_id": self.db_id,
            "url": self.url
        })

    def jsonify_full(self):
        return json.dumps(self.__dict__)
