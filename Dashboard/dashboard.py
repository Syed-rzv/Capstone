import os
from pathlib import Path
from dotenv import load_dotenv
import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from mysql.connector import pooling
from datetime import datetime

# load env from API subfolder
env_path = Path(__file__).parent.parent / 'crisislens-API' / '.env'
load_dotenv(env_path)

# setup db pool
pool = pooling.MySQLConnectionPool(
    pool_name="main",
    pool_size=5,
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def get_date_bounds():
    """Get min/max dates from emergency_data for dynamic date picker defaults"""
    conn = pool.get_connection()
    try:
        df = pd.read_sql("SELECT MIN(DATE(timestamp)) as start, MAX(DATE(timestamp)) as end FROM emergency_data", conn)
        return df.at[0, 'start'], df.at[0, 'end']
    finally:
        if conn.is_connected():
            conn.close()

min_date, max_date = get_date_bounds() 

def get_calls(start=None, end=None, types=None, town=None, zip_code=None):
    """Grab emergency calls with filters, with dynamic date handling"""
    q = """
        SELECT timestamp, emergency_type, caller_age, caller_gender,
               latitude, longitude, emergency_title, township, zipcode
        FROM emergency_data
        WHERE 1=1
    """
    params = []

    # Handle date filters with clamping to actual dataset bounds
    if start and end:
        # Convert to date if string
        start_date = pd.to_datetime(start).date() if isinstance(start, str) else start
        end_date = pd.to_datetime(end).date() if isinstance(end, str) else end

        # Clamp to available min/max dates in dataset
        conn = pool.get_connection()
        try:
            bounds = pd.read_sql(
                "SELECT MIN(DATE(timestamp)) as start, MAX(DATE(timestamp)) as end FROM emergency_data",
                conn
            )
            min_ts = bounds.at[0, 'start']
            max_ts = bounds.at[0, 'end']
            start_date = max(start_date, min_ts)
            end_date = min(end_date, max_ts)
        finally:
            if conn.is_connected():
                conn.close()

        q += " AND DATE(timestamp) BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    # Emergency type filter
    if types and len(types) > 0:
        placeholders = ','.join(['%s'] * len(types))
        q += f" AND emergency_type IN ({placeholders})"
        params.extend(types)

    # Township filter
    if town:
        q += " AND township = %s"
        params.append(town)

    # Zipcode filter
    if zip_code:
        q += " AND zipcode = %s"
        params.append(zip_code)

    # Execute query
    conn = pool.get_connection()
    try:
        df = pd.read_sql(q, conn, params=params)
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"db error: {e}")
        return pd.DataFrame()
    finally:
        if conn.is_connected():
            conn.close()


def get_townships():
    """get unique townships for dropdown"""
    conn = pool.get_connection()
    try:
        query = "SELECT DISTINCT township FROM emergency_data WHERE township IS NOT NULL ORDER BY township"
        df = pd.read_sql(query, conn)
        return [{'label': t, 'value': t} for t in df['township'].tolist()]
    except:
        return []
    finally:
        if conn.is_connected():
            conn.close()

def get_zipcodes():
    """get unique zipcodes for dropdown"""
    conn = pool.get_connection()
    try:
        query = "SELECT DISTINCT zipcode FROM emergency_data WHERE zipcode IS NOT NULL ORDER BY zipcode"
        df = pd.read_sql(query, conn)
        return [{'label': str(z), 'value': str(z)} for z in df['zipcode'].tolist()]
    except:
        return []
    finally:
        if conn.is_connected():
            conn.close()

# dash setup with modern dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "CrisisLens"

