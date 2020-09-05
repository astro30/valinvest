import pytest
from valinvest.fundamentals import Fundamental
API_KEY = ''

aapl = Fundamental('AAPL', API_KEY)
sbux = Fundamental('SBUX', API_KEY)

reference_scores = {
    'sbux': {
        'fscore': 6.7,
        'revenue_score': 1,
        'ebitda_score': 0.7,
        'eps_score': 0.7,
        'roic_score': 0.1,
        'croic_score': 0.8,
        'beta_score': 1,
        'ebitda_cover_score': 1,
        'debt_cost_score': 0.8,
        'eq_buyback_score': 0.6
    },
    'aapl': {
        'fscore': 6.8,
        'revenue_score': 0.8,
        'ebitda_score': 0.7,
        'eps_score': 0.6,
        'roic_score': 1,
        'croic_score': 1,
        'beta_score': 0,
        'ebitda_cover_score': 1,
        'debt_cost_score': 1,
        'eq_buyback_score': 0.7
    }
}


class TestGetFinancials:

    def test_input_types(self):
        # Wrong type input
        with pytest.raises(TypeError):
            Fundamental(12, API_KEY)

        # Empty string
        with pytest.raises(ValueError):
            Fundamental('', API_KEY)

        # Not Nasdaq 100 tickers
        with pytest.raises(ValueError):
            Fundamental('FP', API_KEY)

        # Too many inputs
        with pytest.raises(TypeError):
            Fundamental('AAPL', 'tt', API_KEY)


class TestComputeFScoreSBUX:
    def test_fscore(self):
        assert sbux.fscore() == reference_scores['sbux']['fscore']

    def test_revenue_score(self):
        assert sbux.revenue_score(
        ) == reference_scores['sbux']['revenue_score']

    def test_ebitda_score(self):
        assert sbux.ebitda_score() == reference_scores['sbux']['ebitda_score']

    def test_eps_score(self):
        assert sbux.eps_score() == reference_scores['sbux']['eps_score']

    def test_croic_score(self):
        assert sbux.croic_score() == reference_scores['sbux']['croic_score']

    def test_roic_score(self):
        assert sbux.roic_score() == reference_scores['sbux']['roic_score']

    def test_debt_cost_score(self):
        assert sbux.debt_cost_score(
        ) == reference_scores['sbux']['debt_cost_score']

    def test_eq_buybacks_score(self):
        assert sbux.eq_buyback_score(
        ) == reference_scores['sbux']['eq_buyback_score']

    def test_ebitda_cover_score(self):
        assert sbux.ebitda_cover_score(
        ) == reference_scores['sbux']['ebitda_cover_score']


class TestComputeFScoreAAPL:
    def test_fscore(self):
        assert aapl.fscore() == reference_scores['aapl']['fscore']

    def test_revenue_score(self):
        assert aapl.revenue_score(
        ) == reference_scores['aapl']['revenue_score']

    def test_ebitda_score(self):
        assert aapl.ebitda_score() == reference_scores['aapl']['ebitda_score']

    def test_eps_score(self):
        assert aapl.eps_score() == reference_scores['aapl']['eps_score']

    def test_croic_score(self):
        assert aapl.croic_score() == reference_scores['aapl']['croic_score']

    def test_roic_score(self):
        assert aapl.roic_score() == reference_scores['aapl']['roic_score']

    def test_debt_cost_score(self):
        assert aapl.debt_cost_score(
        ) == reference_scores['aapl']['debt_cost_score']

    def test_eq_buybacks_score(self):
        assert aapl.eq_buyback_score(
        ) == reference_scores['aapl']['eq_buyback_score']

    def test_ebitda_cover_score(self):
        assert aapl.ebitda_cover_score(
        ) == reference_scores['aapl']['ebitda_cover_score']
