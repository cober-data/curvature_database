import streamlit as st 
import plotly.graph_objects as go 
import pandas as pd 
import numpy as np 
from scipy.stats import zscore


def ts_plot(df, nome, units,space):
    
    fig = go.Figure()
    #colors = ['#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094', '#B2292E','#336094','#E0D253', '#0A3254', '#7AADD4', '#B2292E','#336094']
    #colors =['#10022D','#090437','#060C41','#081E4B','#0A3254','#2A5A6C','#4A7E83','#6A9B96','#8AB2A6','#ABC8BB','#CDDED3']
    #colors =  ['#001D17','#5B7587','#9AAAB2','#0A3254','#1A405E','#2B4D68','#3B5B72','#4B687D','#5B7587','#6B8392','#7B909D','#8A9DA8','#9AAAB2','#A9B6BE','#B9C3C9','#003233','#023545']
    colors = ['#E0D253','#7AADD4','#0A3254','#1D4568','#30587C','#486B8E','#607EA0','#7891B0','#8FA4C0','#A7B7CF','#BFCBDE','#031820','#10022D','#090437','#060C41','#081E4B','#081E4B','#023545']
    print(df.columns)
    for i in range(len(df.columns)):
        fig.add_trace(go.Scatter(
                x=df.index, y=df.iloc[:, i], line=dict(color=colors[i], width=2), name=df.columns[i]))

    fig.update_layout(title={ 'text': '<b>'+ nome+'<b>','y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             title_font_size=14,
                             xaxis_title="",
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
                                 y=space,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=True, height=450
                                 )
                                 
    return fig



@st.cache()
def load_curvature():
    ''' simple function to load and cache de data'''

    df_short = pd.read_excel('database_short_5y.xlsx')
    df_long = pd.read_excel('database_long_5y.xlsx')
    df_full = pd.read_excel('database_full_5y.xlsx')

    return df_full,df_short,df_long
 

def build_country_df():
    ''' function to build the df with the curvatures'''
    df_country = df_full[['date',f'{slc_country}']]
    df_country.columns =  ['date','Full']
    df_country['Long'] = df_long[slc_country]
    df_country['Short'] = df_short[slc_country]
    df = df_country.set_index('date')
    df = df.mask(df.sub(df.mean()).div(df.std()).abs().gt(2.7))
    df = df.fillna(method='ffill')
    return df

def outliers_nann(df):
    ''' replace outliers for nan'''

    df =  df.apply(zscore)

    conditions=[(df.Long < 3) or (df.Long > 3),
                (df.Full < 3) or (df.Full > 3),
                (df.Short < 3) or (df.Short > 3)
                ]

    choices =  [np.nan, np.nan, np.nan]

    df = np.select(conditions, choices, default=np.nan)

    return df

def outliers_nan(df):
    df = df.mask(df.sub(df.mean()).div(df.std()).abs().gt(3))
    return df 


############################################# HTML CODE ##############################################################################

html_header="""<head>
<style> @import url('https://fonts.googleapis.com/css2?family=Mulish:wght@400;500;600;700;800&display=swap'); 
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&display=swap'); </style>
<title>C0D_ATA </title>
<meta charset="utf-8">
<meta name="keywords" content="Economics, data science, interest rates, bonds, streamlit, visualizer, data">
<meta name="description" content="C0D_ATA Data Project">
<meta name="author" content="@Cober">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:300%; color:#0A3254; font-family:Mulish; font-weight:800"> Interest Rate Term Structure
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

st.set_page_config(page_title="C0D_DATA - Interest Rate Term Structure", page_icon=link_png, layout="wide")

padding = 1.5
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
 
####################################################### Load Data #####################################################################################################

# create list with available countries
countries_lst = ['Australia', 'Belgium', 'Brazil', 'Canada', 'Chile',
       'China', 'Colombia', 'Czech Republic', 'Egypt', 'France', 'Germany',
       'Greece', 'Hong Kong', 'Hungary', 'India', 'Indonesia', 'Israel',
       'Italy', 'Japan', 'Malaysia', 'Mexico', 'Morocco',
       'Netherlands', 'Pakistan', 'Portugal', 'Romania', 'Russia',
       'Singapore', 'Slovenia', 'South Africa', 'South Korea', 'Spain',
       'Sri Lanka', 'Thailand', 'Turkey', 'Uganda',
       'United Kingdom', 'United States', 'Vietnam']

# select a country
slc_country =  st.selectbox('',countries_lst)

# read in bonds for that country
df = pd.read_excel(f'Bonds_{slc_country}.xlsx')
df = df.set_index('Date')
#df = df.mask(df.sub(df.mean()).div(df.std()).abs().gt(3))
df = df.fillna(method='ffill')

# load in curvature calculations
df_full, df_short, df_long =  load_curvature()

#build df for a given selected country set as global variable
df_country = build_country_df()

##################################################### Streamlit app front end plots and html injections ###########################################################################

fig = ts_plot(df_country,f'Bond term structure curvature for {slc_country}','Curvature',-0.3 )
fig1 = ts_plot(df,f'Bond yields in {slc_country}','Yield',-0.5)


config = {"displayModeBar": False, "showTips": False}

st.plotly_chart(fig, use_container_width=True,config=config )
st.plotly_chart(fig1, use_container_width=True,config=config)

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
<p style="color:Gainsboro; text-align: left;">Source: OECD, Nicolas Woloszko.</p>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">Application developed by: C0D_ATA</p>
"""
st.markdown(html_line, unsafe_allow_html=True)
