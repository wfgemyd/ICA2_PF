#libs for manipulatiing data
#https://www.w3schools.com/python/pandas/pandas_cleaning.asp
import pandas as pd
import geopandas as gpd
import numpy as np
import requests, io
#actual implementation of the data 
#https://plotly.com/python-api-reference/plotly.express.html
#https://dash.plotly.com/dash-core-components/dropdown
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
#I always want to get yesterdays date.
from datetime import date
from datetime import timedelta
import os
y = date.today()- timedelta(days = 1)

#importing data
combined_df=pd.DataFrame()
death_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
confirmed_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
recovered_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
country_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv")
dfm = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv")
dfall = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
confirmed__df = pd.read_csv(os.path.join(os.path.dirname(__file__), "raw_data_files/confirmed_regions.csv"))
deaths_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "raw_data_files/deaths_regions.csv"))



#making all the dfs the same (data wise)
#names to lowercase
country_df.columns = map(str.lower, country_df.columns)
confirmed_df.columns = map(str.lower, confirmed_df.columns)
death_df.columns = map(str.lower, death_df.columns)
recovered_df.columns = map(str.lower, recovered_df.columns)
#setting index to country
confirmed__df.set_index(confirmed__df['Country/Region'],inplace=True)
deaths_df.set_index(deaths_df['Country/Region'],inplace=True)
#Removing first row
confirmed__df = confirmed__df.iloc[1: , :]
deaths_df = deaths_df.iloc[1: , :]
confirmed__df = confirmed__df.astype({"12/30/21": int})
deaths_df = deaths_df.astype({"12/30/21": int})

#renaming
confirmed_df = confirmed_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
recovered_df = recovered_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
death_df = death_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
country_df = country_df.rename(columns={'country_region': 'country'})
confirmed__df.rename(columns={'Country/Region': 'Country', 'Region Name': 'Continent', 'Sub-region Name': 'Region', 'Region Code': 'Continent Code', 'Sub-region Code': 'Region Code'},inplace=True)
deaths_df.rename(columns={'Country/Region': 'Country', 'Region Name': 'Continent', 'Sub-region Name': 'Region', 'Region Code': 'Continent Code', 'Sub-region Code': 'Region Code'},inplace=True)

#removing state
recovered_df = recovered_df.loc[:, recovered_df.columns!='state']
confirmed_df = confirmed_df.loc[:, confirmed_df.columns!='state']
death_df = death_df.loc[:, death_df.columns!='state']
#cleaning country_df
country_df=country_df.drop(columns=['recovered', 'active', 'people_tested', 'people_hospitalized', 'iso3', 'uid'])
confirmed__df=confirmed__df.drop(columns=['Province/State', 'ISO 3166-1 Alpha 3-Codes', 'Intermediate Region Code', 'Intermediate Region Name'])
countries_confirmed_df=confirmed__df.groupby(['Country']).sum().copy()
countries_deaths_df=deaths_df.groupby(['Country']).sum().copy()


#some nan data in lat and long, this .dropna() cleans it
confirmed_df=confirmed_df.dropna(subset=['long','lat'])
recovered_df = recovered_df.dropna(subset=['long','lat'])
death_df = death_df.dropna(subset=['long','lat'])
country_df=country_df.dropna(subset=['long_','lat'])
#droping the duplicats
confirmed_df=confirmed_df.drop_duplicates()
recovered_df = recovered_df.drop_duplicates()
death_df = death_df.drop_duplicates()
country_df=country_df.drop_duplicates()

#making the date columns into a list
combined_df['Confirmed']=countries_confirmed_df[countries_confirmed_df.columns[-1]]
combined_df['Deaths']=countries_deaths_df[countries_deaths_df.columns[-1]]
#combined_df['Recovered']=countries_recovered_df[countries_recovered_df.columns[-1]]
sorted_combined_df=combined_df.loc[:,["Confirmed","Deaths"]].sort_values("Confirmed",ascending=False)
sorted_combined_df['Country']=sorted_combined_df.index
combined_df.loc[:,["Confirmed","Deaths"]].sort_values("Confirmed",ascending=False).style.background_gradient(cmap='Blues',subset=["Confirmed"]).background_gradient(cmap='Reds',subset=["Deaths"]).background_gradient(cmap='Green',subset=["Recovered"])

