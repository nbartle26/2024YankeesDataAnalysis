import os
import pandas as pd
import plotly.graph_objects as go

# URLs for regular season and postseason data
REGULAR_SEASON_URL = 'https://www.baseball-reference.com/teams/NYY/2024-batting.shtml'
POSTSEASON_URL = 'https://www.baseball-reference.com/teams/NYY/2024.shtml#all_players_standard_batting'

# CSV filenames
REGULAR_SEASON_CSV = 'yankees_2024_regular_season.csv'
POSTSEASON_CSV = 'yankees_2024_postseason.csv'

def fetch_and_save_data(url, csv_file, table_index=0):
    print(f"Fetching data from {url}...")
    try:
        tables = pd.read_html(url)
        df = tables[table_index]
        df.to_csv(csv_file, index=False)
        print(f"✅ Data saved to {csv_file}")
        return df
    except Exception as e:
        print(f"❌ Error while fetching data: {e}")
        return pd.DataFrame()

def load_data(csv_file, url, table_index=0):
    if os.path.exists(csv_file):
        print(f"📂 Loading data from {csv_file}")
        return pd.read_csv(csv_file)
    else:
        return fetch_and_save_data(url, csv_file, table_index)

def clean_data(df):
    df.columns = df.columns.str.strip()
    df = df[df['PA'] != 'PA']
    df = df.copy()
    # Remove '*' and '#' from player names
    df['Player'] = df['Player'].str.replace('*', '', regex=False).str.replace('#', '', regex=False)
    df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
    df = df.dropna(subset=['PA'])
    df['PA'] = df['PA'].astype(int)
    for col in ['OBP', 'SLG']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['OBP', 'SLG'])
    return df

def create_figure(regular_df, postseason_df):
    # Filter qualified hitters for regular season (PA >= 150) + team totals
    regular_qualified = regular_df[(regular_df['PA'] >= 150) | (regular_df['Player'] == 'Team Totals')]
    postseason_qualified = postseason_df  # Using all postseason players

    # Separate team totals and individuals for regular season
    reg_team_totals = regular_qualified[regular_qualified['Player'] == 'Team Totals']
    reg_individuals = regular_qualified[regular_qualified['Player'] != 'Team Totals']

    # Separate team totals and individuals for postseason
    post_team_totals = postseason_qualified[postseason_qualified['Player'] == 'Team Totals']
    post_individuals = postseason_qualified[postseason_qualified['Player'] != 'Team Totals']

    # League averages
    reg_league_obp = 0.312
    reg_league_slg = 0.399
    post_league_obp = 0.302
    post_league_slg = 0.400

    fig = go.Figure()

    # Regular Season Traces
    fig.add_trace(go.Scatter(
        x=reg_individuals['OBP'],
        y=reg_individuals['SLG'],
        mode='markers',
        marker=dict(size=8, color='blue', line=dict(width=1, color='DarkSlateGrey')),
        text=reg_individuals['Player'],
        hovertemplate="<b>%{text}</b><br>OBP: %{x:.3f}<br>SLG: %{y:.3f}<extra></extra>",
        name="Qualified Yankee Hitters (Regular Season)",
        visible=True
    ))

    fig.add_trace(go.Scatter(
        x=reg_team_totals['OBP'],
        y=reg_team_totals['SLG'],
        mode='markers',
        marker=dict(size=10, color='black', symbol='circle'),
        text=reg_team_totals['Player'],
        hovertemplate="<b>%{text}</b><br>OBP: %{x:.3f}<br>SLG: %{y:.3f}<extra></extra>",
        name="Team Totals (Regular Season)",
        visible=True
    ))

    fig.add_trace(go.Scatter(
        x=[reg_league_obp],
        y=[reg_league_slg],
        mode='markers+text',
        marker=dict(size=12, color='black', symbol='x'),
        text=["League Avg"],
        textposition="top center",
        name="League Average (Regular Season)",
        visible=True
    ))

    # Postseason Traces (initially hidden)
    fig.add_trace(go.Scatter(
        x=post_individuals['OBP'],
        y=post_individuals['SLG'],
        mode='markers',
        marker=dict(size=8, color='blue', line=dict(width=1, color='DarkSlateGrey')),
        text=post_individuals['Player'],
        hovertemplate="<b>%{text}</b><br>OBP: %{x:.3f}<br>SLG: %{y:.3f}<extra></extra>",
        name="Qualified Yankee Hitters (Postseason)",
        visible=False
    ))

    fig.add_trace(go.Scatter(
        x=post_team_totals['OBP'],
        y=post_team_totals['SLG'],
        mode='markers',
        marker=dict(size=10, color='black', symbol='circle'),
        text=post_team_totals['Player'],
        hovertemplate="<b>%{text}</b><br>OBP: %{x:.3f}<br>SLG: %{y:.3f}<extra></extra>",
        name="Team Totals (Postseason)",
        visible=False
    ))

    fig.add_trace(go.Scatter(
        x=[post_league_obp],
        y=[post_league_slg],
        mode='markers+text',
        marker=dict(size=12, color='black', symbol='x'),
        text=["League Avg"],
        textposition="top center",
        name="League Average (Postseason)",
        visible=False
    ))

    # Update layout with buttons
    fig.update_layout(
        title={'text': "Yankees Offensive Analysis: OBP vs SLG (Regular Season)", 'x': 0.5, 'xanchor': 'center'},
        xaxis_title="On-Base Percentage (OBP)",
        yaxis_title="Slugging Percentage (SLG)",
        xaxis_tickformat=".3f",
        yaxis_tickformat=".3f",
        showlegend=True,
        updatemenus=[dict(
            type="buttons",
            direction="left",
            x=1,
            y=0,
            xanchor="right",
            yanchor="bottom",
            buttons=[
                dict(
                    label="2024 Postseason Analysis",
                    method="update",
                    args=[
                        {"visible": [False, False, False, True, True, True]},
                        {"title": "Yankees Offensive Analysis: OBP vs SLG (Postseason)"}
                    ],
                ),
                dict(
                    label="2024 Season Analysis",
                    method="update",
                    args=[
                        {"visible": [True, True, True, False, False, False]},
                        {"title": "Yankees Offensive Analysis: OBP vs SLG (Regular Season)"}
                    ],
                ),
            ],
        )]
    )

    return fig

def main():
    regular_df = load_data(REGULAR_SEASON_CSV, REGULAR_SEASON_URL)
    postseason_df = load_data(POSTSEASON_CSV, POSTSEASON_URL, table_index=1)

    if regular_df.empty or postseason_df.empty:
        print("❌ One or both datasets are empty, cannot plot.")
        return

    regular_df = clean_data(regular_df)
    postseason_df = clean_data(postseason_df)

    fig = create_figure(regular_df, postseason_df)
    fig.show()

if __name__ == "__main__":
    main()
