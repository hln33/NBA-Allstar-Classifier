import pandas as pd
import multiprocessing as mp
import time
import requests.exceptions
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# constants
OUT_DIR = 'data'
COLS = ['PLAYER_NAME', 'PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP',
        'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB',
        'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
NUM_PLAYERS = 4815


def get_players() -> pd.DataFrame:
    nba_players = players.get_players()
    return pd.DataFrame(nba_players)


def make_api_call(player: pd.Series) -> pd.DataFrame:
    try:
        stats = playercareerstats.PlayerCareerStats(player_id=player['id'], timeout=30)
    except requests.exceptions.ReadTimeout:
        # wait for api to be responsive again and retry
        time.sleep(150)
        stats = playercareerstats.PlayerCareerStats(player_id=player['id'], timeout=30)

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

    # use multiple processes to speed up data gathering
    q = mp.Queue()
    p1 = mp.Process(target=process_stat_batch, args=(player_data[NUM_PLAYERS//2:], q))
    p2 = mp.Process(target=process_stat_batch, args=(player_data[:NUM_PLAYERS//2], q))
    p1.start()
    p2.start()

    batch1 = q.get()
    batch2 = q.get()
    stats = pd.concat([batch1, batch2], ignore_index=True)
    stats.to_csv(f'{OUT_DIR}/regular_seasons.csv')

    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
