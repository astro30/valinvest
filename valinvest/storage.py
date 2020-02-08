import sqlalchemy
import sqlite3
from .config import DATABASE_NAME, DATABASE_TYPE

def initdb():
    engine = sqlalchemy.create_engine('sqlite:///data/storage.db')
    metadata = sqlalchemy.MetaData()
    financials = sqlalchemy.Table('financials', metadata,
                                    sqlalchemy.Column(
                                        'Ticker', sqlalchemy.String(5), primary_key=True),
                                    sqlalchemy.Column(
                                        'Report_Type', sqlalchemy.String(5), primary_key=True),
                                    sqlalchemy.Column(
                                        'Header', sqlalchemy.String(100), primary_key=True),
                                    sqlalchemy.Column(
                                        'Year', sqlalchemy.Integer(), primary_key=True),
                                    sqlalchemy.Column(
                                        'Amount', sqlalchemy.Numeric(15, 2), nullable=False)
                                    )
    technicals = sqlalchemy.Table('technicals', metadata,
                                    sqlalchemy.Column(
                                        'Ticker', sqlalchemy.String(5), primary_key=True),
                                    sqlalchemy.Column(
                                        'Date', sqlalchemy.Date(), primary_key=True),
                                    sqlalchemy.Column(
                                        'Open', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'High', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'Low', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'Close', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'RSI_10', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'RSI_250', sqlalchemy.Numeric(15, 5), nullable=False),  
                                    sqlalchemy.Column(
                                        'MACD_Signal', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'MACD', sqlalchemy.Numeric(15, 5), nullable=False),
                                    sqlalchemy.Column(
                                        'MACD_Hist', sqlalchemy.Numeric(15, 5), nullable=False)
    )
    metadata.create_all(engine, checkfirst=True)


