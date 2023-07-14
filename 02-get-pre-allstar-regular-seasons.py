import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.library.parameters import SeasonSegmentNullable

# constants
IN_DIR = 'data'
OUT_DIR = 'data'
START_YEAR = 1951
END_YEAR = 2022


def get_seasons(start_year, end_year):
    seasons = []
    for year in range(start_year, end_year + 1):
        season_str = str(year) + '-' + str((year + 1) % 100).zfill(2)
        seasons.append(season_str)
    return seasons


def make_api_call(season_str) -> pd.DataFrame:
    game_logs = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season_str,
        season_segment_nullable=SeasonSegmentNullable.pre_all_star
    )
    return game_logs.get_data_frames()[0]


def get_pre_allstar_seasons(season_strs) -> pd.DataFrame:
    df = pd.DataFrame()
    for season_str in season_strs:
        print(season_str)
        game_logs = make_api_call(season_str)
        game_logs['SEASON'] = season_str
        df = pd.concat([df, game_logs], ignore_index=True)
    return df


def main():
    seasons_since_first_allstar = get_seasons(START_YEAR, END_YEAR)
    pre_allstar_seasons = get_pre_allstar_seasons(seasons_since_first_allstar)
    pre_allstar_seasons.to_csv(f'{OUT_DIR}/pre_allstar_regular_seasons')


if __name__ == '__main__':
    main()
