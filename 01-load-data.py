import pandas as pd
import numpy as np
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# constants
OUT_DIR = 'data'


def main():
    nba_players = players.get_players()
    df = pd.DataFrame(nba_players)
    # print(df)

    kareem = playercareerstats.PlayerCareerStats(player_id='76003')
    kareem = kareem.get_data_frames()[0]

    kareem.to_csv(f'{OUT_DIR}/kareem.csv')


if __name__ == '__main__':
    main()
