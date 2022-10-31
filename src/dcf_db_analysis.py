import pandas as pd
import numpy as np
import re

def filter_db(column):
    patterns = ['capex', 'profit', 'revenue', 'earning', 'amort']
    for pattern in patterns:
        if re.search(pattern, column):
            return True
        
    return False
    
    



if __name__ == '__main__':
    
    pd.set_option('display.max.columns', None)
    csv_file = '../extra/FIVE_financemarker.csv'
    
    asset_db = pd.read_csv(csv_file)
    filt_asset_db = asset_db[asset_db['period']=='Y']
    
    last_year = asset_db['year'].max()
    filt_last_year = filt_asset_db['year'].max()
    
    if last_year != filt_last_year:
        
        two_last_years_db = asset_db[(asset_db['year']==last_year) | (asset_db['year']==(last_year-1))]
        two_last_years_crosstab = pd.crosstab(index = asset_db['year'], columns = asset_db['type'])
        aggr_periods = []
        if two_last_years_crosstab.loc[last_year, 'Q'] == 2:
            aggr_periods.append([two_last_years_db[(asset_db['year']==last_year)]['type'].eq('Q').idmax(), last_year])
            aggr_periods.append([two_last_years_db[(asset_db['year']==last_year)]['type'].eq('6M').idmax(), last_year])
            aggr_periods.append([two_last_years_db[(asset_db['year']==(last_year-1))]['type'].eq('6M').idmax(), last_year-1])
        elif two_last_years_crosstab.loc[last_year, 'Q'] > 1 and two_last_years_crosstab.loc[last_year, '6M'] == 0:
            aggr_periods.append([two_last_years_db[(asset_db['year']==last_year)]['type'].eq('Q').idmax(), last_year])
            aggr_periods.append([two_last_years_db[(asset_db['year']==(last_year-1))]['type'].eq('6M').idmax(), last_year-1])
            aggr_periods.append([two_last_years_db[(asset_db['year']==(last_year-1))]['type'].eq('Q').idmax(), last_year-1])
        elif two_last_years_crosstab.loc[last_year, '6M'] != 0:
            aggr_periods.append([two_last_years_db[(asset_db['year']==last_year)]['type'].eq('6M').idmax(), last_year])
            aggr_periods.append([two_last_years_db[(asset_db['year']==(last_year-1))]['type'].eq('6M').idmax(), last_year-1])
        
        
        mod_columns = list(filter(filter_db, two_last_years_db.columns))
        last_year_result = two_last_years_db.loc[aggr_periods[0][0], aggr_periods[0][1]]
        
        for i in range(1:len(aggr_periods)):
            for column in mod_columns:
                last_year_result[mod_columns] +=  two_last_years_db.loc[aggr_periods[i][0], aggr_periods[i][1]][mod_columns]
        
        two_last_years_db.loc[aggr_periods[0][0], aggr_periods[0][1]]['type'] = 'Y'
        filt_asset_db.concat(filt_asset_db, last_year_result)
        
        print(last_year_result)
        
       
        
        
            
       
        
        
        
        