import pandas as pd
from polygon import RESTClient

from typing import cast
from urllib3 import HTTPResponse
import json


#tickers = ['SBEV', 'MLGO', 'PRTG', 'BCTX', 'TIVC', 'AREB']

tickers = ['AREB']     # Add or remove tickers as needed

from datetime import datetime, time, timedelta

def count_vwap_crosses(polygon_client, ticker, date):
    """
    Fetches 2-minute bar data for a given ticker and date and counts VWAP crosses.

    Args:
        polygon_client: The initialized Polygon.io RESTClient.
        ticker (str): The stock ticker symbol.
        date (str): The date in 'YYYY-MM-DD' format.

    Returns:
        int: The number of times the price crossed the VWAP.
    """
    try:
        # Fetch 2-minute bar data
        aggs_data = polygon_client.list_aggs(
            ticker=ticker,
            multiplier=2,
            timespan='minute',
            from_=date,
            to=date,
            #adjusted='true',
            limit=50000 # Increased limit for potentially more bars
        )
        aggs_list = list(aggs_data)
    except Exception as e:
        print(f"Error fetching 2-minute bar data for {ticker} on {date}: {e}")
        return None # Return None on error

    if not aggs_list:
        return 0 # No data means no crosses

    cross_count = 0
    # Initialize previous close and vwap with the first bar's data
    previous_close = aggs_list[0].close
    previous_vwap = aggs_list[0].vwap

    for i in range(1, len(aggs_list)):
        current_bar = aggs_list[i]
        current_close = current_bar.close
        current_vwap = current_bar.vwap

        # Check for a cross: price goes from below VWAP to above, or vice versa
        if previous_close is not None and current_close is not None and previous_vwap is not None and current_vwap is not None:
             if (previous_close < previous_vwap and current_close > current_vwap) or \
                (previous_close > previous_vwap and current_close < current_vwap):
                cross_count += 1

        previous_close = current_close
        previous_vwap = current_vwap

    return cross_count

import pytz

def get_premarket_high_low_data(ticker, polygon_client, date_str):
    try:
        # Fetch 1-minute bar data for the entire day
        aggs_data = polygon_client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan='minute',
            from_=date_str,
            to=date_str,
            limit=50000  # Increased limit to get all bars for the day
        )
        aggs_list = list(aggs_data)

        if not aggs_list:
            print(f"No data available for {ticker} on {date_str}")
            return None

        # Find the maximum high price and its corresponding timestamp
        max_high = -1
        high_timestamp = None

        for bar in aggs_list:
            if bar.high > max_high:
                max_high = bar.high
                high_timestamp = bar.timestamp

        if high_timestamp:
            # Convert timestamp from milliseconds to seconds and then to HH:MM format
            high_datetime_utc= datetime.fromtimestamp(high_timestamp / 1000, tz=pytz.utc)
            est_timezone = pytz.timezone('America/New_York')
            est_datetime = high_datetime_utc.astimezone(est_timezone)
            return est_datetime.strftime('%H:%M')
        else:
            return None

    except Exception as e:
        print(f"Error fetching data for {ticker} on {date_str}: {e}")
        return None

import pytz
from datetime import datetime, time

