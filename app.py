import pandas as pd
import math
from scipy import stats
import matplotlib.pyplot as plt
import sys
import argparse
#Required dependencies

def avg_analysis(csvname,time_in, time_out, bond_name, quote_trace, dataType = "Price"):
    #Finds the average of a bond over the time range provided. Works for both trace and quote data
    start_date = pd.to_datetime(time_in) 
    end_date = pd.to_datetime(time_out)
    quote_trace = quote_trace.lower() # determines which file and converts to lower case 
    if quote_trace == 'quote':
        #The specifications for the quote file
        date_param = "Date"
        count = 'Identifier'
        numTrades = 'Size'
        value = 'ColorValue'
        df = pd.read_csv(csvname, parse_dates = [date_param])
        df.fillna(1, inplace = True) # fills in N/A values that would cause divide by zero errors. This cancels out when taking the average. 
        avg_values = df.loc[(df[date_param] > start_date) & (df[date_param] < end_date)] #filters by rows in the date range
        avg_values = avg_values.loc[(avg_values[count] == bond_name)] #Filters by the bond
        avg_values = avg_values.loc[(avg_values["QuoteType"] == dataType.upper())] #Allows for yield, spread, or price values
        offer = avg_values.loc[(avg_values['ColorType'] == 'OFFER')]    #Splits into offer values
        bid = avg_values.loc[(avg_values['ColorType'] == 'BID')]    #bid values

        if avg_values.empty:    #if no data is left, do not attempt to run the average
            print ('Nothing in date range for this bond')
            return [None, 0,0]
        else:
            totalTrade = (offer[value]*offer[numTrades])  #Get the price per volume
            offer_average = totalTrade.sum()/offer[numTrades].sum()  #average
            totalTrade = (bid[value]*bid[numTrades])   #Get the price per volume
            bid_average = totalTrade.sum()/bid[numTrades].sum() #average
            return[dataType, bid_average, offer_average]

    if quote_trace == 'trace': 
        #Specs for trace file
        date_param = "execution_time"
        count = 'cusip'
        numTrades = 'reported_volume'
        value = 'price'
        df = pd.read_csv(csvname, parse_dates = [date_param]) #imports csv and converts dates into date format
        avg_values = df.loc[(df[date_param] > start_date) & (df[date_param] < end_date)] #Filters down by dates
        avg_values = avg_values.loc[(avg_values[count] == bond_name)] #filters down by bond

        if avg_values.empty: #if not values, do not continue
            print ('Nothing in date range for this bond')
            return 0
        
        else:
            totalTrade = (avg_values[value]*avg_values[numTrades])
            average = totalTrade.sum()/avg_values[numTrades].sum()
            return average

def reset(quote_trace): #Returns the working data to the given data (useful if additional data is added)
    if quote_trace == 'trace':
        og = pd.read_csv('./data/trace.csv')
        og.to_csv('./data/trace_curr.csv', encoding='utf-8')
    
    if quote_trace == 'quote':
        og = pd.read_csv('./data/solve_quotes.csv')
        og.to_csv('./data/quotes_curr.csv', encoding='utf-8')
    
    else:
        og = pd.read_csv('./data/trace.csv')
        og.to_csv('./data/trace_curr.csv')
        og = pd.read_csv('./data/solve_quotes.csv')
        og.to_csv('./data/quotes_curr.csv', encoding='utf-8')

def importData(newcsv, quote_trace): #adds additional data
    if quote_trace == 'trace':
        og = pd.read_csv('./data/trace.csv')
        new = pd.read_csv(newcsv)
        
        if og.columns.any()!=new.columns.any():
            print('header mismatch')
            pass
        
        else:
            new = pd.concat([og, new], sort='True')
            new.to_csv('./data/trace_curr.csv', encoding='utf-8')
    
    if quote_trace == 'quote':
        og = pd.read_csv('./data/solve_quotes.csv')
        new = pd.read_csv(newcsv)
    
        if og.columns.any()!=new.columns.any():
            print('header mismatch')
            pass
    
        else:
            new = pd.concat([og, new], sort='True')
            new.to_csv('./data/quotes_curr.csv', encoding='utf-8') 

