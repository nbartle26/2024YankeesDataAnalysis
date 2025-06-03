import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick   #axis scatter plot formatting

CSV_FILE = 'yankees_2024_batting.csv'
URL = 'https://www.baseball-reference.com/teams/NYY/2024-batting.shtml'

def fetch_and_save_data():
    """Fetches the Yankees 2024 batting data from Baseball-Reference and saves it as a CSV file."""
    print("Fetching data from Baseball-Reference...")
    try:
        tables = pd.read_html(URL)
        for table in tables:
            if 'PA' in table.columns:
                df = table
                break
        else:
            print("❌ 'PA' column not found in any table.")
            return pd.DataFrame()

        df.to_csv(CSV_FILE, index=False)
        print(f"✅ Data saved to {CSV_FILE}")
        return df
    except Exception as e:
        print(f"❌ Error while fetching data: {e}")
        return pd.DataFrame()

def load_data():
    """Loads the batting data from CSV if it exists; otherwise fetches from the web."""
    if os.path.exists(CSV_FILE):
        print(f"📂 Loading data from {CSV_FILE}")
        return pd.read_csv(CSV_FILE)
    else:
        return fetch_and_save_data()

def clean_and_split(df):
    """Cleans the DataFrame and returns both qualified and unqualified hitters."""
    df.columns = df.columns.str.strip()
    print("Available columns:", list(df.columns))

    df = df[df['PA'] != 'PA']  # Remove repeated header rows if present
    df = df.copy()
    df['PA'] = pd.to_numeric(df['PA'], errors='coerce')
    df = df.dropna(subset=['PA'])
    df['PA'] = df['PA'].astype(int)


    for col in ['OBP', 'SLG']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['OBP', 'SLG'])    

    # Filter for qualified and unqualified hitters
    qualified = df[df['PA'] >= 200].copy()
    unqualified = df[(df['PA'] < 200) & (df['PA'] > 0)].copy()  # Exclude PA == 0


    return qualified, unqualified




##Building a OBP vs SLG Scatter Plot for Qualified Hitters
def plot_obp_vs_slg(df):
    plt.figure(figsize=(12, 7))
    scatter = plt.scatter(
        df['OBP'], 
        df['SLG'], 
        s=df['PA'] / 5,  # size proportional to Plate Appearances
        alpha=0.7, 
        edgecolors='black',
        ##cmap='viridis'
    )
    
    for _, row in df.iterrows():
        plt.text(
            row['OBP'] + 0.002,  # small offset for readability
            row['SLG'] + 0.002,
            row['Player'],
            fontsize=8,
            alpha=0.75
        )
    
    plt.xlabel('On-Base Percentage (OBP)')
    plt.ylabel('Slugging Percentage (SLG)')
    plt.title('Yankees Qualified Hitters: OBP vs SLG (2024 Regular Season)')
    plt.grid(True)

    plt.gca().yaxis.set_major_formatter(mtick.FormatStrFormatter('%.3f'))   #format the y-axis

    plt.show()


def main():
    data = load_data()
    if data.empty:
        print("❌ No data available to process.")
        return

    qualified, unqualified = clean_and_split(data)

    columns_to_display = ['Player', 'PA', 'AB', 'H', 'HR', 'RBI', 'BB', 'BA', 'OBP', 'SLG']

    print("\n✅ Qualified Hitters (≥200 Plate Appearances):")
    qualified_cols = [col for col in columns_to_display if col in qualified.columns]
    print(qualified[qualified_cols])

    print("\n📋 Unqualified Hitters (<200 Plate Appearances, excluding PA = 0):")
    unqualified_cols = [col for col in columns_to_display if col in unqualified.columns]
    print(unqualified[unqualified_cols])

    # Calling the plotting function here
    plot_obp_vs_slg(qualified)

if __name__ == "__main__":
    main()

