import json
from datetime import datetime


def generate_code_url(start_station: str, end_station: str, station_num: int, date: str) -> str:
    url = "qrcodeURL"
    return url


def generate_ticket_uri(start_station: str, end_station: str, station_num: int, date: str, code_url: str) -> str:
    uri = {
        "station_num": station_num,
        "start_station": start_station,
        "end_station": end_station,
        "date": date,
        "code_url": code_url
    }
    return json.dumps(uri)


class Ticket:
    def __init__(self, start_station: str, end_station: str, station_num: int, date: str, url: str, tk_id: int = 0,
                 used: bool = False, refunded: bool = False):
        self.__id = tk_id
        self.__start_station = start_station
        self.__end_station = end_station
        self.__station_num = station_num
        self.__date = date
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
    def start_station(self) -> str:
        return self.__start_station

    @property
    def end_station(self) -> str:
        return self.__end_station

    @property
    def date(self) -> str:
        return self.__date

    # format '%d/%m/%y %H:%M:%S.%f'
    def date_as_int(self) -> int:
        a = datetime.strptime(self.__date, '%d/%m/%y')
        return a.microsecond

    @property
    def station_num(self):
        return self.__station_num

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

    def jsonify(self):
        return json.dumps(self.__dict__)