def get_avg_dates(bond1='all', bond2='all'): #gets the average per day of the given bonds
    df = pd.read_csv('./data/trace_curr.csv', parse_dates=["execution_time"])
    date_min=df.execution_time[0] #for some reason time.min is wrong, but this gets the first date 
    date_max=df.execution_time.max()    #last date
    dates=pd.date_range(start=date_min, end=date_max, normalize='True') #sets all date and times to midnight
    prev_day=dates[0]   #fetches first date, trails behind loop by one rotation
    
    for i in range(1, len(dates)):
        curr_Day=dates[i]
        avg_values=df.loc[(df["execution_time"] >= prev_day) & (df["execution_time"] <= curr_Day)]
        prev_day=curr_Day
    
        if avg_values.empty:    #if nothing left, stop
            pass
    
        else:
            if bond1 == 'all' and bond2 == 'all':   #allows for market calculations, not needed
                avg_values1=avg_values
                avg_values2=avg_values
    
            if bond1 == 'all':  #market, this is not even possible with how the prompts are set up
                avg_values1=avg_values
                avg_values2=avg_values.loc[(avg_values['cusip'] == bond2)]
               
            if bond2 == 'all':  #market
                avg_values2=avg_values
                avg_values1=avg_values.loc[(avg_values['cusip'] == bond1)]
    
            else:   #Two bonds
                avg_values1=avg_values.loc[(avg_values['cusip'] == bond1)]
                avg_values2=avg_values.loc[(avg_values['cusip'] == bond2)]    
    
        if avg_values1.empty or avg_values2.empty: #Checking for valid data
            pass
    
        else:   #gets the average. Very similar to above      
            totalTrade=(avg_values1['price']*avg_values1['reported_volume'])
            average1=totalTrade.sum()/avg_values1['reported_volume'].sum()

            totalTrade=(avg_values2['price']*avg_values2['reported_volume'])
            average2=totalTrade.sum()/avg_values2['reported_volume'].sum()
            yield [average1, average2]

def beta(bonda, bondb): #Fetches the average values to determine the devation and beta
    x=[]
    y=[]
    marketAVG = get_avg_dates(bonda, bondb)
    
    for i in marketAVG:
        x.append(i[0])
        y.append(i[1])
    slope = stats.linregress(x,y).slope
    return slope

def visualize(bond, time_in, time_out): #Visualizes a bond's trace and quote data
    time_in = pd.to_datetime(time_in)
    time_out = pd.to_datetime(time_out)
    #just a bunch of filtering data down. This could be done with fewer lines, 
    #I chose to do it in a very verbose way so that I know it is giving me the right values. 
    traceData = pd.read_csv('./data/trace_curr.csv', parse_dates = ['execution_time'])
    quoteData = pd.read_csv('./data/quotes_curr.csv', parse_dates = ['Date'])
    traceData = traceData[['cusip', 'price', 'execution_time']]
    quoteData = quoteData[['Identifier', 'Date', "ColorValue", "QuoteType", "ColorType" ]]
    traceData = traceData.loc[(traceData['execution_time'] > time_in) & (traceData['execution_time'] < time_out)]
    quoteData = quoteData.loc[(quoteData['Date'] > time_in) & (quoteData['Date'] < time_out)]
    traceData = traceData.loc[(traceData['cusip'] == bond)]
    quoteData = quoteData.loc[(quoteData['Identifier'] == bond)]
    quoteData = quoteData.loc[(quoteData['QuoteType'] == "PRICE")]
    quoteBids = quoteData.loc[(quoteData['ColorType'] == "BID")]
    quoteOffers = quoteData.loc[(quoteData['ColorType'] == "OFFER")]
    traceData = traceData[['price', 'execution_time']]
    quoteBids = quoteBids[['ColorValue', 'Date']]
    quoteOffers = quoteOffers[['ColorValue', 'Date']]
    #renames values to match
    traceData.rename(columns = {'price': 'Price', 'execution_time': 'Date'}, inplace = True)
    quoteBids.rename(columns = {'ColorValue': 'Price'}, inplace = True)
    quoteOffers.rename(columns = {'ColorValue': 'Price'}, inplace = True)
    
    if traceData.empty or quoteData.empty:
        print ('Nothing in date range for this bond')
        return 0
    
    else:
        print("Close graph to continue")
        plt.figure()
        key=['Trace', 'Bids', 'Offers']
        for frame in [traceData, quoteBids, quoteOffers]:  #fills plot with data
            ax=plt.plot(frame['Date'], frame['Price'])
    plt.xlabel('Date') #adds labels. All other parameters fail though
    plt.ylabel('Price')
    plt.legend(key, loc='best')
    plt.show() #Cannot change options for some reason, super annoying!

