<h1 align="center">
  <br>
  <strong>Valinvest</strong>
  <br>
  <br>
  <img src="https://imgs.xkcd.com/comics/technical_analysis_2x.png" />
</h1>

<h4 align="center">A value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts</h4>

# Welcome to Valinvest
> NB: This is still in early development.

## Table of contents :books:
- [Introduction](#introduction)
- [Installation](#installation)
- [Examples](#examples)
- [License](#license)
- [Credits](#credits)

## Introduction
The aim of the package is to evaluate a stock according to his fundamentals by setting a score and identify buy and sells opportunies through technical indicators.

## Methodology description
The scoring methodology is based on Joseph Piotroski's study ([Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers](http://www.chicagobooth.edu/~/media/FE874EE65F624AAEBD0166B1974FD74D.pdf)). The F-Score is used to help financial investment decisions by finding the best value stocks on the market.<br>

The score is calculated based on 9 criteria divided into 3 groups:
#### Profitability
* Return on Assets (1 point if it is positive in the current year, 0 otherwise)
* Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise)
* Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one, 0 otherwise)
* Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise)
#### Leverage, Liquidity and Source of Funds
* Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one, 0 otherwise)
* Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
* Change in the number of shares (1 point if no new shares were issued during the last year)
#### Operating Efficiency
* Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
* Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)

This software calculates an alternate version of the F-Score as follows:

## Installation
`pip install valinvest`

## Examples
> Exemple Excel de SBUX

> Exemple Excel de AAPL

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/astro30/valinvest/blob/master/LICENSE) file for details

## Credits
This software uses code from several open source packages:
- [pandas](http://pandas.pydata.org)
- [numpy](http://numpy.pydata.org)
- [requests](https://requests.readthedocs.io/en/master/)
- [alpha_vantage](https://github.com/RomelTorres/alpha_vantage)

