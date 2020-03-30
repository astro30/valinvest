from .fundamentals import *
from .config import SP_500_TICKERS, NASDAQ_100_TICKERS

def get_tickers_scores(ticker_list=SP_500_TICKERS):
    res = []
    for ticker in ticker_list:
        try:
            score = get_scores(ticker).iloc[:,-5:].mean(axis=1).sum()
            res.append([ticker, score])
            print(ticker, score)
        except Exception as e:
            print(ticker, e)
    return res

