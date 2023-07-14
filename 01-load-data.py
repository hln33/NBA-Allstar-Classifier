import pandas as pd
import numpy as np
import multiprocessing as mp
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# constants
OUT_DIR = 'data'
COLS = ['PLAYER_NAME', 'PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP',
        'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB',
        'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
CUTOFF = 100  # cutoff for number of players to load
NUM_PLAYERS = 100  # 4815


def get_players() -> pd.DataFrame:
    nba_players = players.get_players()
    return pd.DataFrame(nba_players)


def make_api_call(player: pd.Series) -> pd.DataFrame:
    stats = playercareerstats.PlayerCareerStats(player_id=player['id'], timeout=120)
    stats = stats.get_data_frames()[0]
    stats['PLAYER_NAME'] = player['full_name']
    return stats


def process_stat_batch(player_data: pd.DataFrame, shared_queue):
    players_loaded = 0
    stats = pd.DataFrame(columns=COLS)

    for _, player in player_data.iterrows():
        player_stats = make_api_call(player)
        stats = pd.concat([stats, player_stats], ignore_index=True)
        players_loaded += 1
        print(players_loaded)

    shared_queue.put(stats)


def main():
    player_data = get_players()
    print(len(player_data))

    p1 = mp.Process(target=process_stat_batch, args=(player_data[NUM_PLAYERS/2:], q))
    p2 = mp.Process(target=process_stat_batch, args=(player_data[:NUM_PLAYERS/2], q))
    p1.start()
    p2.start()

    print(q.get())
    print(q.get())

    p1.join()
    p2.join()

    # stats.to_csv(f'{OUT_DIR}/stats.csv')


if __name__ == '__main__':
    q = mp.Queue()
    main()
