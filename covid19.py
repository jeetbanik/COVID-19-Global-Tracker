# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 04:21:00 2020
@author: jeetb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd  # also install descartes
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from bs4 import BeautifulSoup
import requests
import dash
import dash_html_components as html
import dash_core_components as dcc
import base64

url = "https://www.worldometers.info/coronavirus/"
req = requests.get(url)
html1 = req.text
soup = BeautifulSoup(html1, 'html.parser')
txt = soup.title.text

l_d = soup.find_all('div', id='maincounter-wrap')
t_b = soup.find('tbody')
t_r = t_b.find_all('tr')

c = []
t_c = []
n_c = []
t_d = []
n_d = []
t_rec = []
a_c = []

for tr in t_r:
    td = tr.find_all('td')
    c.append(td[1].text)
    t_c.append(td[2].text)
    n_c.append(td[3].text)
    t_d.append(td[4].text)
    n_d.append(td[5].text)
    t_rec.append(td[6].text)
    a_c.append(td[7].text)

headers = ['Country', 'Total Cases', 'Cases Today', 'Total Deaths', 'Deaths Today', 'Total Recovered',
           'Active Cases']
data = pd.DataFrame(list(zip(c, t_c, n_c, t_d, n_d, t_rec, a_c)), columns=headers)
data = data[8:]
data.to_csv('corona_world.csv')
data = pd.read_csv('corona_world.csv')

data = data.iloc[:, 1:]

hov = 'Active Cases' + '<br>' + data['Total Cases'] + ' Total' + '<br>' + data[
    'Total Recovered'] + ' Recovered' + '<br>' + data['Total Deaths'] + ' Dead'

data.replace('CAR', 'Central African Republic', inplace=True)

a = []
b = []
c = []
d = []
e = []
f = []

data['Active Cases'].replace(np.nan, '123456789', inplace=True)
for i in range(len(data['Active Cases'])):
    a = data['Active Cases'][i].split(',')
    b.append(a)
data['Active Cases'] = list(map(''.join, b))
data['Active Cases'] = data['Active Cases'].astype(int)

data['Total Cases'].replace(np.nan, '123456789', inplace=True)
for j in range(len(data['Total Cases'])):
    c = data['Total Cases'][j].split(',')
    d.append(c)
data['Total Cases'] = list(map(''.join, d))
data['Total Cases'] = data['Total Cases'].astype(int)

for k in range(len(data['Total Deaths'])):
    e = data['Total Deaths'][k].split(',')
    f.append(e)
f = list(map(''.join, f))
f = [x.strip() for x in f]
data['Total Deaths'] = f
data['Total Deaths'].replace('', 0, inplace=True)
data['Total Deaths'] = data['Total Deaths'].astype(int)

data['Death Rate'] = (data['Total Deaths'] / data['Total Cases'])
data['Death Rate'].replace(np.inf, 0, inplace=True)
data['Death Rate'] = data['Death Rate'].apply('{:.0%}'.format)

data.replace(123456789, np.nan, inplace=True)
data.replace(np.nan, 'N/A', inplace=True)

pio.templates.default = "plotly_dark"

table_fig = go.Figure(data=[go.Table(
    header=dict(values=list(data.columns),
                fill_color='blue', line_color='darkslategray',
                align='center', font=dict(color='white', size=18)),
    cells=dict(values=[data['Country'], data['Total Cases'], data['Cases Today'], data['Total Deaths'],
                       data['Deaths Today'], data['Total Recovered'], data['Active Cases'],
                       data['Death Rate']], fill_color='lavender', line_color='darkslategray',
               align='center', height=30, font=dict(color='black', size=15)))
])
table_fig.update_layout(
    title='Live Demographics of Most COVID-19 Affected Countries in the World (Scroll Down in the Table to see Data of All Countries.)',
    title_x=0.5)

fig = go.Figure(data=go.Choropleth(
    locations=data['Country'],
    locationmode='country names',
    z=data['Active Cases'],
    colorscale=['rgb(172,49,36)', 'rgb(120,14,40)', 'rgb(89,13,31)',
                'rgb(89,13,31)', 'rgb(60,9,17)', 'rgb(60,9,17)', 'rgb(60,9,17)'],
    text=hov,
    marker_line_color='Orange',
    marker_line_width=0.5,
))
fig.update_layout(
    title_text='COVID-19 Cases Globally (Move across the Globe and Pan to a Country to see its Active & Total Cases, Recoveries, and Deaths.)',
    legend_title='No. of Active Cases',
    title_x=0.5,
    autosize=True,
    geo=dict(
        showframe=False,
        showcoastlines=True, coastlinecolor='Orange',
        showocean=True, oceancolor='rgba(192,229,232,0.1)',
        projection_type='orthographic'
    ))
