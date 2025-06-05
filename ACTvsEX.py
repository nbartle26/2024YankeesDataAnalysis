import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objects as go

DATA_FILE = '2024regEXvsACT.csv'
LEAGUE_AVG_BA = 0.243

def load_expected_data(file_path):
    df = pd.read_csv(file_path)
    df['pa'] = pd.to_numeric(df['pa'], errors='coerce')
    df['ba'] = pd.to_numeric(df['ba'], errors='coerce')
    df['xba'] = pd.to_numeric(df['xba'], errors='coerce')
    df.dropna(subset=['pa', 'ba', 'xba'], inplace=True)
    return df

def create_bar_chart(df):
    qualified_df = df[df['pa'] >= 20].copy()
    qualified_df.sort_values(by='ba', ascending=False, inplace=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=qualified_df['player_name'],
        y=qualified_df['ba'],
        name='Avg',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=qualified_df['player_name'],
        y=qualified_df['xba'],
        name='xAvg',
        marker_color='red'
    ))

    # Add league average BA line as shape
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(qualified_df) - 0.5,
        y0=LEAGUE_AVG_BA,
        y1=LEAGUE_AVG_BA,
        line=dict(color='black', width=1, dash='dash'),
        xref='x',
        yref='y'
    )

    # Add dummy trace for legend entry
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        name='League Average BA = 0.243',
        showlegend=True
    ))

    fig.update_layout(
        title=dict(
            text="2024 Yankees Offensive Analysis: Actual vs Expected Performance",
            x=0.5,
            xanchor='center'
        ),
        yaxis=dict(
            tickformat=".3f",
            range=[0, 0.5]
        ),
        barmode='group',
        legend=dict(title="")
    )
    return fig

def main():
    df = load_expected_data(DATA_FILE)

    app = Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id='bar-chart', figure=create_bar_chart(df))
    ])

    app.run(debug=True)

if __name__ == "__main__":
    main()
