import requests
import pandas as pd
import datetime
from pytz import timezone
import requests_cache

maximum_candle_limit = {"minute" : 60,
                         "3minute" : 100,
                         "5minute" : 100,
                          "10minute" : 100,
                          "15minute" : 200,
                          "30minute" : 200,
                          "60minute" : 400,
                          "day" : 2000
                        }

maximum_time_candle_call = {"minute" : 1,
                         "3minute" : 1,
                         "5minute" : 1,
                          "10minute" : 1,
                          "15minute" : 1,
                          "30minute" : 1,
                          "60minute" : 2,
                          "day" : 0
                        }
higher_time_frame_data = {"minute" : "day",
                         "3minute" : "day",
                         "5minute" : "day",
                          "10minute" : "day",
                          "15minute" : "day",
                          "30minute" : "week",
                          "60minute" : "week",
                          "day" : "month"
                        }
timeout = 30
kite_authorization_df = pd.read_csv("https://docs.google.com/spreadsheets/d/1EcGGvmEATua3T_t4UskqiDeYRqJcqw-JMHeT_WE51NI/export?gid=0&format=csv")
kite_authorization = kite_authorization_df['Unnamed: 7'][0]
# kite_authorization = "enctoken WzAdBY9BLRlPbQ8SkNMNvdcOnDL6FrIaaSGcB7vCkY6Mt8lhT8MEYJLlCs/uATxrGe0rM Ut09pJkGjAjLa vmpic/jc4MfpFKe07oUyAhllKuCjSa2alA=="
print(kite_authorization)

def string_Formatting(urls,params):
  formatted_urls = urls.format(**params)
  return formatted_urls

def get_candle_data(session,url):
    session.cookies.clear()
    headers_authorization = kite_authorization
    headers = {
        "authorization": headers_authorization,
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    proxies={"http": "http://111.233.225.166:1234"}
    response = session.get(url=url,
                            proxies=proxies,
                            headers=headers,
                            timeout = timeout
                          )
    response.raise_for_status()
    data = response.json()
    candles = data["data"]["candles"]
    candles =  pd.DataFrame(candles)

    if(len(candles)):
      candles.columns = ["Datetime", "Open", "High", "Low", "Close", "Volume","temp"]
      candles.drop(["temp"], axis=1,inplace=True)
      candles['Year'] = pd.to_datetime(candles["Datetime"]).dt.strftime('%Y').astype(int)
      candles['Month'] = pd.to_datetime(candles["Datetime"]).dt.strftime('%m').astype(int)
      candles['Day'] = pd.to_datetime(candles["Datetime"]).dt.strftime('%d').astype(int)
      candles['Hour'] = pd.to_datetime(candles["Datetime"]).dt.strftime('%H').astype(int)
      candles['Minute'] = pd.to_datetime(candles["Datetime"]).dt.strftime('%M').astype(int)
      candles['Second'] = pd.to_datetime(candles["Datetime"]).dt.strftime('%S').astype(int)
      candles['Week'] = pd.to_datetime(candles["Datetime"]).dt.isocalendar().week
      candles["Datetime"] = pd.to_datetime(candles["Datetime"]).dt.strftime('%d-%m-%Y %H:%M:%S')
      candles.set_index("Datetime",inplace = True)
    return candles

def get_kite_url(session,rows,timeFrame,is_history_starting_from=False,is_add_indicator=True,number_of_time_called=0):
  stock_name = rows['STOCK NAME']
  index_name = rows['INDEX NAME']
  stock_instrument_token = rows['INSTRUMENT_TOKEN']
  fno = rows['FNO']
  print(stock_name,index_name,stock_instrument_token,fno,number_of_time_called)
  candles = []
  n = maximum_candle_limit[timeFrame]
  url_dates = []

  if(is_history_starting_from):
    current_date = datetime.datetime.now(timezone("Asia/Kolkata"))
    current_date = datetime.datetime(current_date.year,current_date.month,current_date.day)
    start_date = datetime.datetime(2000,1,1)

    while(start_date<current_date):
      start_date_string = start_date.strftime("%Y-%m-%d")
      start_date = start_date + datetime.timedelta(days=n)
      end_date_string = start_date.strftime("%Y-%m-%d")
      url_dates.append([start_date_string,end_date_string])
    number_of_calls = maximum_time_candle_call[timeFrame]
    url_dates = url_dates[-number_of_calls:]
  else:
    current_date = datetime.datetime.now(timezone("Asia/Kolkata"))
    start_date = current_date - datetime.timedelta(days=n)
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = current_date.strftime("%Y-%m-%d")
    url_dates.append([start_date,end_date])

  url = "https://kite.zerodha.com/oms/instruments/historical/{stock_instrument_token}/{timeframe}?user_id=TW8928&oi=1&from={start_date}&to={end_date}"
  for url_date in url_dates:
    params = {"timeframe":timeFrame,"stock_instrument_token":stock_instrument_token,"start_date":url_date[0],"end_date":url_date[1]}
    api_url = string_Formatting(url,params.copy())
    candles_data = get_candle_data(session,api_url)
    if(len(candles_data)>0):
      candles.append(candles_data)
  candles = pd.concat(candles, axis=0)
  candles = candles[~candles.index.duplicated(keep='first')]
  candles.drop_duplicates(inplace=True)
  candles.reset_index(inplace=True)
  candles.insert(1,"Stock name",stock_name)
  candles.insert(2,"Index name",index_name)
  global df,stockname
  df = candles
  stockname = stock_name
  return candles
