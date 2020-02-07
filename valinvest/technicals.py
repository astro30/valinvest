import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from findash.config import *

ti = TechIndicators(key=ALPHA_VANTAGE_KEY, output_format='pandas')

def get_rsi(ticker, period=250):
    df = ti.get_rsi(ticker, interval='daily', time_period=period)[0]
    return df.sort_index(ascending=False).iloc[0].values[0]

def get_macd(ticker):
    df = ti.get_rsi(ticker, interval='daily')[0]
    return df.sort_index(ascending=False).iloc[0].values[0]

def get_momentum(ticker):
    trend_rsi = get_rsi(ticker, period=250)

    res = dict()
    res['rsi'] = trend_rsi

    if trend_rsi >= 50:
        res['momentum'] = "bullish"
    else:
        res['momentum'] = "bearish"
    return res

def get_trading_way(ticker):
    rsi = get_rsi(ticker, period=10)

    res = dict()
    res['rsi'] = rsi
    res['position'] = 'normal'

    if rsi >= 60:
        res['position'] = 'overbought'
    if rsi <= 30:
        res['position'] = 'oversold'
    return res

# TODO créer un indice WallStreetBet