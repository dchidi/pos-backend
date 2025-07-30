from enum import Enum


class Currency(str, Enum):
    US_DOLLAR = "USD"
    EURO = "EUR"
    BRITISH_POUNDS = "GBP"
    NAIRA = "NGN"
