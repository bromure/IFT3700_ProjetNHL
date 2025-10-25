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
    # ---- Base dowloader ----
    load_data()
    # -----------------------------------------
    
    '''
    Setup heuristic:
        1. Run script when opening project
        2. Check if data folder exists
            a. If not, create it and download data from API
            b. If it does, check if it is empty
                i. If empty, ask user if they want to provide a new path or download from API
                ii. If not empty, check if all games are present
                    - If not all games are present, ask user if they want to download missing years/games from API
                    - If all games are present, do nothing
            
    ├── main
    │   └── load_data                   <- Wrapper to load data for multiple years
    |      └── get_yearly_data          <- NHL data retrieval for a given year
    |            └── get_data           <- Checks for local data, else calls get_web_data
    |                 └── get_web_data  <- Gets data from API
 
    '''

# -----------------------------------------------------------------------



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

    # Send a GET request to the download URL 
    response = requests.get(download_url, stream=True)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e: # If the request fails (e.g., 404 Not Found), log the error and return None
        logger.warning(f"Failed to download from {download_url} - HTTP {response.status_code}: {e}")
        return None
    else:
        # Ensure the save directory exists (even if nested)
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = save_path / file_name

        # Write the content to a file in (8KB) chunks to avoid large RAM usage
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded and saved file to {file_path}")

    return file_path
    
    
def get_data(input_path: str, gameID: str, download_url: str, missing_games: list[str]) -> Path:
    """
    Wrapper to get data from web API. Calls get_web_data.
    
    Args:
        input_path (str): User-specified path to the folder of the wanted files (datasets).
        gameID (str): Game ID of the NHL game to download.
        download_url (str): Start of API URL to get web data if not found locally.
        missing_games (str): List to append missing game's gameIDs to.

    Returns:
        Path: Path to the dataset file.
    """
    # Construct file name and path
    file_name = f"play_by_play_{gameID}_data.json"
    file_path = Path(input_path) / file_name
    
    # Check if file already exists locally
    if file_path.exists():
        logger.info(f"File {file_name} already exists locally. Skipping download.")
    else:
        # File not found locally, attempt to download from API
        full_url = f"{download_url}gamecenter/{gameID}/play-by-play"
        path = get_web_data(file_name, full_url, input_path)
        if path is None: # If download failed, append to missing games
            logger.error(f"Game data for gameID {gameID} failed to download from {download_url}.")
            missing_games.append(gameID)
    
    return file_path


def get_n_game(year: int) -> int:
    """
    Function to get the total number of games in a single year

    Args:
        year(int) : First year of the NHL season (e.g., 2023 for the 2023-2024 season).
    
    Returns:
        int : Number of games that year
    """

        # Amount of games per season  
    match year:
        case y if y >= 2022: # 32 team seasons
            return 32*82 / 2 # 1312 games
            
        case 2020: # Covid shortened season
            return 31*56 / 2 # 868 games
        
        case 2019: # Covid-cut season
            return 1082  
            
        case y if y >= 2017: # 31 team seasons
            return 31*82 / 2 # 1271 games
        
        case y if y >= 2000: # 30 team seasons
            return 30*82 / 2 # 1230 games
        case _:
            logger.error("Year must be 2000 or later.")
            raise ValueError()

