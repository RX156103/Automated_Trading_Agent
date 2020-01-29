import sys
import pandas as pd
import talib
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import mpl_finance as mpf

import get_data as GD

### Data Preparation
GD.Download_Data()
file_path = file_path = GD.file_path
data = pd.read_csv(file_path)
data.set_index("Date", inplace=True)
data.index = pd.to_datetime(data.index)
# data.drop(["Symbol"], axis=1, inplace=True) 
data = data.iloc[::-1] # Reverse date
# data.head()

# Technical Indicators
data['sma_short'] = talib.SMA(data['Close'].values, 7)
data['sma_long'] = talib.SMA(data['Close'].values, 14)
data['ema_short'] = talib.SMA(data['Close'].values, 3)
data['ema_long'] = talib.SMA(data['Close'].values, 5)
data['K'], data['D'] = talib.STOCH(data['High'], data['Low'], data['Close'])
data['RSI_5'] = talib.RSI(data['Close'], 5)
data['RSI_10'] = talib.RSI(data['Close'], 10)
data['Upper'], data['Middle'], data['Lower'] = talib.BBANDS(data['Close'], timeperiod=10, nbdevup=2, nbdevdn=2)
data['MACD'] = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)[0]
data['OBV'] = talib.OBV(data['Close'], data.iloc[:, -2])
data['AROON Down'], data['AROON Up'] = talib.AROON(data['High'], data['Low'], timeperiod=7)

## Sentiment Analysis
# Sentiment = pd.read_csv("./dataset/sentiment.csv")
# data['Sentiment'] = Sentiment['sentiment']

def slice_date(df, start_date=None, end_date=None):
    # Pass if start_time, end_time are not set
    if start_date == None:
        start_date = df.index[0]
    if end_date == None:
        end_date = df.index[-1]
    # Slice data into time interval
    df = df[(df.index >= start_date) & (df.index <= end_date)]
    return df

data_train = slice_date(data, "2017-01-01", "2018-12-31")
test_length = sys.argv[4] # "year", "half-year", "month", "week"
if test_length == "year":
    data_test = slice_date(data, "2019-01-01", "2019-12-31")
elif test_length == "half-year":
    data_test = slice_date(data, "2019-07-01", "2019-12-31")
elif test_length == "month":
    data_test = slice_date(data, "2019-12-01", "2019-12-31")
elif test_length == "week":
    data_test = slice_date(data, "2019-12-25", "2019-12-31")


chosen_features = ['ema_short', 'ema_long', 'K', 'D', 'RSI_5', 'RSI_10', 'Upper', 'Middle', 'Lower', 'MACD', 'OBV', 'AROON Down', 'AROON Up', 'Close']
# chosen_features = ['ema_short', 'ema_long', 'K', 'D', 'Close']
train_features = data_train[chosen_features]
train_features.fillna(0, inplace=True)
test_features = data_test[chosen_features]
test_features.fillna(0, inplace=True)
# features = data[['Sentiment', 'Close']]

def normalize(train, test):
    minmax_sc = MinMaxScaler()
    train_norm = pd.DataFrame(minmax_sc.fit_transform(train),
                              columns=train.columns,
                              index=train.index)
    test_norm = pd.DataFrame(minmax_sc.transform(test),
                             columns=test.columns,
                             index=test.index)
    return train_norm, test_norm, minmax_sc

train_norm, test_norm, sc = normalize(train_features, test_features)

if __name__ == "__main__":
    pd.plotting.register_matplotlib_converters()

    fig = plt.figure(figsize=(30, 35))
    ax1 = fig.add_axes([0.05,0.45,0.9,0.45])
    ax2 = fig.add_axes([0.05,0.30,0.9,0.15])
    ax3 = fig.add_axes([0.05,0.05,0.9,0.25])

    # a.) Candlestick chart with 2 moving average line(10days and 30days)
    Select = data_test
    Select.index = Select.index.strftime('%Y-%m-%d')
    mpf.candlestick2_ochl(ax1, Select['Open'], Select['Close'], Select['High'],
                          Select['Low'], width=0.6, colorup='r', colordown='g', alpha=0.75)

    ax1.plot(Select['sma_short'], label='MA short')
    ax1.plot(Select['sma_long'], label='MA long')
    ax1.legend()
    ax1.autoscale()
    ax1.set_ylim((Select['Close'].min()*0.9, Select['Close'].max()*1.1))

    # b.) KD line chart.
    ax2.plot(Select['K'], label='K')
    ax2.plot(Select['D'], label='D')
    ax2.legend()

    # c.) Volume bar chart.
    mpf.volume_overlay(ax3, Select['Open'], Select['Close'], Select['Volume %s' % GD.SYMBOL],
                       colorup='r', colordown='g', width=0.5, alpha=0.8)

    ax3.set_xticks(range(0, len(Select.index), 20))
    ax3.set_xticklabels(Select.index[::20])

    fig.savefig("./fig/%s_charts.png" % GD.SYMBOL)
    plt.clf()
    plt.close()
    print(data_train.shape)
    print(data_test.shape)
    print(train_norm.shape)
    print(test_norm.shape)
