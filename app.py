# Importing the necessary modules
import pandas as pd
from dash import dash, dcc, html, Input, Output, State, dash_table

# Data source:
# https://data.gov.ro/en/dataset?q=evaluare+nationala

# Importing the file that contains the results of the National Assessment for the years 2014 - 2023
df_total = pd.read_csv("data/evnat_2014_2023.csv", low_memory=False)


def calculeaza_medie(df_calc, nota_coloana, grupare_coloana):
    """
    Calculate the average grades based on a specific grouping criterion.

    Parameters:
    - df_calc: DataFrame containing the data.
    - nota_coloana: Column in the DataFrame representing the grade for which the average will be calculated.
    - grupare_coloana: Column used for grouping to compute the average.

    Returns:
    - DataFrame containing the average grades for each year and specified grouping.
    """
    medie_df = df_calc.groupby(['an', grupare_coloana])[nota_coloana].mean().reset_index()
    ani = sorted(df_calc['an'].unique())
    categorii = df_calc[grupare_coloana].unique()
    index = pd.MultiIndex.from_product([ani, categorii], names=['an', grupare_coloana])
    medie_df = medie_df.set_index(['an', grupare_coloana]).reindex(index).reset_index()
    medie_df[nota_coloana] = medie_df[nota_coloana].round(2)
    return medie_df


def is_dark_color(hex_color):
    """
    Determine if a given hex color is dark or not.

    Parameters:
    - hex_color: A string representing the hex color code.

    Returns:
    - A boolean indicating if the color is dark (True) or not (False).
    """
    # Convert hex to RGB values
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    # Calculate the brightness of the color
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128  # Return True if the color is dark


def get_continuous_color_gradient(value, min_value, max_value):
    """
    Generate a continuous color gradient based on the provided values.

    Parameters:
    - value: The current value for which the color needs to be determined.
    - min_value: The minimum value in the range.
    - max_value: The maximum value in the range.

    Returns:
    - A string representing the hex color code corresponding to the value.
    """
    normalized = (value - min_value) / (max_value - min_value)
    idx = int(normalized * (len(ylgnbu_colors) - 1))
    return ylgnbu_colors[idx]


def prepare_data_for_selected_column(column_name):
    """
    Prepare the data for the selected grade column by categorizing it into predefined grade intervals.

    Parameters:
    - column_name: Name of the column in df_total which represents the grade of interest.

    Returns:
    - DataFrame with the count of students for each year and grade category.
    """
    df_total['Grade Category'] = pd.cut(df_total[column_name], bins=bins, labels=labels, right=False)
    grade_counts_by_year = df_total.groupby(['an', 'Grade Category']).size().unstack().fillna(0).astype(int)

    return grade_counts_by_year


def generate_line_chart_figure(data_records):
    """
    Generate the figure (data and layout) for a line chart visualization based on the provided data records.

    Parameters:
    - data_records: List of dictionaries representing the data to be plotted.

    Returns:
    - A dictionary containing the data and layout for the line chart.
    """
    data_df = pd.DataFrame(data_records).set_index("Grade Category")
    return {
        'data': [
            {'x': list(range(2014, 2024)),
             'y': data_df.loc[grade].values[:-1],  # exclude coloana "Total"
             'mode': 'lines+markers',
             'name': grade,
             'text': [f"Categorie notă: {grade}<br>An: {x}<br>Număr de elevi: {y}"
                      for x, y in zip(list(range(2014, 2024)), data_df.loc[grade])],
             'hoverinfo': 'text'
             } for grade in labels
        ],
        'layout': {
            'title': 'Evoluția notelor pe ani',
            'xaxis': {'title': 'An'},
            'yaxis': {'title': 'Număr de elevi'}
        }
    }


# Color palette
ylgnbu_colors = [
    "#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"
]

# Categorizing the grades
bins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
labels = ["1 - 1.99", "2 - 2.99", "3 - 3.99", "4 - 4.99", "5 - 5.99", "6 - 6.99", "7 - 7.99", "8 - 8.99",
          "9 - 9.99", "10"]

# Creating the application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Defining the appearance of the application
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
        ], id="title2", className="create_container1")
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
        ], id="title3", className="create_container1")
    ], id="header2", className="flex-display", style={"margin": "50px"}),
    dcc.Dropdown(
        id='column-dropdown',
        options=[
            {'label': 'Nota finală română', 'value': 'nota finala romana'},
            {'label': 'Nota finală matematică', 'value': 'nota finala matematica'},
            {'label': 'Media finală', 'value': 'media finala'},
            {'label': 'Media V-VIII', 'value': 'media v-viii'}
        ],
        value='media finala',  # default value
        clearable=False  # prevent the user from clearing the selection
    ),
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
    dcc.Graph(id='line-chart'),
])


# Defining the function to update the chart based on the grade and grouping
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
    [Output('dynamic-table', 'children'),
     Output('line-chart', 'figure')],
    [Input('display-mode', 'value'),
     Input('column-dropdown', 'value')]
)
def update_table_and_chart(display_mode, selected_column):
    grade_counts_by_year = prepare_data_for_selected_column(selected_column)

    transposed_table = grade_counts_by_year.transpose()
    transposed_table["Total"] = transposed_table.sum(axis=1)

    min_value = transposed_table.drop("Total", axis=1).values.min()
    max_value = transposed_table.drop("Total", axis=1).values.max()
    if display_mode == "numbers":
        data = transposed_table.reset_index().to_dict("records")
    else:
        percentage_data = (transposed_table.div(transposed_table.sum(axis=0), axis=1) * 100).round(2)
        data = percentage_data.reset_index().to_dict("records")

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
                'backgroundColor': get_continuous_color_gradient(value, min_value, max_value),
                'color': 'white' if is_dark_color(get_continuous_color_gradient(value, min_value, max_value))
                else 'black',
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
    line_chart_figure = generate_line_chart_figure(data)
    return table, line_chart_figure


# Starting the Dash server
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