#setting the country as a usable index
confirmed_countries = confirmed__df.filter(['Country', 'Lat', 'Long', '12/30/21'])
confirmed_countries['Long'] = confirmed_countries['Long'].fillna(0.0).astype(float)
confirmed_countries['Long'] = confirmed_countries['Long'].fillna(0.0).astype(int)
confirmed_countries['Lat'] = confirmed_countries['Lat'].fillna(0.0).astype(float)
confirmed_countries['Lat'] = confirmed_countries['Lat'].fillna(0.0).astype(int)
column_names = {'12/30/21':'Confirmed', 'Lat':'Lat','Long':'Long'}
#setting the region as a usable index
confirmed_regions = confirmed__df.filter(['Region Code', 'Region', 'Lat', 'Long', '12/30/21'])
confirmed_regions['Long'] = confirmed_regions['Long'].fillna(0.0).astype(float)
confirmed_regions['Long'] = confirmed_regions['Long'].fillna(0.0).astype(int)
confirmed_regions['Lat'] = confirmed_regions['Lat'].fillna(0.0).astype(float)
confirmed_regions['Lat'] = confirmed_regions['Lat'].fillna(0.0).astype(int)
column_names = {'12/30/21':'Confirmed', 'Lat':'Lat','Long':'Long'}
confirmed_regions = confirmed_regions.groupby(['Region', 'Region Code']).agg({'12/30/21':'sum', 'Lat':'mean','Long':'mean'}).rename(columns=column_names)
confirmed_regions = confirmed_regions.reset_index()
#setting the region deaths as a usable index
deaths_regions = deaths_df.filter(['Region Code', 'Region', 'Lat', 'Long', '12/30/21'])
deaths_regions['Long'] = deaths_regions['Long'].fillna(0.0).astype(float)
deaths_regions['Long'] = deaths_regions['Long'].fillna(0.0).astype(int)
deaths_regions['Lat'] = deaths_regions['Lat'].fillna(0.0).astype(float)
deaths_regions['Lat'] = deaths_regions['Lat'].fillna(0.0).astype(int)
column_names = {'12/30/21':'Deaths', 'Lat':'Lat','Long':'Long'}
deaths_regions = deaths_regions.groupby(['Region', 'Region Code']).agg({'12/30/21':'sum', 'Lat':'mean','Long':'mean'}).rename(columns=column_names)
deaths_regions = deaths_regions.reset_index()
#setting the continent as a usable index
confirmed_continents = confirmed__df.groupby(['Continent Code', 'Continent'], as_index=False).sum()
confirmed_continents = confirmed_continents.reset_index()
new_col_Longtitude = [100.6197, 9.0000, -75.2551, 34.5085, 125.0188]  
new_col_Latitude = [34.0479, 53.0000, 10, 8.7832, -10.7359]
confirmed_continents.insert(loc=0, column='Long', value=new_col_Longtitude)
confirmed_continents.insert(loc=0, column='Lat', value=new_col_Latitude)

print("__________________________________________")
# join two datasets together and make manufactuerer data columns.
dfv = (
    dfall.set_index(["location", "date"])
    .join(
        dfm.set_index(["location", "date", "vaccine"])
        .unstack("vaccine")
        .droplevel(0, 1),
        how="inner",
    )
    .reset_index()
)
# filter to latest data only
dfplot = (
    dfv.sort_values(["iso_code", "date"])
    .groupby("iso_code", as_index=False)
    .last()
    .sort_values("people_fully_vaccinated_per_hundred", ascending=False)
)

app = dash.Dash(__name__)
server = app.server

#fig0 is confirmed cases
fig0 = px.bar(confirmed_df.sort_values(str(y.month) + "/" + str(y.day) + "/" + str(y.year)[2:], ascending= False).head(10), 
            x='country', y=str(y.month) + "/" + str(y.day) + "/" + str(y.year)[2:], color='country',title="top 10 - confirmed cases ") 


