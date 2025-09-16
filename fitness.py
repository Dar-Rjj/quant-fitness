import os
import pandas as pd
import numpy as np

from scipy.stats import pearsonr


def fetch_data(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
    dfs, keys = [], []
    for dic in os.listdir('data'):
        if dic.endswith('.csv'):
            try:
                df = pd.read_csv(f'data/{dic}', index_col=0, parse_dates=True)
                df = df[['开盘', '收盘', '最高', '最低', '成交量', '成交额']].loc[start_date:end_date]
                df.rename(columns={'开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount'}, inplace=True)
                df['vwap'] = df['amount'] / (df['volume'] * 100)
                df.index.name = 'date'
                dfs.append(df)
                keys.append(dic[:6])
            except Exception as e:
                continue

    return pd.concat(dfs, keys=keys, names=['stock_code', 'date']).sort_index()

'''
这是一个示例, 在这里alpha是你的因子函数, 具体来说一个可执行函数,
在不同的模型中, fitness的计算过程存在不同的实现方式, 这个只作为参考,
如果你只需要数据, 直接调用fetch_data()即可
'''
def fitness(market_data, alpha):
    market_data['factor'] = market_data.groupby('stock_code').apply(lambda x: alpha(x)).reset_index(level=0, drop=True)
    market_data['future_return_6d'] = market_data.groupby('stock_code')['close'].shift(-6) / market_data['close'] - 1

    # 取所有日期
    all_dates = market_data.index.get_level_values('date').unique()
    ic_values = []

    for date in all_dates:
        daily = market_data.xs(date, level='date')
        factors = daily['factor']
        returns = daily['future_return_6d']
        # mask = factors.notna() & returns.notna()
        mask = factors.notna() & returns.notna() & np.isfinite(factors) & np.isfinite(returns)
        if mask.sum() >= 10:
            ic, _ = pearsonr(factors[mask], returns[mask])
            if not np.isnan(ic):
                ic_values.append(ic)

    return np.mean(ic_values) if ic_values else 0


if __name__ == "__main__":
    print(fetch_data(pd.Timestamp('2020-01-01'), pd.Timestamp('2024-06-01')))