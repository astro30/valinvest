import pytest
from valinvest.fundamentals import *

aapl = get_financial_statements('AAPL')


class TestRetrieveFinancials:

    def test_input_types(self):
        # Wrong type input
        with pytest.raises(TypeError):
            get_financial_statements(12)

        # Empty string
        with pytest.raises(ValueError):
            get_financial_statements('')

        # Not Nasdaq 100 tickers
        with pytest.raises(ValueError):
            get_financial_statements('XWZ')

        # Too many inputs
        with pytest.raises(TypeError):
            get_financial_statements('AAPL', 'tt')


        # TODO Tests EBITDA
        # TODO Tests REVENUE
        # TODO Tests CROIC
        # TODO Tests ROIC
        # TODO Tests DEBT_COST
        # TODO Tests EQ_BUY_BACK
        # TODO Tests EBITDA COVER
