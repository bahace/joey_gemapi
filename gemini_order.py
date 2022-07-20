# The intent was to quickly write a script to take advantage of Gemini's
# API trade discount, and allowing to make trades in other cryptos to avoid
# taxable transactions (USD and stablecoins)
#
# Sandbox Usage:
#
#       python gemini_order.py
#
# Production Usage:
#
#       python gemini_order.py --production


import config
import requests
import json
import base64
import hmac
import hashlib
import datetime
import time
import argparse


def main(args):
    if args.production:
        base_url = "https://api.gemini.com"
        gemini_api_key = config.gemini_prod_api
        gemini_api_secret = config.gemini_prod_secret.encode()

    else:
        base_url = "https://api.sandbox.gemini.com"
        gemini_api_key = config.gemini_sandbox_api
        gemini_api_secret = config.gemini_sandbox_secret.encode()

    buy_curr = input("Coin [ETH, BTC, etc]: ")
    sell_curr = input("Buy with (USD, BTC, etc]: ")
    buy_price = float(input(f"{buy_curr}+{sell_curr} limit price: "))
    sell_total = float(input(f"Purchase price in {sell_curr}: "))
    buy_qty = round(sell_total / buy_price, 5)
    payload_symbol = buy_curr + sell_curr.lower()

    fees = round(sell_total * .001, 8)
    total = round(sell_total - fees, 8)

    print("Order type: Limit")
    print(f"Price: ${buy_price}")
    print("Quantity:")
    print(f"{buy_qty} {buy_curr}")
    print(f"Subtotal: {sell_total} {sell_curr}")
    print(f"Fee(0.1%): {fees} {sell_curr}")
    print(f"Total Proceeds: {total} {sell_curr}")

    proceed = input("do you want to proceed? Y/N: ").lower()
    if proceed == "n":
        print("You have chosen not to proceed. Order not submitted. ")
        exit()

    t = datetime.datetime.now()
    payload_nonce = str(int(time.mktime(t.timetuple()) * 1000))
    # Note that options is an array. If you omit options or provide an empty
    # array, your order will be a standard limit order - it will immediately
    # fill against any open orders at an equal or better price, then the
    # remainder of the order will be posted to the order book.
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": payload_symbol,
        "amount": buy_qty,
        "price": buy_price,
        "side": "buy",
        "type": "exchange limit",
    }

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    request_headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': gemini_api_key,
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }

    endpoint = "/v1/order/new"
    url = base_url + endpoint
    response = requests.post(url, headers=request_headers)

    my_trades = response.json()
    print(my_trades)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--production",
                        help="Enable to make prod API calls",
                        default=False,
                        required=False,
                        action="store_true")
    args = parser.parse_args()
    main(args)
