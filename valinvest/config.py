import yaml
import pathlib

# Name of root directory containing project configuration.
CONF_ROOT = "config"

with open(pathlib.Path('.', CONF_ROOT, 'local/credentials.yml')) as credfile:
    credentials_config = yaml.safe_load(credfile)

with open(pathlib.Path('.', CONF_ROOT, 'environment.yml')) as envfile:
    environment_config = yaml.safe_load(envfile)

with open(pathlib.Path('.', CONF_ROOT, 'logging.yml')) as logfile:
    logging_config = yaml.safe_load(logfile)

# API Keys to constants
ALPHA_VANTAGE_KEY = credentials_config['alpha_vantage']['key']
FINNHUB_KEY = credentials_config['finnhub']['key']
REDDIT_CLIENT_ID = credentials_config['reddit']['client_id']
REDDIT_CLIENT_SECRET = credentials_config['reddit']['client_secret']
REDDIT_USER_AGENT = credentials_config['reddit']['user_agent']

NASDAQ_100_TICKERS = environment_config['nasdaq_100_tickers']
SP_500_TICKERS = environment_config['sp_500_tickers']
