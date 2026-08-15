import os
import io
import sys
import zipfile
import requests
import polars as pl
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.utils.logger import initialize_logger
from src.utils.identifier import parse_identifier

load_dotenv()
logging = initialize_logger(log_destination='ingest.log', logger_name='ingest')

START_YEAR = 2010
END_YEAR = 2021
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

IMPORT_COLUMNS = [
  *list(range(0, 21)),
  22,
  45,
  50,
  73,
  159,
  160
]

IMPORT_COLUMNS_HEADERS = [
  'date',
  'game_in_day',
  'day_of_week',
  'away_team',
  'away_league',
  'away_team_game_number',
  'home_team',
  'home_league',
  'home_team_game_number',
  'away_score',
  'home_score',
  'number_of_outs',
  'day_night',
  'completion_data',
  'forfeit',
  'protest',
  'park',
  'attendance',
  'minutes',
  'away_box',
  'home_box',
  'away_hits',
  'away_errors',
  'home_hits',
  'home_errors',
  'addl',
  'acq'
]

# Data updated infrequently, only needs ingestion annually
def import_historical_baseball():
  import_year = START_YEAR
  while import_year < END_YEAR and import_year < datetime.now().year:
    logging.info(f"Retrieving historical baseball data for year={import_year}")
    exists_method = "replace" if import_year == START_YEAR else "append"
    try:
      url = f"https://www.retrosheet.org/gamelogs/gl{import_year}.zip"
      response = requests.get(url)
      response.raise_for_status()

      with zipfile.ZipFile(io.BytesIO(response.content)) as unzipped:
        for filename in unzipped.namelist():
          logging.info(f"Zip retrieval successful for {filename}")

          with unzipped.open(filename) as gamelogs:
            gl = pl.read_csv(
              gamelogs,
              has_header=False,
              columns=IMPORT_COLUMNS,
              new_columns=IMPORT_COLUMNS_HEADERS,
              schema_overrides={
                'away_box': pl.Utf8,
                'home_box': pl.Utf8
              })

            gl = gl.with_columns(
              pl.struct(["away_box", "home_box", "away_score", "home_score", "away_hits", "home_hits", "away_errors", "home_errors"])
              .map_elements(
                parse_identifier,
                return_dtype=pl.Struct({
                  "9_shape": pl.Int32,
                  "home_no_bat": pl.Boolean,
                  "9_score": pl.Utf8,
                  "ex_shape": pl.Utf8,
                  "ex_score": pl.Utf8,
                  "rhe": pl.Utf8,
                  "less_than_nine": pl.Boolean
                }))
              .alias("parsed")
            ).unnest("parsed")

            df = gl.to_pandas()
            df.to_sql("raw_linescores", engine, index=False, if_exists=exists_method, method="multi")
    except Exception as e:
      logging.error(f"Error in historical baseball data transfer for year={import_year}: {e}")
    finally:
      import_year += 1
      print(f"Completed ingestion for {import_year}")

if __name__ == "__main__":
  import_historical_baseball()
