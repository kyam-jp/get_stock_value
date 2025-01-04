#!/e/ksk/tool/python/python.exe
import datetime
import jpholiday
import holidays
import calendar
import pandas as pd
import yfinance as yf
import io
from dateutil.relativedelta import relativedelta
import csv

# データ
# ticker_list:tikerのリスト。各国まとめて管理
# 

# ティッカーを指定
# 1306.T 国内ETF
# 8316.T 三井住友
# 7201.T 日産
# 7261.T マツダ
# 7244.T 市光工業
# 7276.T 小糸製作所
ticker_list=['1306.T','8316.T','7201.T','7261.T','7244.T',
             '7276.T',
            'VT'     ,'VWO'   ,'TSLA'  ,'INTC'  , 'AMD'  ,
             'QCOM'  ,'TSM'   ,'TOK'   ,'JPY=X' ,'AAPL'  ,
             'NVDA'  ,'ARM']


# 土日、祝日を判定する関数  0:休日 1:営業日
def is_bizday_jp(day):
    if day.weekday()>=5 or jpholiday.is_holiday(day):
        return 0
    else:
        return 1

def is_bizday_us(day):
    us_holidays = holidays.US()
    if day.weekday()>=5 or day in us_holidays:
        return 0
    else:
        return 1

# 各国における休日判定
def is_bizday(country,day):
    if country == 'JP':
        return is_bizday_jp(day)
    elif country == 'US':
        return is_bizday_us(day)
    else:
        return 1 

# 指定国の最終営業日を返す
def get_day_bycountry(year, month, country):
    day = (calendar.monthrange(year, month)[1])
    yymmdd = datetime.date(year,month,day)
    if is_bizday(country,yymmdd) == 0:
        # 1日ずらす
        yymmdd = yymmdd +datetime.timedelta(days=-1)  
        # もう一度判定
        while(is_bizday(country, yymmdd) == 0):
            yymmdd = yymmdd +datetime.timedelta(days=-1)
        return yymmdd
    else:
        return datetime.date(year,month,day)

# Yahoo Finance からデータを取得
def get_data_yahoo(tiker_list, start,end):
    
    data = yf.download(tiker_list,start,end)
    close_data = data['Close']
    return close_data

# 指定された年の終値を取得
def get_stock_table(ticker_list, start_day,end_day):
    # end 指定 1日前までを集計するので end_day を +1 しておく
    end_day = end_day+datetime.timedelta(days=1)
    df = get_data_yahoo(ticker_list,start=start_day,end=end_day)
    return df

# 指定国の月末日を取得
def get_month_end_days_bycountry(start_day,end_day,country):
    days =[]
    current_day = start_day
    year = start_day.year
    current_month = start_day.month
    # 月末日を取得
    while current_month <= end_day.month:
        current_day = get_day_bycountry(current_day.year,current_month,country)
        current_month = current_month + 1
        days.append(current_day.isoformat())
    return days

# 各月の営業末日を取得
# 各国で末日が異なる場合はそのまま登録する
def get_month_end_days(start_day,end_day):
    days =[]
    current_day = start_day
    year = start_day.year
    current_month = start_day.month
    # 日本の月末日を登録
    days.extend(get_month_end_days_bycountry(start_day,end_day,"JP"))
    # USの月末日を登録
    days.extend(get_month_end_days_bycountry(start_day,end_day,"US"))


    # 重複データを取り除いておく
    days = list(set(days)) 
    days.sort()
    return days


# 指定された年の月末価格を取得する
def get_stock_val(year):
    """ ここから
    もっとも簡単なコード
    y_symbols = ['SCHAND.NS', 'TATAPOWER.NS', 'ITC.NS']
    from datetime import datetime
    startdate = datetime(2022,12,1)
    enddate = datetime(2022,12,15)
    data = pdr.get_data_yahoo(y_symbols, start=startdate, end=enddate)
    print(data)
    ここまで
    """
    # start_dayからend_dayまでの全日の株価を取得
    # start_day:指定年の1/1。株価リスト取得の初日
    # end_day:株価リスト取得最終日

    start_day = datetime.date(year,1,1)

    if datetime.datetime.now().year > year:
        end_month = 12
    else:
    # 指定年内に実行したときは前月末日までを期間とする
       end_month = datetime.datetime.now().month -1
    
    # 月末日を取得
    last_day = calendar.monthrange(year,end_month)[1]
    # フォーマットを整える
    end_day = datetime.date(year,end_month,last_day)
    # 期間内全日の終値を取得
    df = get_stock_table(ticker_list, start_day,end_day) 
    # CSV 形式でバッファへ書き込む
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
 
    #各月末日を取得
    # 国ごとの稼働月末日を集計
    # 異なる場合はそのまま集計対象とする
    days=[]
    days = get_month_end_days(start_day,end_day)
    # 末日の株価を抽出しCSVに書き込む
    vals=[]

# 複数行を抜き出す
# 縦横を入れ替えておく
    vals = df.loc[days,:].transpose()
    # CSV 形式でファイルへ書き込む場合はこちら
    vals.to_csv('./out.csv')
   
#    vals=[]
#    for day in days:
#        val = df_val[day:day]
#        vals.append(val.to_string(header=False,index=False))


###### 実行結果 ######
"""
Ticker	2024/1/31	2024/2/29	2024/3/29	2024/4/30	2024/5/31	2024/6/28	2024/7/31	2024/8/30	2024/9/30	2024/10/31
1306.T	2618.554688	2750.953613	2867.170166	2837.257813	2893.159668	2911.303223	2900.5	2811	2767	2818
7201.T	573.7728882	574.1629028	607	581.7000122	558.4000244	545.9000244	486.2000122	425.5	402.5	411.2000122
7244.T	573.5877686	534.7004395	534.7004395	521.0899048	544.4222412	535.2039795	487.9801025	441.7400513	439.7723999	449.6107178
7261.T	1776.219238	1714.297729	1713.187378	1764.0354	1620.780884	1521.529419	1341.605591	1194.928589	1070	1107.5
7276.T	2214.8396	1842.781616	2007.075439	2096.82666	2188.057373	2188.550537	2214.687012	2113.593506	1975	1993

上記が以下のファイルへ格納される
./out.csv
"""
## 使い方
"""
コード先頭付近にある Tickerリストを編集
場合によってはget_stock_valの引数（指定年）を編集
"""


get_stock_val(2024)