# Enhanced CSS with FIXED z-index for all dropdowns
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            body {
                background: #0a0a0a;
                color: #e0e0e0;
                margin: 0;
                padding: 0;
            }
            
            /* CRITICAL: Fix all dropdown z-index issues */
            .DateRangePicker_picker {
                z-index: 9999 !important;
                margin-top: 8px !important;
            }
            
            .DayPickerKeyboardShortcuts_panel {
                z-index: 10000 !important;
            }
            
            /* Fix for react-select dropdowns */
            div[class*="menu"] {
                z-index: 9999 !important;
            }
            
            .Select-menu-outer {
                z-index: 9999 !important;
            }
            
            /* Ensure filter section has lower z-index */
            .filter-section {
                position: relative;
                z-index: 1 !important;
            }
            
            /* Chart containers should be below dropdowns */
            .chart-container {
                position: relative;
                z-index: 0;
            }
            
            /* Glass morphism cards */
            .glass-card {
                background: rgba(18, 18, 18, 0.85);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(34, 197, 94, 0.15);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 
                            0 0 0 1px rgba(34, 197, 94, 0.1) inset;
                transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
                overflow: hidden;
            }
            
            .glass-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 16px 48px rgba(34, 197, 94, 0.15),
                            0 0 0 1px rgba(34, 197, 94, 0.2) inset;
                border-color: rgba(34, 197, 94, 0.3);
            }
            
            /* Metric cards with CONSISTENT HEIGHT */
            .metric-card {
                background: linear-gradient(135deg, 
                    rgba(34, 197, 94, 0.08) 0%, 
                    rgba(21, 128, 61, 0.12) 100%);
                border: 1px solid rgba(34, 197, 94, 0.25);
                border-radius: 14px;
                padding: 24px;
                text-align: center;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                min-height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, 
                    transparent, 
                    rgba(34, 197, 94, 0.1), 
                    transparent);
                transition: left 0.5s;
            }
            
            .metric-card:hover::before {
                left: 100%;
            }
            
            .metric-card:hover {
                background: linear-gradient(135deg, 
                    rgba(34, 197, 94, 0.12) 0%, 
                    rgba(21, 128, 61, 0.16) 100%);
                transform: translateY(-2px) scale(1.02);
                border-color: rgba(34, 197, 94, 0.4);
            }
            
            /* CONSISTENT metric value sizing */
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: #22c55e;
                text-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
                margin-bottom: 8px;
                line-height: 1.2;
                min-height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .metric-value.large-text {
                font-size: 1.75rem;
            }
            
            .metric-label {
                font-size: 0.8rem;
                color: #9ca3af;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-weight: 500;
            }
            
            /* Chart containers */
            .chart-container {
                background: rgba(18, 18, 18, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 14px;
                padding: 16px;
                border: 1px solid rgba(34, 197, 94, 0.12);
                transition: all 0.3s ease;
                cursor: pointer;
                height: 100%;
                position: relative;
                z-index: 0;
            }
            
            .chart-container:hover {
                border-color: rgba(34, 197, 94, 0.35);
                box-shadow: 0 8px 24px rgba(34, 197, 94, 0.15);
                transform: translateY(-2px);
            }
            
            /* Header styling */
            h1 {
                color: #22c55e;
                text-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
                font-weight: 700;
                letter-spacing: 1px;
                margin: 0;
            }
            
            /* Filter section */
            .filter-section {
                background: rgba(18, 18, 18, 0.9);
                backdrop-filter: blur(15px);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid rgba(34, 197, 94, 0.2);
                margin-bottom: 24px;
                position: relative;
                z-index: 1;
            }
            
            /* Dropdown and input styling */
            .Select-control, 
            .form-control,
            div[class*="css-"] div[class*="control"] {
                background: rgba(30, 30, 30, 0.8) !important;
                border: 1px solid rgba(34, 197, 94, 0.25) !important;
                border-radius: 8px !important;
                color: #22c55e !important;
                transition: all 0.2s ease !important;
            }
            
            .Select-control:hover,
            div[class*="css-"] div[class*="control"]:hover {
                border-color: rgba(34, 197, 94, 0.4) !important;
                box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1) !important;
            }
            
            /* Date picker styling */
            .DateRangePickerInput {
                background: rgba(30, 30, 30, 0.8) !important;
                border: 1px solid rgba(34, 197, 94, 0.25) !important;
                border-radius: 8px !important;
            }
            
            .DateInput_input {
                background: transparent !important;
                color: #22c55e !important;
                font-size: 0.85rem !important;
                padding: 8px 12px !important;
            }
            
            .CalendarDay__selected {
                background: #22c55e !important;
                color: #0a0a0a !important;
            }
            
            .CalendarDay__selected_span {
                background: rgba(34, 197, 94, 0.2) !important;
                color: #22c55e !important;
            }
            
            .DayPickerKeyboardShortcuts_show__bottomRight {
                border-right: 33px solid #22c55e !important;
            }
            
            /* Labels */
            label {
                color: #22c55e !important;
                font-weight: 500;
                margin-bottom: 10px;
                font-size: 0.85rem !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                display: block;
            }
            
            /* Modal styling */
            .modal-content {
                background: rgba(18, 18, 18, 0.95) !important;
                border: 1px solid rgba(34, 197, 94, 0.2) !important;
                backdrop-filter: blur(20px);
            }
            
            .modal-header {
                border-bottom: 1px solid rgba(34, 197, 94, 0.2) !important;
            }
            
            .modal-title {
                color: #22c55e !important;
            }
            
            /* Loading spinner */
            ._dash-loading {
                color: #22c55e !important;
            }
            
            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(30, 30, 30, 0.5);
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(34, 197, 94, 0.3);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(34, 197, 94, 0.5);

            /* Dropdown menu items styling */
            .Select-menu-outer, div[class*="menu"] {
                background-color: #1e1e1e !important;
                color: #22c55e !important;
            }

            .Select-option {
                background-color: #1e1e1e !important;
                color: #22c55e !important;
            }

            .Select-option:hover {
                background-color: #15803d !important;
                color: #ffffff !important;
            }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Preload dropdown options
