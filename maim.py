
import os
import time
import json
import urllib.request
import urllib.parse
from collections import deque

SYMBOL = "solusdt"
INTERVAL = "1m"
PATTERN = ["G", "G", "G", "R", "G"]
POLL_SECONDS = 3

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

history = deque(maxlen=20)
last_candle = None
last_alert = None

def get_candles():
    url = (
        "https://api.binance.com/api/v3/klines"
        f"?symbol={SYMBOL.upper()}&interval={INTERVAL}&limit=10"
    )
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode())

def color(candle):
    open_price = float(candle[1])
    close_price = float(candle[4])
    if close_price > open_price:
        return "G"
    if close_price < open_price:
        return "R"
    return "D"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()

send_telegram("Bot SOL/USDT iniciado. Monitoramento de candles de 1 minuto ativo.")

while True:
    try:
        candles = get_candles()
        # A última vela ainda está aberta; usamos somente velas fechadas.
        closed = candles[:-1]

        if closed:
            latest = closed[-1]
            candle_id = latest[0]

            if candle_id != last_candle:
                last_candle = candle_id
                history.append(color(latest))

                if len(history) >= len(PATTERN):
                    recent = list(history)[-5:]

                    if recent == PATTERN and last_alert != candle_id:
                        send_telegram(
                            "SINAL DETECTADO - SOL/USDT 1m\n"
                            "Padrão fechado: VERDE, VERDE, VERDE, "
                            "VERMELHO, VERDE.\n"
                            "Estratégia em teste: observar possível VERMELHO "
                            "no próximo candle.\n"
                            "Confirme o horário e a vela na sua plataforma."
                        )
                        last_alert = candle_id

    except Exception as error:
        print("Erro temporário:", error)

    time.sleep(POLL_SECONDS)
