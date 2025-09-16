import akshare as ak
import pandas as pd
import time
from tqdm import tqdm


def get_stocks():
    stocks = pd.read_csv('csi300.txt', header=None)[0]
    stocks = pd.Series([s[2:8] for s in stocks]).unique().tolist()
    return stocks

def get_data():
    stocks = get_stocks()
    for stock in tqdm(stocks, desc="Downloading stock data"):
        try:
            df = ak.stock_zh_a_hist(symbol=stock, period='daily', start_date='20100101', end_date='20500101', adjust="qfq")
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.set_index('日期')
            df.to_csv(f'data/{stock}.csv')
        except Exception as e:
            print(f"Error downloading data for {stock}: {e}")

        time.sleep(2)

if __name__ == "__main__":
    get_data()