township_options = get_townships()
zipcode_options = get_zipcodes()
def get_emergency_types():
    """Get unique emergency types for dropdown"""
    conn = pool.get_connection()
    try:
        df = pd.read_sql("SELECT DISTINCT emergency_type FROM emergency_data WHERE emergency_type IS NOT NULL ORDER BY emergency_type", conn)
        return [{'label': t, 'value': t} for t in df['emergency_type'].tolist()]
    finally:
        if conn.is_connected():
            conn.close()

type_options = get_emergency_types()

# Enhanced layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1(" CrisisLens", className="text-center mb-2", style={'fontSize': '3.5rem'}),
            html.P("Real-Time Emergency Analytics Dashboard", 
                   className="text-center", 
                   style={'fontSize': '1rem', 'color': '#9ca3af', 'letterSpacing': '1px'})
        ])
    ], className="my-4"),
    
    # Filters with proper z-index
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Label("Date Range"),
                        dcc.DatePickerRange(
                            id='date-range',
                            start_date=min_date,
                            end_date=max_date,
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'}
                        ),
                    ], md=3),
                    dbc.Col([
                        html.Label("Emergency Type"),
                        dcc.Dropdown(
                            id='call-types',
                            options=type_options,
                            multi=True, # Allow multiple selections
                            placeholder="All types",
                            style={
                                    'backgroundColor': '#1e1e1e',  # dark background
                                     'color': '#22c55e',            # text color
                        'border': '1px solid rgba(34, 197, 94, 0.25)'
                        }
    
                        ),
                    ], md=3),
                    dbc.Col([
                        html.Label("Township"),
                        dcc.Dropdown(
                            id='township',
                            options=township_options,
                            placeholder="All townships",
                            style={
                                'backgroundColor': '#1e1e1e',  # dark background
                                'color': '#22c55e',            # text color
                                'border': '1px solid rgba(34, 197, 94, 0.25)'
                            }
                        ),
                    ], md=3),
                    dbc.Col([
                        html.Label("Zipcode"),
                        dcc.Dropdown(   
                            id='zipcode',
                            options=zipcode_options,
                            placeholder="All zipcodes",
                            style={
                                'backgroundColor': '#1e1e1e',  # dark background
                                'color': '#22c55e',            # text color
                                'border': '1px solid rgba(34, 197, 94, 0.25)'
                            }
                        ),
                    ], md=3),
                ], className="g-3")
            ], className="filter-section")
        ])
    ]),
    
    # KPI Metrics with consistent heights
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div(id='total-calls', children="0", className="metric-value"),
                html.Div("Total Calls", className="metric-label")
            ], className="metric-card")
        ], md=3),
        dbc.Col([
            html.Div([
                html.Div(id='top-type', children="—", className="metric-value large-text"),
                html.Div("Most Common", className="metric-label")
            ], className="metric-card")
        ], md=3),
        dbc.Col([
            html.Div([
                html.Div(id='avg-age', children="—", className="metric-value"),
                html.Div("Average Age", className="metric-label")
            ], className="metric-card")
        ], md=3),
        dbc.Col([
            html.Div([
                html.Div(id='peak-hour', children="—", className="metric-value large-text"),
                html.Div("Peak Hour", className="metric-label")
            ], className="metric-card")
        ], md=3),
    ], className="mb-4 g-3"),
    
    # Charts Grid
    dbc.Row([
        # Left column - 2x2 grid
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            dcc.Graph(
                                id='timeline-chart', 
                                config={'displayModeBar': False}, 
                                style={'height': '260px'}
                            ), 
                            type="default",
                            color="#22c55e"
                        )
                    ], className="chart-container", id='timeline-container')
                ], md=6),
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            dcc.Graph(
                                id='type-pie', 
                                config={'displayModeBar': False}, 
                                style={'height': '260px'}
                            ), 
                            type="default",
                            color="#22c55e"
                        )
                    ], className="chart-container", id='pie-container')
                ], md=6),
            ], className="mb-3 g-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            dcc.Graph(
                                id='age-bars', 
                                config={'displayModeBar': False}, 
                                style={'height': '260px'}
                            ), 
                            type="default",
                            color="#22c55e"
                        )
                    ], className="chart-container", id='age-container')
                ], md=6),
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            dcc.Graph(
                                id='gender-chart', 
                                config={'displayModeBar': False}, 
                                style={'height': '260px'}
                            ), 
                            type="default",
                            color="#22c55e"
                        )
                    ], className="chart-container", id='gender-container')
                ], md=6),
            ], className="g-3")
        ], md=8),
        
        # Right column - Map
        dbc.Col([
            html.Div([
                dcc.Loading(
                    dcc.Graph(
                        id='map-view', 
                        config={'displayModeBar': False}, 
                        style={'height': '550px'}
                    ), 
                    type="default",
                    color="#22c55e"
                )
            ], className="chart-container", id='map-container')
        ], md=4),
    ], className="g-3"),
    
    # Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id='modal-title')),
        dbc.ModalBody(id='modal-body'),
    ], id='chart-modal', size='xl', centered=True),
    
], fluid=True, style={'maxWidth': '1900px', 'padding': '24px'})

