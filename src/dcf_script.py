import pandas as pd
import numpy as np

class DCF_calc:
    def __init__(self, csv_file, betta, rf, rm, country_risk, horizont):

        self.betta = betta
        self.rf = rf
        self.rm = rm
        self.country_risk = country_risk
        self.horizont = horizont

        asset_db = pd.read_csv(csv_file)
        filt_asset_db = asset_db[asset_db['period']=='Y']
        
        last_year = asset_db['year'].max()
        filt_last_year = filt_asset_db['year'].max()
        
        
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
            
            
            dict_data = dict(zip(last_year_result.index, last_year_result.values))
            last_year_result = pd.DataFrame(data=dict_data, index=[max(filt_asset_db.index)+1] )
            filt_asset_db = pd.concat([filt_asset_db, last_year_result])
           
        
        self.asset_db = filt_asset_db
                    
            
            
    @staticmethod
    def filter_db(column):
        patterns = ['capex', 'profit', 'revenue', 'earning', 'amort', 'expense']
        for pattern in patterns:
            if re.search(pattern, column):
                return True
        
        return False
        
    def calculate_fair_share_price(self):
        # Enterprice value calculation
        lst_row = self.asset_db[self.asset_db['year'] == self.last_year].iloc[0]
        self.ev = lst_row['capital'] + lst_row['total_debt'] - lst_row['cash_and_equiv']

        #WACC calculation

        tax_rate = 1 - lst_row['earnings'] / lst_row['earnings_wo_tax']
        we = lst_row['capital']/(lst_row['capital'] + lst_row['total_debt'])
        wd = lst_row['total_debt']/(lst_row['capital'] + lst_row['total_debt'])

        #ke calcultation via CAPM method
        betta_l = self.betta*(1- tax_rate)*lst_row['total_debt']/lst_row['equity']
        ke = self.rf + betta_l*(self.rm-self.rf)

        #kd calculation
        kd = lst_row['interest_expense']/lst_row['total_debt']

        self.wacc = kd*wd*(1-tax_rate)+ke*we

        #npv calculation
        npv_dataset = self.asset_db[['year', 'earnings_wo_tax', 'depr_depl_amort', 'capex', 'current_assets', 'current_liabilities']]
        nwc = npv_dataset['current_assets'] - npv_dataset['current_liabilities']
        nwc.rename('nwc')
        pd.concat([npv_dataset, nwc], axis=1, sort=False)
        nwc_change = pd.Series(np.zeros(len(npv_dataset)), index = npv_dataset.index)

        aver_ebt = 0
        aver_amrtz = 0
        aver_capex = 0
        aver_nwc_change = 0

        for i in range(1, len(npv_dataset)):
            aver_ebt = aver_ebt + (npv_dataset['earnings_wo_tax'].iloc[i] - npv_dataset['earnings_wo_tax'].iloc[i-1])/npv_dataset['earnings_wo_tax'].iloc[i-1]
            aver_amrtz = aver_amrtz + (npv_dataset['depr_depl_amort'].iloc[i] - npv_dataset['depr_depl_amort'].iloc[i-1])/npv_dataset['depr_depl_amort'].iloc[i-1]
            aver_capex = aver_capex + (npv_dataset['capex'].iloc[i] - npv_dataset['capex'].iloc[i - 1])/npv_dataset['capex'].iloc[i - 1]
            if i >= 2:
                nwc_change.iloc[i] = npv_dataset['nwc'].iloc[i] - npv_dataset['nwc'].iloc[i-1]
                nwc_change.iloc[i-1] = npv_dataset['nwc'].iloc[i-1] - npv_dataset['nwc'].iloc[i - 2]
                aver_nwc_change = aver_nwc_change + (nwc_change.iloc[i] - nwc_change.iloc[i-1])/nwc_change.iloc[i-1]

        aver_ebt = aver_ebt / (len(npv_dataset)-1)
        aver_amrtz = aver_amrtz / (len(npv_dataset)-1)
        aver_capex = aver_capex / (len(npv_dataset) - 1)
        aver_nwc_change = aver_nwc_change / (len(npv_dataset) - 2)
        npv_dataset.assign({'nwc_change':nwc_change.values})


        df_ = pd.DataFrame(index=range(self.horizont), columns=npv_dataset.columns)
        df_ = df_.fillna(0)
        old_len = len(npv_dataset)
        npv_dataset.append(df_, ignore_index=True)

        for i in range(old_len, old_len + self.horizont):
            npv_dataset.iloc[i]['year'] = npv_dataset.iloc[i-1]['year']
            npv_dataset.iloc[i]['earnings_wo_tax'] = npv_dataset.iloc[i]['earnings_wo_tax'] * (1 + aver_ebt)
            npv_dataset.iloc[i]['depr_depl_amort'] =  npv_dataset.iloc[i-1]['depr_depl_amort']* (1 + aver_amrtz)
            npv_dataset.iloc[i]['capex'] = npv_dataset.iloc[i - 1]['capex'] * (1 + aver_capex)
            npv_dataset.iloc[i]['nwc_change'] = npv_dataset.iloc[i - 1]['nwc_change'] * (1 + aver_nwc_change)
            j = j + 1


if __name__=='__main__':
    dcf_clc = DCF_calc('..\\extra\\FIVE_financemarker.csv', 1, 7.5, 20, 5, 1)
    dcf_clc.asset_db.describe()