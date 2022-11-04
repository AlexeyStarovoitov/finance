import pandas as pd
import numpy as np
import numpy_financial as npf
import re

def filter_db(column):
    patterns = ['capex', 'profit', 'revenue', 'earning', 'amort', 'expense']
    for pattern in patterns:
        if re.search(pattern, column):
            return True
        
    return False
    
    
def interpolate_last_year(asset_db, filt_asset_db):

    last_year = asset_db['year'].max()

    two_last_years_db = asset_db[(asset_db['year'] == last_year) | (asset_db['year'] == (last_year - 1))]
    two_last_years_crosstab = pd.crosstab(index=asset_db['year'], columns=asset_db['period'])
    #print(two_last_years_crosstab)

    aggr_periods = []

    if two_last_years_crosstab.loc[last_year, '9M'] == 1:
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == last_year) & (
                    two_last_years_db['period'] == '9M')].index.values.astype(int)[-1])
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == 'Q')].index.values.astype(int)[-1])
    elif two_last_years_crosstab.loc[last_year, 'Q'] == 2 and two_last_years_crosstab.loc[last_year, '6M'] == 1:
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == last_year) & (
                    two_last_years_db['period'] == '6M')].index.values.astype(int)[-1])
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == '6M')].index.values.astype(int)[-1])
    elif two_last_years_crosstab.loc[last_year, 'Q'] == 1:
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == last_year) & (
                    two_last_years_db['period'] == 'Q')].index.values.astype(int)[-1])
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == 'Q')].index.values.astype(int)[-1])
        aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == '6M')].index.values.astype(int)[-1])

    mod_columns = list(filter(filter_db, two_last_years_db.columns))
    last_year_result = two_last_years_db.loc[aggr_periods[0], :].copy()

    for i in range(1, len(aggr_periods)):
        for column in mod_columns:
            last_year_result.loc[column] += two_last_years_db.loc[aggr_periods[i], column]

    last_year_result.loc['period'] = 'Y'
    last_year_result.loc['month'] = 12

    dict_data = dict(zip(last_year_result.index, last_year_result.values))
    last_year_result = pd.DataFrame(data=dict_data, index=[max(filt_asset_db.index) + 1])

    # print(f'\last_year_result:\n{last_year_result}')
    filt_asset_db = pd.concat([filt_asset_db, last_year_result])
    # print(f'\filt_asset_db:\n{filt_asset_db}')
    # print(f'\nfilt_asset_db:\n{filt_asset_db[filt_asset_db["year"] == last_year]}')
    # print(f'\nasset_db:\n{asset_db[(asset_db["year"] == last_year) | (asset_db["year"] == last_year-1)]}')

    return filt_asset_db


