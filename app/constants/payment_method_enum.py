from enum import Enum


class PaymentMethod(str, Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    CASH = "cash"
    POINTS = "points"
    SCANPAY_WALLET = "scanpay_wallet"
    NO_PAYMENT = "no_payment"
    PAY_LATER = "pay_later"
    DIRECT_DEBIT = "direct_debit"
    OTHER = "other"