def get_premarket_high_low_data(ticker, polygon_client, date_str):
    """
    Fetches the daily high price, low price, and their timestamps for a given ticker and date
    within the standard trading hours (9:30 AM to 4:00 PM EST).

    Args:
        ticker (str): The stock ticker symbol.
        polygon_client: The initialized Polygon.io RESTClient.
        date_str (str): The date in 'YYYY-MM-DD' format.

    Returns:
        tuple: A tuple containing:
            - max_high (float or None): The maximum high price for the day within trading hours.
            - high_timestamp_est (str or None): The timestamp (HH:MM EST) of the daily high within trading hours.
            - min_low (float or None): The minimum low price for the day within trading hours.
            - low_timestamp_est (str or None): The timestamp (HH:MM EST) of the daily low within trading hours.
            or (None, None, None, None) if data is not available or an error occurs.
    """
    try:
        est_timezone = pytz.timezone('America/New_York')

        # Define the start and end times in EST for the trading day
        start_datetime_est = est_timezone.localize(datetime.strptime(f"{date_str} 04:00", '%Y-%m-%d %H:%M'))
        end_datetime_est = est_timezone.localize(datetime.strptime(f"{date_str} 9:30", '%Y-%m-%d %H:%M'))

        # Convert EST datetimes to UTC timestamps (in milliseconds) for the API call
        start_timestamp_utc_ms = int(start_datetime_est.timestamp() * 1000)
        end_timestamp_utc_ms = int(end_datetime_est.timestamp() * 1000)


        # Fetch 1-minute bar data for the specified time range
        aggs_data = polygon_client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan='minute',
            from_=start_timestamp_utc_ms,
            to=end_timestamp_utc_ms,
            limit=50000  # Increased limit to get all bars for the specified range
        )
        aggs_list = list(aggs_data)

        if not aggs_list:
            print(f"No data available for {ticker} between 4:00 AM and 9:30 AM EST on {date_str}")
            return None, None, None, None

        # Find the maximum high price and its corresponding timestamp
        max_high = -1
        high_timestamp = None
        min_low = float('inf')
        low_timestamp = None

        for bar in aggs_list:
            if bar.high > max_high:
                max_high = bar.high
                high_timestamp = bar.timestamp

            if bar.low < min_low:
                min_low = bar.low
                low_timestamp = bar.timestamp

        high_timestamp_est = None
        if high_timestamp:
            high_datetime_utc = datetime.fromtimestamp(high_timestamp / 1000, tz=pytz.utc)
            high_datetime_est = high_datetime_utc.astimezone(est_timezone)
            high_timestamp_est = high_datetime_est.strftime('%H:%M')

        low_timestamp_est = None
        if low_timestamp:
            low_datetime_utc = datetime.fromtimestamp(low_timestamp / 1000, tz=pytz.utc)
            low_datetime_est = low_datetime_utc.astimezone(est_timezone)
            low_timestamp_est = low_datetime_est.strftime('%H:%M')


        return max_high, high_timestamp_est, min_low, low_timestamp_est

    except Exception as e:
        print(f"Error fetching data for {ticker} on {date_str} between 4:00 AM and 9:30 AM EST: {e}")
        return None, None, None, None
    
    import pytz
from datetime import datetime, time

def get_daily_high_low_data(ticker, polygon_client, date_str):
    """
    Fetches the daily high price, low price, and their timestamps for a given ticker and date
    within the standard trading hours (9:30 AM to 4:00 PM EST).

    Args:
        ticker (str): The stock ticker symbol.
        polygon_client: The initialized Polygon.io RESTClient.
        date_str (str): The date in 'YYYY-MM-DD' format.

    Returns:
        tuple: A tuple containing:
            - max_high (float or None): The maximum high price for the day within trading hours.
            - high_timestamp_est (str or None): The timestamp (HH:MM EST) of the daily high within trading hours.
            - min_low (float or None): The minimum low price for the day within trading hours.
            - low_timestamp_est (str or None): The timestamp (HH:MM EST) of the daily low within trading hours.
            or (None, None, None, None) if data is not available or an error occurs.
    """
    try:
        est_timezone = pytz.timezone('America/New_York')

        # Define the start and end times in EST for the trading day
        start_datetime_est = est_timezone.localize(datetime.strptime(f"{date_str} 09:30", '%Y-%m-%d %H:%M'))
        end_datetime_est = est_timezone.localize(datetime.strptime(f"{date_str} 16:00", '%Y-%m-%d %H:%M'))

        # Convert EST datetimes to UTC timestamps (in milliseconds) for the API call
        start_timestamp_utc_ms = int(start_datetime_est.timestamp() * 1000)
        end_timestamp_utc_ms = int(end_datetime_est.timestamp() * 1000)


        # Fetch 1-minute bar data for the specified time range
        aggs_data = polygon_client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan='minute',
            from_=start_timestamp_utc_ms,
            to=end_timestamp_utc_ms,
            limit=50000  # Increased limit to get all bars for the specified range
        )
        aggs_list = list(aggs_data)

        if not aggs_list:
            print(f"No data available for {ticker} between 9:30 AM and 4:00 PM EST on {date_str}")
            return None, None, None, None

        # Find the maximum high price and its corresponding timestamp
        max_high = -1
        high_timestamp = None
        min_low = float('inf')
        low_timestamp = None

        for bar in aggs_list:
            if bar.high > max_high:
                max_high = bar.high
                high_timestamp = bar.timestamp

            if bar.low < min_low:
                min_low = bar.low
                low_timestamp = bar.timestamp

        high_timestamp_est = None
        if high_timestamp:
            high_datetime_utc = datetime.fromtimestamp(high_timestamp / 1000, tz=pytz.utc)
            high_datetime_est = high_datetime_utc.astimezone(est_timezone)
            high_timestamp_est = high_datetime_est.strftime('%H:%M')

        low_timestamp_est = None
        if low_timestamp:
            low_datetime_utc = datetime.fromtimestamp(low_timestamp / 1000, tz=pytz.utc)
            low_datetime_est = low_datetime_utc.astimezone(est_timezone)
            low_timestamp_est = low_datetime_est.strftime('%H:%M')


        return max_high, high_timestamp_est, min_low, low_timestamp_est

    except Exception as e:
        print(f"Error fetching data for {ticker} on {date_str} between 9:30 AM and 4:00 PM EST: {e}")
        return None, None, None, None
    