if __name__ == '__main__':

    #Initial data:
    csv_file = '../extra/FIVE_financemarker.csv'
    Rf = 8.75
    Rm = 25.95
    betta = 0.751410601722233
    CPR = 16.78
    #CPR = 0
    invst_hrznt = 2

    #Asset Db Initialization

    pd.set_option('display.max.columns', None)
    asset_db = pd.read_csv(csv_file)
    filt_asset_db = asset_db[asset_db['period']=='Y']
    last_year = asset_db['year'].max()
    filt_last_year = filt_asset_db['year'].max()

    if last_year != filt_last_year:
        asset_db = interpolate_last_year(asset_db, filt_asset_db)

    #Evaluation price calculation
    last_year_result = asset_db.iloc[-1, :].copy()
    share_nums = []
    share_prices = []
    for column in last_year_result.index:
        if re.search('num[1-9].??$', column):
            share_nums.append(last_year_result[column])
        if re.search('price[1-9].??_day$', column):
            share_prices.append(last_year_result[column])


    last_year_result['capital'] = 0
    for (share_price,share_num) in list(zip(share_prices, share_nums)):
        last_year_result['capital'] += share_price*share_num

    share_ratios = [share_price/share_prices[0] for share_price in share_prices]
    capital_structure = list(zip(share_ratios, share_nums))

    ev = last_year_result['capital'] + last_year_result['total_debt'] - last_year_result['cash_and_equiv']

    #WACC calculation
    #print(f'asset_db:\n{asset_db}')
    #print(asset_db.columns)

   #wd/we calculation
    we = last_year_result['equity']/(last_year_result['equity']+last_year_result['total_debt'])
    wd = last_year_result['total_debt'] / (last_year_result['equity'] + last_year_result['total_debt'])
    #print(f'we1: {we}\nwd1: {wd}\n')

    ke = Rf + betta*(Rm-Rf) + CPR
    kd = last_year_result['interest_expense']/last_year_result['total_debt']*100
    T = (last_year_result['earnings_wo_tax'] - last_year_result['earnings'])/last_year_result['earnings_wo_tax']

    WACC = (ke*we*(1-T) + kd*wd)/100
    #print(f'WACC: {WACC}')

    #FCF calculation
    fcf_indexes = ['earnings', 'depr_depl_amort', 'capex', 'ebitda', 'nwc', 'delta_nwc', 'fcf']
    fcf_columns = list(asset_db['year'].apply(str).values)
    for year in range(asset_db['year'].max() + 1, asset_db['year'].max() + invst_hrznt + 1):
        fcf_columns.append(str(year))

    #print(f'fcf_columns: {fcf_columns}')

    fcf_df = pd.DataFrame(data = np.zeros((len(fcf_indexes), len(fcf_columns))), index = fcf_indexes, columns = fcf_columns)

    init_min_max_year = [str(asset_db['year'].min()),str(asset_db['year'].max())]


    for i in fcf_indexes:
        #print(f'asset_db[i]:\n{asset_db[i]}')
        if i in ['earnings', 'depr_depl_amort', 'capex']:
            fcf_df.loc[i, init_min_max_year[0]:init_min_max_year[1]] = np.array(asset_db[i].values)
        elif i == 'ebitda':
            fcf_df.loc[i, init_min_max_year[0]:init_min_max_year[1]] = np.array(asset_db['earnings_wo_tax'] + (asset_db['interest_expense'] - asset_db['interest_income']) + asset_db['depr_depl_amort'])
        elif i == 'nwc':
            nwc_series = asset_db['current_assets'] - asset_db['current_liabilities']
            fcf_df.loc[i, init_min_max_year[0]:init_min_max_year[1]] = np.array(nwc_series.values)
        elif i == 'delta_nwc':
            for j in range(int(init_min_max_year[0])+1, int(init_min_max_year[1])+1):
                fcf_df.loc[i, str(j)] = fcf_df.loc['nwc', str(j)] - fcf_df.loc['nwc', str(j-1)]
        elif i == 'fcf':
            fcf_df.loc[i, :] = fcf_df.loc['earnings', :] + fcf_df.loc['depr_depl_amort', :] - fcf_df.loc['capex', :]  - fcf_df.loc['delta_nwc', :]

    interp_compnts = ['earnings', 'depr_depl_amort', 'capex', 'ebitda', 'nwc']
    interp_coef = pd.Series(data=np.zeros(len(interp_compnts)), index = interp_compnts)
    for i in interp_compnts:
        for j in range(int(init_min_max_year[0])+1, int(init_min_max_year[1])+1):
            interp_coef[i] += (fcf_df.loc[i, str(j)] - fcf_df.loc[i, str(j-1)]) / fcf_df.loc[i, str(j-1)]
        interp_coef[i] = interp_coef[i]/(int(init_min_max_year[1]) - int(init_min_max_year[0]))

    ext_period = [str(int(init_min_max_year[1]) + 1),  str(int(init_min_max_year[1]) + invst_hrznt)]
    for i in fcf_indexes:
        if i in interp_compnts:
            for j in range(int(ext_period[0]), int(ext_period[1])+1):
                fcf_df.loc[i, str(j)] = fcf_df.loc[i, str(j-1)]*(1+interp_coef[i])
        elif i == 'delta_nwc':
            for j in range(int(ext_period[0]), int(ext_period[1])+1):
                fcf_df.loc[i, str(j)] = fcf_df.loc['nwc', str(j)] - fcf_df.loc['nwc', str(j - 1)]
        elif i == 'fcf':
            fcf_df.loc[i, ext_period[0]:ext_period[1]] = fcf_df.loc['earnings', ext_period[0]:ext_period[1]] + fcf_df.loc['depr_depl_amort', ext_period[0]:ext_period[1]] - \
                                                         fcf_df.loc['capex',ext_period[0]:ext_period[1]] - fcf_df.loc['delta_nwc', ext_period[0]:ext_period[1]]


    #print(f'interp_coef:\n{interp_coef}')
    #print(f'fcf_df:\n{fcf_df}')

    #Net present value calculation
    #last_year_result = asset_db.iloc[-1, :].copy()
    npv = npf.npv(WACC, fcf_df.loc['fcf', ext_period[0]:ext_period[1]].values)
    ev_ebitda = ev/fcf_df.loc['ebitda', init_min_max_year[1]]
    tv = ev_ebitda*fcf_df.loc['ebitda', ext_period[1]]/(1+WACC)**invst_hrznt
    ev_dcf = npv + tv
    ev_cap = ev_dcf - last_year_result['total_debt'] + last_year_result['cash_and_equiv']


    priv_share_num = 0
    for (ratio_num, num) in capital_structure:
        priv_share_num += ratio_num*num
    priv_share_num = int(priv_share_num)


    ev_base_price = ev_cap/priv_share_num
    ev_share_prices  = [ev_base_price*capital_structure[i][0] for i in range(len(capital_structure))]
    cur_share_prices = share_prices

    print('Num  Current price   Evaluated price Margin,%')
    for i in range(len(ev_share_prices)):
        stock_margin = (ev_share_prices[i] - cur_share_prices[i]) / cur_share_prices[i] * 100
        print(f'{i}:  {cur_share_prices[i]} {ev_share_prices[i]}    {stock_margin}')

