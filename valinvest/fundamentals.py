import requests
import pandas as pd
import io
import re
import numpy as np
from .config import SP_500_TICKERS, NASDAQ_100_TICKERS

STATEMENT_API_URL = "https://financialmodelingprep.com/api/v3/financials/{statement}/{ticker}?apikey={apikey}"
BETA_API_URL = "https://financialmodelingprep.com/api/v3/company/profile/{ticker}?apikey={apikey}"
INCOME_STATEMENT = "income-statement"
BALANCE_STATEMENT = "balance-sheet-statement"
CASH_FLOW_STATEMENT = "cash-flow-statement"


class Fundamental:
    """A Fundamental object contains fundamental financial data of a given ticker,
    methods including computation of the custom F-Score.

    Parameters
    ----------
    ticker : str
        symbol of the company to analyse

    api_key : str
        Financial Modeling Prep API Key (get yours at https://financialmodelingprep.com/login)

    Raises
    ------
    TypeError
        raised when ticker is not a string
    ValueError
        raised when ticker is not listed on SP500 or NASDAQ100 markets.
    """

    def __init__(self, ticker, apikey):
        self.statement_strings = [
            INCOME_STATEMENT,
            BALANCE_STATEMENT,
            CASH_FLOW_STATEMENT,
        ]

        # Sanity check on tickers
        if not isinstance(ticker, str):
            raise TypeError("Ticker should be a string.")

        if not isinstance(apikey, str):
            raise TypeError("API KEY should be a string.")

        self.ticker = ticker.upper()
        self.apikey = apikey

        # Checks if ticker in SP500 or NASDAQ
        if self.ticker not in NASDAQ_100_TICKERS and self.ticker not in SP_500_TICKERS:
            raise ValueError(
                "Ticker should be a NASDAQ 100 ticker or SP 500 ticker")

        self.statements = self._get_financial_statements()

    def _get_financial_statement(self, statement):
        """ Get financial statement from Financial Modeling Prep API.
        This method can retrieve the three key financial reports, ie balance sheet, cash flow and income statements.

        Parameters
        ----------
        statement : str
            financial report to be retrieved. Should be either "balance-sheet-statement", "cash-flow-statement" or "income-statement"

        Returns
        -------
        pandas.DataFrame
            DataFrame-shaped requested financial report.
        """
        url = STATEMENT_API_URL.format(
            statement=statement,
            ticker=self.ticker,
            apikey=self.apikey)

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
        """Merge the three financials statements in one DataFrame.

        Returns
        -------
        pandas.DataFrame
            All three financial reports in a DataFrame format.
        """
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
        """Returns if the obversed financial statement 'header' value is growing from one year to another.
        Compute growth (1 if increase else 0)

        Parameters
        ----------
        header : str
            Label of the financial statement header. Ex: EBITDA, Total liabilities, interest expense, etc.
        name : str
            Name of the metric

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if growth between year (Y) and year before (Y-1). First year is defaulted to 0.

        Raises
        ------
        ValueError
            Raised if header is not in the data.
        """
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
        """Returns beta (volatility of the security vs market)

        Returns
        -------
        float
            Beta
        """
        url = BETA_API_URL.format(ticker=self.ticker, apikey=self.apikey)
        res = requests.get(url).json()

        beta = float("inf")
        if res["profile"]["beta"]:
            beta = float(res["profile"]["beta"])

        return beta

    @property
    def eps_growth(self):
        """Returns series of year on year growth of earnings per share.

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if growth between year (Y) and year before (Y-1). First year is defaulted to 0.
        """
        return self._metric_growth("eps_diluted", "eps_g")

    @property
    def revenue_growth(self):
        """Returns series of year on year growth of revenue.

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if growth between year (Y) and year before (Y-1). First year is defaulted to 0.
        """
        return self._metric_growth("revenue", "rev_g")

    @property
    def ebitda_growth(self):
        """Returns series of year on year growth of ebitda.

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if growth between year (Y) and year before (Y-1). First year is defaulted to 0.
        """
        return self._metric_growth("ebitda", "ebt_g")

    @property
    def roic_growth(self):
        """Returns series of yearly ROIC (return on invested capital).
        ROIC = NOPLAT / Invested Capital
        Invested Capital = Debt + Equity
        NOPLAT = net operating profit less adjusted taxes

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if ROIC > 10%.
        """
        stmt = self.statements

        operating_income = stmt[
            (stmt["header"] == "operating_income")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        operating_expenses = stmt[
            (stmt["header"] == "operating_expenses")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        operating_profit = operating_income - operating_expenses

        income_tax_expense = stmt[
            (stmt["header"] == "income_tax_expense")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        earnings_before_tax = stmt[
            (stmt["header"] == "earnings_before_tax")
            & (stmt["statement"] == "income-statement")
        ]["amount"].values

        tax_rate_length_array = len(operating_profit)
        tax_rate = np.array([float('1')] * tax_rate_length_array)

        np.divide(income_tax_expense,
                  earnings_before_tax,
                  out=tax_rate,
                  where=earnings_before_tax != 0)

        total_shareholders_equity = stmt[
            (stmt["header"] == "total_shareholders_equity")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        total_debt = stmt[
            (stmt["header"] == "total_debt")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        length_array = len(operating_profit)
        value_array = np.array([float('0')] * length_array)

        np.divide(operating_profit * (1 - tax_rate),
                  (total_shareholders_equity + total_debt),
                  out=value_array,
                  where=total_shareholders_equity + total_debt != 0)

        index_array = (
            stmt[stmt["header"] == "net_income"].groupby(
                ["ticker", "year"]).sum().index
        )

        res = pd.Series(np.where(value_array > 0.10, 1, 0), index=index_array)

        return res.rename("roic")

    @property
    def croic_growth(self):
        """Returns series of yearly CROIC (cash return on invested capital).
        CROIC = Free Cash Flow / Invested Capital
        Invested Capital = Debt + Equity

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if CROIC > 10%.
        """
        stmt = self.statements

        free_cash_flow = stmt[
            (stmt["header"] == "free_cash_flow")
            & (stmt["statement"] == "cash-flow-statement")
        ]["amount"].values

        total_shareholders_equity = stmt[
            (stmt["header"] == "total_shareholders_equity")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        total_debt = stmt[
            (stmt["header"] == "total_debt")
            & (stmt["statement"] == "balance-sheet-statement")
        ]["amount"].values

        length_array = len(free_cash_flow)
        value_array = np.array([float('0')] * length_array)

        np.divide(free_cash_flow,
                  (total_shareholders_equity + total_debt),
                  out=value_array,
                  where=total_shareholders_equity + total_debt != 0)

        index_array = (
            stmt[stmt["header"] == "net_income"].groupby(
                ["ticker", "year"]).sum().index
        )

        res = pd.Series(np.where(value_array > 0.10, 1, 0), index=index_array)

        return res.rename("croic")

    @property
    def ebitda_cover_growth(self):
        """Returns series of yearly interest coverage by EBITDA ratio. Good if EBITDA > 6 * interest

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if coverage > 6.
        """
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

        res = pd.Series(np.where(value_array > 6, 1, 0), index=index_array)

        return res.rename("ebitda_cover")

    @property
    def eq_buyback_growth(self):
        """Returns year on year outstanding shares decrease. 
        If outstanding shares decrease, we suppose that the company is doing share buybacks, 
        which increase the EPS.

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if number of shares decreased.
        """
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
        """Returns cost of debt on a yearly basis, i.e. interest expense over total debt.

        Returns
        -------
        pandas.Series
            Serie of 0 and 1. 1 if cost of debt < 0.05.
        """
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
        """Returns sum of Series created by xxx_growth properties on a timeframe defaulted to 10 years.

        Parameters
        ----------
        property : differents xxx_growth properties of this object
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            Score for the given property on the given timeframe.

        Raises
        ------
        TypeError
            Raised if years is not an int
        ValueError
            Raised if years is not in ]0, 10] range.
        """
        if not isinstance(years, int):
            raise TypeError("'years' should be an integer")
        if years > 10 or years <= 0:
            raise ValueError("'years' should be between 0 and 10")

        return property[-years:].sum() / years

    def eps_score(self, years=10):
        """Returns EPS score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            EPS Score
        """
        return self._score(self.eps_growth, years)

    def revenue_score(self, years=10):
        """Returns revenue score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            Revenue score
        """
        return self._score(self.revenue_growth, years)

    def ebitda_score(self, years=10):
        """Returns EBITDA score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            EBITDA score
        """
        return self._score(self.ebitda_growth, years)

    def roic_score(self, years=10):
        """Returns ROIC score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            ROIC score
        """
        return self._score(self.roic_growth, years)

    def croic_score(self, years=10):
        """Returns CROIC score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            CROIC score
        """
        return self._score(self.croic_growth, years)

    def debt_cost_score(self, years=10):
        """Returns debt cost score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            Debt cost score
        """
        return self._score(self.debt_cost_growth, years)

    def eq_buyback_score(self, years=10):
        """Returns equity buyback score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            Equity buybacks score
        """
        return self._score(self.eq_buyback_growth, years)

    def ebitda_cover_score(self, years=10):
        """Returns EBITDA cover score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            EBITDA cover score
        """
        return self._score(self.ebitda_cover_growth, years)

    def beta_score(self):
        """Returns Beta score

        Returns
        -------
        float
            Beta score
        """
        return 1 if self.beta <= 1.0 else 0

    def fscore(self, years=10):
        """Returns the sum of all scores, also known as custom F-Score

        Parameters
        ----------
        years : int, optional
            timeframe, by default 10 years

        Returns
        -------
        float
            F score
        """
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
