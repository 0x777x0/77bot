from ca.binance import get_binance_price
from ca.okx import get_okx_price

def get_exchange_price(symbol):
    price,priceChangePercent = get_binance_price(symbol)
    if price is not None and isinstance(price, int) and price == 0:
        price,priceChangePercent = get_okx_price(symbol)
    return {price,priceChangePercent}  



