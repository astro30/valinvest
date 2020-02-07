import yaml

with open('../config/local/credentials.yml') as credfile:
    credentials = yaml.load(credfile, Loader=yaml.BaseLoader)

ALPHA_VANTAGE_KEY = credentials.alpha_vantage.key
FINNHUB_KEY = credentials.finnhub.key