def get_gap_up_day_stats(ticker, polygon_client):
    """
    Analyzes historical data for a given ticker to identify significant gap-ups.

    Args:
        ticker (str): The stock ticker symbol.
        polygon_client: The initialized Polygon.io RESTClient.
    Returns:
        list: A list of dictionaries, each representing a gap-up day with relevant data.
    """
    user_input_gap_up = 25
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=1095) # Fetch data for the last 3 years

    try:
        aggs_data = polygon_client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan='day',
            from_=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d'),
            adjusted='true',
            limit=10000
        )
        aggs_list = list(aggs_data)
    except Exception as e:
        print(f"Error fetching daily data for {ticker}: {e}")
        return [] # Return empty list on error

    gap_up_days = []

    for i in range(1, len(aggs_list)):
        previous_day_agg = aggs_list[i-1]
        current_day_agg = aggs_list[i]

        previous_day_close = previous_day_agg.close
        current_day_open = current_day_agg.open



        if previous_day_close is not None and current_day_open is not None:
            gap_up_percent = ((current_day_open - previous_day_close) / previous_day_close) * 100

            if gap_up_percent >= user_input_gap_up:

                current_day_high = current_day_agg.high

                date_str = datetime.fromtimestamp(current_day_agg.timestamp / 1000).strftime('%Y-%m-%d')
                current_day_high_time = get_daily_high_low_data(ticker, polygon_client, date_str)[1]
                #print('current_day_high_time:', current_day_high_time)
                current_day_close = current_day_agg.close
                current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                percent_gap_high = ((current_day_high - previous_day_close) / previous_day_close) * 100 if previous_day_close is not None else None
                closing_percent = ((current_day_close - previous_day_close) / previous_day_close) * 100 if previous_day_close is not None else None

                # Fetch Daily Ticker Summary for the specific date
                try:
                    daily_summary = polygon_client.get_daily_open_close_agg(
                        ticker=ticker,
                        date=date_str,
                        adjusted="true",
                    )
                    premarket_open = daily_summary.pre_market if daily_summary.pre_market else None
                    premarket_high = get_premarket_high_low_data(ticker, polygon_client, date_str)[0]
                    premarket_high_time = get_premarket_high_low_data(ticker, polygon_client, date_str)[1]
                    afterhours_close = daily_summary.after_hours if daily_summary.after_hours else None
                except Exception as e:
                    print(f"Error fetching daily summary for {ticker} on {date_str}: {e}")
                    premarket_open = None
                    afterhours_close = None

                # Determine if the day was a Runner or Fader
                runner_fader = "Runner" if current_day_close > current_day_open else ("Fader" if current_day_close < current_day_open else "Neutral")

                # Count VWAP crosses
                vwap_crosses = count_vwap_crosses(polygon_client, ticker, date_str)

                gap_up_days.append({
                    'date': date_str,
                    'pd close': previous_day_close,
                    'premarket open': premarket_open,
                    'premarket high' : premarket_high,
                    'premarket high time': premarket_high_time,
                    #'premarket low' : premarket_low,
                    #'premarket low time': premarket_low_time,
                    'open': current_day_open,
                    'gap up % at open': gap_up_percent,
                    'day high': current_day_high,
                    'day high time': current_day_high_time,
                    'day high %': percent_gap_high,
                    #'day low' : current_day_low,
                    #'day low time': current_day_low_time,
                    #'day low %': percent_gap_low,
                    'close price': current_day_close,
                    'closing percent': closing_percent,
                    'afterhours close': afterhours_close,
                    'VWAP Crosses': vwap_crosses,
                    'Runner/Fader': runner_fader,
                })
    #print (gap_up_days)
    return gap_up_days

