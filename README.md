## Required Libraries
- nba_api (https://github.com/swar/nba_api)
- Pandas
- NumPy
- BeautifulSoup
- Unidecode
- Matplotlib
- Seaborn
- Scikit-learn

## Order of Execution
- 01-get-data.py
- 02-clean-game-logs.py
- 03-get-advanced-box-scores.py
- 04-calculate-advanced-box-scores.py
- 05-extract-relevant-stats.py
- 06-get-allstar-labels.py
- 07-create-training-data.ipynb
- 08-model-predict-ipynb

**Note:** <br>
we recommend using the data provided in the repo and avoiding running steps 01 and 03 in their entirety as they can take hours to run  

## Commands
- Simply run each file without any command-line arguments (arguments are hard-coded)

## Inputs
- **01-get-data.py**
  - None


- **02-clean-game-logs.py**
  - raw_data/game_logs.csv


- **03-get-advanced-box-scores.py**
  - cleaned_data/cleaned_game_logs.csv


- **04-calculate-advanced-box-scores.py**
  - raw_data/
    - pre_allstar_player_stats.csv
    - pre_allstar_team_stats.csv
    - raw_data/pre_allstar_player_stats.csv
    - advanced_team_box_scores.csv
  - cleaned_data/
    - cleaned_game_logs.csv.csv


- **05-extract-relevant-stats.py**
  - raw_data/
    - pre_allstar_player_stats.csv
    - advanced_player_box_scores.csv
    - advanced_player_stats.csv
  - cleaned_data/
    - cleaned_game_logs.csv


- **06-get-allstar-labels.py**
  - None


- **07-create-training-data.ipynb**
  - final_data/
    - allstars.csv
    - final_player_stats.csv


- **08-model-predict-ipynb**
  - final_data/
    - final_data.csv
    - 2023_season.csv


## Files Produced
- **01-get-data.py**
  - raw_data/
    - pre_allstar_player_stats.csv
    - pre_allstar_team_stats.csv
    - game_logs.csv


- **02-clean-game-logs.py**
  - cleaned_data/cleaned_game_logs.csv

  
- **03-get-advanced-box-scores.py**
  - raw_data/
    - advanced_team_box_scores.csv
    - advanced_player_box_scores.csv


- **04-calculate-advanced-box-scores.py**
  - raw_data/advanced_player_stats


- **05-extract-relevant-stats.py**
  - final_data/final_player_stats.csv


- **06-get-allstar-labels.py**
  - final_data/allstars.csv


- **07-create-training-data.ipynb**
  - final_data/final_data.csv


- **08-model-predict-ipynb**
  - None
