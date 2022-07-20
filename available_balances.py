import config
import requests
import json
import base64
import hmac
import hashlib
import datetime
import time
import argparse
import pprint

pp = pprint.PrettyPrinter(indent=4)


def main(args):
    if args.production:
        base_url = "https://api.gemini.com"
        gemini_api_key = config.gemini_prod_api
        gemini_api_secret = config.gemini_prod_secret.encode()

    else:
        base_url = "https://api.sandbox.gemini.com"
        gemini_api_key = config.gemini_sandbox_api
        gemini_api_secret = config.gemini_sandbox_secret.encode()

    urn = "/v1/notionalbalances/usd"
    url = base_url + urn

    t = datetime.datetime.now()
    payload_nonce = str(int(time.mktime(t.timetuple()) * 1000))
    payload = {
        "request": urn,
        "nonce": payload_nonce,
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

    response = requests.post(url, headers=request_headers)

    message = response.json()
    pp.pprint(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--production",
                        help="Enable to make prod API calls",
                        default=False,
                        required=False,
                        action="store_true")
    args = parser.parse_args()
    main(args)
