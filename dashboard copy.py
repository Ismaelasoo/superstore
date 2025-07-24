# --- 0. IMPORTACIÓN DE LIBRERÍAS ---
from dash import Dash, dcc, html, dash_table, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import os
import dash_bootstrap_components as dbc

# --- 1. CARGA Y PREPARACIÓN DE DATOS ---
RUTA_CARPETA_DATOS = "data"
NOMBRE_ARCHIVO = "data_all.csv"
RUTA_COMPLETA_ENTRADA = os.path.join(RUTA_CARPETA_DATOS, NOMBRE_ARCHIVO)

try:
    df = pd.read_csv(RUTA_COMPLETA_ENTRADA)
except FileNotFoundError:
    print(f"ERROR: No se encontró el archivo '{RUTA_COMPLETA_ENTRADA}'.")
    # En un entorno de servidor, es mejor lanzar una excepción que salir
    raise FileNotFoundError(f"El archivo de datos no se encontró en la ruta: {RUTA_COMPLETA_ENTRADA}")

df['OrderDate'] = pd.to_datetime(df['OrderDate'])
df['ShipDate'] = pd.to_datetime(df['ShipDate'])
df = df.sort_values('OrderDate')

us_state_to_abbrev = {"Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
df['State_Code'] = df['States'].map(us_state_to_abbrev)
abbrev_to_us_state = {v: k for k, v in us_state_to_abbrev.items()}

# --- 2. INICIALIZACIÓN DE LA APP DASH ---
# Usamos un tema externo de Bootstrap para un look más moderno
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# --- 3. DISEÑO DEL LAYOUT DEL DASHBOARD ---
app.layout = dbc.Container([
    dcc.Store(id='crossfilter-store'),
    
    dbc.Row(dbc.Col(html.H1("Dashboard de Análisis de Ventas", className='text-center text-white my-4'), width=12)),
    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='dropdown-region', options=[{'label': region, 'value': region} for region in df['Region'].unique()] + [{'label': 'Todas las Regiones', 'value': 'All'}], value='All', clearable=False), width=6),
            dbc.Col(dcc.DatePickerRange(id='datepicker-range', min_date_allowed=df['OrderDate'].min().date(), max_date_allowed=df['OrderDate'].max().date(), start_date=df['OrderDate'].min().date(), end_date=df['OrderDate'].max().date(), display_format='DD/MM/YYYY'), width=6),
        ])
    ]), className='mb-4'),
    dbc.Row(id='kpi-cards-row', className='mb-4'),
    dbc.Row([dbc.Col(dbc.Card(dcc.Graph(id='line-chart-ventas')), width=12, className='mb-4')]),
    
    # ==================== INICIO DE LA REESTRUCTURACIÓN DEL LAYOUT ====================
    dbc.Row([
        # --- Columna Izquierda (Mapa + Tabla) ---
        dbc.Col([
            # Componente 1: Mapa
            dbc.Card(dcc.Graph(id='map-ventas-estado')),
            
            # Componente 2: Tabla
            html.H4("Top 10 Clientes por Ventas", className='text-center text-white mt-4 mb-3'),
            dbc.Card(dash_table.DataTable(
                id='table-top-clientes',
                style_as_list_view=True,
                style_cell={'textAlign': 'left', 'font-family': 'sans-serif', 'padding': '10px'},
                style_header={'backgroundColor': 'white', 'fontWeight': 'bold', 'border-bottom': '2px solid black'},
                style_data_conditional=[{"if": {"state": "active"}, "style": {"backgroundColor": "rgba(44, 62, 80, 0.3)", "color": "white", 'border': '1px solid #2c3e50'}}]
            ))
        ], width=7),

        # --- Columna Derecha (Treemap) ---
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(dbc.Row([
                    dbc.Col(html.H5("Desglose por Producto", className="my-auto")),
                    dbc.Col(dbc.Button("Reiniciar Filtros", id="reset-button", color="secondary", size="sm"), className="text-end")
                ])),
                dbc.CardBody(dcc.Graph(id='treemap-productos', style={'height': '100%'}))
            ], style={'height': '100%'}),
            width=5
        ),
    ], className='mb-4 align-items-stretch'),
    # ===================== FIN DE LA REESTRUCTURACIÓN DEL LAYOUT ======================

], fluid=True, style={'backgroundColor': "#b0b0b0"})

# --- 4. CALLBACKS PARA LA INTERACTIVIDAD ---
@app.callback(
    Output('crossfilter-store', 'data'),
    Input('map-ventas-estado', 'clickData'),
    Input('treemap-productos', 'clickData'),
    Input('reset-button', 'n_clicks')
)
def update_crossfilter_store(map_click, treemap_click, reset_clicks):
    triggered_id = ctx.triggered_id
    if triggered_id == 'reset-button': return {}
    store_data = {}
    if triggered_id == 'map-ventas-estado' and map_click:
        state_code = map_click['points'][0]['location']
        store_data = {'type': 'state', 'value': state_code}
    elif triggered_id == 'treemap-productos' and treemap_click:
        path = treemap_click['points'][0].get('id', '').split('/')
        if len(path) > 1:
            filter_type = 'Category' if len(path) == 2 else 'SubCategory'
            filter_value = path[-1]
            store_data = {'type': filter_type, 'value': filter_value}
    return store_data

