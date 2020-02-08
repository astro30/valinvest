import pandas as pd
import numpy as np
from alpha_vantage.techindicators import TechIndicators
from .config import *

ti = TechIndicators(key=ALPHA_VANTAGE_KEY, output_format='pandas')

def get_rsi(ticker, period=250):
    df = ti.get_rsi(ticker, interval='daily', time_period=period)[0]
    return df.sort_index(ascending=False).iloc[0].values[0]


def get_macd(ticker):
    df = ti.get_macd(ticker, interval='daily')[0]
    return df.sort_index(ascending=False).iloc[0].values


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


def get_technicals(ticker):
    macd = ti.get_macd(ticker, interval='daily')[0]
    rsi_250 = ti.get_rsi(ticker, interval='daily', time_period=250)[0]
    rsi_250.columns = ['RSI_250']
    rsi_10 = ti.get_rsi(ticker, interval='daily', time_period=10)[0]
    rsi_10.columns = ['RSI_10']

    res = macd.join(rsi_10).join(rsi_250)
    res['momentum'] = np.where(res['RSI_250'] >= 50, 'bullish', 'bearish')
    res['rsi_position'] = np.where(res['RSI_10'] >= 60, 'overbought', np.where(res['RSI_10'] <= 30, 'oversold', 'normal'))

    res['macd_xing'] = np.where((res['MACD_Hist'] > 0) & (res['MACD_Hist'].shift(-1) * res['MACD_Hist'] < 0), 
                                'Upward xing', 
                                np.where((res['MACD_Hist'] < 0) & (res['MACD_Hist'].shift(-1) * res['MACD_Hist'] < 0),
                                    'Downward xing', ''))
    
    return res.dropna()

def get_xing_signal(ticker):
    res = get_technicals(ticker)

    return res.iloc[0, res.columns.get_loc("macd_xing")]