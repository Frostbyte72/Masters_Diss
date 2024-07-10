import yfinance as yf
import requests
import string
import pandas as pf
import networkx as nx
import matplotlib.pyplot as plt

class star:
    def __init__(self,name,ticker,info,hist,holders):
        self.name = name
        self.ticker  = ticker
        self.info = info
        self.hist = hist
        self.inst_holders = holders #Institutional Holders

    def plot_graph(self):
        plt.clf() #clear plot
        graph = nx.Graph()

        # Add central node
        graph.add_node(self.name)
        for index, row in self.inst_holders.iterrows():
            graph.add_node(row['Holder'])
            graph.add_edge(self.name,row['Holder'],weight = row['pctHeld'])

        #Postions of graph
        pos = nx.spring_layout(graph)
        #Show labels
        #nx.draw_networkx_labels(graph, pos, font_size=8, font_family="sans-serif")
                                
        plt.figure()
        plt.title('Graph representation of {} top holders'.format(self.name))
        nx.draw(graph,pos,with_labels = True, font_size = 10)

        #set edge labels
        edge_labels = nx.get_edge_attributes(graph,'weight')
        nx.draw_networkx_edge_labels(graph,pos,edge_labels=edge_labels,label_pos = 0.5,verticalalignment = 'bottom')

        ax = plt.gca()
        ax.margins(0.20)
        plt.axis("off")
        plt.show()

    def plot_hist(self):
        
        plt.clf() #Clear plot

        #Plot Target Comapny
        target_standardised = self.hist['Open'].apply(lambda x: (x - self.hist['Open'].mean())/self.hist['Open'].std())
        plt.plot(target_standardised,label = self.name)

        #Plot holders
        for index, row in self.inst_holders.iterrows():
            sd = row['History']['Open'].std()
            mean = row['History']['Open'].mean()
            standardised = row['History']['Open'].apply(lambda x: (x - mean)/sd)
            plt.plot(standardised,'--',label = self.inst_holders.loc[index]['Holder'], alpha = 0.6)

        plt.title('Z-score Stadarsised Market Open \n {}'.format(self.name))
        plt.legend()
        plt.show()

# Not my code 
# Modified version of code found at the following link:
# https://gist.github.com/leftmove/dd9d981c8c37983f61e423a45085e063
def get_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance, params=params, headers={'User-Agent': user_agent})
    data = res.json()
    
    if len(data['quotes']) == 0:
        return None
    company_code = data['quotes'][0]['symbol']
    return company_code

#Target
stock = yf.Ticker('INTC')
holders_df = stock.institutional_holders 


holders_df['Ticker'] = holders_df['Holder'].apply(lambda x: get_ticker(x)) #Find tickers of the holders

#Filter out None
holders_df.dropna(axis = 0, how = 'any',inplace= True)

#Cleans tickers that don't match back to the same name 
# - adds historical data once ticker is verified
holders_df['History'] = None
for index , row in holders_df.iterrows():
    check_name = yf.Ticker(row['Ticker']).info['longName'].lower().translate(str.maketrans('', '', string.punctuation))
    
    if check_name != row['Holder'].lower().translate(str.maketrans('', '', string.punctuation)):
        holders_df.drop(index,inplace = True)
    
    #get historical data for the company
    holders_df['History'][index] = yf.Ticker(row['Ticker']).history(period="1y")

print(stock.info['longName'])
print(holders_df)

Target = star(stock.info['longName'],'AAPL',stock.info,stock.history(period="1y"),holders_df)
Target.plot_hist()
#Target.plot_graph()