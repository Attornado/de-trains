import json
from datetime import datetime

EURO_WEI = 370816960785710
TICKET_PRICE_SHORT = EURO_WEI
TICKET_PRICE_MEDIUM = 2 * EURO_WEI
TICKET_PRICE_LONG = 3 * EURO_WEI
MIN_STATION_MEDIUM = 5
MIN_STATION_LONG = 13


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

    def jsonify_light(self):
        return json.dumps({
            "id": self.id, "start_station": self.start_station, "end_station": self.end_station,
            "station_num": self.station_num, "date": self.date, "url": self.url
        })

    def jsonify_full(self):
        return json.dumps(self.__dict__)

    def price_wei(self) -> int:
        if self.station_num < MIN_STATION_MEDIUM:
            return TICKET_PRICE_SHORT
        elif MIN_STATION_MEDIUM <= self.station_num < MIN_STATION_LONG:
            return TICKET_PRICE_MEDIUM
        elif self.station_num >= MIN_STATION_LONG:
            return TICKET_PRICE_LONG
        return 0
