# importando as biblitecas necessárias
import streamlit as st
import pandas as pd
import datetime as dt
from datetime import datetime
from datetime import date, timedelta
import numpy as np
import plotly.graph_objects as go
import investpy as inv
import numpy as np
import re
import time
from urllib.request import urlopen
from zipfile import ZipFile
from pycountry_convert import *
import plotly_express as px

################################################################################# Funções auxíliares ###################################################################

def log(f):
    def wrapper(df, *args, **kwargs):
        tic = dt.datetime.now()
        result= f(df, *args, **kwargs)
        toc= dt.datetime.now()
        print(f"{f.__name__} took {toc-tic}")
        return result
    return wrapper

def dates_map():
    meses = {'OUT':'10','DEZ':'12', 'AGO':'8','FEV':'2', 'MAR':'3', 'ABR':'4', 'SET':'9', 'NOV':'11', 'JAN':'1','JUL':'7', 'JUN':'6', 'MAI':'5'}
    return meses 

################################################################################# Funções para pagina 1 ###################################################################

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

@log
def ts_plot(df, nome, units,source):
    
    fig = go.Figure()
    #colors = ['#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094']
    #colors =['#10022D','#090437','#060C41','#081E4B','#0A3254','#2A5A6C','#4A7E83','#6A9B96','#8AB2A6','#ABC8BB','#CDDED3']
    #colors =  ['#001D17','#5B7587','#9AAAB2','#0A3254','#1A405E','#2B4D68','#3B5B72','#4B687D','#5B7587','#6B8392','#7B909D','#8A9DA8','#9AAAB2','#A9B6BE','#B9C3C9','#003233','#023545']
    colors = ['#E0D253','#7AADD4','#0A3254','#1D4568','#30587C','#486B8E','#607EA0','#7891B0','#8FA4C0','#A7B7CF','#BFCBDE','#031820','#10022D','#090437','#060C41','#081E4B','#B2292E']
    print(df.columns)
    for i in range(len(df.columns)):
        fig.add_trace(go.Scatter(
                x=df.index, y=df.iloc[:, i], line=dict(color=colors[i], width=2), name=df.columns[i]))

    fig.update_layout(title={ 'text': '<b>'+ nome+'<b>','y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             title_font_size=14,
                             xaxis_title=f"{source}",
                             yaxis_title=units, 
                             template='plotly_white',
                             font_family="Verdana",
                             images=[dict(source='https://raw.githubusercontent.com/caiquecober/Research/master/logo_sem_nome.-PhotoRoom.png',
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5,
                                 sizex=0.65, sizey=0.65,
                                 opacity=0.5,
                                 xanchor="center",
                                 yanchor="middle",
                                 sizing="contain",
                                 visible=True,
                                 layer="below")],
                             legend=dict(
                                 orientation="h",
                                 yanchor="bottom",
                                 y=-0.3,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=True
                                 )
                                 
    return fig

@st.cache()
def get_data_di_countries(country):
    #pegando lista de bonds do país
    lst_bonds = inv.get_bonds_list(country)
    #print(lst_bonds)
    #organizando lista de bonds
    lst_bonds = sort_months_year(lst_bonds)
    #lst_bonds = lst_bonds[0:-2]
    #print(len(lst_bonds))
    #cutting the short term rates and long term rates
    half= int(len(lst_bonds)/2)
    first_half = lst_bonds[0:half]
    #print(first_half)
    second_half = lst_bonds[half:]
    #print(second_half)

    #lista parametros de dados
    data_inicio = '03/03/2019'
    last_week_day = prev_weekday(date.today())
    data_fim = pd.to_datetime(last_week_day).strftime('%d/%m/%Y')
    #for loop para agregar os dados 
    bonds = pd.DataFrame()

    for prazo in lst_bonds:
        bonds[prazo] = inv.get_bond_historical_data(prazo, from_date=data_inicio, to_date=data_fim)['Close']
        
    bonds.index = pd.to_datetime(bonds.index)
    bonds = bonds.fillna(method='ffill')
    #bonds['Spot Rate'] = data['RU']
    #bonds.insert(loc=0, column='Spot R', value=data['RU']) #checar se alinha as duas bases de forma coerente
    #bonds = bonds.fillna(method='ffill')
    data = pd.DataFrame()
    data['full'] = get_curvature(bonds)
    data['short'] = get_curvature(bonds[first_half])
    data['long'] = get_curvature(bonds[second_half])
    return country, data, bonds

def get_data_di_groups(country):
    #pegando lista de bonds do país
    lst_bonds = inv.get_bonds_list(country)
    #organizando lista de bonds
    lst_bonds = sort_months_year(lst_bonds)
    half= int(len(lst_bonds)/2)
    first_half = lst_bonds[0:half]
    second_half = lst_bonds[half:]
    #lista parametros de dados
    data_inicio = '01/02/2020'
    last_week_day = prev_weekday(date.today())
    data_fim = pd.to_datetime(last_week_day).strftime('%d/%m/%Y')
    #for loop para agregar os dados 
    bonds = pd.DataFrame()

    for prazo in lst_bonds:
        bonds[prazo] = inv.get_bond_historical_data(prazo, from_date=data_inicio, to_date=data_fim)['Close']
        
    bonds.index = pd.to_datetime(bonds.index)
    bonds = bonds.fillna(method='ffill')
    data_full = get_curvature(bonds)
    data_short = get_curvature(bonds[first_half])
    data_long = get_curvature(bonds[second_half])
    return data_full, data_short, data_long

@log
def get_curvature(df):
    """ calculates a proxy for the curvature of the futures curve to visualize contango or backwardation over the curve (matplotlib)
    
    """
    #calculating the curvature of the curve by date
    dates = [str(x)[0:10] for x in df.index] #getting dates to plot after 
    df = df.reset_index(drop=True) 
    df = df.apply(lambda x: sum(np.gradient(x)), axis=1).reset_index()
    df['index'] = dates
    df.columns = ['date','value']
    df.sort_index(inplace=True,ascending=True)
    df.set_index('date',inplace=True)
    return df

def get_countries_lst():
    lst = inv.get_bonds_list()
    df = pd.DataFrame(lst, columns=['countries'])
    df['countries'] = df['countries'].str.split("(\d+)").str[0]
    lst_paises = df['countries'].unique()
    return lst_paises
################################################################################# Funções para pagina 2 ###################################################################

def get_spot_i():
    zipurl = 'https://www.bis.org/statistics/full_webstats_cbpol_d_dataflow_csv_row.zip'
    # Download the file from the URL
    zipresp = urlopen(zipurl)
        # Create a new file on the hard drive
    tempzip = open(r"C:\Windows\Temp\tempfile.zip", "wb")
        # Write the contents of the downloaded file into the new file
    tempzip.write(zipresp.read())
        # Close the newly-created file
    tempzip.close()
        # Re-open the newly-created file with ZipFile()
    zf = ZipFile(r"C:\Windows\Temp\tempfile.zip")
    df = pd.read_csv(zf.open('WEBSTATS_CBPOL_D_DATAFLOW_csv_row.csv'), header=2)
        # Extract its contents into <extraction_path>
        # note that extractall will automatically create the path
    #zf.extractall(path = '/tmp')
        # close the ZipFile instance
    zf.close()
    return df

@log
def clean_cb_rates(df):
    df = df.ffill().dropna()
    df['Time Period'] = pd.to_datetime(df['Time Period'])
    df.set_index('Time Period', inplace=True)
    df.columns = df.columns.str.strip('D:')
    return df


@log
def clean_data_spot_i(df):
    df = df[df.index>'2020-03-01']
    df = df.apply(lambda x: 0 if x.empty else x/x.iloc[0]-1.0)
    melt = df.reset_index().melt(id_vars='Time Period', var_name='iso2',value_name='pct_change_2020')
    melt = melt[~melt['iso2'].isin(['K','I','XM'])]
    melt['country_name']  = melt['iso2'].map(lambda a: country_alpha2_to_country_name(a))
    melt['code']  = melt['country_name'].map(lambda a: country_name_to_country_alpha3(a))
    melt['baseline'] = 0
    melt_pivot = melt.pivot_table(index='Time Period', columns= 'country_name', values='pct_change_2020')
    melt =  melt.set_index('Time Period')
    return melt, melt_pivot

@st.cache(allow_output_mutation=True)
def pipeline_spot_i():
    df = get_spot_i().pipe(clean_cb_rates).pipe(clean_data_spot_i)
    return df


def mp_conditions(db):
    db  = db.reset_index()
    db =  db[db['Time Period'] >'2021-03-03']
    db['Time Period'] =  db['Time Period'].dt.strftime('%m-%d-%Y')

    conditions = [db.pct_change_2020 == 0, 
                (db.pct_change_2020 > 0),
                (db.pct_change_2020 < 0) & (db.pct_change_2020 > -0.25),
                (db.pct_change_2020 <= -0.25) & (db.pct_change_2020 > -0.5),
                (db.pct_change_2020 <= -0.5) & (db.pct_change_2020 > -0.75),
                (db.pct_change_2020 <= -0.75) & (db.pct_change_2020 > -1)
                ]
    choices =  ['Neutral','Tight','Small acomodation', 'Medium acommodation','Strong acomodation','Very Strong acomodation']

    db['Monetary Policy Condition'] = np.select(conditions, choices, default=np.nan)
    db  = db.dropna()
    return db 

@log
def ts_plot(df, nome, units,source):
    
    fig = go.Figure()
    #colors = ['#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094']
    #colors =['#10022D','#090437','#060C41','#081E4B','#0A3254','#2A5A6C','#4A7E83','#6A9B96','#8AB2A6','#ABC8BB','#CDDED3']
    #colors =  ['#001D17','#5B7587','#9AAAB2','#0A3254','#1A405E','#2B4D68','#3B5B72','#4B687D','#5B7587','#6B8392','#7B909D','#8A9DA8','#9AAAB2','#A9B6BE','#B9C3C9','#003233','#023545']
    colors = ['#E0D253','#7AADD4','#0A3254','#1D4568','#30587C','#486B8E','#607EA0','#7891B0','#8FA4C0','#A7B7CF','#BFCBDE','#031820','#10022D','#090437','#060C41','#081E4B',]
    print(df.columns)
    for i in range(len(df.columns)):
        fig.add_trace(go.Scatter(
                x=df.index, y=df.iloc[:, i], line=dict(color=colors[i], width=2), name=df.columns[i]))

    fig.update_layout(title={ 'text': '<b>'+ nome+'<b>','y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             title_font_size=14,
                             xaxis_title=f"{source}",
                             yaxis_title=units, 
                             template='plotly_white',
                             font_family="Verdana",
                             images=[dict(source='https://raw.githubusercontent.com/caiquecober/Research/master/logo_sem_nome.-PhotoRoom.png',
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5,
                                 sizex=0.65, sizey=0.65,
                                 opacity=0.5,
                                 xanchor="center",
                                 yanchor="middle",
                                 sizing="contain",
                                 visible=True,
                                 layer="below")],
                             legend=dict(
                                 orientation="h",
                                 yanchor="bottom",
                                 y=-0.3,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=True
                                 )
                                 
    return fig



############################################# Streamlit  HTML  ##################################################################################################

html_header="""
<head>
<style> @import url('https://fonts.googleapis.com/css2?family=Mulish:wght@400;500;600;700;800&display=swap'); 
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&display=swap'); </style>
<title>C0D_ATA </title>
<meta charset="utf-8">
<meta name="keywords" content="Economics, data science, interest rates, streamlit, visualizer, data">
<meta name="description" content="C0D_ATA Data Project">
<meta name="author" content="@Cober">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:300%; color:#0A3254; font-family:Mulish; font-weight:800"> Interest rate term structure curvature   
<br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1px;"></h1>
"""

html_line_2="""
<br>
<hr style= "  display: block;
  margin-top: 0.3em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1px;">
"""

link_png = 'https://raw.githubusercontent.com/caiquecober/Research/master/logo_sem_nome.-PhotoRoom.png'

st.set_page_config(page_title="C0D_DATA - Interest Rates", page_icon=link_png, layout="wide")

padding = 1.2
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

st.markdown('<style>body{background-color: #D2D5D4}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style> 
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


############################## ST APP ###################### ################################################################################################

paginas = st.sidebar.selectbox('',['Selected countries','Interest rate curvature by Country','Geoviz - Spot interest rate'])

############################### Page 1 #######################################################################################################################
# df= get_vendas()

if paginas == 'Selected countries':

    #pegando os dados específicos com o df1 além do df inicial que é usado como base para todas as perspectivas
    country, df, curva = get_data_di_countries('United States')
    country1, df1, curva1 = get_data_di_countries('Brazil')

    config = {"displayModeBar": False, "showTips": False}
    ############################# Backend para criação das figuras #################################################################################
    
    fig0 = ts_plot(df.rolling(1).mean(),f'Curvature of yield curve of {country}','Curvature','')
    fig1 = ts_plot(df1.rolling(1).mean(),f'Curvature of yield curve of {country1}','Curvature','')
    fig2 = ts_plot(curva.rolling(15).mean(),f'Goverment bond rates of {country}','Interest rate 15 day rolling mean','')
    fig3 = ts_plot(curva1.rolling(15).mean(),f'Goverment bond rates of  {country1}','Interest rate 15 day rolling mean','')

    ################## ST LAYOUT ###################################################################################################
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig0, use_container_width=True,config=config)
    col2.plotly_chart(fig1, use_container_width= True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig2, use_container_width=True)
    col2.plotly_chart(fig3, use_container_width= True)


############################### Page 2 #######################################################################################################################
if paginas == 'Interest rate curvature by Country':
    with st.sidebar.expander("Choose country"): 
        lst_paises =  get_countries_lst()
        selected_country= st.selectbox('',lst_paises)
        country2, df2, curva2 = get_data_di_countries(selected_country)

        
    #plotting data of the selected country
    fig3 = ts_plot(df2.rolling(1).mean(),f'Curvature of yield curve of {country2}','Curvature','')
    fig4 = ts_plot(curva2.rolling(15).mean(),f'Goverment bond rates for {country2}','Interest rate 15 day rolling mean','')
    fig5 = ts_plot(df2.rolling(10).mean().diff(1),f'Curvature difference of  {country2}','15 day rolling mean','')
    fig6 = ts_plot(df2.rolling(10).mean().pct_change(1),f'Curvature pct. change of {country2}','15 day rolling mean','')


    ################## ST LAYOUT  do paginina 2####################################################################################################
    config = {"displayModeBar": False, "showTips": False}
    col1,col2 = st.columns(2)
    col1.plotly_chart(fig3, use_container_width=True,config=config)
    col2.plotly_chart(fig4, use_container_width=True,config=config)

    col1,col2 = st.columns(2)
    col1.plotly_chart(fig5, use_container_width=True,config=config)
    col2.plotly_chart(fig6, use_container_width=True,config=config)
    
############################### Page 3 #######################################################################################################################
if paginas == 'Geoviz - Spot interest rate': 
    #Data
    db, df  = pipeline_spot_i()  
    db_2 = mp_conditions(db)
    #Chose data
    # with st.sidebar.expander("Choose country"): 
    #     lst_paises =  db['country_name'].unique()
    #     selected_country= st.selectbox('',lst_paises )


    #fig6 = ts_plot(db[db.country_name==selected_country][['pct_change_2020','baseline']], nome=f'Spot interest rate relative to pre pandemic level for {selected_country}',units='level',source='')
    fig7 = px.choropleth(db_2, locations="code",
                    color='Monetary Policy Condition',
                    hover_name="country_name", # column to add to hover information
                    color_discrete_sequence= ['#7AADD4','#E0D253','#0A3254','#1D4568','#30587C','#B2292E','#486B8E','#607EA0','#607EA0'],#px.colors.sequential.Plasma_r,
                   animation_frame="Time Period")
    fig7.update_layout(title={ 'text': '<b>'+'The evolution of monetary policy conditions'+'<b>','y':1 ,'x':0.45,'xanchor': 'center','yanchor': 'top'},title_font_size=22, autosize=True,height=700)
    
    
    fig6 = px.histogram(db_2,x="Monetary Policy Condition",
                    color='Monetary Policy Condition',
                    hover_name="country_name", # column to add to hover information
                    color_discrete_sequence= ['#7AADD4','#E0D253','#0A3254','#1D4568','#30587C','#B2292E','#486B8E','#607EA0','#607EA0'],#px.colors.sequential.Plasma_r,
                   animation_frame="Time Period")
    fig6.update_layout(title={ 'text': '<b>'+'The evolution of the distribution of monetary policy conditions'+'<b>','y':1 ,'x':0.45,'xanchor': 'center','yanchor': 'top'},title_font_size=22, autosize=True,height=700,                            
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             template='plotly_white',
                             font_family="Verdana",
                             images=[dict(source='https://raw.githubusercontent.com/caiquecober/Research/master/logo_sem_nome.-PhotoRoom.png',
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5,
                                 sizex=0.65, sizey=0.65,
                                 opacity=0.5,
                                 xanchor="center",
                                 yanchor="middle",
                                 sizing="contain",
                                 visible=True,
                                 layer="below")])
    ################## ST LAYOUT  do paginina 3####################################################################################################
    config = {"displayModeBar": False, "showTips": False}
    st.plotly_chart(fig6, use_container_width=True,config=config)
    st.plotly_chart(fig7, use_container_width=True,config=config)

############################### Page 4 #######################################################################################################################

if paginas == 'Interest Rates curvature analyses by country':
    db, df  = pipeline_spot_i()
    with st.sidebar.expander("Choose country"): 
        lst_groups = ['G10','EM','BRICS']
        lst_paises =  db['country_name'].unique()
        selected_group= st.selectbox('',lst_groups )
        
        if selected_group=='G10':
            countries = ['Belgium', 'Canada', 'France', 'Germany', 'Italy', 'Japan', 'Netherlands', 'Sweden', 'Switzerland', 'United Kingdom', 'United States']
            df_full= pd.DataFrame()
            df_short= pd.DataFrame()
            df_long = pd.DataFrame()

            for i in countries:
                df_full[i],df_short[i],df_long[i] = get_data_di_groups(i)
                time.sleep(15) 
                
            fig3 = ts_plot(df_full.rolling(1).mean(),f'Curvature of yield curve of {selected_group}','Curvature','')
            fig4 = ts_plot(df_short.rolling(1).mean(),f'Curvature of yield curve of {selected_group}','Curvature','')
            fig5 = ts_plot(df_long.rolling(1).mean(),f'Curvature of yield curve of {selected_group}','Curvature','')

        elif selected_group == 'BRICS':
            countries = ['Brazil', 'Russia', 'India','China','South Africa']
            df_full= pd.DataFrame()
            df_short= pd.DataFrame()
            df_long = pd.DataFrame()

            for i in countries:
                df_full[i],df_short[i],df_long[i] = get_data_di_groups(i)
                time.sleep(15) 
                
            fig3 = ts_plot(df_full.rolling(1).mean(),f'Curvature of yield curve of {selected_group}','Curvature','')
            fig4 = ts_plot(df_short.rolling(1).mean(),f'Curvature of yield curve of {selected_group}','Curvature','')
            fig5 = ts_plot(df_long.rolling(1).mean(),f'Curvature of yield curve of {selected_group}','Curvature','')
               
 

################## ST LAYOUT  do paginina 4####################################################################################################
    config = {"displayModeBar": False, "showTips": False}
    st.plotly_chart(fig3, use_container_width=True,config=config)
    st.plotly_chart(fig4, use_container_width=True,config=config)
    st.plotly_chart(fig5, use_container_width=True,config=config)
         
         
        
    
    ############################ get rows that are in countries then pivot them to plot them!
    
################## ST LAYOUT do parte inferior ####################################################################################################
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

html_line="""
<br>
<br>
<br>
<br>
<p style="color:Gainsboro; text-align: left;">Fonte: Investing.com, BIS.</p>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">Made_by: C0D_ATA</p>
"""
st.markdown(html_line, unsafe_allow_html=True)
