import pandas as pd
import sys
from nba_api.stats.endpoints import boxscoreadvancedv2

# constants
IN_DIR = 'raw_data'
OUT_DIR = 'cleaned_data'

PLAYER_INFO = ['PLAYER_ID', 'PLAYER_NAME']
TEAM_STATS = ['TEAM_ABBREVIATION', 'W']
BASIC_PLAYER_STATS = ['GP', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PLUS_MINUS']


# get game logs and team pace so that they may be used in the calculation of advanced stats
def main():
    res = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id='0029600012').get_data_frames()[1]
    res.to_csv('test/adv_boxscore.csv')
    print(res)


if __name__ == '__main__':
    main()
