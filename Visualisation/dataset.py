from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from Visualisation.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    # ----------------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")
    for i in tqdm(range(10), total=10):
        if i == 5:
            logger.info("Something happened for iteration 5.")
    logger.success("Processing dataset complete.")
    # -----------------------------------------
    '''
    Setup heuristic:
        1. Run script when opening project
        2. Asks for (input_path)
            i) if path is given, uses that path to load data locally
            ii) if no path is given, defaults to downloading the data from API
    '''


if __name__ == "__main__":
    app()