#fig1 is top 10 countries with the highst mortality rate 
fig1 = px.bar(country_df.sort_values('mortality_rate', ascending= False).head(11)[1:], y='mortality_rate', x='country', text_auto='.2s',
                title="top 10 - mortality rate ") 

#fig2 is top 10 countries with most deaths 
fig2=px.scatter(country_df.sort_values('deaths', ascending= False).head(60), x="country", y="deaths", size="deaths", color="country", hover_name="country", size_max=85)
fig2.update_layout(
title=str(60) +" Worst hit countries (deaths) ",
xaxis_title="Countries",
yaxis_title="Confirmed Cases",
width = 700)

#fig3 using 2 dfs and displaying it as a line
country = 'World'
labels = ['recovered', 'deaths','confirmed']
colors = ['green', 'red', 'blue']
mode_size = [6, 8, 10]
line_size = [4, 5, 6]

df_list = [recovered_df, death_df, confirmed_df]

fig3 = go.Figure()

for i, df in enumerate(df_list):
    if country == 'World' or country == 'world':
        x_data = np.array(list(df.iloc[:, 20:].columns))
        y_data = np.sum(np.asarray(df.iloc[:,4:]),axis = 0)
        
    else:    
        x_data = np.array(list(df.iloc[:, 20:].columns))
        y_data = np.sum(np.asarray(df[df['country'] == country].iloc[:,20:]),axis = 0)
        
    fig3.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines+markers',
    name=labels[i],
    line=dict(color=colors[i], width=line_size[i]),
    connectgaps=True,
    text = "Total " + str(labels[i]) +": "+ str(y_data[-1])
    ))

fig3.update_layout(
    title="COVID 19 cases of " + country,
    xaxis_title='Date',
    yaxis_title='No. of recovered Cases',
    margin=dict(l=20, r=20, t=40, b=20),
    width = 800)
fig3.update_yaxes(type="linear")


fig4 = px.bar(
    dfplot.assign(
        **{c: dfplot[c] / dfplot["population"] for c in dfm["vaccine"].unique()}
    ),
    x="location",
    y=dfm["vaccine"].unique(),
)
# add a line of people fully vaccinated
fig4.add_trace(
    go.Scatter(
        x=dfplot["location"],
        y=dfplot["people_fully_vaccinated_per_hundred"] / 100,
        name="Fully vaccinated",
        mode="lines",
        line={"color": "purple", "width": 4},    
    )
)


app.layout = html.Div(children=[
    html.H1(children='Pandemic Data Visualisation'), 
    html.Br(),
    html.Div([
            html.Div([
                html.H3("Covid - 19", style={"margin-bottom": "0px", 'color': 'black'}),
                html.H5("Track Covid - 19 Cases", style={"margin-top": "0px", 'color': 'black'}),
            ])
        ], className="one-half column", id="title"),
    html.Div([
            html.H6('Last Updated: ' + str(y.month) + "/" + str(y.day) + "/" + str(y.year)[:2] + '  00:01 (UTC)',
                    style={'color': 'orange'}),

        ], className="one-third column", id='title1'),
    html.Div(children=[
        dcc.RadioItems(
        options=[
            {'label': 'Country', 'value': 'Country'},
            {'label': 'Region', 'value': 'Region'},
            {'label': 'Continent', 'value': 'Continent'},
        ],
        value='Country',
        id='radio_space'
        ),
        dcc.Graph(id='map_world', figure={},
            style={
                'background-color':'#ffffff',
                "verticalAlign": "center",
                "horizontalAlign": "center",
                }),
        ], 
        style={
            'textAlign': 'center',
            'margin': 'auto',
            "margin-left": "20px",
            "verticalAlign": "top",
            "horizontalAlign": "center",
            'padding': 10, 
            'flex': 1
        })
    ,html.Br(),
    html.Div([
            dcc.Graph(figure=fig0)
            ])
    ,html.Br(),
    html.Div([
            dcc.Graph(figure=fig1)
            ])
    ,html.Br(),
    html.Div([
            dcc.Graph(figure=fig2)
            ])
    ,html.Br(),
    html.Div([
            dcc.Graph(figure=fig3)
            ])
    ,html.Br(),
    html.Div([
            dcc.Graph(figure=fig4)
            ])
],style={
            'textAlign': 'center',
            'margin': 'auto',
            "margin-left": "20px",
            "verticalAlign": "top",
            "horizontalAlign": "center",
            'padding': 10, 
            'flex': 1
        })  

