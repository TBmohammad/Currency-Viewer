from flask import Flask, render_template
import requests
import os

app = Flask(__name__)

# Better to use environment variables
API_KEY = os.getenv("BRS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def fetch_json(url, params=None):
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


@app.route("/")
def index():

    # -------------------- Crypto --------------------
    crypto = []

    crypto_url = "https://api.coingecko.com/api/v3/coins/markets"

    crypto_params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
    }

    crypto_data = fetch_json(crypto_url, crypto_params)

    if crypto_data:
        for coin in crypto_data:
            crypto.append(
                {
                    "name": coin["name"],
                    "symbol": coin["symbol"].upper(),
                    "price": f'{coin["current_price"]}$',
                }
            )

    # -------------------- Commodities --------------------
    commodities = []

    commodity_url = f"https://Api.BrsApi.ir/Market/commodity.php?key={API_KEY}"

    commodity_data = fetch_json(commodity_url)

    if commodity_data:

        for metal in commodity_data.get("metal_precious", []):
            commodities.append(
                {"symbol": metal["symbol"], "price": f'{metal["price"]} USD'}
            )

        for metal in commodity_data.get("metal_base", []):
            commodities.append(
                {"symbol": metal["symbol"], "price": f'{metal["price"]} USD'}
            )

        for energy in commodity_data.get("energy", []):
            commodities.append(
                {"symbol": energy["symbol"], "price": f'{energy["price"]} USD'}
            )

    # -------------------- Fiat --------------------
    fiat = []

    fiat_url = f"https://Api.BrsApi.ir/Market/Gold_Currency.php?key={API_KEY}"

    fiat_data = fetch_json(fiat_url)

    if fiat_data and "currency" in fiat_data:

        for currency in fiat_data["currency"]:
            fiat.append(
                {"name": currency["symbol"], "price": f'{currency["price"]} IRR'}
            )

    # -------------------- Forex --------------------
    fx = []

    fx_url = "https://open.er-api.com/v6/latest/USD"

    fx_data = fetch_json(fx_url)

    if fx_data and "rates" in fx_data:

        for currency, rate in fx_data["rates"].items():
            fx.append({"currency": f"USD/{currency}", "rate": rate})

    return render_template(
        "index.html", crypto=crypto, fiat=fiat, commodities=commodities, fx=fx
    )


application = app

if __name__ == "__main__":
    app.run(debug=True)