def fetch_intraday_1_min(polygon_client, ticker, date_str):
    """
    Fetches intraday 1-minute bar data for a given ticker and date.

    Args:
        polygon_client: The initialized Polygon.io RESTClient.
        ticker (str): The stock ticker symbol.
        date_str (str): The date in 'YYYY-MM-DD' format.

    Returns:
        list: A list of intraday 1-minute bar aggregates, or an empty list on error.
    """
    try:
        intraday_aggs_data = polygon_client.list_aggs(
            ticker=ticker,
            multiplier=1,
            timespan='minute',
            from_=time(9,30,0),
            to=time(10,0,0),
            limit=50000
        )
        return list(intraday_aggs_data)
    except Exception as e:
        print(f"Error fetching intraday data for {ticker} on {date_str}: {e}")
        return []
    
import pdb
def analyze_intraday_first_30_mins(intraday_aggs_list, daily_high):
    """
    Analyzes intraday 1-minute bar data for the first 30 minutes of trading.

    Args:
        intraday_aggs_list (list): A list of intraday 1-minute bar aggregates.
        daily_high (float): The high price for the entire trading day.

    Returns:
        tuple: A tuple containing:
            - max_price_30min (float or None): The maximum price within the first 30 minutes.
            - max_price_30min_timestamp (str or None): The timestamp (HH:MM) of the 30-min high.
            - high_within_30min (bool): True if the daily high occurred within the first 30 minutes.
    """
    max_price_30min = None
    max_price_30min_timestamp = None
    interval_start_time = time(9, 30)
    interval_end_time_30min = time(10, 0)
    high_within_30min = False
    bars_in_30min = []

    for bar in intraday_aggs_list:

        bar_datetime = datetime.fromtimestamp(bar.timestamp / 1000)
        bar_time = bar_datetime.time()
        pdb.set_trace()
        if interval_start_time <= bar_time < interval_end_time_30min:
            print('inside the intraday-aggs-list on ' + str(bar_datetime.strftime('%Y-%m-%d')) )
            bars_in_30min.append(bar)

    if not bars_in_30min:
        return None, None, False

    # Initialize max_price_30min with the high of the first bar
    max_price_30min = bars_in_30min[0].high
    #print('max_price_30min for RELI on: ' + str(datetime.fromtimestamp(bars_in_30min[0].timestamp / 1000).strftime('%Y-%m-%d')) + ' = ' + str( max_price_30min)) #datetime.strptime(date_str, '%Y-%m-%d').date()
    max_price_30min_timestamp = datetime.fromtimestamp(bars_in_30min[0].timestamp / 1000).strftime('%H:%M')

    for bar in bars_in_30min:
        if bar.high < max_price_30min:
            #print('bar.high:', bar.high)
            max_price_30min = bar.high
            max_price_30min_timestamp = datetime.fromtimestamp(bar.timestamp / 1000).strftime('%H:%M') # Store as HH:MM string

        if bar.high == daily_high:
            high_within_30min = True


    return max_price_30min, max_price_30min_timestamp, high_within_30min

def categorize_fade(runner_fader, high_within_30min, percent_high_from_open_30min):
    """
    Categorizes a 'Fader' day based on intraday price action.

    Args:
        runner_fader (str): The 'Runner' or 'Fader' label for the day.
        high_within_30min (bool): True if the daily high occurred within the first 30 minutes.
        percent_high_from_open_30min (float or None): The percentage difference between the
                                                    30-min high and the open price.

    Returns:
        str or None: The fade category ('Straight Down Fade', 'Quick Swipe and Fade',
                     'Steady gap up and Fade'), or None if not a Fader or category cannot be determined.
    """
    fade_category = None
    if runner_fader == "Fader":
        if high_within_30min and percent_high_from_open_30min is not None:
            if percent_high_from_open_30min < 10:
                fade_category = "Straight Down Fade"
            elif 10 <= percent_high_from_open_30min < 40:
                fade_category = "Quick Swipe and Fade"
            elif 40 <= percent_high_from_open_30min < 100:
                 fade_category = "Steady gap up and Fade"
        elif not high_within_30min:
            fade_category = "Straight Down Fade"
    return fade_category

