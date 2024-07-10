import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from tqdm import tqdm
import numpy as np
from dtaidistance import dtw

import networkx as nx
import matplotlib.pyplot as plt


def percent_change(sector):
    tickers = cursor.execute('SELECT Ticker FROM Info WHERE Sector = "technology" ').fetchall()

    print(tickers)
    for t in tickers: #object is tuple second half not needed
        raw = cursor.execute('SELECT Open FROM History WHERE Ticker = "{}" '.format(t[0])).fetchall()
        x = pd.DataFrame([i[0] for i in raw],columns = ['Price'])
        x['Percent_change'] = x['Price'].pct_change(1)
        plt.plot(range(len(x)-1),x['Percent_change'].iloc[1:],alpha = 0.4,label = t[0])
        

    plt.legend()
    plt.show()
        
#Calaculates Pearson Coeraltion of each Time Series then converts it to a distance metric
def Calculate_Correlation(tickers):
    Series = []
    too_short = []
    for idx , t in enumerate(tickers):
        print(t)
        history = [x[0] for x in cursor.execute('SELECT Open From History WHERE Ticker ="{}"'.format(t)).fetchall()]
        if len(history) < 1250:
            print('History not long enough leght found : {}'.format(len(history)))
            too_short.append(idx)
             #Remove it from list of tickers
            continue
        
        Series.append(history[-1250:])

    for idx in sorted(too_short,reverse=True):
        del tickers[idx]


    #Calc Pearson Correlation
    
    Pearson_Cor_Matrix = np.corrcoef(Series)
    print(Pearson_Cor_Matrix)
    print('Converting Cor to Dist \n')
    Cor2Dist= np.vectorize(lambda x: np.sqrt(2*(1-x))) #Potential rounding error [1][1] gives v small value but should be 0 (Shouldn't matter wont be used)
    cor_dist_Matrix = Cor2Dist(Pearson_Cor_Matrix)
    print(cor_dist_Matrix)

    #Convert to df
    Pearson_df = pd.DataFrame(data = cor_dist_Matrix,columns=tickers)
    Pearson_df['Ticker'] = tickers
    print(Pearson_df)
    return Pearson_df

def Calculate_DTW(tickers):
    
    
    Series = []
    print('Gathering and Normalising Data')
    for idx , t in enumerate(tickers):
        print(t)
        history = [x[0] for x in cursor.execute('SELECT Open From History WHERE Ticker ="{}"'.format(t)).fetchall()]
        
        #Normalsie the Data so scale is removed
        open_min = min(history)
        open_max = max(history)
        Series.append( np.array([(open-open_min)/(open_max-open_min) for open in history]))
        
    
    print('Calculating DTW Matirx')
    DTW_Matrix = dtw.distance_matrix(Series,compact = False)
    print(f"DTW Distance Matrix:")

    #Convert Matrix to dataframe
    DTW_df = pd.DataFrame(data = DTW_Matrix,columns=tickers)
    DTW_df['Ticker'] = tickers
    return DTW_df


# Takes DTW Matrix and plots weighted Graph representation
def plot_Network(Simalarity_df):
    graph = nx.Graph()

    #Colour nodes based on sector
    color_map = []
    sector_colour = {'industrials' : 'grey', 
                    'healthcare' : 'cyan', 
                    'technology' : 'orange',
                    'consumer-cyclical' : 'deeppink', 
                    'utilities' : 'saddlebrown', 
                    'financial-services' : 'g', 
                    'basic-materials' : 'Navy',
                    'real-estate' : 'indigo',
                    'communication-services' : 'red',
                    'consumer-defensive': 'yellow',
                    'energy' : 'magenta' }

    for idx , row in Simalarity_df.iterrows():
        print(row['Ticker'])
        graph.add_node(row['Ticker']) 

        #Add node base off sector
        query = cursor.execute('SELECT Sector From Info WHERE Ticker ="{}"'.format(row['Ticker'])).fetchall()
        color_map.append(sector_colour[query[0][0]])
        

        for item in row.items():
            if item[0] == row['Ticker'] or item[0] == 'Ticker': #Skip if its itelf as weight will be zero, or if its the ticker col
                continue
            graph.add_edge(row['Ticker'],item[0],length = item[1] , weight = abs(round(item[1],2)))


    #Postions of graph
    pos = nx.spring_layout(graph, weight='length')
    #Show labels
    #nx.draw_networkx_labels(graph, pos, font_size=8, font_family="sans-serif")
                            
    plt.figure()
    plt.title('Graph representation of SNP 500 Largest 50')
    
    graph = nx.minimum_spanning_tree(graph)
    #graph = nx.maximum_spanning_tree(graph) #No longer needed to due to pearson to dist coeficent
    nx.draw(graph,pos,node_color=color_map,with_labels = True, font_size = 10)

    #set edge labels
    edge_labels = nx.get_edge_attributes(graph,'weight')
    nx.draw_networkx_edge_labels(graph,pos,edge_labels=edge_labels,label_pos = 0.5,verticalalignment = 'bottom')

    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.show()

#Calculate the MST Tree
def Calculate_MST_Matrix(df):
    
    return

conn = sqlite3.connect('Main.db')
cursor = conn.cursor()
tickers = [t[0] for t in cursor.execute('SELECT Ticker FROM Info ORDER BY MarketCap ASC').fetchall()][0:60]

"""
#Get the DTW_Matrix
DTW_df = Calculate_DTW(Tickers)
DTW_df.to_csv('DTW_Matrix.csv',index=False)

DTW_df = pd.read_csv('DTW_Matrix.csv')
print(DTW_df)
plot_Network(DTW_df)
"""

Pearson_df = Calculate_Correlation(tickers)
plot_Network(Pearson_df)