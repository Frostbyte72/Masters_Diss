import pandas as pd
import sqlite3
import numpy as np


conn = sqlite3.connect('Main.db')
cursor = conn.cursor()
   

def gen_dataset():
    tickers = [x[0] for x in cursor.execute('SELECT Ticker FROM Info ').fetchall()]

    dataset = pd.DataFrame(columns=['Period','Correlation','Ticker1','Ticker2','Sector1','Sector2','Industry1','Industry2','20d_Volume1','20d_Volume2','close_SD1','close_SD2']) #'Country1','Economy1','Sentiment_Market1','Sentiment_Company1'])
    
    seen = {}
    index = 0
    for ticker1 in tickers:
        History1 = [ [x[0],x[1],x[2]] for x in cursor.execute('SELECT Date, Close, Volume FROM History WHERE Ticker = "{}" ORDER By Date DESC'.format(ticker1)).fetchall()]
        
        seen[ticker1] = True
        for ticker2 in tickers:
            if ticker2 in seen:
                continue
            
            print(ticker1,ticker2)

            History2 = [ [x[0],x[1],x[2]] for x in cursor.execute('SELECT Date, Close, Volume FROM History WHERE Ticker = "{}" ORDER By Date DESC'.format(ticker2)).fetchall()]
            

            for i in range(0,min(len(History1),len(History2)),20):
                if i+20 > min(len(History1),len(History2)):
                    # Not enough data for a complete period
                    break
                
                vol_sum1 = 0
                vol_sum2 = 0
                closes1 = []
                closes2 = []
                for idx in range(i,i+20):
                    
                    closes1.append(History1[idx][1])
                    closes2.append(History2[idx][1])
                    vol_sum1 += History1[idx][2]
                    vol_sum2 += History2[idx][2]
    
                #Calcualte Statstical measures  
                correlation = np.corrcoef(closes1,closes2)[0][1]
                sd1 = np.std(closes1)
                sd2 = np.std(closes2)
                volume1 = vol_sum1/20
                volume2 = vol_sum2/20

                #Retrive Sector / Industry from SQL DB
                SI1 = cursor.execute('SELECT Sector, Industry From Info Where Ticker = "{}"'.format(ticker1)).fetchone()
                SI2 = cursor.execute('SELECT Sector, Industry From Info Where Ticker = "{}"'.format(ticker2)).fetchone()

                dataset.loc[index] = ["{} : {}".format(History1[i][0] , History1[i+20][0]),correlation,ticker1,ticker2,SI1[0],SI2[0],SI1[1],SI2[1],volume1,volume2,sd1,sd2]
                index += 1
                
                
                
                break

            
            break
    dataset = pd.concat([dataset,pd.get_dummies(dataset[['Sector1','Sector2']])],axis =1)
    dataset.drop(columns=['Sector1','Sector2','Industry1','Industry2'],inplace=True)
    print(dataset.head(5))
    return dataset
    
    
dataset = gen_dataset()
dataset.to_csv('Input.csv')