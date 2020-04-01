import requests
import pandas as pd
import io
import re
import numpy as np
from .config import SP_500_TICKERS, NASDAQ_100_TICKERS

STATEMENT_API_URL = "https://financialmodelingprep.com/api/v3/financials/{statement}/{ticker}"
BETA_API_URL = "https://financialmodelingprep.com/api/v3/company/profile/{ticker}"
INCOME_STATEMENT = "income-statement"
BALANCE_STATEMENT = "balance-sheet-statement"
CASH_FLOW_STATEMENT = "cash-flow-statement"


class Fundamental:
    def __init__(self, ticker):
        self.statement_strings = [
            INCOME_STATEMENT,
            BALANCE_STATEMENT,
            CASH_FLOW_STATEMENT,
        ]

        # Sanity check on tickers
        if not isinstance(ticker, str):
            raise TypeError("Ticker should be a string.")

        self.ticker = ticker.upper()
        if self.ticker not in NASDAQ_100_TICKERS and self.ticker not in SP_500_TICKERS:
            raise ValueError(
                "Ticker should be a NASDAQ 100 ticker or SP 500 ticker")

        self.statements = self._get_financial_statements()

    def _get_financial_statement(self, statement):
        url = STATEMENT_API_URL.format(
            statement=statement,
            ticker=self.ticker)

        res = requests.get(url).json()

        df = pd.json_normalize(res["financials"])

        df["ticker"] = self.ticker
        df["statement"] = statement
        df["year"] = pd.to_datetime(df["date"]).dt.year
        df.columns = [column.replace(' ', '_').lower()
                      for column in df.columns]
        del df["date"]

        df.set_index(["ticker", "statement", "year"], inplace=True)

        financials_series = (df.stack()
                             .replace('', np.nan)
                             .astype(np.float32))

        financials_series.rename('amount', inplace=True)

        financials_series.index.set_names(
            ['ticker', 'statement', 'year', 'header'], inplace=True)

        result = financials_series.reorder_levels(
            ['ticker', 'statement', 'header', 'year'])

        return result.sort_index(level=3).reset_index()

    def _get_financial_statements(self):
        res = pd.DataFrame(
            [], columns=['ticker', 'statement', 'header', 'year', 'amount'])
        for statement in self.statement_strings:
            res = pd.concat([res, self._get_financial_statement(statement)])

        res.loc[-1] = [self.ticker, "beta", "beta",
                       res["year"].max(), self.beta]

        dates = pd.DataFrame(range(2009, 2020), columns=['year'])
        dates['key'] = 1
        headers_index = (res.groupby(['ticker', 'statement', 'header'])
                            .size()
                            .reset_index()[['ticker', 'statement', 'header']])
        headers_index['key'] = 1

        cartesian_step = pd.merge(dates, headers_index, on='key')
        del cartesian_step['key']

        res = pd.merge(cartesian_step, res, on=[
                       'year', 'ticker', 'statement', 'header'], how='left')

        res['amount'].fillna(0, inplace=True)

        return res.sort_values(by=["ticker", "statement", "header", "year"]).reset_index(drop=True)

    def _metric_growth(self, header, name):
        if header not in self.statements["header"].values:
            raise ValueError(
                "Requested Company does not have {header} available.".format(
                    header)
            )

        _header_df = self.statements[self.statements["header"] == str(
            header)][["year", "amount"]].copy()
        _header_df.set_index("year", inplace=True)
        _header_df.sort_index(inplace=True)
        _header = _header_df.squeeze()

        _df = _header.pct_change().fillna(0)

        res = pd.Series(np.where(_df > 0, 1, 0), index=_df.index)

        return res.rename(name)

    @property
    def beta(self):
        url = BETA_API_URL.format(ticker=self.ticker)
        res = requests.get(url).json()

        beta = float("inf")
        if res["profile"]["beta"]:
            beta = float(res["profile"]["beta"])

        return beta

    @property
    def eps_growth(self):
        return self._metric_growth("eps_diluted", "eps_g")

    @property
    def revenue_growth(self):
        return self._metric_growth("revenue", "rev_g")

    @property
    def ebitda_growth(self):
        return self._metric_growth("ebitda", "ebt_g")

    @property
    def roic_growth(self):
        stmt = self.statements

        net_income = stmt[
            (stmt["header"] == "net_income")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        total_shareholders_equity = stmt[
            (stmt["header"] == "total_shareholders_equity")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        long_term_debt = stmt[
            (stmt["header"] == "long-term_debt")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        length_array = len(net_income)
        value_array = np.array([float('inf')] * length_array)

        np.divide(net_income,
                  (total_shareholders_equity + long_term_debt),
                  out=value_array,
                  where=total_shareholders_equity + long_term_debt != 0)

        index_array = (
            stmt[stmt["header"] == "net_income"].groupby(
                ["ticker", "year"]).sum().index
        )

        res = pd.Series(np.where(value_array >= 0.10, 1, 0), index=index_array)

        return res.rename("roic")

    @property
    def croic_growth(self):
        stmt = self.statements

        free_cash_flow = stmt[
            (stmt["header"] == "free_cash_flow")
            & (stmt["statement"] == "cash-flow-statement")
        ]["amount"].values

        total_shareholders_equity = stmt[
            (stmt["header"] == "total_shareholders_equity")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        long_term_debt = stmt[
            (stmt["header"] == "long-term_debt")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        length_array = len(free_cash_flow)
        value_array = np.array([float('inf')] * length_array)

        np.divide(free_cash_flow,
                  (total_shareholders_equity + long_term_debt),
                  out=value_array,
                  where=total_shareholders_equity + long_term_debt != 0)

        index_array = (
            stmt[stmt["header"] == "net_income"].groupby(
                ["ticker", "year"]).sum().index
        )

        res = pd.Series(np.where(value_array >= 0.10, 1, 0), index=index_array)

        return res.rename("croic")

    @property
    def ebitda_cover_growth(self):
        stmt = self.statements

        interest_expense = stmt[
            (stmt["header"] == "interest_expense")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        ebitda = stmt[
            (stmt["header"] == "ebitda")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        length_array = len(interest_expense)
        value_array = np.array([float('inf')] * length_array)

        np.divide(ebitda,
                  interest_expense,
                  out=value_array,
                  where=interest_expense != 0)

        index_array = (
            stmt[stmt["header"] == "net_income"].groupby(
                ["ticker", "year"]).sum().index
        )

        res = pd.Series(np.where(value_array >= 6, 1, 0), index=index_array)

        return res.rename("croic")

    @property
    def eq_buyback_growth(self):
        _header_df = self.statements[self.statements["header"] == "weighted_average_shs_out_(dil)"][[
            "year", "amount"]].copy()
        _header_df.set_index("year", inplace=True)
        _header_df.sort_index(inplace=True)
        _header = _header_df.squeeze()

        _df = _header.pct_change().fillna(0)

        res = pd.Series(np.where(_df < 0, 1, 0), index=_df.index)

        return res.rename("eq_buyback")

    @property
    def debt_cost_growth(self):
        stmt = self.statements

        interest_expense = stmt[
            (stmt["header"] == "interest_expense")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        total_debt = stmt[
            (stmt["header"] == "total_debt")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        length_array = len(interest_expense)
        value_array = np.array([float('0')] * length_array)

        np.divide(interest_expense,
                  total_debt,
                  out=value_array,
                  where=total_debt != 0)

        index_array = (
            stmt[stmt["header"] == "net_income"].groupby(
                ["ticker", "year"]).sum().index
        )

        res = pd.Series(np.where(value_array < 0.05, 1, 0), index=index_array)

        return res.rename("debt_cost")

    def _score(self, property, years=10):
        if not isinstance(years, int):
            raise TypeError("'years' should be an integer")
        if years > 10 or years <= 0:
            raise ValueError("'years' should be between 0 and 10")

        return property[-years:].sum() / years

    def eps_score(self, years=10):
        return self._score(self.eps_growth, years)

    def revenue_score(self, years=10):
        return self._score(self.revenue_growth, years)

    def ebitda_score(self, years=10):
        return self._score(self.ebitda_growth, years)

    def roic_score(self, years=10):
        return self._score(self.roic_growth, years)

    def croic_score(self, years=10):
        return self._score(self.croic_growth, years)

    def debt_cost_score(self, years=10):
        return self._score(self.debt_cost_growth, years)

    def eq_buyback_score(self, years=10):
        return self._score(self.eq_buyback_growth, years)

    def ebitda_cover_score(self, years=10):
        return self._score(self.ebitda_cover_growth, years)

    def beta_score(self):
        return 1 if self.beta <= 1.0 else 0

    def fscore(self, years=10):
        return round(
            self.ebitda_score(years) +
            self.revenue_score(years) +
            self.eps_score(years) +
            self.beta_score() +
            self.ebitda_cover_score(years) +
            self.debt_cost_score(years) +
            self.eq_buyback_score(years) +
            self.roic_score(years) +
            self.croic_score(years), 2)
