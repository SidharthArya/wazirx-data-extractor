import requests
import time
import configparser as CP
import os
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
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
    out = []
    if Path(location+"/"+market+".csv"):
        output = pd.read_csv(location+"/"+market+".csv")
        out.append(output)
        try:
            start = datetime.strptime( np.array(output.tail(1)["Date"])[0], "%Y-%m-%d %H:%M:%S").strftime("%s")
        except:
            output.drop_duplicates().to_csv(location+"/"+market+".csv",index=False)
            return
    if limit is None:
        start = int(start)
        limit = 2000
        times =int(time.strftime("%s"))
        while start < times:
            response = requests.get("https://x.wazirx.com/api/v2/k?market="+market+"&limit="+str(limit)+"&period="+period+"&timestamp="+str(start))
            output = pd.DataFrame(response.json(),columns=["Date", "Open", "High", "Low", "Close", "Volume"])
            output["Date"] =pd.to_datetime(output["Date"],unit="s")
            out.append(output)
            start += 2000*int(period)*60
            if times - start < 2000:
                limit = times-start
            print(market, ": ", start)
            # print(out, out[0].shape)
            # time.sleep(10)
        output = pd.concat(out)
    elif int(limit) > 2000:
        limit = int(limit)
        start = int(start)
        out = []
        while start < int(time.strftime("%s")) and limit > 0:
            response = requests.get("https://x.wazirx.com/api/v2/k?market="+market+"&limit=2000"+"&period="+period+"&timestamp="+str(start))
            output = pd.DataFrame(response.json(),columns=["Date", "Open", "High", "Low", "Close", "Volume"])
            output["Date"] =pd.to_datetime(output["Date"],unit="s")
            out.append(output)
            if limit > 2000:
                start += 2000*int(period)*60
                limit -= 2000
            else:
                start += 2000*int(period)*60
                limit=0
            print(market, ": ", start)
            # print(out, out[0].shape)
            # time.sleep(10)
        output = pd.concat(out)
        
    else:
        response = requests.get("https://x.wazirx.com/api/v2/k?market="+market+"&period="+period+"&limit="+limit+"&timestamp="+start)
        output = pd.DataFrame(response.json(),columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        output["Date"] =pd.to_datetime(output["Date"],unit="s")
        print(market, ": ", start)
    output.drop_duplicates(inplace=True)
    output.to_csv(location+"/"+market+".csv", index=False)


# get_historical("ethinr", "1", "1", start)
try:
    os.mkdir("data")
except Exception as e:
    pass


for market in markets:
    get_historical(market,period, limit, start)
