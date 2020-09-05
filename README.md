<h1 align="center">
  <br>
  <strong>Valinvest</strong>
  <br>
  <br>
  <img src="https://imgs.xkcd.com/comics/technical_analysis_2x.png" />
</h1>

<h4 align="center">A value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts</h4>

# Welcome to Valinvest <!-- omit in toc -->
## 🔥 Important update 🔥 <!-- omit in toc -->
The Financial API used by valinvest to get financial data has been rewritten and now requires a API Key in order to make request. So, the first step now is to register on https://financialmodelingprep.com/login and get an API key. Keep it, you will need it to use valinvest ;)

## ✨tl;dr ✨ <!-- omit in toc -->
For a given stock ticker, `valinvest` calculates a score from 0 to 9. The higher the score, the better the company is according to the scoring methodology.
1. Install it
```bash
pip install valinvest
```

2. Calculate score
```python
>>> import valinvest
>>> aapl = valinvest.Fundamental('AAPL', YOUR_API_KEY)
>>> aapl.fscore()
6.8
```


## Table of contents :books: <!-- omit in toc -->

- [Introduction](#introduction)
- [Methodology description](#methodology-description)
    - [Growth](#growth)
    - [Profitability](#profitability)
    - [Debts](#debts)
    - [Market sensibility](#market-sensibility)
    - [Investment](#investment)
- [Installation](#installation)
- [Examples](#examples)
  - [Starbucks Corporation (SBUX)](#starbucks-corporation-sbux)
  - [Apple Inc. (AAPL)](#apple-inc-aapl)
- [License](#license)
- [Credits](#credits)

## Introduction

The aim of the package is to evaluate a stock according to his fundamentals by setting a score and identify buy and sells opportunies through technical indicators.

## Methodology description

The scoring methodology is based on Joseph Piotroski's study ([Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers](http://www.chicagobooth.edu/~/media/FE874EE65F624AAEBD0166B1974FD74D.pdf)). The F-Score is used to help financial investment decisions by finding the best value stocks on the market.<br>

> The Piostroski score is calculated based on 9 criteria divided into 3 groups:
> 
> #### Profitability
>
> - Return on Assets (1 point if it is positive in the current year, 0 otherwise)
> - Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise)
> - Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one, 0 otherwise)
> - Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise)
>
> #### Leverage, Liquidity and Source of Funds
>
> - Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one, 0 otherwise)
> - Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
> - Change in the number of shares (1 point if no new shares were issued during the last year)
>
> #### Operating Efficiency
>
> - Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
> - Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
> 

This software calculates an alternate version of the F-Score as follows:
#### Growth
- Net Revenue
- EBITDA
- Earnings per share (EPS)

#### Profitability
- CROIC
- ROIC

#### Debts
- EBITDA cover ratio
- Debt coverage

#### Market sensibility
- Beta

#### Investment
- Equity buyback

## Installation

> `pip install valinvest`

## Examples

### Starbucks Corporation (SBUX)

|              | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | Score |
| ------------ | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ----- |
| REV_G        |      | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1     |
| EBT_G        |      | 1    | 1    | 1    | 0    | 1    | 1    | 1    | 0    | 0    | 1    | 0.7   |
| EPS_G        |      | 1    | 1    | 1    | 0    | 1    | 0    | 1    | 1    | 1    | 0    | 0.7   |
| ROIC         | 0    | 0    | 1    | 0    | 0    | 0    | 0    | 0    | 0    | 0    | 0    | 0.1   |
| CROIC        | 1    | 1    | 1    | 1    | 1    | 0    | 1    | 1    | 1    | 1    | 1    | 0.9   |
| 5YRS_BETA    |      |      |      |      |      |      |      |      |      |      |      | 1     |
| EBITDA_COVER | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1     |
| DEBT_COST    | 0    | 0    | 0    | 0    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 0.7   |
| EQ_BUYBACK   |      | 1    | 0    | 0    | 1    | 0    | 0    | 1    | 1    | 1    | 1    | 0.6   |
| F-SCORE      |      |      |      |      |      |      |      |      |      |      |      | 6.7   |

```python
>>> import valinvest
>>> sbux = valinvest.Fundamental('SBUX')
>>> sbux.fscore()
6.7
```

### Apple Inc. (AAPL)

|              | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | Score |
| ------------ | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ----- |
| REV_G        |      | 1    | 1    | 1    | 1    | 1    | 1    | 0    | 1    | 1    | 0    | 0.8   |
| EBT_G        |      | 1    | 1    | 1    | 0    | 1    | 1    | 0    | 1    | 1    | 0    | 0.7   |
| EPS_G        |      | 1    | 1    | 1    | 0    | 0    | 1    | 0    | 1    | 1    | 0    | 0.6   |
| ROIC         | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1     |
| CROIC        | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1     |
| 5YRS_BETA    |      |      |      |      |      |      |      |      |      |      |      | 0     |
| EBITDA_COVER | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1     |
| DEBT_COST    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1     |
| EQ_BUYBACK   |      | 1    | 0    | 0    | 1    | 0    | 1    | 1    | 1    | 1    | 1    | 0.7   |
| F-SCORE      |      |      |      |      |      |      |      |      |      |      |      | 6.8   |

```python
>>> import valinvest
>>> aapl = valinvest.Fundamental('AAPL')
>>> aapl.fscore()
6.8
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/astro30/valinvest/blob/master/LICENSE) file for details

## Credits

This software uses code from several open source packages:

- [pandas](http://pandas.pydata.org)
- [numpy](http://numpy.pydata.org)
- [requests](https://requests.readthedocs.io/en/master/)
