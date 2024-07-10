import yfinance as yf
import pandas as pd
import sqlite3

def get_history(ticker):
    history = yf.download(ticker, period='5y')
    history['Ticker'] = ticker
    history['Date'] = history.index
    history.rename(columns = {'Adj Close':'Adj_Close'},inplace = True)

    return history

conn = sqlite3.connect('Main.db')
cursor = conn.cursor()
try:
    cursor.execute('''SELECT 1 FROM History;''')
#If not create DB
except:
    cursor.execute('''CREATE TABLE History
                    (Ticker TEXT,
                    Date TEXT,
                    Open REAL,
                    High REAL,
                    Low REAL,
                    Close REAL,
                    Adj_Close Real,
                    Volume REAL,
                    PRIMARY KEY (Ticker, Date))''')
    
try:
    cursor.execute('''SELECT 1 FROM Info;''')
#If not create DB
except:
    cursor.execute('''CREATE TABLE Info
                    (Ticker TEXT,
                    Name TEXT,
                    Industry Text,
                    Sector Text,
                    MarketCap REAL,
                    PRIMARY KEY (Ticker))''')
    
#Historical, Info, Fundemental
def main(h = True,i = True,f=True):

    for ticker in pd.read_csv('SP500_tickers.csv')['Symbol']:
        if h:
            history = get_history(ticker)
            try:
                history.to_sql(name='History', con=conn, if_exists='append',index = False)
            except Exception as e:
                print(e)
        

        if i:
            stock = yf.Ticker(ticker)
            try:
                info = [ticker,stock.info['longName'],stock.info['industryKey'],stock.info['sectorKey'],stock.info['marketCap']]
            except:
                print('Info not found check Ticker is valid for : {}'.format(ticker))
                continue
            sql = ('''INSERT INTO 
                        Info(Ticker,Name,Industry,Sector,MarketCap) 
                        VALUES(?,?,?,?,?)
                            ''')
            cursor.execute(sql,info)
            conn.commit()
            
            print(info)
        
        """
        if f:
            stock =  yf.download('AAPL',start="2019-07-01", end="2024-07-01")
            print(stock)

            print(stock.income_stmt)
            print('£££££££££££££££££££££££££')
            print(stock.recommendations)
            print('£££££££££££££££££££££££££')
            print(stock.balance_sheet)
            print('£££££££££££££££££££££££££')
            print(stock.dividends)
            print('£££££££££££££££££££££££££')
            print(stock.actions)
            print('£££££££££££££££££££££££££')
            for key,val in stock.info.items():
                print("{} : {}".format(key,val))


            
            try:
                fundemntal = [ticker,stock.info['longName'],stock.info['industryKey'],stock.info['sectorKey'],stock.info['marketCap']]
            except:
                print('Info not found check Ticker is valid for : {}'.format(ticker))
                continue
            sql = ('''INSERT INTO 
                        Info(Ticker,Name,Industry,Sector,MarketCap) 
                        VALUES(?,?,?,?,?)
                            ''')
            cursor.execute(sql,info)
            conn.commit()
            """
        break


main(False,False,True)