@app.callback(
Output(component_id='map_world', component_property='figure'),
[Input(component_id='radio_space', component_property='value')])
def update_map(option_slctd):
    if (option_slctd == "Country"):
        if 'Text' not in confirmed_countries.columns:
            confirmed_countries.insert(loc=0, column='Text', value="")
            confirmed_countries['Text'] = confirmed_countries['Country'] + " confirmed cases: " + confirmed_countries['12/30/21'].astype(str)
        fig = go.Figure(data=go.Scattergeo(
            lon = confirmed_countries['Long'],
            lat = confirmed_countries['Lat'],
            text = confirmed_countries['Text'],
            mode = 'markers',
            marker = dict(
            opacity = 0.8,
            symbol = 'triangle-down-dot',
            colorscale = 'inferno',
            color=list(range(850)),
            cmax = 850,
            cmin = 30,
            size = confirmed_countries['12/30/21'] / 500000 + 10
            )))    
    elif (option_slctd == "Continent"):
        if 'Text' not in confirmed_continents.columns:
            confirmed_continents.insert(loc=0, column='Text', value="")
            confirmed_continents['Text'] = confirmed_continents['Continent'] + " confirmed cases: " + confirmed_continents['12/30/21'].astype(str)
        fig = go.Figure(data=go.Scattergeo(
            lon = confirmed_continents['Long'],
            lat = confirmed_continents['Lat'],
            text = confirmed_continents['Text'],
            mode = 'markers',
            marker = dict(
            opacity = 0.8,
            autocolorscale = True,
            symbol = 'triangle-left-dot',
            colorscale = 'inferno',
            cmin = 0,
            color=list(range(140)),
            cmax = 140,
            size = confirmed_continents['12/30/21'] / 1000000 + 30
            )))
    elif (option_slctd == "Region"):
        if 'Text' not in confirmed_regions.columns:
            confirmed_regions.insert(loc=0, column='Text', value="")
            confirmed_regions['Text'] = confirmed_regions['Region'] + " confirmed cases: " + confirmed_regions['Confirmed'].astype(str)
        fig = go.Figure(data=go.Scattergeo(
            lon = confirmed_regions['Long'],
            lat = confirmed_regions['Lat'],
            text = confirmed_regions['Text'],
            mode = 'markers',
            marker = dict(
            opacity = 0.8,
            autocolorscale = False,
            symbol = 'triangle-right-dot',
            colorscale = 'solar',
            color=list(range(80)),
            cmax = 80,
            cmin = 1,
            size = confirmed_regions['Confirmed'] / 1000000 + 10
            )))

    map_title = "Confirmed Covid-19 Cases By " + option_slctd

    fig.update_layout(
        title = map_title,
        title_font_color="#000000",
        title_x=0.5,
        geo = dict(
            scope='world',
            projection_type='orthographic',
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            bgcolor='rgb(255,255,255)',
            countrywidth = 0.5,
            subunitwidth = 0.5,
        ),
    )

    fig.update_geos(
    resolution=110,
    showcoastlines=True, coastlinecolor="Black",
    showland=True, landcolor="LightGreen",
    showocean=True, oceancolor="White",
    showlakes=True, lakecolor="LightBlue",
    showrivers=True, rivercolor="LightBlue"
    )
    
    fig.update_layout(height=700, paper_bgcolor = "rgb(255,255,255)")
    
    return fig  
   
if __name__ == '__main__':
    app.run_server(debug=True)
    
