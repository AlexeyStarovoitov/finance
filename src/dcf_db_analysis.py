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
        
        if two_last_years_crosstab.loc[last_year, 'Q'] == 2:
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
        elif two_last_years_crosstab.loc[last_year, 'Q'] == 1 and two_last_years_crosstab.loc[last_year, '6M'] == 0:
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])
        elif two_last_years_crosstab.loc[last_year, '6M'] != 0:
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==last_year) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year']==(last_year-1)) & (two_last_years_db['period']=='6M')].index.values.astype(int)[-1])	
        
        
        mod_columns = list(filter(filter_db, two_last_years_db.columns))
        last_year_result = two_last_years_db.loc[aggr_periods[0], :]
        
        # print(f'\nmod_columns:\n{mod_columns}')
        # print(f'\nlast_year_result:\n{last_year_result}')
        # print(last_year_result.shape)
        # print(last_year_result['period'])
        # print(two_last_years_db)  
        
        # print(aggr_periods)
        
        for i in range(1,len(aggr_periods)):
            for column in mod_columns:
                last_year_result[column] +=  two_last_years_db.loc[aggr_periods[i],column]
        
        last_year_result['period']='Y'
        print(max(filt_asset_db.index))
        
        #must be debugged
        print(list(last_year_result.index))
        print(np.array(last_year_result.values))
        last_year_result = pd.DataFrame(data=list(last_year_result.values), index=[max(filt_asset_db.index)] , columns=list(last_year_result.index))
        
        print(f'\nlast_year_result:\n{last_year_result}')
        print(type(last_year_result))
        
        #print(f'\nfilt_asset_db:\n{filt_asset_db}')         
        
        pd.concat(filt_asset_db, last_year_result, axis=1)
        
    # print(filt_asset_db)  