def get_yearly_data(year: int, download_url: str, missing_games: list[str], input_path: str = RAW_DATA_DIR, game_types: list[str] = ["02", "03"] ) -> Path:
    """
    Wrapper to get data for a specific year. Sets the API URL and file name.
    
    Args:
        year (int): First year of the NHL season (e.g., 2023 for the 2023-2024 season).
        download_url (str): Start of API URL to get web data if not found locally.
        missing_games (str): List to append missing game's gameIDs to.
        input_path (str, optional): User-specified path to the folder of the wanted files (datasets). Defaults to RAW_DATA_DIR.
        game_types (list[str], optional): List of game types to download. Defaults to ["02", "03"] (regular season and playoffs).


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
    
    
    # Amount of games per season 
    games = get_n_game(year)
    games = range(1, int(games)+1) # Game numbers start at 0001
    
    # Create/ensure year folder exists (for organization)
    input_path = Path(input_path)/f"{year}"
    input_path.mkdir(parents=True, exist_ok=True)
    
    # Loop through all game types and numbers to construct game IDs
    for game_type in game_types:
        gameID_pre = f"{year}{game_type}" # Prefix of game ID (missing last 4 digits)
        
        # Construct game ID based on gametype format
        match game_type:
            case t if t=="01"or t=="02": # Preseason or regular season
                for game_num in tqdm(games, desc=f"Year {year} - Game Type {game_type}"):
                    gameID = f"{gameID_pre}{game_num:04d}"
                    get_data(input_path, gameID, download_url, missing_games)
                    
            case "03": # Playoffs
                # Last 4 gameID digits: 1- "0", 2- rounds(i=1 to 4), 3- matchups(2^(4-i)=8,4,2,1), 4- games(up to 7)
                for round_num in tqdm(range(1, 5), desc=f"Year {year} - Game Type {game_type}"): # 4 rounds
                    matchups = 2**(4-round_num) # 8,4,2,1 matchups per round
                    for matchup in range(1, matchups+1):
                        for game in range(1, 5): # up to 7 games per matchup
                            gameID = f"{gameID_pre}0{round_num}{matchup}{game}"
                            
                            if game <= 4: # Games 1,2,3,4 always
                                get_data(input_path, gameID, download_url, missing_games)  
                            else: 
                                # Games 5,6,7 only if necessary (break if not found, and don't add to missing_games)         
                                file_name = f"play_by_play_{gameID}_data.json"
                                if not (input_path / file_name).exists():
                                    path = get_web_data(file_name, f"{download_url}gamecenter/{gameID}/play-by-play", input_path)
                                    if path is None: # If download failed, append to missing games
                                        break
                                
                                 

                            
            case "04": # All-star
                # TODO
                continue
            
            case _:
                logger.error(f"Game type {game_type} not recognized. Skipping.")


def load_data(input_path: str = RAW_DATA_DIR, download_url: str = "https://api-web.nhle.com/v1/", years: list[int] = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]) -> list[str]:
    """
    Wrapper to load data for multiple years.
    
    Args:
        input_path (str, optional): User-specified path to look for the dataset.
        download_url (str): Start of API URL to get web data if not found locally.
        years (list[int]): List of years to load data for.
        
    Returns:
        missing_games (list[str]): List of missing game dataset's gameIDs.
    """
            
    # Create default dataset directory
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if input_path:
        data_path = Path(input_path)
    else:
        data_path = RAW_DATA_DIR

    # Ensure folder exists
    data_path.mkdir(parents=True, exist_ok=True)
    
    # Folder exists but is empty
    if len(os.listdir(data_path)) == 0 and input_path != RAW_DATA_DIR:
        ans = input(f"Directory at {data_path} not found is empty. Try again with a different path? [y/n] ")
        if ans.lower() == "y":
            new_path = input("Enter new path: ")
            return load_data(input_path=new_path) # Retry with new path
        else:
            # Default to downloading from API ('y' will be assumed)
            ans = input(f"Download data from web API? [y/n] ")
            if ans.lower() == "n":
                logger.error("No data found locally and download declined. Exiting.")
                raise FileNotFoundError()
            else:
                input_path = RAW_DATA_DIR
        
    missing_games = [] # List of missing game dataset's gameIDs
    
    # ---- Base dowloader ----
    logger.info("Starting data retrieval...")
    for year in years:
        get_yearly_data(year, download_url, missing_games, input_path)
        
    # If there are missing games, ask user if they want to retry downloading them
    amt_games_missing = len(missing_games)
    if amt_games_missing > 0:
        ans = input(f"Found {amt_games_missing} missing games. Do you want to retry downloading from API? [y/n] ")
        if ans.lower() == "y":
            # Retry downloading only missing games
            for game_id in tqdm(missing_games, desc="Retrying downloads"):
                get_web_data(f"play_by_play_{game_id}_data.json", f"{download_url}gamecenter/{game_id}/play-by-play", input_path)
                
            logger.info("Retry complete. Check logs for any failed downloads.")
    else:
        logger.success(f"All data for years {years} is present in {input_path}.")
    
    return missing_games
        

if __name__ == "__main__":
    app()
    # python Visualisation/dataset.py
