import os
import time
from binance.client import Client

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# ✅ Debug temporaire : vérifie que les variables sont bien récupérées
print("Clé API présente ?", API_KEY is not None)
print("Clé SECRÈTE présente ?", API_SECRET is not None)

client = Client(API_KEY, API_SECRET)

def should_buy(symbol):
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=14)
    closes = [float(kline[4]) for kline in klines]
    avg = sum(closes) / len(closes)
    current_price = closes[-1]
    return current_price < avg * 0.98

def should_sell(symbol, buy_price):
    current_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
    return current_price >= buy_price * 1.02

def run_bot():
    symbol = "DOGEUSDC"
    quantity = 5  # En USDC
    asset = "DOGE"
    usdc_balance = float(client.get_asset_balance(asset="USDC")["free"])

    if usdc_balance >= quantity and should_buy(symbol):
        order = client.order_market_buy(symbol=symbol, quoteOrderQty=quantity)
        buy_price = float(order["fills"][0]["price"])
        print(f"Achat à {buy_price}")

        while True:
            if should_sell(symbol, buy_price):
                asset_balance = float(client.get_asset_balance(asset=asset)["free"])
                client.order_market_sell(symbol=symbol, quantity=round(asset_balance, 1))
                print("Vente exécutée")
                break
            time.sleep(30)

if __name__ == "__main__":
    run_bot()
