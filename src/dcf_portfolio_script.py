import pandas as pd
import numpy as np
import argparse
import re
import dcf_script as dcf

def parse_column_names(db_columns):
	pattern_dict = dict(id = ["id"], betta=["betta"], file=["file"], rm=["rm"], rf=["rf"], crp=["crp"], hrznt =["hrznt"])
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
	
	stock_db = pd.read_csv(args.portfolio_db)
	
	
	