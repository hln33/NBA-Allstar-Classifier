import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats, leaguegamelog
from nba_api.stats.library.parameters import SeasonSegmentNullable

# constants
OUT_DIR = 'raw_data'
START_YEAR = 1996
END_YEAR = 2022


def get_seasons(start_year, end_year):
    seasons = []
    for year in range(start_year, end_year + 1):
        season_str = str(year) + '-' + str((year + 1) % 100).zfill(2)
        seasons.append(season_str)
    return seasons


def make_api_call(api_call, season_str, has_season_segment=True) -> pd.DataFrame:
    # some api calls do not use a season_segment parameter
    if has_season_segment:
        data = api_call(season=season_str, season_segment_nullable=SeasonSegmentNullable.pre_all_star)
    else:
        data = api_call(season=season_str)
    return data.get_data_frames()[0]


def get_data(api_call, season_strs, has_season_segment=True) -> pd.DataFrame:
    df = pd.DataFrame()
    for season_str in season_strs:
        print(season_str)
        data = make_api_call(api_call, season_str, has_season_segment)
        data['SEASON'] = season_str
        df = pd.concat([df, data], ignore_index=True)
    return df


# this only can only get seasons after 1996 (seems like there is a year cutoff with this api call)
def main():
    seasons_strs = get_seasons(START_YEAR, END_YEAR)
    pre_allstar_player_data = get_data(leaguedashplayerstats.LeagueDashPlayerStats, seasons_strs)
    pre_allstar_team_data = get_data(leaguedashteamstats.LeagueDashTeamStats, seasons_strs)
    game_logs = get_data(leaguegamelog.LeagueGameLog, seasons_strs, has_season_segment=False)

    pre_allstar_player_data.to_csv(f'{OUT_DIR}/pre_allstar_player_stats.csv')
    pre_allstar_team_data.to_csv(f'{OUT_DIR}/pre_allstar_team_stats.csv')
    game_logs.to_csv(f'{OUT_DIR}/game_logs.csv')


if __name__ == '__main__':
    main()
