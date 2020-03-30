import requests
import pandas as pd
import io
import re
import numpy as np
from .config import *

def get_financial_statements(ticker):
    res = pd.DataFrame()
    for statement in ['income-statement', 'balance-sheet-statement', 'cash-flow-statement']:
        res = pd.concat([res, get_financial_statement(ticker, statement)])
    res.reset_index(drop=True)

    res.loc[-1] = [ticker, 'beta', res['Year'].max(), 'Beta', get_beta(ticker)]

    return res.sort_values(by=['Ticker', 'Statement', 'Header', 'Year']).reset_index(drop=True)

def get_beta(ticker):
    if not isinstance(ticker, str):
        raise TypeError("Ticker should be a string.")

    url = 'https://financialmodelingprep.com/api/v3/company/profile/{_ticker}'.format(_ticker=ticker)
    res = requests.get(url)
    data = res.json()
    beta = float(data['profile']['beta']) if data['profile']['beta'] else float('inf')

    return beta


def get_financial_statement(ticker, statement):
    if not isinstance(ticker, str):
        raise TypeError("Ticker should be a string.")
    if ticker not in NASDAQ_100_TICKERS or ticker not in SP_500_TICKERS:
        raise ValueError("Ticker should be a NASDAQ 100 ticker or SP 500 ticker")
    if statement not in ['income-statement', 'balance-sheet-statement', 'cash-flow-statement']:
        raise ValueError(
            "Statement should be income-statement: Income Statement, cash-flow-statement: Cash Flow Statement or balance-sheet-statement: Balance Sheet.")

    url = 'https://financialmodelingprep.com/api/v3/financials/{_statement}/{_ticker}'.format(_statement=statement, _ticker=ticker)
    res = requests.get(url)
    data = res.json()

    df = pd.json_normalize(data['financials'])

    df['Ticker'] = ticker.upper()
    df['Statement'] = statement
    df['Year'] = pd.to_datetime(df['date']).dt.year
    del df['date']
    unpivoted_df = pd.melt(df, id_vars=['Ticker', 'Statement', 'Year'])
    unpivoted_df.rename(columns={'variable':'Header', 'value':'Amount'}, inplace=True)
    unpivoted_df['Amount'] = (unpivoted_df['Amount']
                                .replace('', np.nan)
                                .fillna('0')
                                .astype('float'))

    return unpivoted_df.sort_values(by=['Ticker', 'Statement', 'Header', 'Year'])


def ebitda_score(stmt):
    if 'EBITDA' not in stmt['Header'].values:
        raise ValueError("Requested Company does not have EBITDA available.")

    _df = stmt[stmt['Header'] == 'EBITDA'].groupby(['Ticker', 'Statement', 'Header'])[
        'Amount'].pct_change().fillna(0)

    _df_index = stmt[stmt['Header'] == 'EBITDA'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df > 0, 1, 0), index=_df_index)

    return res.rename('EBT_G')


def revenue_score(stmt):
    _df = stmt[stmt['Header'] == 'Revenue'].groupby(['Ticker', 'Statement', 'Header'])[
        'Amount'].pct_change().fillna(0)

    _df_index = stmt[stmt['Header'] == 'Revenue'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df > 0, 1, 0), index=_df_index)

    return res.rename('REV_G')


def eps_score(stmt):
    _df = stmt[stmt['Header'] == 'EPS Diluted'].groupby(['Ticker', 'Statement', 'Header'])[
        'Amount'].pct_change().fillna(0)

    _df_index = stmt[stmt['Header'] == 'EPS Diluted'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df > 0, 1, 0), index=_df_index)

    return res.rename('EPS_G')


def roic_score(stmt):
    _df = stmt[(stmt['Header'] == 'Net Income') & (stmt['Statement'] == 'income-statement')]['Amount'].values / \
        (stmt[(stmt['Header'] == "Total shareholders equity") & (stmt['Statement'] == 'balance-sheet-statement')]['Amount'].values +
         stmt[(stmt['Header'] == 'Long-term debt') & (stmt['Statement'] == 'balance-sheet-statement')]['Amount'].values)

    _df_index = stmt[stmt['Header'] == 'Net Income'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df >= 0.10, 1, 0), index=_df_index)

    return res.rename('ROIC')


def croic_score(stmt):
    _df = stmt[(stmt['Header'] == 'Free Cash Flow') & (stmt['Statement'] == 'cash-flow-statement')]['Amount'].values / \
        (stmt[(stmt['Header'] == "Total shareholders equity") & (stmt['Statement'] == 'balance-sheet-statement')]['Amount'].values +
         stmt[(stmt['Header'] == 'Long-term debt') & (stmt['Statement'] == 'balance-sheet-statement')]['Amount'].values)

    _df_index = stmt[stmt['Header'] == 'Net Income'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df >= 0.10, 1, 0), index=_df_index)

    return res.rename('CROIC')


def five_year_beta_score(stmt):
    beta = stmt[stmt['Header'] == 'Beta']['Amount'].values[0]

    _df_index = stmt[stmt['Header'] == 'Net Income'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(beta <= 1.0, 1, 0), index=_df_index)

    return res.rename('BETA')


def ebitda_cover_score(stmt):
    _df = stmt[(stmt['Header'] == 'EBITDA') & (stmt['Statement'] == 'income-statement')]['Amount'].values / \
        (stmt[(stmt['Header'] == "Interest Expense") &
              (stmt['Statement'] == 'income-statement')]['Amount'].values)

    _df_index = stmt[stmt['Header'] == 'Net Income'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df >= 6, 1, 0), index=_df_index)

    return res.rename('EBITDA_COVER')


def debt_cost_score(stmt):
    _df = stmt[(stmt['Header'] == 'Interest Expense') & (stmt['Statement'] == 'income-statement')]['Amount'].values / \
        (stmt[(stmt['Header'] == "Total liabilities") &
              (stmt['Statement'] == 'balance-sheet-statement')]['Amount'].values)

    _df_index = stmt[stmt['Header'] == 'Net Income'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df <= 0.05, 1, 0), index=_df_index)

    return res.rename('DEBT_COST')


def eq_buyback_score(stmt):
    _df = stmt[(stmt['Header'] == 'Weighted Average Shs Out (Dil)') & (stmt['Statement'] == 'income-statement')].groupby(['Ticker', 'Statement', 'Header'])[
        'Amount'].pct_change().fillna(0)

    _df_index = stmt[stmt['Header'] == 'Revenue'].groupby(
        ['Ticker', 'Year']).sum().index

    res = pd.Series(np.where(_df < 0, 1, 0), index=_df_index)

    return res.rename('EQ_BUYBACK')


def get_scores(ticker):
    stmt = get_financial_statements(ticker)
    res = pd.DataFrame([
        revenue_score(stmt),
        ebitda_score(stmt),
        eps_score(stmt),
        roic_score(stmt),
        croic_score(stmt),
        five_year_beta_score(stmt),
        ebitda_cover_score(stmt),
        debt_cost_score(stmt),
        eq_buyback_score(stmt)
    ])

    return res