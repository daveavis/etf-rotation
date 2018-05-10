#import urllib.request
#import json
import pandas
import numpy
import matplotlib.pyplot as plt
import math

# return a list containing column i in 2d-list matrix
def column(matrix, i):
    return [row[i] for row in matrix]

# return a list containing the ranks of the given column smallest = 1
def rank_column_small_to_big(column):
    index = [0]*len(column)

    for i in range(len(column)):
        index[column.index(min(column))] = i+1
        column[column.index(min(column))] = max(column)+1
    
    return index
    
# return a list containing the ranks fo the given column biggest = 1
def rank_column_big_to_small(column):
    index = [0]*len(column)

    for i in range(len(column)):
        index[column.index(max(column))] = i+1
        column[column.index(max(column))] = min(column)-1
    
    return index

etf_list = ["SPY","IWM","VEA","EEM","TLT","TLH","DBC","GLD","VNQ","RWX"]
#etf_list = ["SPY", "IWM"]
all_data = {}  # holds one data-frame per etf, indexed by etf
raw_results = []

# weights
r3m_weight = 0.4
r20d_weight = 0.3
v20d_weight = 0.3

# store all of the data_frames from the json's in a list
def get_all_data(etf_list):
    all_data = {}
    for etf in etf_list:
        df = pandas.read_json("https://api.iextrading.com/1.0/stock/" + etf + "/chart/1y")
        all_data[etf] = df
    return all_data

#get all of the data into a 2d list
# offset allows us to use an ending date other than yesterday
# offset = 0 is for the  most current results
def get_raw_results(etf_list, offset):
    raw_results = []
    for etf in etf_list:
        #df = pandas.read_json("https://api.iextrading.com/1.0/stock/" + etf + "/chart/1y")
        df = all_data[etf]
        length = len(df.index) - offset
    
        date = pandas.to_datetime(df.loc[length-1]['date'])
        return_3m = (df.loc[length-1]['close']-df.loc[length-1-64]['close'])/df.loc[length-1-64]['close']
        return_20d = (df.loc[length-1]['close']-df.loc[length-1-19]['close'])/df.loc[length-1-19]['close']
    
        returns_1d = []
        for x in range(20):
            #returns_1d.append( (df.loc[length-x-1]['close'] - df.loc[length-x-2]['close'])/df.loc[length-x-2]['close'] )
            returns_1d.append( df.loc[length-x-1]['changePercent'] )
            
        arr_1d = numpy.array( returns_1d )
        volatility_20d = numpy.std( arr_1d ) * math.sqrt(252)
    
        raw_results.append([etf, return_3m, return_20d, volatility_20d, date])

    return raw_results

# rank each column
def get_ranks( raw_results, etf_list ):
    return_3m_rank = rank_column_big_to_small( column( raw_results, 1 ) )
    return_20d_rank = rank_column_big_to_small( column( raw_results, 2 ) )
    volatility_20d_rank = rank_column_small_to_big( column( raw_results, 3 ) )
    
    # put ranked columns into array
    ranks = [] # etf, 3m return, 20d return, 20d volatility, weighted avg rank, final rank
    for x in range(len(etf_list)):
        ranks.append([etf_list[x], return_3m_rank[x], return_20d_rank[x], volatility_20d_rank[x], 0, 0])
    
    # calculate the weighted average rank for each etf
    for x in range(len(etf_list)):
        wavg = ranks[x][1] * r3m_weight + ranks[x][2] * r20d_weight + ranks[x][3] * v20d_weight
        ranks[x][4] = wavg
    
    # calculate final ranking
    final_ranks = rank_column_small_to_big( column( ranks, 4 ) )
    for x in range(len(final_ranks)):
        temp = ranks[x]
        ranks[x] = [ temp[0], temp[1], temp[2], temp[3], temp[4], final_ranks[x] ]
    
    return ranks

print("Getting All Data...")
all_data = get_all_data( etf_list )
print("Getting Raw Results...")
raw_results = get_raw_results( etf_list, 0 )
print("Compiling Ranks...")
ranks = get_ranks( raw_results, etf_list )

print("ETF\tAvg\tRank")
for result in ranks:
    print( "%s\t%.1f\t%.0f" % (result[0], result[4], result[5]) )
    
#for x in range(len(ranks)):
#    print( ranks[x] )
    
#print()

#for x in range(len(raw_results)):
#    print( raw_results[x] )

# compile historical ranks into a list
def get_historical_ranks( etf_list ):
    hist_ranks = []
    
    for x in range(len(etf_list)):
        #print(".",end="")
        hist_ranks.append([ etf_list[x] ])
    
    hist_ranks.append( ["Date"] )  # add a date row

    for x in range(251-64):  # one trading year minus 3 trading months
        #print(";",end="")
        #print("x = ", x)
        raw_results = get_raw_results( etf_list, x)
        ranks = get_ranks( raw_results, etf_list )
        rank_list = column(ranks,5)
        for y in range(len(rank_list)):
            #print("y = ", y)
            hist_ranks[y].append(rank_list[y])
            
        hist_ranks[y+1].append( raw_results[0][4])   # populate the date row
        #print( raw_results[0][4])
        #hist_ranks.append( column( raw_results[0], 4 ) )
    #for y in range(len(raw_results)):
        #print(raw_results[y])       
    return hist_ranks
    
    #for x in range(len(ranks)):
        #print( ranks[x] )

print("Processing Historical Ranks...")
historical_ranks = get_historical_ranks( etf_list )
for x in range(len(historical_ranks)):
    print( historical_ranks[x])


#plt.plot_date(df['date'],df['close'],'-')
#plt.show()
print("Done.")