@app.callback(
    [Output('timeline-chart', 'figure'),
     Output('type-pie', 'figure'),
     Output('age-bars', 'figure'),
     Output('gender-chart', 'figure'),
     Output('map-view', 'figure'),
     Output('total-calls', 'children'),
     Output('top-type', 'children'),
     Output('avg-age', 'children'),
     Output('peak-hour', 'children')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('call-types', 'value'),
     Input('township', 'value'),
     Input('zipcode', 'value')]
)
def update_dashboard(start, end, types, town, zip_code):
    # Fetch filtered data
    df = get_calls(start, end, types, town, zip_code)
    
    # Define theme colors
    GREEN = '#22c55e'
    GREEN_DARK = '#15803d'
    GREEN_LIGHT = '#86efac'
    
    # Handle empty data
    if df.empty:
        empty = go.Figure()
        empty.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'No data available for selected filters',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False,
                'font': {'size': 18, 'color': '#6b7280'}
            }]
        )
        return [empty]*5 + ["0", "—", "—", "—"]
    
    # Smart time aggregation based on date range
    if not df.empty and 'timestamp' in df.columns:
        start_dt = df['timestamp'].min()
        end_dt = df['timestamp'].max()
        days_span = (end_dt - start_dt).days
    else:
        days_span = 365  # fallback

    # Determine aggregation level
    if days_span > 730:  # More than 2 years - aggregate by year
        df['period'] = df['timestamp'].dt.to_period('Y').astype(str)
        time_label = 'Yearly Volume'
        hover_format = '<b>%{x}</b><br>Calls: %{y:,}<extra></extra>'
    elif days_span > 90:  # More than 3 months - aggregate by month
        df['period'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()
        time_label = 'Monthly Volume'
        hover_format = '<b>%{x|%B %Y}</b><br>Calls: %{y:,}<extra></extra>'
    else:  # Daily aggregation
        df['period'] = df['timestamp'].dt.date
        time_label = 'Daily Volume'
        hover_format = '<b>%{x}</b><br>Calls: %{y:,}<extra></extra>'
    
    # Aggregate timeline data
    timeline_data = df.groupby('period').size().reset_index()
    timeline_data.columns = ['period', 'count']
    
    # Timeline chart
    timeline = go.Figure()
    timeline.add_trace(go.Scatter(
        x=timeline_data['period'], 
        y=timeline_data['count'],
        mode='lines',
        line=dict(color=GREEN, width=3, shape='spline'),
        fill='tozeroy',
        fillcolor=f'rgba(34, 197, 94, 0.15)',
        hovertemplate=hover_format
    ))
    timeline.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={'text': time_label, 'font': {'size': 16, 'color': GREEN}, 'x': 0.5, 'xanchor': 'center'},
        margin=dict(l=50, r=30, t=50, b=40),
        xaxis={'showgrid': False, 'color': '#6b7280'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(34, 197, 94, 0.1)', 'color': '#6b7280'},
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(18, 18, 18, 0.9)', font_color=GREEN)
    )
    
    # Type breakdown pie
    type_counts = df['emergency_type'].value_counts()
    colors_pie = [GREEN, GREEN_DARK, GREEN_LIGHT, '#166534']
    
    type_pie = go.Figure(data=[go.Pie(
        labels=type_counts.index,
        values=type_counts.values,
        hole=0.5,
        marker=dict(colors=colors_pie, line=dict(color='#0a0a0a', width=2)),
        textfont=dict(size=13, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>'
    )])
    type_pie.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={'text': 'Type Breakdown', 'font': {'size': 16, 'color': GREEN}, 'x': 0.5, 'xanchor': 'center'},
        margin=dict(l=30, r=30, t=50, b=30),
        showlegend=True,
        legend=dict(font=dict(size=11, color='#e0e0e0'), bgcolor='rgba(0,0,0,0)')
    )
    
    # Age distribution
    age_hist = go.Figure()
    age_hist.add_trace(go.Histogram(
        x=df['caller_age'],
        nbinsx=25,
        marker=dict(
            color=GREEN, 
            line=dict(color='#0a0a0a', width=1),
            opacity=0.8
        ),
        hovertemplate='Age: %{x}<br>Count: %{y:,}<extra></extra>'
    ))
    age_hist.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={'text': 'Age Distribution', 'font': {'size': 16, 'color': GREEN}, 'x': 0.5, 'xanchor': 'center'},
        margin=dict(l=50, r=30, t=50, b=40),
        xaxis={'title': {'text': 'Age', 'font': {'color': '#9ca3af'}}, 'showgrid': False, 'color': '#6b7280'},
        yaxis={'title': {'text': 'Count', 'font': {'color': '#9ca3af'}}, 'showgrid': True, 'gridcolor': 'rgba(34, 197, 94, 0.1)', 'color': '#6b7280'},
        bargap=0.05
    )
    
    # Gender donut
    gender_data = df['caller_gender'].value_counts()
    gender_colors = [GREEN, GREEN_DARK, GREEN_LIGHT]
    
    gender_donut = go.Figure(data=[go.Pie(
        labels=gender_data.index,
        values=gender_data.values,
        hole=0.65,
        marker=dict(colors=gender_colors[:len(gender_data)], line=dict(color='#0a0a0a', width=2)),
        textfont=dict(size=13, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>'
    )])
    gender_donut.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={'text': 'Gender Distribution', 'font': {'size': 16, 'color': GREEN}, 'x': 0.5, 'xanchor': 'center'},
        margin=dict(l=30, r=30, t=50, b=30),
        showlegend=True,
        legend=dict(font=dict(size=11, color='#e0e0e0'), bgcolor='rgba(0,0,0,0)')
    )
    
    # Map visualization
    map_fig = px.scatter_mapbox(
        df, 
        lat='latitude', 
        lon='longitude',
        hover_name='emergency_title',
        hover_data={
            'township': True,
            'zipcode': True,
            'emergency_type': True,
            'latitude': False,
            'longitude': False
        },
        color='emergency_type',
        color_discrete_map={
            'EMS': GREEN, 
            'Fire': '#ef4444', 
            'Traffic': '#3b82f6'
        },
        zoom=9, 
        height=550
    )
    map_fig.update_layout(
        mapbox_style="carto-darkmatter",
        paper_bgcolor='rgba(0,0,0,0)',
        margin={"r":0, "t":0, "l":0, "b":0},
        legend=dict(
            font=dict(size=11, color='#e0e0e0'), 
            bgcolor='rgba(18, 18, 18, 0.8)',
            bordercolor='rgba(34, 197, 94, 0.2)',
            borderwidth=1
        )
    )
    
    # Calculate KPIs
    total = len(df)
    top_type = df['emergency_type'].mode()[0] if len(df) > 0 and not df['emergency_type'].empty else "—"
    avg_age = int(df['caller_age'].mean()) if not df['caller_age'].isna().all() else "—"
    
    if len(df) > 0 and 'timestamp' in df.columns:
        hour_mode = df['timestamp'].dt.hour.mode()
        if len(hour_mode) > 0:
            peak = hour_mode[0]
            peak_hour = f"{peak:02d}:00"
        else:
            peak_hour = "—"
    else:
        peak_hour = "—"
    
    return (
        timeline, type_pie, age_hist, gender_donut, map_fig,
        f"{total:,}", top_type, str(avg_age), peak_hour
    )

