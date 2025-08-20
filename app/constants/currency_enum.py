from enum import Enum


class Currency(str, Enum):
    US_DOLLAR = "USD"
    EURO = "EUR"
    BRITISH_POUNDS = "GBP"
    NAIRA = "NGN"
    GHANA_CEDI = "GHS"
    SOUTH_AFRICA_RAND = "ZAR"

_MINOR = {
    Currency.NAIRA: 100,
    Currency.GHANA_CEDI: 100,
    Currency.SOUTH_AFRICA_RAND: 100,
    Currency.US_DOLLAR: 100,    
    Currency.EURO: 100,
    Currency.BRITISH_POUNDS: 100
}


def to_minor_units(amount_major: float | int | str, currency: Currency = Currency.NAIRA) -> int:
    if currency not in _MINOR:
        raise ValueError(f"Unsupported currency: {currency}")
    return int(round(float(amount_major) * _MINOR[currency]))