import time
import openpyxl
import pandas as pd
import datetime as dt
from datetime import date, timedelta
import numpy as np
import investpy as inv
import re
from urllib.request import urlopen
from zipfile import ZipFile

# functios for the pipeline
def log(f):
    def wrapper(df, *args, **kwargs):
        tic = dt.datetime.now()
        result= f(df, *args, **kwargs)
        toc= dt.datetime.now()
        print(f"{f.__name__} took {toc-tic}")
        return result
    return wrapper

def get_countries_lst():
    lst = inv.get_bonds_list()
    df = pd.DataFrame(lst, columns=['countries'])
    df['countries'] = df['countries'].str.split("(\d+)").str[0]
    lst_paises = df['countries'].unique()
    return lst_paises

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

@log
def sort_months_year(text):
    ''' Funcition that order the futures curve rates names to cal the right function'''
    lst1 = []
    lst2 = []
    
    for i in text:
        regexp_month = re.compile(r'(\d+)M')
        regexp_year = re.compile(r'(\d+)Y')
        if regexp_month.search(i):
            lst1.append(i)
        elif regexp_year.search(i):
            lst2.append(i)
         
    lst1.sort(key=natural_keys)
    lst2.sort(key=natural_keys)
    lst_f = lst1+lst2
            
    return lst_f

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate

def get_curvature(df):
    """ calculates a proxy for the curvature of the futures curve to visualize contango or backwardation over the curve (matplotlib)
    
    """
    #calculating the curvature of the curve by date
    dates = [str(x)[0:10] for x in df.index] #getting dates to plot after 
    df = df.reset_index(drop=True) 
    #print(df)
    df = df.apply(lambda x: sum(np.gradient(x)), axis=1).reset_index()
    df['index'] = dates
    df.columns = ['date','value']
    df.sort_index(inplace=True,ascending=True)
    df.set_index('date',inplace=True)
    return df

def get_data_di_countries(country):
    #pegando lista de bonds do país
    lst_bonds = inv.get_bonds_list(country)
    # print(lst_bonds)
    #organizando lista de bonds
    lst_bonds = sort_months_year(lst_bonds)

    ide_5y = find_5y(lst_bonds)
    #lst_bonds = lst_bonds[0:-2]
    # print(len(lst_bonds))
    # #cutting the short term rates and long term rates
    #half= int(len(lst_bonds)/2)
    first_half = lst_bonds[0:ide_5y]
    print(first_half)
    second_half = lst_bonds[ide_5y:]
    print(second_half)

    #lista parametros de dados
    data_inicio = '01/02/2022'
    last_week_day = prev_weekday(date.today())
    data_fim = pd.to_datetime(last_week_day).strftime('%d/%m/%Y')
    #for loop para agregar os dados 
    bonds = pd.DataFrame()

    try:
    # block raising an exception
        for prazo in lst_bonds:
            bonds[prazo] = inv.get_bond_historical_data(prazo, from_date=data_inicio, to_date=data_fim)['Close']
    except:
        pass
        
    bonds.index = pd.to_datetime(bonds.index)
    bonds = bonds.fillna(method='ffill')
    #bonds['Spot Rate'] = data['RU']
    #bonds.insert(loc=0, column='Spot R', value=data['RU']) #checar se alinha as duas bases de forma coerente
    #bonds = bonds.fillna(method='ffill')
    #data = pd.DataFrame()
    data = get_curvature(bonds)
    #data = get_curvature(bonds[first_half])
    # data['long'] = get_curvature(bonds[second_half])
    return data


def find_5y(lst):  
    ide = [ i for i, word in enumerate(lst) if word.endswith('5Y') ]
    return ide
#################### pipeline ##################################################################################################

def find_5y(lst):  
    ide = [i for i, item in enumerate(lst) if re.search('5Y', item)]

    return ide

def get_daily_data(country):
    #pegando lista de bonds do país
    lst_bonds = inv.get_bonds_list(country)

    #organizando lista de bonds
    lst_bonds = sort_months_year(lst_bonds)

    # # #cutting the short term rates and long term rates
    # half= int(len(lst_bonds)/2)
    # first_half = lst_bonds[0:half]
    # print(first_half)
    # second_half = lst_bonds[half:]
    # print(second_half)
    ide_5y = find_5y(lst_bonds)[0]

    #lst_bonds = lst_bonds[0:-2]
    # print(len(lst_bonds))
    # #cutting the short term rates and long term rates
    #half= int(len(lst_bonds)/2)
    first_half = lst_bonds[0:ide_5y]
    second_half = lst_bonds[ide_5y:]

    #lista parametros de dados

    last_week_day = prev_weekday(date.today())
    data_inicio = '01/01/2019'
    data_fim = pd.to_datetime(last_week_day).strftime('%d/%m/%Y')
    #for loop para agregar os dados 
    bonds = pd.DataFrame()

    try:
    # block raising an exception
        for prazo in lst_bonds:
            bonds[prazo] = inv.get_bond_historical_data(prazo, from_date='20/02/2020', to_date=data_fim)['Close']
    except:
        pass
        
    bonds.index = pd.to_datetime(bonds.index)
    bonds = bonds.fillna(method='ffill')
    bonds = bonds.ffill()

    data = get_curvature(bonds)
    data_short = get_curvature(bonds[first_half])
    data_long = get_curvature(bonds[second_half])
    return data, data_short, data_long, bonds


def add_data_pipe():
    ''' add data'''

    countries_lst = ['Australia', 'Belgium', 'Brazil', 'Canada', 'Chile',
       'China', 'Colombia', 'Czech Republic', 'Egypt', 'France', 'Germany',
       'Greece', 'Hong Kong', 'Hungary', 'India', 'Indonesia', 'Israel',
       'Italy', 'Japan', 'Malaysia', 'Mexico', 'Morocco',
       'Netherlands', 'Pakistan', 'Portugal', 'Romania', 'Russia',
       'Singapore', 'Slovenia', 'South Africa', 'South Korea', 'Spain',
       'Sri Lanka', 'Thailand', 'Turkey', 'Uganda',
       'United Kingdom', 'United States', 'Vietnam']
    
                    
    _full = pd.DataFrame()
    _short = pd.DataFrame()
    _long = pd.DataFrame()
    _bonds = pd.DataFrame()
    
    df_full = pd.DataFrame()
    df_short = pd.DataFrame()
    df_long = pd.DataFrame()
    df_melt = pd.DataFrame(columns=['Date','variable','value'])

    for i in countries_lst:
        _full, _short, _long, _bonds = get_daily_data(i)
        time.sleep(30) 
        df_bonds = pd.DataFrame()
        df_bonds= df_bonds.append(_bonds)
        df_bonds.to_excel(f'Bonds_{i}.xlsx')
        df_bonds = df_bonds.reset_index().melt(id_vars='Date')
        df_melt = df_melt.append(df_bonds)

        df_full[i] = _full
        df_short[i] = _short
        df_long[i] = _long

    df_melt.to_excel('database_melted_bonds.xlsx')
    #df_full = pd.read_excel('database_full.xlsx')
    #df_full = df_full.append(_full)
    df_full.to_excel('database_full_5y.xlsx')

    #df_short = pd.read_excel('database_short.xlsx')
    #df_short= df_short.append(_short)
    df_short.to_excel('database_short_5y.xlsx')

    #df_long = pd.read_excel('database_long.xlsx')
    #df_long  = df_long.append(_long)
    df_long.to_excel('database_short_5y.xlsx')

    return print('fineshed building the dataframes')
#####################################################################################################

add_data_pipe()
