"""
load_data.py

Downloads Premier League results + betting odds from football-data.co.uk,
keeps an untouched copy of each raw file, and loads a cleaned version
into a SQLite database (data/football.db, table: matches).

Run from the project root:  python load_data.py
"""
from pathlib import Path
import sqlite3

import pandas as pd

# Season codes used by football-data.co.uk: "2526" = 2025/26
SEASONS = ["2122", "2223", "2324", "2425", "2526"]
BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"  # E0 = Premier League

RAW_DIR = Path("data/raw")
DB_PATH = Path("data/football.db")

# The raw files have 100+ columns. We keep results + a few odds sources.
# H/D/A = home win / draw / away win.
# Columns without "C" were collected 1-2 days before the match;
# columns with "C" are closing odds (just before kickoff).
KEEP_COLUMNS = [
    "Date", "Time", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR",            # full-time home goals, away goals, result (H/D/A)
    "B365H", "B365D", "B365A",        # Bet365
    "PSH", "PSD", "PSA",              # Pinnacle (a "sharp" bookmaker, low margin)
    "AvgH", "AvgD", "AvgA",           # average across bookmakers
    "B365CH", "B365CD", "B365CA",     # Bet365 closing
    "PSCH", "PSCD", "PSCA",           # Pinnacle closing
    "AvgCH", "AvgCD", "AvgCA",        # market average closing
]


def download_season(season: str) -> pd.DataFrame:
    """Download a season once and save the raw file. Later runs reuse the saved copy."""
    raw_file = RAW_DIR / f"E0_{season}.csv"
    if not raw_file.exists():
        url = BASE_URL.format(season=season)
        print(f"Downloading {url}")
        df = pd.read_csv(url, encoding="latin-1")
        df.to_csv(raw_file, index=False)
    return pd.read_csv(raw_file, encoding="latin-1")


def clean(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Keep the columns we need, drop empty rows, fix dates, tag the season."""
    cols = [c for c in KEEP_COLUMNS if c in df.columns]  # not every season has every column
    df = df[cols].copy()
    df = df.dropna(subset=["HomeTeam", "AwayTeam"])      # files sometimes end with blank rows
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)  # source uses dd/mm/yyyy
    df.insert(0, "season", season)
    return df


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    frames = [clean(download_season(s), s) for s in SEASONS]
    matches = pd.concat(frames, ignore_index=True)

    conn = sqlite3.connect(DB_PATH)
    matches.to_sql("matches", conn, if_exists="replace", index=False)
    conn.close()

    print(f"\nLoaded {len(matches)} matches into {DB_PATH}")
    print(matches.groupby("season").size())  # expect 380 per season


if __name__ == "__main__":
    main()
