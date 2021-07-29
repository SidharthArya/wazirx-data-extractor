import requests
import time
import configparser as CP
import os
from datetime import datetime
import pandas as pd
cfg = CP.ConfigParser()

cfg.read("config.cfg")

try:
    markets = cfg["data"]["markets"]
except:
    response = requests.get('https://api.wazirx.com/api/v2/tickers')
    tickers = response.json()
    markets = list(tickers.keys())
period = cfg["data"]["period"]
start = datetime.strptime(cfg["data"]["start"], "%Y-%m-%d").strftime("%s")
location = cfg["data"]["location"]
try:
    limit = cfg["data"]["limit"]
except:
    limit = None


def get_historical(market, period, limit, start):
    if limit is None:
        response = requests.get("https://x.wazirx.com/api/v2/k?market="+market+"&period="+period+"&timestamp="+start)
    else:
        response = requests.get("https://x.wazirx.com/api/v2/k?market="+market+"&period="+period+"&limit="+limit+"&timestamp="+start)
    
    output = pd.DataFrame(response.json(),columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    output["Date"] =pd.to_datetime(output["Date"],unit="s")
    output.to_csv(location+"/"+market+".csv", index=False)


# get_historical("ethinr", "1", "1", start)
try:
    os.mkdir("data")
except Exception as e:
    pass


for market in markets:
    get_historical(market,period, limit, start)
