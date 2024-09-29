# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 11:02:49 2024
Trader_bot__R4 failure:
    R4+ and then fail.. then short the stock and see what happens.
@author: Shantanu R Nakhate 
Contact: fastlanecapital40@gmail.com
"""

import pandas as pd

# Defines
MIN_TURNOVER = 1000000 # minimum amount of Rs turnover in a stock in a single day.
FIXED_GAIN = 1.1 # Gains where you want to book profits after selling.
# Load the data
minute_data_path = r'D:\intraday\Data\IntradayData\OPTIEMUS_5min.csv' # path to 5min OHLC data file.
ohlc_data = pd.read_csv(minute_data_path)
camarilla_data_path = r'D:\intraday\Data\IntradayData\camarillaDataFile.csv' # path to 15min time frame camarilla pivots, 1 day OHLC data file
camarilla_data = pd.read_csv(camarilla_data_path)

# Ensure datetime columns are in the correct format
ohlc_data['datetime'] = pd.to_datetime(ohlc_data['datetime'], format='%Y-%m-%d %H:%M:%S')
camarilla_data['datetime'] = pd.to_datetime(camarilla_data['datetime'], format='%d-%m-%Y %H:%M')

# Function to check trade execution for a given day
def check_trade_execution_for_day(day_data, camarilla_row):
    trades = []
    stop_loss = camarilla_row['R4'] * 1.01
    for i in range(2, len(day_data)):
        prev_row = day_data.iloc[i-1] 
        row = day_data.iloc[i]
        close_value = camarilla_row['close']
        if prev_row['high'] > camarilla_row['R4'] and row['low'] < camarilla_row['R4'] * 0.999:
            sell_price = row['high'] - ((row['high'] - row['low']) / 2)
            position_size = 1000 / sell_price
            fixedGainPrice = sell_price *(1- (FIXED_GAIN/100))
            if position_size <= row['volume'] and camarilla_row['dayVolume']*camarilla_row['close']>MIN_TURNOVER:
                remaining_data = day_data.iloc[i+1:]
                max_gain = ((sell_price - remaining_data['low'].min()) / sell_price) * 100 # gains that happen after holding trade to the lowest value for the day after trade entry.
                close_gain = ((sell_price - close_value) / sell_price) * 100 # gains that happen after holding trade to the close point of the day.
                stop_loss_hit = remaining_data[remaining_data['high'] > stop_loss] # losses that happen due to stop loss trigger.
                fixed_gains_hit = remaining_data[remaining_data['low'] < fixedGainPrice]
                if not stop_loss_hit.empty:
                    stop_loss_price = stop_loss #stop_loss_hit.iloc[0]['high']
                    stop_loss_gain = ((sell_price - stop_loss_price) / sell_price) * 100
                else:
                    stop_loss_gain = None
                    
                if not fixed_gains_hit.empty:
                   fixed_gain = FIXED_GAIN
                else:
                    if not stop_loss_hit.empty:
                        fixed_gain = stop_loss_gain
                    else:
                        fixed_gain = close_gain
              
                trades.append({
                    'Datetime': row['datetime'],
                    'Sell Price': sell_price,
                    'Lowest Value': remaining_data['low'].min(),
                    'Close Value': close_value,
                    'Max Gains': max_gain,
                    'Close Price Gains': close_gain,
                    'Stop Loss Gains': stop_loss_gain,
                    'FixedGains':fixed_gain,
                    'FixedGainPrice':fixedGainPrice,
                    'R4': camarilla_row['R4'],
                    'S4': camarilla_row['S4'],
                    'Open': camarilla_row['open'],
                    'High': camarilla_row['high'],
                    'Low': camarilla_row['low'],
                    'Close': camarilla_row['close'],
                    'dayVolume':camarilla_row['dayVolume'],
                })
    return trades

# Process each date in the Camarilla data
all_trades = []
for index, camarilla_row in camarilla_data.iterrows():
    date = camarilla_row['datetime'].date()
    day_data = ohlc_data[ohlc_data['datetime'].dt.date == date]
    
    # Debugging: Print the date and number of rows in day_data
    print(f"Processing date: {date}, Number of rows in day_data: {len(day_data)}")
    
    trades = check_trade_execution_for_day(day_data, camarilla_row)
    all_trades.extend(trades)

# Convert the results to a DataFrame
output = pd.DataFrame(all_trades)

# Save the output to a CSV file
output.to_csv(r'D:\intraday\Data\IntradayData\trade_results.csv', index=False)

print(output)
