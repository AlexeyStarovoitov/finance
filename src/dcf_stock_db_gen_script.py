import pandas as pd
import numpy as np
import argparse


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-betta_csv', dest='betta_csv', type=str)
    arg_parser.add_argument('-stock_csv', dest='stock_csv', type=str)
    
    args = arg_parser.parse_args()
    
    betta_db = pd.read_csv(args.betta_csv)
    stock_db = pd.read_csv(args.stock_csv)
    
    base_stock = 'RTS'
    invest_horizont = 2
    country_risk = 16.78
    rf = 8.1
    rm = 25.87
    for stock in stock_db['ID']:
        #print(stock)
        betta_index = betta_db[(betta_db.iloc[:,1]==stock) & (betta_db.iloc[:,2]==base_stock)].index[0]
        stock_index = stock_db[stock_db['ID']==stock].index[0]
        stock_db.loc[stock_index, 'betta'] = float(betta_db.loc[betta_index, betta_db.iloc[:,4].name].replace(',', '.'))
        stock_db.loc[stock_index, 'country_risk'] = country_risk
        stock_db.loc[stock_index, 'rm'] = rm
        stock_db.loc[stock_index, 'rf'] = rf
        stock_db.loc[stock_index, 'invest_horizont'] = invest_horizont
    
    
    stock_db.to_csv(args.stock_csv) 
        
    