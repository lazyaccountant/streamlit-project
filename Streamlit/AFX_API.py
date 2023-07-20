import requests
import pandas as pd
import re

# retrieve stock data, date format: yyyy-mm-dd
def get_data(ticker, start, stop):
    url = "https://afx.kwayisi.org/chart/ngx/" + ticker
    r = requests.get(url)
    js = r.text

    bb = re.split("data:", js)[1]
    bb = bb[1:-9]
    bb = bb.split("],")

    pattern = r"[^0-9-,.]"

    bb = [re.sub(pattern, "", b) for b in bb]

    data = {
        "Date": [],
        "Price": []
    }

    for b in bb:
        data["Date"].append(b.split(",")[0])
        data["Price"].append(b.split(",")[1])
        
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df["Price"] = df["Price"].astype(float)
        
        
    df = df.loc[start:stop]
    
    return df


def get_stocks(tickers, start, stop):
    df = pd.DataFrame()
    for i in range(len(tickers)):
        pf = get_data(tickers[i], start, stop)
        pf.rename(columns = {"Price": tickers[i]}, inplace = True)
        df = pd.concat([df, pf], axis=1)
        
    return df



def highest_ngx_returns(ticker_list,top_no, start, stop):

    stock_returns = {}

    for t in ticker_list:
        stock = get_data(t, start, stop)
        returns = stock.pct_change().dropna(how="all")
        CAGR = (1+returns).prod() ** (252 / returns.count()) - 1

        stock_returns[t] = CAGR[0]
        
    stock_returns = sorted(stock_returns.items(), key=lambda x:x[1], reverse=True)
    stock_returns = dict(stock_returns)
    top_list = [stock for stock in stock_returns][:top_no]
        
    return top_list
