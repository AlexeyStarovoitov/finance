import pandas as pd
import numpy as np
import argparse
import re
import dcf_script as dcf

def parse_column_names(db_columns, pattern_dict):
	
	col_dict={}
	for column in db_columns:
		for pattern_key, pattern_vals in pattern_dict.items():
			for pattern_val in pattern_vals:
				if re.search(pattern_val, column):
					col_dict[pattern_key]=column
					break
			if pattern_key in col_dict:
				break
	
	return col_dict
	
	

if __name__=='__main__':
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-portfolio_db", dest=portfolio_db, type=str)
	args=argparser.parse_args()
	
	portfolio_db = pd.read_csv(args.portfolio_db)
    
    new_columns = dict(current_prices="current_prices", calculated_prices="calculated_prices", margin="margin")
    for column_key in new_columns:
    	new_col = pd.Series(data=np.zeros(len(portfolio_db)), index=portfolio_db.index, dtype = np.float64)
    	portfolio_db.insert(loc = len(portfolio_db.columns), column=new_columns[column_key], value=new_col)
    	
    	pattern_dict = dict(id = ["id"], betta=["betta"], file=["file"], rm=["rm"], rf=["rf"], crp=["crp"], hrznt =["hrznt"], cur_price=["cur_price"], ev_prices=["ev_prices"], margin=["margin"])
    	column_dict = parse_column_names(portfolio_db.columns, pattern_dict)
    	
    	for row_index in portfolio_db.index:
    		cur_row = portfolio_db.loc[row_index, :]
    		dcf_clc = dcf.DCF_calc(csv_file=column_dict[file], betta =column_dict[betta], rf = column_dict[rf], rm = column_dict[rm], country_risk = column_dict[crp], invst_hrznt=column_dict[hrznt])
    	result_stock_price = dcf_clc.calculate_fair_share_price()
    	for key in result_stock_price.keys():
    		cur_row[key] = result_stock_price[key]
    	
    	portfolio_db_ file_path = args.portfolio_db
    	portfolio_db_ file_path_splt = portfolio_db_ file_path.split(".csv")
    	new_portfolio_db_ file_path = portfolio_db_ file_path_splt[0]+ "dcf_analysis.csv"
    	portfolio_db.to_csv(new_portfolio_db_ file_path)
    	
	
	