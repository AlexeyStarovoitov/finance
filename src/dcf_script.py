import pandas as pd
import numpy as np

class DCF_calc:
    def __init__(self, csv_file, betta, rf, rm, country_risk, horizont):

        self.betta = betta
        self.rf = rf
        self.rm = rm
        self.country_risk = country_risk
        self.horizont = horizont

        aggregate_fields = ['revenue', 'gross_profit', 'sel_gen_adm_expenses', \
                                'total_expenses', 'operating_income', 'interest_income']

        asset_db = pd.read_csv(csv_file)
        self.asset_db = asset_db_max_year[asset_db_max_year['period']=='Y']
        
        init_last_year = self.asset_db['year'].max()
        res_last_year = asset_db['year'].max()
        
        if init_last_year != res_last_year:
            
            last_year_period = ['6M']
            
            year_cross_tab = pd.crosstab(index = asset_db['period'], values = asset_db['year'])
            if year_cross_tab['6M', init_last_year] == 0:
                last_year_period.append('Q')
            
            asset_db_last_year = asset_db[asset_db['year'] == init_last_year]
            asset_db_last_year_1 = asset_db[(asset_db['period'] in last_year_period) & \
                                   asset_db['year'] == (init_last_year - 1)]
            
            for entry in asset_db_last_year_1.index:
                for column in asset_db_last_year_1.columns:
                    if column.find('revenue') != -1 or column.find('expenses') == -1 or \
                       column.find('income') != -1 or column.find('capex') != -1 or column.find('profit') != -1:
                       asset_db_last_year[:1][column] +=  asset_db_last_year_1.loc[entry, column]
            
            pd.concat(self.asset_db, asset_db_last_year, axes = 0, sort = False)
                    
            
            
        
        
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