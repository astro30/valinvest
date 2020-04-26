import yaml
import pathlib

CONF_ROOT = "config"

with open(pathlib.Path('.', CONF_ROOT, 'environment.yml')) as envfile:
    environment_config = yaml.safe_load(envfile)

NASDAQ_100_TICKERS = environment_config['nasdaq_100_tickers']
SP_500_TICKERS = environment_config['sp_500_tickers']
