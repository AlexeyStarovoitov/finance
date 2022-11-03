import pandas as pd
import numpy as np
import re

def filter_db(column):
    patterns = ['capex', 'profit', 'revenue', 'earning', 'amort', 'expense']
    for pattern in patterns:
        if re.search(pattern, column):
            return True
        
    return False
    
    



if __name__ == '__main__':
    
    
    pd.set_option('display.max.columns', None)
    csv_file = '../extra/FIVE_financemarker.csv'
    
    asset_db = pd.read_csv(csv_file)
    filt_asset_db = asset_db[asset_db['period']=='Y']
    
    print(filt_asset_db)
    last_year = asset_db['year'].max()
    filt_last_year = filt_asset_db['year'].max()
    print(f"last_year: {last_year}\nfilt_last_year: {filt_last_year}")
    
    if last_year != filt_last_year:
        
        two_last_years_db = asset_db[(asset_db['year']==last_year) | (asset_db['year']==(last_year-1))]
        two_last_years_crosstab = pd.crosstab(index = asset_db['year'], columns = asset_db['period'])
        print(two_last_years_crosstab)
 
        aggr_periods = []
        
        if two_last_years_crosstab.loc[last_year, '9M'] == 1:
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='9M')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
        elif two_last_years_crosstab.loc[last_year, 'Q'] == 2 and two_last_years_crosstab.loc[last_year, '6M'] == 1:
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])	
        elif two_last_years_crosstab.loc[last_year, 'Q'] == 1:
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])	
        
        
        print(f'aggr_periods:\n{aggr_periods}')
        
        mod_columns = list(filter(filter_db, two_last_years_db.columns))
        last_year_result = two_last_years_db.loc[aggr_periods[0], :]
        
        
        
        for i in range(1,len(aggr_periods)):
            for column in mod_columns:
                last_year_result[column] +=  two_last_years_db.loc[aggr_periods[i],column]
        
        last_year_result['period']='Y'
        last_year_result['month']=12
        print(max(filt_asset_db.index))
        
        dict_data = dict(zip(last_year_result.index, last_year_result.values))
        
        #print(dict_data)
        
        last_year_result = pd.DataFrame(data=dict_data, index=[max(filt_asset_db.index)+1] )
        
        #print(f'\nlast_year_result:\n{last_year_result}')
        #print(type(last_year_result))
        
              
        # print(f'\last_year_result:\n{last_year_result}')   
        filt_asset_db = pd.concat([filt_asset_db, last_year_result])
        # print(f'\filt_asset_db:\n{filt_asset_db}')   
        
        print(f'\nfilt_asset_db:\n{filt_asset_db[filt_asset_db["year"] == last_year]}')   
        
        print(f'\nasset_db:\n{asset_db[(asset_db["year"] == last_year) | (asset_db["year"] == last_year-1)]}')   
        
   