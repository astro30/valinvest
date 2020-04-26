from .fundamentals import Fundamental
from .config import SP_500_TICKERS, NASDAQ_100_TICKERS


def get_tickers_scores(ticker_list=NASDAQ_100_TICKERS):
    res = []
    for ticker in ticker_list:
        try:
            score = Fundamental(ticker).fscore()
            res.append([ticker, score])
            print(ticker, score)
        except Exception as e:
            print(ticker, e)
    return res
