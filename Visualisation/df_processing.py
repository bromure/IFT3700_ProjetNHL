from pathlib import Path
from loguru import logger
import pandas
from tqdm import tqdm
import typer
import pandas as pd
from dotenv import load_dotenv
import os
import requests
import json

from Visualisation.dataset import DATA_DIR, INTERIM_DATA_DIR, EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, PROJ_ROOT, load_data

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR,
    output_path: Path = INTERIM_DATA_DIR,
    years: list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    # ----------------------------------------------
):
    # ---- Base dowloader ----
    dataframer(input_path, output_path, years)
    # -----------------------------------------
    

# -----------------------------------------------------------------------


def dataframer(input_path: str = RAW_DATA_DIR, output_path: str = INTERIM_DATA_DIR, 
               years: list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]) -> None:
    """
    From raw JSON play-by-play files, produce a DataFrame where each row is a single play,
    including game-level metadata like game ID, teams, score, etc.
    """
    events = []
    rosters = []
    
    # create output directories if they don't exist
    if not Path(output_path).exists():
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
    event_path = Path(output_path)/"events"
    roster_path = Path(output_path)/"rosters"
    event_path.mkdir(parents=True, exist_ok=True)
    roster_path.mkdir(parents=True, exist_ok=True)

    # process each year
    for year in tqdm(years):
        year_events, year_rosters = get_yearly_data(year, input_path)
        
        # convert to DataFrame
        df_events = pd.DataFrame(year_events)
        df_rosters = pd.DataFrame(year_rosters)
        
        # log shapes
        logger.info(f"{year} events DataFrame shape: {df_events.shape}")
        logger.info(f"{year} rosters DataFrame shape: {df_rosters.shape}")

        try:
            # save to CSV
            df_events.to_csv(event_path / f"events_{year}.csv", index=False)
            df_rosters.to_csv(roster_path / f"rosters_{year}.csv", index=False)
            logger.success(f"Data for {year} processed and saved to {output_path}.")
            
        except Exception as e:
            logger.error(f"Error saving DataFrames to CSV at {output_path}: {e}")
            raise e

    return None


def get_yearly_data(year: int, input_path: str) -> list[dict]:
    """
    Retrieve NHL data for a given year from local storage or API,
    returning a list of game dictionaries.
    """
    # Initialize lists to hold events and rosters
    year_events = []
    year_rosters = []
    year_path = Path(input_path) / str(year)
    
    # Check if data exists locally; if not, download it
    if not year_path.exists():
        logger.info(f"Data for year {year} not found locally at {year_path}. Downloading from API...")
        load_data(year, input_path)
        return get_yearly_data(year, input_path)
    
    # Process each game file in the year's directory
    for game_file in tqdm(year_path.glob("play_by_play_*.json"), desc=f"Loading games for {year}"):
        with open(game_file, 'r') as f:
            # load game data and separate plays and roster
            game_data = json.load(f)
            roster = game_data.pop('rosterSpots', [])
            plays = game_data.pop('plays', [])
            
            # we do not care about these...
            rmv = ['easternUTCOffset', 'venueUTCOffset', 'tvBroadcasts', 'gameState']
            game_data = {k: v for k, v in game_data.items() if k not in rmv}
            game_info = flatten_json(game_data)
            
            # process plays and roster
            for play in plays:
                play_record = {**game_info, **flatten_json(play)}
                year_events.append(play_record)

            for player in roster:
                players = {**game_info, **flatten_json(player)}
                year_rosters.append(players)

    return year_events, year_rosters



def flatten_json(obj, parent_key="", sep="."):
    """
    TODO
    Docstring for flatten_json
    
    :param obj: Description
    :param parent_key: Description
    :param sep: Description
    """
    items = {}

    def join(key):
        return f"{parent_key}{sep}{key}" if parent_key else key

    # -------- dict --------
    if isinstance(obj, dict):
        for k, v in obj.items():
            items.update(flatten_json(v, join(k), sep))
        return items

    # -------- list --------
    if isinstance(obj, list):
        # check unordered-list condition
        can_merge = (
            all(isinstance(el, dict) for el in obj) and
            len(
                set().union(*(el.keys() for el in obj))
            ) == sum(len(el) for el in obj)
        )

        # unordered → merge keys
        if can_merge:
            for el in obj:
                for k, v in el.items():
                    items.update(flatten_json(v, join(k), sep))
            return items

        # ordered → index-based
        for i, el in enumerate(obj):
            items.update(flatten_json(el, join(str(i)), sep))
        return items

    # -------- scalar --------
    items[parent_key] = obj
    return items



if __name__ == "__main__":
    app()
    # python Visualisation/df_processing.py