@app.callback(
    Output('kpi-cards-row', 'children'),
    Output('line-chart-ventas', 'figure'),
    Output('map-ventas-estado', 'figure'),
    Output('treemap-productos', 'figure'),
    Output('table-top-clientes', 'data'),
    Output('table-top-clientes', 'columns'),
    Input('dropdown-region', 'value'),
    Input('datepicker-range', 'start_date'),
    Input('datepicker-range', 'end_date'),
    Input('crossfilter-store', 'data')
)
def update_all_components(region, start_date, end_date, crossfilter_data):
    dff = df[(df['OrderDate'] >= start_date) & (df['OrderDate'] <= end_date)]
    if region != 'All': dff = dff[dff['Region'] == region]
    
    crossfilter_data = crossfilter_data or {}
    filter_type = crossfilter_data.get('type')
    filter_value = crossfilter_data.get('value')
    
    if filter_type == 'state': dff = dff[dff['State_Code'] == filter_value]
    elif filter_type == 'Category': dff = dff[dff['Category'] == filter_value]
    elif filter_type == 'SubCategory': dff = dff[dff['SubCategory'] == filter_value]

    ventas_totales = dff['Sales'].sum()
    beneficio_total = dff['Profit'].sum()
    ordenes_unicas = dff['OrderID'].nunique()
    card_ventas = dbc.Card(dbc.CardBody([html.H5("Ventas Totales"), html.P(f"${ventas_totales:,.2f}", className="card-text fs-3 text-success")]))
    card_beneficio = dbc.Card(dbc.CardBody([html.H5("Beneficio Total"), html.P(f"${beneficio_total:,.2f}", className="card-text fs-3 text-primary")]))
    card_ordenes = dbc.Card(dbc.CardBody([html.H5("Órdenes Únicas"), html.P(f"{ordenes_unicas:,}", className="card-text fs-3 text-info")]))
    kpi_cards = [dbc.Col(card_ventas, width=4), dbc.Col(card_beneficio, width=4), dbc.Col(card_ordenes, width=4)]

    ventas_mensuales = dff.groupby(pd.Grouper(key='OrderDate', freq='ME'))['Sales'].sum().reset_index()
    fig_linea = px.line(ventas_mensuales, x='OrderDate', y='Sales', title='Evolución de Ventas Mensuales', labels={'OrderDate': 'Mes', 'Sales': 'Ventas'})
    fig_linea.update_traces(mode='lines+markers', line_color='#2c3e50').update_layout(paper_bgcolor='white', plot_bgcolor='white', font_color='#2c3e50', margin=dict(t=50, b=10, l=10, r=10))

    dff_map = df[(df['OrderDate'] >= start_date) & (df['OrderDate'] <= end_date)]
    if region != 'All': dff_map = dff_map[dff_map['Region'] == region]
    ventas_por_estado = dff_map.groupby(['States', 'State_Code'])['Sales'].sum().reset_index()
    fig_mapa = px.choropleth(ventas_por_estado, locations='State_Code', locationmode='USA-states', color='Sales', scope='usa', title='Ventas por Estado', hover_name='States', color_continuous_scale=px.colors.sequential.Teal, labels={'Sales': 'Ventas Totales'})
    fig_mapa.update_layout(paper_bgcolor='white', geo_bgcolor='white', font_color='#2c3e50', margin=dict(t=50, b=10, l=10, r=10))
    if filter_type == 'Category' or filter_type == 'SubCategory':
        fig_mapa.update_traces(colorscale=[[0, '#e9ecef'], [1, '#e9ecef']], showscale=False)

    fig_treemap = px.treemap(dff, path=[px.Constant("Total"), 'Category', 'SubCategory'], values='Sales', color='Sales', color_continuous_scale=px.colors.sequential.GnBu)
    fig_treemap.update_layout(paper_bgcolor='white', font_color='#2c3e50', margin=dict(t=10, b=10, l=10, r=10), title_text=None)

    top_clientes_df = dff.groupby('CustomerName')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(10)
    top_clientes_df['Sales'] = top_clientes_df['Sales'].map('${:,.2f}'.format)
    data_tabla = top_clientes_df.to_dict('records')
    columnas_tabla = [{'name': i, 'id': i} for i in top_clientes_df.columns]

    return kpi_cards, fig_linea, fig_mapa, fig_treemap, data_tabla, columnas_tabla

# --- 5. EJECUCIÓN DE LA APLICACIÓN ---
if __name__ == '__main__':
    # Cambiamos app.run() a app.run_server() que es la forma recomendada
    app.run(debug=True)