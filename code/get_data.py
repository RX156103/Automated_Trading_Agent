import os
import sys
from datetime import datetime, timedelta
import re

import requests

data_path = "./dataset"
if not os.path.exists(data_path):
    os.mkdir(data_path)

### Retrieve CryptoCurrencyData Data
# Set the symbol and current date to filename
SYMBOL = sys.argv[1] # BTC/ETH/LTC
TICK = sys.argv[2] # 1h/d

date = datetime.today().strftime("%Y-%m-%d").replace('-', '')
filename = SYMBOL + '_' + TICK + '_' + date + ".csv"
file_path = os.path.join(data_path, filename)

def Download_Data():
    if os.path.isfile(file_path):
        print(file_path + " was already Downloaded!")
    else:
        print("Retrieving Data...")
        # Crpyto Data World
        # https://www.cryptodatadownload.com/data/northamerican/
        url = 'https://www.cryptodatadownload.com/cdd/Coinbase_'+SYMBOL+'USD_'+TICK+'.csv'
        raw_text = requests.get(url, verify=False).text
        raw_text = re.sub(r".+?(?=\r\nDate)", '', raw_text)[2:]

        with open(file_path, 'w') as text_file:
            text_file.write(raw_text)

    # return file_path

if __name__ == "__main__":
    Download_Data()