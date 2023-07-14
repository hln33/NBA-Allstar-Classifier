import pandas as pd
import numpy as np
import multiprocessing
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# constants
OUT_DIR = 'data'
COLS = ['PLAYER_NAME', 'PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP',
        'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB',
        'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
CUTOFF = 100  # cutoff for number of players to load


def get_players() -> pd.DataFrame:
    nba_players = players.get_players()
    nba_players = pd.DataFrame(nba_players)
    return nba_players[['id', 'full_name']]


def get_player_stats(player: pd.Series) -> pd.DataFrame:
    stats = playercareerstats.PlayerCareerStats(player_id=player['id'])
    stats = stats.get_data_frames()[0]
    stats['PLAYER_NAME'] = player['full_name']
    return stats


def get_stats_process(player_data: pd.DataFrame) -> pd.DataFrame:
    players_loaded = 0
    stats = pd.DataFrame(columns=COLS)

    for _, player in player_data.iterrows():
        player_stats = get_player_stats(player)
        stats = pd.concat([stats, player_stats], ignore_index=True)
        players_loaded += 1
        print(players_loaded)

    return stats

def main():
    player_data = get_players()

    # this will take some time...
    players_loaded = 0
    stats = pd.DataFrame(columns=COLS)
    for _, player in player_data.iterrows():
        player_stats = get_player_stats(player)
        stats = pd.concat([stats, player_stats], ignore_index=True)

        players_loaded += 1
        print(players_loaded)
        # if players_loaded >= CUTOFF:
        #     break
    stats.to_csv(f'{OUT_DIR}/stats.csv')


if __name__ == '__main__':
    main()
