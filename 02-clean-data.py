import pandas as pd
import sys

# constants
IN_DIR = 'data'
OUT_DIR = 'cleaned_data'

PLAYER_INFO = ['PLAYER_ID', 'PLAYER_NAME']
TEAM_STATS = ['TEAM_ABBREVIATION', 'W']
BASIC_PLAYER_STATS = ['GP', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PLUS_MINUS']


def main():
    seasons = pd.read_csv(f'{IN_DIR}/{sys.argv[1]}')

    # extract relevant features
    cleaned_seasons = seasons[PLAYER_INFO + TEAM_STATS + BASIC_PLAYER_STATS]

    cleaned_seasons.to_csv(f'{OUT_DIR}/cleaned_pre_allstar_seasons.csv')


if __name__ == '__main__':
    main()