# Expandable charts modal
@app.callback(
    [Output('chart-modal', 'is_open'),
     Output('modal-title', 'children'),
     Output('modal-body', 'children')],
    [Input('timeline-container', 'n_clicks'),
     Input('pie-container', 'n_clicks'),
     Input('age-container', 'n_clicks'),
     Input('gender-container', 'n_clicks'),
     Input('map-container', 'n_clicks')],
    [State('chart-modal', 'is_open'),
     State('timeline-chart', 'figure'),
     State('type-pie', 'figure'),
     State('age-bars', 'figure'),
     State('gender-chart', 'figure'),
     State('map-view', 'figure')],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, n4, n5, is_open, timeline_fig, pie_fig, age_fig, gender_fig, map_fig):
    if not ctx.triggered_id:
        return is_open, "", ""
    
    chart_map = {
        'timeline-container': ('Call Volume Over Time', dcc.Graph(figure=timeline_fig, style={'height': '70vh'}, config={'displayModeBar': True})),
        'pie-container': ('Emergency Type Distribution', dcc.Graph(figure=pie_fig, style={'height': '70vh'}, config={'displayModeBar': True})),
        'age-container': ('Caller Age Distribution', dcc.Graph(figure=age_fig, style={'height': '70vh'}, config={'displayModeBar': True})),
        'gender-container': ('Gender Distribution', dcc.Graph(figure=gender_fig, style={'height': '70vh'}, config={'displayModeBar': True})),
        'map-container': ('Geographic Distribution', dcc.Graph(figure=map_fig, style={'height': '70vh'}, config={'displayModeBar': True})),
    }
    
    if ctx.triggered_id in chart_map:
        title, body = chart_map[ctx.triggered_id]
        return not is_open, title, body
    
    return is_open, "", ""

if __name__ == '__main__':
    app.run(debug=True, port=8050)