fig.update_xaxes(automargin=True)
fig.update_yaxes(automargin=True)

df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv')

df = df[df['Confirmed'] > 0]
df = df.groupby(['Date', 'Country']).sum().reset_index()
df['Active'] = df['Confirmed'] - df['Recovered'] - df['Deaths']

idx = np.where(df['Country']=='US')[0]
idx = idx[len(idx)-1]
end = df.iloc[idx,5]

ani_fig = px.choropleth(df,
                        locations="Country",
                        locationmode="country names",
                        color='Active',
                        color_continuous_scale='RdBu',
                        range_color=(0, end),
                        hover_name="Country",
                        animation_frame="Date"
                        )
ani_fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)
ani_fig.update_layout(
    title_text='Spread of Coronavirus Cases over Time Globally (Click on the Play button Below or Move across the Slider.)',
    title_x=0.5,
    autosize=True,
    geo=dict(
        showframe=True,
        showcoastlines=True, coastlinecolor="Light Green",
        showocean=True, oceancolor='rgba(128,205,193,0.5)',
        projection_type='natural earth'
    ))
ani_fig.update_xaxes(automargin=True)
ani_fig.update_yaxes(automargin=True)

data1 = pd.read_csv('https://raw.githubusercontent.com/imdevskp/covid-19-india-data/master/complete.csv')
data1 = data1.rename(columns={'Name of State / UT': 'State'})
data1 = data1.rename(columns={'Total Confirmed cases': 'Confirmed'})
data1 = data1.rename(columns={'Cured/Discharged/Migrated': 'Recovered'})
data1 = data1.rename(columns={'Death': 'Deaths'})

shp = ("Admin2.shp")
map1 = gpd.read_file(shp)

map1['ST_NM'].iloc[0] = 'Andaman and Nicobar Islands'
map1['ST_NM'].iloc[1] = 'Arunachal Pradesh'
map1['ST_NM'].iloc[12] = 'Jammu and Kashmir'
map1['ST_NM'].iloc[23] = 'Delhi'
map1['ST_NM'].iloc[29] = 'Telengana'

map_data = map1.set_index('ST_NM').join(data1.set_index('State'))

i = 0
while i<=1:
    fig1, ax = plt.subplots(1, figsize=(30, 20))
    ax.set_title('Heat Map of Live Spread of COVID-19 in India - State Wise',
                 fontdict={'color': 'white', 'fontsize': '30', 'fontweight': '7'})
    map_data.plot(column='Confirmed', cmap='YlOrRd', linewidth=0.3, ax=ax, edgecolor='black', legend=True)
    plt.rcParams['xtick.color'] = 'white'
    plt.rcParams['ytick.color'] = 'white'
    plt.legend(framealpha=0.5, loc='upper right', labelspacing=1, fontsize='xx-large', title='Total Confirmed Cases')
    fig1.savefig("coronaindiamap.png", dpi=300, transparent=True)
    i += 1

img_file = 'coronaindiamap.png'
fig_img = base64.b64encode(open(img_file, 'rb').read())

data1.dropna(inplace=True)
data1.fillna(data1.mean(), inplace=True)
data1['Active'] = data1['Confirmed'] - data1['Recovered'] - data1['Deaths']

ts_fig = px.line(data1, x='Date', y='Active',
                 title='Time Series Graph of Active Cases in India with Rangeslider (Move across the Slider Below.)',
                 color="State", line_group="State", hover_name="State")
ts_fig.update_xaxes(rangeslider_visible=True)
ts_fig.update_layout(title_x=0.5)

ts_fig1 = px.line(data1, x='Date', y='Confirmed',
                  title='Time Series Graph of Total Confirmed Cases in India with Rangeslider (Move across the Slider Below.)',
                  color="State", line_group="State", hover_name="State")
ts_fig1.update_xaxes(rangeslider_visible=True)
ts_fig1.update_layout(title_x=0.5)

ts_fig2 = px.line(data1, x='Date', y='Recovered',
                  title='Time Series Graph of Recovered Cases in India with Rangeslider (Move across the Slider Below.)',
                  color="State", line_group="State", hover_name="State")
ts_fig2.update_xaxes(rangeslider_visible=True)
ts_fig2.update_layout(title_x=0.5)

ts_fig3 = px.line(data1, x='Date', y='Deaths',
                  title='Time Series Graph of Death Cases in India with Rangeslider (Move across the Slider Below.)',
                  color="State", line_group="State", hover_name="State")
ts_fig3.update_xaxes(rangeslider_visible=True)
ts_fig3.update_layout(title_x=0.5)

