from pathlib import Path
from loguru import logger
from tqdm import tqdm
import typer
from dotenv import load_dotenv
import os
import requests

from Visualisation.config import DATA_DIR, INTERIM_DATA_DIR, EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, PROJ_ROOT

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR,
    download_url: str = "https://api-web.nhle.com/v1/",
    years: list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    # ----------------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")
    for year in tqdm(years):
        get_yearly_data(year, file_name=f"nhl_data_{year}.csv", download_url=download_url, input_path=input_path)
    # -----------------------------------------
    
    '''
    Setup heuristic:
        1. Run script when opening project
        2. Asks for (input_path)
            i) if path is given, uses that path to load data locally
            ii) if no path is given, defaults to downloading the data from API
            
    ├── main
    │   ├── get_yearly_data         <- NHL data retrieval for a given year 
    |   │   ├── get_data            <- Gets data locally or from API
    |   |   |   └── get_web_data    <- Gets data from API
    |   │   ├── XXX save_data       <- Saves data locally (split from get_web_data)
 
    '''

# ---------------------------------------
# Load environment variables from .env
# ---------------------------------------
# When the project is opened in VS Code (or any IDE), python-dotenv
# will read the .env file in the project root.
# Users can edit .env locally to change DATASET_PATH without touching code.
'''
load_dotenv()

# Default dataset path from environment variable, fallback to ./data
DFT_LOCAL_DATA_PATH = os.getenv("DATASET_PATH", "./data")

# Ensure the directory exists
dataset_dir = Path(DFT_LOCAL_DATA_PATH)
dataset_dir.mkdir(parents=True, exist_ok=True)

'''

def get_web_data(file_name: str, download_url: str, save_path: str ) -> Path:
    """
    Download a dataset from a remote API and save it locally.
    
    Args:
        file_name (str): Name of the dataset file.       
        download_url (str): URL to download the dataset.
        save_path (str): Path to save the downloaded dataset.


    Returns:
        Path: Path to the dataset file.
        
    """

    response = requests.get(download_url, stream=True)
    response.raise_for_status()  # Raise an error for bad responses

    # Ensure the save directory exists (even if nested)
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    file_path = save_path / file_name

    # Write the content to a file in (8KB) chunks to avoid large RAM usage
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.success(f"Downloaded data from {download_url} and saved to {file_path}")
    return file_path
    


def get_data(file_name: str, download_url: str, input_path: str = None) -> Path:
    """
    Load a dataset either from a local path or from a remote API.
    
    Args:
        file_name (str): Name of the dataset file.       
        download_url (str): URL to download the dataset if not found locally.
        input_path (str, optional): User-specified path to look for the dataset.


    Returns:
        Path: Path to the dataset file.
        
    """
    # Create default dataset directory
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Determine the directory to use
    if input_path:
        data_path = Path(input_path)
    else:
        data_path = RAW_DATA_DIR

    # Ensure folder exists
    data_path.mkdir(parents=True, exist_ok=True)
    file_path = data_path / file_name\
        
    # | Branching of cases
    # └────────────────────────────
    # Case 1: Get data from local path
    
    # Check if file exists locally
    if file_path.exists():
        logger.info(f"Found local dataset: {file_path}")
        return file_path
    
    # Ask if path was correct and if user wants to try again
    answer = input(f"{file_name} not found at {file_path}. Try again with a different path? [y/n] ")
    if answer.lower() == "y":
        new_path = input("Enter new path: ")
        return get_data(file_name, download_url, input_path=new_path)
    
    # Case 2: Download data from API
    
    # Offer to download
    if download_url:
        answer = input(f"{file_name} not found locally. Download from API and save locally? [y/n] ")
        if answer.lower() == "y":
            logger.info(f"Downloading {file_name} from API...")
            return get_web_data(file_name, download_url, save_path=data_path)
        else:
            logger.warning("Download skipped. File not available locally.")
    
    # Case 3: Raise error if file cannot be found or downloaded
    logger.error(f"{file_name} not found locally and download declined or API.URL not provided.")
    raise FileNotFoundError()



def get_yearly_data(year: int, file_name: str, download_url: str, input_path: str = None) -> Path:
    """
    Wrapper to get data for a specific year. Sets the API URL and file name.
    
    Args:
        year (int): Year of the dataset.
        file_name (str): Name of the dataset file.       
        download_url (str): Start of API URL to get web data if not found locally.
        input_path (str, optional): User-specified path to look for the dataset.


    Returns:
        Path: Path to the dataset file.
        
    Game ID format (by https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md#game-ids):
        
    The first 4 digits identify the season of the game (ie. 2017 for the 2017-2018 season). 
    Always refer to a season with the starting year. A game played in March 2018 would still have a game ID that starts with 2017
        
    The next 2 digits give the type of game, where 01 = preseason, 02 = regular season, 03 = playoffs, 04 = all-star
        
    The final 4 digits identify the specific game number. 
    For regular season and preseason games, this ranges from 0001 to the number of games played. 
    (1353 for seasons with 32 teams (2022 - Present), 1271 for seasons with 31 teams (2017 - 2020) and 1230 for seasons with 30 teams). 
    For playoff games, the 2nd digit of the specific number gives the round of the playoffs, the 3rd digit specifies the matchup, and the 4th digit specifies the game (out of 7).
    """
    
    
    # Construct the full download URL for the given year
    # https://api-web.nhle.com/v1/gamecenter/GAME_ID/play-by-play
    # We want to change the GAME_ID so that we can get all data for a given year
    
    # TODO


if __name__ == "__main__":
    app()
