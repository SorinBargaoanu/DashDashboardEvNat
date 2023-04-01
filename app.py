# Importare modulele necesare
import pandas as pd
import numpy as np
from dash import dash, dcc, html, Input, Output, State

# Sursa datelor:
# https://data.gov.ro/en/dataset?q=evaluare+nationala

# Încărcarea datelor
df_2014 = pd.read_csv("data/evnat_2014.csv", sep=",", encoding='latin')
df_2015 = pd.read_csv("data/evnat_2015.csv", sep=",", encoding='latin')
df_2016 = pd.read_csv("data/evnat_2016.csv", sep=",", encoding='latin')
df_2017 = pd.read_csv("data/evnat_2017.csv", sep=",", encoding='latin')
df_2019 = pd.read_csv("data/evnat_2019.csv", sep=",", encoding='latin')
df_2020 = pd.read_csv("data/evnat_2020.csv", sep=",", encoding='latin')
df_2022 = pd.read_csv("data/evnat_2022.csv", sep=",", encoding='latin')

# Crearea unei liste de df-uri
dfs = [df_2014, df_2015, df_2016, df_2017, df_2019, df_2020, df_2022]

# Conversia tuturor numelor de coloane în litere mici și eliminarea spațiilor goale
for df in dfs:
    df.columns = df.columns.str.lower().str.strip()

# Păstrarea doar a coloanelor dorite
df_2014 = df_2014[['cod unic candidat', 'sex', 'mediu', 'nota romana', 'nota matematica', 'media en',
                   'media v-viii', 'judet']]
df_2015 = df_2015[['cod unic candidat', 'sex', 'mediu', 'nota finala romana', 'nota finala matematica', 'media']]
df_2016 = df_2016[['cod unic candidat', 'sex', 'mediu', 'nota finala romana', 'nota finala matematica',
                   'media', 'media v-viii']]
df_2017 = df_2017[['cod unic candidat', 'sex', 'mediu', 'nota finala romana', 'nota finala matematica',
                   'media', 'media v-viii']]
df_2019 = df_2019[['cod unic candidat', 'sex', 'mediu', 'nota finala romana', 'nota finala matematica',
                   'media', 'media v-viii']]
df_2020 = df_2020[['cod unic candidat', 'sex', 'mediu', 'nota finala romana', 'nota finala matematica',
                   'media', 'media v-viii']]
df_2022 = df_2022[['cod unic candidat', 'sex', 'mediu', 'nota finala romana', 'nota finala matematica',
                   'media', 'media v-viii', 'judet']]

# Curățare coloană "media" de conținut tip string
df_2015.loc[:, 'media'] = df_2015['media'].replace('Absent', np.nan).astype(float)

# Redenumire coloane
df_2014 = df_2014.rename(columns={'media en': 'media', 'nota romana': 'nota finala romana',
                                  'nota matematica': 'nota finala matematica'})
dfs = [df_2014, df_2015, df_2016, df_2017, df_2019, df_2020, df_2022]
for df in dfs:
    df.rename(columns={"sex": "genul elevului"}, inplace=True)
    df.rename(columns={"media": "media finala"}, inplace=True)
    df.rename(columns={"mediu": "urban/rural"}, inplace=True)

# Adăugarea coloanei 'an' pentru fiecare df
df_2014.loc[:, 'an'] = 2014
df_2015.loc[:, 'an'] = 2015
df_2016.loc[:, 'an'] = 2016
df_2017.loc[:, 'an'] = 2017
df_2019.loc[:, 'an'] = 2019
df_2020.loc[:, 'an'] = 2020
df_2022.loc[:, 'an'] = 2022

# Combinarea tuturor df-urilor într-unul singur
df_total = pd.concat([df_2014, df_2015, df_2016, df_2017, df_2019, df_2020, df_2022], ignore_index=True)


# Definirea funcției pentru calcularea mediei în funcție de notă și grupare
def calculeaza_medie(df_calc, nota_coloana, grupare_coloana):
    medie_df = df_calc.groupby(['an', grupare_coloana])[nota_coloana].mean().reset_index()
    ani = sorted(df_calc['an'].unique())
    categorii = df_calc[grupare_coloana].unique()
    index = pd.MultiIndex.from_product([ani, categorii], names=['an', grupare_coloana])
    medie_df = medie_df.set_index(['an', grupare_coloana]).reindex(index).reset_index()
    medie_df[nota_coloana] = medie_df[nota_coloana].round(2)
    return medie_df