def main(sysinput): #User input time

    if sysinput == 'upload': #user input should catch on one of these if statements
         filename = input("Please enter the path and filename of the file you wish to upload ")
         filename = str(filename) #stringifys the response 
         which = input('Would you like to merge that with the trace or quote data? ')
         which = str(which).lower() #determines which CSV parameters to pull from 
         importData(filename, which)

    if sysinput == 'reset':
        option = input("Please enter if you wish to reset trace, quote or both: ")
        reset(str(option).lower())
        print('reset finished')

    if sysinput == "average":
        bond = input("Please enter which bond you wish to average by identifier (AAAAAAAAA): ")
        bond = str(bond).upper()
        start_date = input ('Please enter the start date in MM/DD/YYYY format: ')
        start_date = str(start_date)
        start_time = input ('Please enter the start time in 24 hour HH:MM format: ')
        start_time = str(start_time)
        start = start_date + ' ' + start_time

        end_date = input ('Please enter the start date in MM/DD/YYYY format: ')
        end_date = str(end_date)
        end_time = input ('Please enter the start time in 24 hour HH:MM format: ')
        end_time = str(end_time)
        end = end_date + ' ' + end_time

        quote_trace = input('Would you like to average quote or trace data? ')
        quote_trace = str(quote_trace).lower()
        
        if quote_trace == 'quote':
            data_type = input('Would you like to average the price, spread, or yield? ')
            data_type = str(data_type).lower()
            csvname = './data/quotes_curr.csv'
            average = avg_analysis(csvname,start, end, bond, quote_trace, data_type) #pushes data into function
            print(average[0], 'bid average is', average[1])
            print(average[0], 'offer average is', average[2])   #since quote returns a list and trace returns a float. They are seperated. 
        
        if quote_trace =='trace':
            csvname = './data/trace_curr.csv'
            average = avg_analysis(csvname,start, end, bond, quote_trace)
            print('Trace average is', average)

    if sysinput == "beta": 
        bond1 = input("Please enter the first bond identifier (AAAAAAAAA): ")
        bond1 = str(bond1).upper()
        bond2 = input("Please enter the second bond identifier (AAAAAAAAA): ")
        bond2 = str(bond2).upper()
        out = beta(bond1, bond2) 
        print(out)

    if sysinput == 'visualize':
        bond = input("Please enter the bond identifier (AAAAAAAAA): ")
        bond = str(bond).upper()

        start_date = input ('Please enter the start date in MM/DD/YYYY format: ')
        start_date = str(start_date)
        start_time = input ('Please enter the start time in 24 hour HH:MM format: ')
        start_time = str(start_time)
        start = start_date + ' ' + start_time

        end_date = input ('Please enter the start date in MM/DD/YYYY format: ')
        end_date = str(end_date)
        end_time = input ('Please enter the start time in 24 hour HH:MM format: ')
        end_time = str(end_time)
        end = end_date + ' ' + end_time
        visualize(bond, start, end) 

    if sysinput == 'exit' or sysinput== 'quit':
        sys.exit()        

if __name__ == "__main__":
    while True:
        system=input("\nPlease add one of the following options \nhere are the options: \n -upload \n -reset \n -average \n -beta \n -visualize \n -exit \nType which one you would like: " )
        main(system)