url1 = "https://www.mohfw.gov.in/#state-data"
req1 = requests.get(url1)
html2 = req1.text
soup1 = BeautifulSoup(html2, 'html.parser')

table_body = soup1.find('tbody')
table_rows = table_body.find_all('tr')
all_rows = table_body("tr")[:33]

state = []
cases = []
cured = []
death = []

for tr in all_rows:
    td = tr.find_all('td')
    state.append(td[1].text)
    cases.append(td[2].text)
    cured.append(td[3].text)
    death.append(td[4].text)

col_headers = ['State/UT', 'Confirmed Cases', 'Recovered', 'Deaths']
dat = pd.DataFrame(list(zip(state, cases, cured, death)), columns=col_headers)

dat['Confirmed Cases'] = dat['Confirmed Cases'].astype(int)
dat['Recovered'] = dat['Recovered'].astype(int)
dat['Deaths'] = dat['Deaths'].astype(int)
dat['Active Cases'] = dat['Confirmed Cases'] - dat['Recovered'] - dat['Deaths']
dat['Death Rate'] = (dat['Deaths'] / dat['Confirmed Cases'])
dat['Death Rate'].replace(np.nan, 0.00, inplace=True)
dat['Death Rate'] = dat['Death Rate'].apply('{:.0%}'.format)

tfig = go.Figure(data=[go.Table(
    header=dict(values=list(dat.columns),
                fill_color='orange', line_color='darkslategray',
                align='center', height=40, font=dict(color='white', size=18)),
    cells=dict(values=[dat['State/UT'], dat['Confirmed Cases'], dat['Recovered'], dat['Deaths'], dat['Active Cases'],
                       dat['Death Rate']],
               fill_color='light green', line_color='darkslategray',
               align='center', height=30, font=dict(color='black', size=16)))
])
tfig.update_layout(
    title='Live Demographics of India Affected by COVID-19 (Scroll Down in the Table to see the Data of All Indian States/UT.)',
    title_x=0.5)

bfig = go.Figure(data=[
    go.Bar(name='Confirmed Cases', x=dat['State/UT'], y=dat['Confirmed Cases']),
    go.Bar(name='Deaths', x=dat['State/UT'], y=dat['Deaths']),
    go.Bar(name='Recovered', x=dat['State/UT'], y=dat['Recovered'])
])
bfig.update_layout(barmode='group',
                   title_text='Clustered Bar Chart of Coronavirus Confirmed Cases, Deaths & Recoveries in India (Point at Bars to see Exact Numbers.)',
                   title_x=0.5, height=666)

external_stylesheets = [
    {
        'href': 'assets/style.css',
        'rel': 'stylesheet',
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div([
    html.Div(children=[html.H1("COVID-19 CORONAVIRUS PANDEMIC GLOBAL TRACKER [Targeted on India: scroll down]",
                               style={'color': 'orange', 'text-align': 'center', 'text-decoration': 'underline',
                                      'font-family': 'Georgia'})],
             style={'border': '0px white solid', 'float': 'left', 'width': '100%', 'height': '70px'}),
    html.Div(children=[html.H2("Made for the community, by Jeet Banik.",
                               style={'color': 'white', 'text-align': 'center', 'text-decoration': 'underline',
                                      'font-family': 'Courier New'})],
             style={'border': '0px white solid', 'float': 'left', 'width': '100%', 'height': '50px',
                    'margin-top': '10px'}),
    html.Div(children=[html.H1(txt, style={'color': 'red', 'text-align': 'center', 'text-decoration': 'underline'})],
             style={'border': '0x white solid', 'float': 'left', 'width': '100%', 'height': '100px'}),
    html.Div(children=[dcc.Graph(id='world-map', figure=fig,
                                 style={'height': '100vh', 'width': '100%', 'display': 'inline-block',
                                        'vertical-align': 'middle'})],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='animated-world-map', figure=ani_fig,
                                 style={'height': '100vh', 'width': '100%', 'display': 'inline-block',
                                        'vertical-align': 'middle'})],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='world-data', figure=table_fig)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(html.Img(src='data:image/png;base64,{}'.format(fig_img.decode()),
                      style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'middle'}),
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='india-data', figure=tfig)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='india-bar-chart', figure=bfig)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='india-ts-graph1', figure=ts_fig1)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='india-ts-graph2', figure=ts_fig2)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='india-ts-graph3', figure=ts_fig3)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'}),
    html.Div(children=[dcc.Graph(id='india-ts-graph', figure=ts_fig)],
             style={'border': '0px white solid', 'display': 'inline-block', 'vertical-align': 'middle',
                    'width': '100%'})
])

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)