# Crearea aplicației

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Definirea aspectului aplicației
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
            # html.Img(src='/assets/images/logo_intuitext.png')
            html.H1('Rezultate Evaluarea Națională 2014 - 2022', style={'margin-bottom': '0px', 'color': 'black'})
        ], id="title", className="create_container1"),
    ], id="header", className="flex-display", style={"margin": "50px"}),
    dcc.Dropdown(
        id='nota-selector',
        options=[
            {'label': 'Nota finală română', 'value': 'nota finala romana'},
            {'label': 'Nota finală matematică', 'value': 'nota finala matematica'},
            {'label': 'Media finală', 'value': 'media finala'},
            {'label': 'Media V-VIII', 'value': 'media v-viii'}
        ],
        value='media finala',
        multi=False
    ),
    dcc.Dropdown(
        id='grupare-selector',
        options=[
            {'label': 'Genul elevului', 'value': 'genul elevului'},
            {'label': 'Urban/Rural', 'value': 'urban/rural'}
        ],
        value=['genul elevului'],
        multi=True
    ),
    html.Button('Calculeaza rezultatul', id='calculeaza-button', n_clicks=0,
                style={'background-color': 'rgb(30,144,255)', 'color': 'white'}),
    dcc.Graph(id='rezultat-grafic')
])


# Definirea funcției pentru actualizarea graficului în funcție de notă și grupare
@app.callback(
    Output('rezultat-grafic', 'figure'),
    [Input('calculeaza-button', 'n_clicks')],
    [State(component_id='nota-selector', component_property='value'),
     State(component_id='grupare-selector', component_property='value')]
)
def update_grafic(n_clicks, nota_coloana, grupare_coloane):
    if n_clicks == 0:
        nota_coloana = 'media finala'
        grupare_coloane = ['genul elevului']

    # Crearea structurii de bază a graficului
    fig = {
        'data': [],
        'layout': {
            'title': f'Evoluția mediei "{nota_coloana}" în funcție de "{", ".join(grupare_coloane)}"',
            'xaxis': {'title': 'An'},
            'yaxis': {'title': f'Medie "{nota_coloana}"'}
        }
    }

    if len(grupare_coloane) == 2:
        grupare1, grupare2 = grupare_coloane
        for valoare_grupare1 in df_total[grupare1].unique():
            for valoare_grupare2 in df_total[grupare2].unique():
                medie_df = \
                    df_total[(df_total[grupare1] == valoare_grupare1) & (df_total[grupare2] == valoare_grupare2)].\
                    groupby(['an'])[nota_coloana].mean().reset_index()
                fig['data'].append({
                    'x': medie_df['an'],
                    'y': medie_df[nota_coloana],
                    'type': 'line',
                    'name': f'{valoare_grupare1} din {valoare_grupare2}'
                })
    else:
        for grupare_coloana in grupare_coloane:
            medie_df = calculeaza_medie(df_total, nota_coloana, grupare_coloana)
            ani = sorted(df_total['an'].unique())
            categorii = df_total[grupare_coloana].unique()

            for categorie in categorii:
                valori_medii = medie_df[medie_df[grupare_coloana] == categorie][nota_coloana]

                fig['data'].append({
                    'x': ani,
                    'y': valori_medii,
                    'type': 'line',
                    'name': f'{categorie} ({grupare_coloana})'
                })

    # # Adăugarea liniilor în grafic pentru fiecare categorie și grupare
    # for grupare_coloana in grupare_coloane:
    #     medie_df = calculeaza_medie(df_total, nota_coloana, grupare_coloana)
    #     ani = sorted(df_total['an'].unique())
    #     categorii = df_total[grupare_coloana].unique()
    #
    #     for categorie in categorii:
    #         valori_medii = medie_df[medie_df[grupare_coloana] == categorie][nota_coloana]
    #
    #         fig['data'].append({
    #             'x': ani,
    #             'y': valori_medii,
    #             'type': 'line',
    #             'name': f'{categorie} ({grupare_coloana})'
    #         })

    # Returnarea graficului actualizat
    return fig


# Pornirea serverului Dash
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