def analyze_gap_ups(ticker, polygon_client):
    """
    Analyzes historical data for a given ticker to identify significant gap-ups
    and includes premarket open and afterhours close prices, open, close,
    a 'Runner' or 'Fader' label, and VWAP cross count, and intraday high/time
    within the first 30 minutes for Faders.

    Args:
        ticker (str): The stock ticker symbol.
        polygon_client: The initialized Polygon.io RESTClient.
    Returns:
        pandas.DataFrame: A DataFrame containing gap-up information, premarket open,
                          and afterhours close prices, open, close, a 'Runner'
                          or 'Fader' label, VWAP cross count, and intraday high/time
                          within the first 30 minutes for the ticker,
                          or an empty DataFrame if no significant gap-ups are found
                          or if there's an error fetching data.
    """
    gap_up_days_data = get_gap_up_day_stats(ticker, polygon_client)

    if not gap_up_days_data:
        return pd.DataFrame()

    processed_gap_up_days = []
    for day_data in gap_up_days_data:
        date_str = day_data['date']
        #print('date_str:', date_str)
        current_day_open = day_data['open']
        daily_high = day_data['day high']
        runner_fader = day_data['Runner/Fader']

        intraday_aggs_list = fetch_intraday_1_min(polygon_client, ticker, date_str)
        #print('intraday_aggs_list:', intraday_aggs_list)

        max_price_30min, max_price_30min_timestamp, high_within_30min = analyze_intraday_first_30_mins(intraday_aggs_list, daily_high)

        # Calculate percentage difference between 30-min high and open
        percent_high_from_open_30min = None
        if max_price_30min is not None and current_day_open is not None and current_day_open != 0:
            percent_high_from_open_30min = ((max_price_30min - current_day_open) / current_day_open) * 100

        fade_category = categorize_fade(runner_fader, high_within_30min, percent_high_from_open_30min)

        day_data.update({
            #'intraday_bars': intraday_aggs_list,
            #'intraday_high_30min': max_price_30min,
            #'intraday_high_30min_time': max_price_30min_timestamp,
            #'percent_high_from_open_30min': percent_high_from_open_30min,
            #'high_within_30min': high_within_30min,
            #'fade_category': fade_category
        })
        processed_gap_up_days.append(day_data)


    df_gap_up = pd.DataFrame(processed_gap_up_days)


    return df_gap_up

# --- Main part of the script to process multiple tickers ---

# Define the list of tickers
tickers = tickers # Add or remove tickers as needed

# Initialize the Polygon client (assuming POLYGON_API_KEY is already in userdata)
from polygon import RESTClient
import config
polygon_client = RESTClient(config.polygon_api_key)

# Dictionary to store results for each ticker
all_tickers_gap_up_results = {}

# Process each ticker and store the results
for ticker in tickers:
    print(f"Analyzing gap ups for {ticker}...")
    gap_up_results = analyze_gap_ups(ticker, polygon_client)

    """gap_up_results Returns:
        pandas.DataFrame: A DataFrame containing gap-up information, premarket open,
                          and afterhours close prices, open, close, a 'Runner'
                          or 'Fader' label, VWAP cross count, and intraday high/time
                          within the first 30 minutes for the ticker,
                          or an empty DataFrame if no significant gap-ups are found
                          or if there's an error fetching data.
    """

    if not gap_up_results.empty:
        print(f"Significant gap ups for {ticker}:")
        # Format the percentage columns
        gap_up_results['gap up % at open'] = gap_up_results['gap up % at open'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '')
        gap_up_results['day high %'] = gap_up_results['day high %'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '')
        gap_up_results['closing percent'] = gap_up_results['closing percent'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '')
       # gap_up_results['percent_high_from_open_30min'] = gap_up_results['percent_high_from_open_30min'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '')


        all_tickers_gap_up_results[ticker] = gap_up_results # Store the results in the dictionary
        # Removed the InteractiveSheet creation
        # sheet = sheets.InteractiveSheet(all_tickers_gap_up_results) # Pass dictionary as keyword arguments
        # display(sheet) # Removed display of InteractiveSheet
    else:
        print(f"No significant gap ups (>= 25%) found for {ticker} in the last 3 years.")
print('all_tickers_gap_up_results:', all_tickers_gap_up_results)
# Display each DataFrame as a separate table
if all_tickers_gap_up_results:
    print("\nDisplaying results for each ticker in separate tables:")
    for ticker, results_df in all_tickers_gap_up_results.items():
        print(f"\n--- Results for {ticker} ---")
        display(results_df)
else:
    print("\nNo significant gap ups found for any of the provided tickers to display.")