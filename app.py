# Importare modulele necesare
import pandas as pd
from dash import dash, dcc, html, Input, Output, State, dash_table

# Sursa datelor:
# https://data.gov.ro/en/dataset?q=evaluare+nationala

# Importare fisier unit ce contine rezultatele la Evaluarea Nationala pentru anii 2014 - 2023
# df_total = pd.read_pickle("data/evnat_2014_2023.pkl")
df_total = pd.read_csv("data/evnat_2014_2023.csv", low_memory=False)


# Definirea funcției pentru calcularea mediei în funcție de notă și grupare
def calculeaza_medie(df_calc, nota_coloana, grupare_coloana):
    medie_df = df_calc.groupby(['an', grupare_coloana])[nota_coloana].mean().reset_index()
    ani = sorted(df_calc['an'].unique())
    categorii = df_calc[grupare_coloana].unique()
    index = pd.MultiIndex.from_product([ani, categorii], names=['an', grupare_coloana])
    medie_df = medie_df.set_index(['an', grupare_coloana]).reindex(index).reset_index()
    medie_df[nota_coloana] = medie_df[nota_coloana].round(2)
    return medie_df


# Generate a continuous gray gradient based on the values in the table
def get_continuous_gray_color(value):
    # Adjust the range of the gradient
    light_gray = 0.97  # close to 1 (which is white), but slightly gray
    dark_gray = 0.5  # mid-gray

    normalized = (value - min_value) / (max_value - min_value)
    adjusted = light_gray - normalized * (light_gray - dark_gray)

    gray_value = int(255 * adjusted)
    return f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"


# Clasificarea notelor în categorii
bins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # 11 este folosit pentru a include 10 în ultimul interval
labels = ["2 - 2.99", "3 - 3.99", "4 - 4.99", "5 - 5.99", "6 - 6.99", "7 - 7.99", "8 - 8.99", "9 - 9.99", "10"]
df_total['Grade Category'] = pd.cut(df_total['media finala'], bins=bins, labels=labels, right=False)

# Grupare după an și categorie de notă pentru a obține numărul de elevi pentru fiecare an și categorie de notă
grade_counts_by_year = df_total.groupby(['an', 'Grade Category']).size().unstack().fillna(0).astype(int)
transposed_table = grade_counts_by_year.transpose()
transposed_table["Total"] = transposed_table.sum(axis=1)
percentage_table_corrected = (transposed_table.div(transposed_table.sum(axis=0), axis=1) * 100).round(2)
percentage_table_corrected["Total"] = round(percentage_table_corrected.sum(axis=1), 2)

min_value = transposed_table.drop("Total", axis=1).values.min()
max_value = transposed_table.drop("Total", axis=1).values.max()

# Crearea aplicației

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Definirea aspectului aplicației
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
            # html.Img(src='/assets/images/logo_intuitext.png')
            html.H1('Rezultate Evaluarea Națională 2014 - 2023',
                    style={'margin-bottom': '0px', 'color': 'black'})
        ], id="title", className="create_container1"),
        html.Div([
            # html.Img(src='/assets/images/logo_intuitext.png')
            html.H3('Evoluția mediei anuale (2014-2023)',
                    style={'margin-bottom': '0px', 'color': 'rgb(30,144,255)'})
        ], id="title", className="create_container1")
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
    dcc.Graph(id='rezultat-grafic'),
    html.Div([
        html.Div([
            # html.Img(src='/assets/images/logo_intuitext.png')
            html.H3('Distribuția notelor elevilor pe ani (2014-2023)',
                    style={'margin-bottom': '0px', 'color': 'rgb(30,144,255)'})
        ], id="title", className="create_container1")
    ], id="header", className="flex-display", style={"margin": "50px"}),

    dcc.Dropdown(
        id="display-mode",
        options=[
            {"label": "Numere", "value": "numbers"},
            {"label": "Procente", "value": "percentages"}
        ],
        value="numbers",
        clearable=False
    ),
    # Locație rezervată pentru tabelul dinamic
    html.Div(id="dynamic-table"),
    dcc.Graph(
        id='line-chart',
        figure={
            'data': [
                {'x': list(range(2014, 2024)), 'y': transposed_table.loc[grade],
                 'mode': 'lines+markers', 'name': grade} for grade in labels
            ],
            'layout': {
                'title': 'Evoluția notelor pe ani',
                'xaxis': {'title': 'An'},
                'yaxis': {'title': 'Număr de elevi'}
            }
        }
    ),
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
            'title': f'Evoluția mediei "{str(nota_coloana)}" '
                     f'în funcție de "{", ".join([str(item) for item in grupare_coloane])}"',
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
                    'name': f'{str(valoare_grupare1)} din {str(valoare_grupare2)}'
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
                    'name': f'{str(categorie)} ({str(grupare_coloana)})'
                })
    return fig


@app.callback(
    Output("dynamic-table", "children"),
    [Input("display-mode", "value")]
)
def update_table(display_mode):
    if display_mode == "numbers":
        data = transposed_table.reset_index().to_dict("records")
    else:
        data = percentage_table_corrected.reset_index().to_dict("records")

    table = dash_table.DataTable(
        # Columns definition remains the same
        columns=[{"name": str(i), "id": str(i)} for i in (["Grade Category"] + list(range(2014, 2024)) + ["Total"])],
        data=data,

        # Conditional Coloring
        style_data_conditional=[
            {
                'if': {
                    'column_id': str(col),
                    'row_index': idx
                },
                'backgroundColor': get_continuous_gray_color(value),
            }
            for col in list(range(2014, 2024))
            for idx, value in enumerate(transposed_table[col])
        ],

        # Horizontal Scroll
        style_table={
            'overflowX': 'scroll'
        },

        # Styling Header
        style_header={
            'backgroundColor': '#636EFA',
            'fontWeight': 'bold',
            'color': 'white'
        },

        # Sorting
        sort_action="native"
    )
    return table


# Pornirea serverului Dash
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
