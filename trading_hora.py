import ccxt
import numpy as np
import talib
import time
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email_user = 'tuCorreo@gmail.com'
email_password = 'tuPasswordDeAplicacion'
email_recipient = 'tuCorreo@gmail.com'

# Configurar intercambio y símbolo de trading
exchange = ccxt.binance()
symbol = 'BTC/USDT'

# Configurar RSI
rsi_period = 14
overbought = 70
oversold = 30

# Obtener datos históricos
candlestick_data = exchange.fetch_ohlcv(symbol, '1d')
closing_prices = np.array([c[4] for c in candlestick_data])

def send_email(signal, price, timestamp):
    subject = f"Señal de trading: {signal}"

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_recipient
    msg['Subject'] = subject

    body = f"{timestamp} - {signal} - Precio: {price}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, email_recipient, text)
        server.quit()
        print(f"Correo enviado: {signal}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


# Función para actualizar el RSI y emitir señales de trading
def check_rsi():
    # Actualizar datos
    new_candlestick = exchange.fetch_ohlcv(symbol, '1h', since=exchange.milliseconds() - 3600 * 1000)
    new_closing_price = new_candlestick[-1][4]
    closing_prices[-1] = new_closing_price

    # Calcular RSI
    rsi = talib.RSI(closing_prices, timeperiod=rsi_period)[-1]
    
    print(f"Valor actual del RSI Minuto: {rsi}")


    # Generar señales de trading
    if rsi < oversold:
        return 'Compra ahora', new_closing_price
    elif rsi > overbought:
        return 'Vende ahora', new_closing_price
    else:
        return None, new_closing_price

# Bucle para verificar el RSI en tiempo real
while True:
    signal, price = check_rsi()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if signal:
        print(f"{current_time} - {signal} - Precio: {price}")
        send_email(signal, price, current_time)
    else:
        print(f"{current_time} - Sin señal - Precio: {price}")
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados.txt"), "a") as file:
            file.write(f"{current_time} - {signal} - Precio: {price}\n")
    time.sleep(15)
