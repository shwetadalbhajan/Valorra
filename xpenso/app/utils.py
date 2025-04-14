import requests
from decimal import Decimal

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount

    url = "https://api.freecurrencyapi.com/v1/latest"
    params = {
        "apikey": "fca_live_uvpRZhgejJkX7iBvbaN3U14KKQkvEhEn4admRZ6o",
        "base_currency": from_currency
    }
    response = requests.get(url, params=params).json()
    rate = response['data'].get(to_currency)

    if rate:
        # Convert both amount and rate to Decimal using str() for precision
        amount_decimal = Decimal(str(amount))
        rate_decimal = Decimal(str(rate))
        return round(amount_decimal * rate_decimal, 2)

    return amount
