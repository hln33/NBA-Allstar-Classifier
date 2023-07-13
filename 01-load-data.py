import pandas as pd
import numpy as np
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# constants
OUT_DIR = 'data'
STAT_COLS = ['PLAYER_NAME', 'PLAYER_ID', 'SEASON_ID', 'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M',
             'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']


def get_players() -> pd.DataFrame:
    nba_players = players.get_players()
    nba_players = pd.DataFrame(nba_players)
    return nba_players[['id', 'full_name']]


def get_player_stats(player: pd.DataFrame) -> pd.DataFrame:
    stats = playercareerstats.PlayerCareerStats(player_id=player.id)
    stats = stats.get_data_frames()[0]
    stats['PLAYER_NAME'] = player['full_name']
    stats = stats.drop(columns=['LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION'])  # drop unneeded columns
    return stats


def main():
    player_data = get_players()
    player_data = player_data[:5]
    print(player_data)

    stats = pd.DataFrame(columns=STAT_COLS)
    for _, player in player_data.iterrows():
        player_stats = get_player_stats(player)
        stats = pd.concat([stats, player_stats], ignore_index=True)
    print(stats)

    stats.to_csv(f'{OUT_DIR}/stats.csv')


if __name__ == '__main__':
    main()
