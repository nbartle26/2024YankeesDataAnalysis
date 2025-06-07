import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context
import plotly.graph_objects as go

DATA_FILE = '2024regEXvsACT.csv'

LEAGUE_AVGS = {
    'avg': 0.243,
    'xavg': 0.242,
    'obp': 0.320,
    'xobp': 0.324,
    'slg': 0.399,
    'xslg': 0.397,
    'woba': 0.310,
    'xwoba': 0.312
}

BUTTONS = [
    {'key': 'avg', 'label': 'Avg vs xAvg', 'col1': 'ba', 'col2': 'xba',
     'ymax': 0.4, 'yinterval': 0.05, 'league_avg1': LEAGUE_AVGS['avg'], 'league_avg2': LEAGUE_AVGS['xavg'],
     'league_avg1_color': 'blue', 'league_avg2_color': 'red'},
    {'key': 'slg', 'label': 'SLG vs xSLG', 'col1': 'slg', 'col2': 'xslg',
     'ymax': 0.8, 'yinterval': 0.1, 'league_avg1': LEAGUE_AVGS['slg'], 'league_avg2': LEAGUE_AVGS['xslg'],
     'league_avg1_color': 'blue', 'league_avg2_color': 'red'},
    {'key': 'obp', 'label': 'OBP vs xOBP', 'col1': 'obp', 'col2': 'xobp',
     'ymax': 0.6, 'yinterval': 0.1, 'league_avg1': LEAGUE_AVGS['obp'], 'league_avg2': LEAGUE_AVGS['xobp'],
     'league_avg1_color': 'blue', 'league_avg2_color': 'yellow'},
    {'key': 'woba', 'label': 'WOBA vs xWOBA', 'col1': 'woba', 'col2': 'xwoba',
     'ymax': 0.6, 'yinterval': 0.05, 'league_avg1': LEAGUE_AVGS['woba'], 'league_avg2': LEAGUE_AVGS['xwoba'],
     'league_avg1_color': 'blue', 'league_avg2_color': 'red'},
]

def load_expected_data(file_path):
    df = pd.read_csv(file_path)
    # Convert numeric columns and drop rows with missing key data
    numeric_cols = ['pa', 'ba', 'xba', 'obp', 'xobp', 'slg', 'xslg', 'woba', 'xwoba']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['pa', 'ba', 'xba'], inplace=True)
    return df

def create_bar_chart(df, col1, col2, league_avg1, league_avg2, league_avg1_color, league_avg2_color, ymax, yinterval):
    qualified_df = df[df['pa'] >= 20].copy()
    qualified_df.sort_values(by=col1, ascending=False, inplace=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=qualified_df['player_name'],
        y=qualified_df[col1],
        name=col1.upper(),
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=qualified_df['player_name'],
        y=qualified_df[col2],
        name=col2.upper(),
        marker_color='red'
    ))

    # Add league average lines
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(qualified_df) - 0.5,
        y0=league_avg1,
        y1=league_avg1,
        line=dict(color=league_avg1_color, width=2, dash='dot'),
        xref='x',
        yref='y'
    )
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(qualified_df) - 0.5,
        y0=league_avg2,
        y1=league_avg2,
        line=dict(color=league_avg2_color, width=2, dash='dot'),
        xref='x',
        yref='y'
    )

    # Dummy traces for legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='lines',
        line=dict(color=league_avg1_color, width=2, dash='dot'),
        name=f'League Average {col1.upper()} = {league_avg1:.3f}'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='lines',
        line=dict(color=league_avg2_color, width=2, dash='dot'),
        name=f'League Average {col2.upper()} = {league_avg2:.3f}'
    ))

    fig.update_layout(
        title=dict(
            text=f"2024 Yankees Offensive Analysis: {col1.upper()} vs {col2.upper()}",
            x=0.5,
            xanchor='center'
        ),
        yaxis=dict(
            tickformat=".3f",
            range=[0, ymax],
            dtick=yinterval
        ),
        barmode='group',
        legend=dict(title="")
    )
    return fig

def main():
    df = load_expected_data(DATA_FILE)
    app = Dash(__name__)

    # Initial figure for Avg vs xAvg
    initial_button = BUTTONS[0]
    initial_fig = create_bar_chart(
        df,
        initial_button['col1'],
        initial_button['col2'],
        initial_button['league_avg1'],
        initial_button['league_avg2'],
        initial_button['league_avg1_color'],
        initial_button['league_avg2_color'],
        initial_button['ymax'],
        initial_button['yinterval']
    )

    app.layout = html.Div(
        children=[
            dcc.Graph(id='bar-chart', figure=initial_fig),
            html.Div(
                [
                    html.Button(button['label'], id={'type': 'metric-button', 'index': button['key']}, n_clicks=0)
                    for button in BUTTONS
                ],
                style={
                    'position': 'fixed',
                    'bottom': '20px',
                    'right': '20px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '10px',
                    'zIndex': '1000'  # make sure buttons are on top
                }
            )
        ],
        style={
            'background-image': 'url("/assets/dashSitebackground.jpeg")',
            'background-size': 'cover',
            'background-repeat': 'no-repeat',
            'background-position': 'center center',
            'height': '100vh',
            'width': '100vw',
            'padding': '20px',
            'color': 'white'  # Optional: make text white for contrast
        }
    )

    @app.callback(
        Output('bar-chart', 'figure'),
        [Input({'type': 'metric-button', 'index': button['key']}, 'n_clicks') for button in BUTTONS]
    )
    def update_figure(*n_clicks):
        ctx = callback_context
        if not ctx.triggered:
            button_id = BUTTONS[0]['key']
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            # button_id looks like '{"type":"metric-button","index":"avg"}'
            import json
            button_id = json.loads(button_id)['index']

        button = next(filter(lambda b: b['key'] == button_id, BUTTONS), BUTTONS[0])

        fig = create_bar_chart(
            df,
            button['col1'],
            button['col2'],
            button['league_avg1'],
            button['league_avg2'],
            button['league_avg1_color'],
            button['league_avg2_color'],
            button['ymax'],
            button['yinterval']
        )
        return fig

    app.run(debug=True)


if __name__ == "__main__":
    main()
