import pandas as pd
import sys

# constants
IN_DIR = 'raw_data'
OUT_DIR = 'final_data'


def filter_box_scores(box_scores: pd.DataFrame) -> pd.DataFrame:
    box_scores = box_scores[[
        'SEASON',
        'TEAM_ID',
        'PLAYER_ID',
        'TS_PCT',
        'USG_PCT',
        'PIE'
    ]]
    return box_scores


def filter_combined_data(combined: pd.DataFrame) -> pd.DataFrame:
    combined = combined[[
        'SEASON',
        'PLAYER_ID',
        'PLAYER_NAME',
        'TEAM_ID',
        'TEAM_ABBREVIATION',
        'GP',
        'MIN',
        'PTS',
        'REB',
        'AST',
        'STL',
        'BLK',
        'TOV',
        'FG3M',
        'TS_PCT',
        'USG_PCT',
        'PIE',
        'PER',
        'WS'
    ]]
    return combined


def aggregate_player_box_scores(box_scores: pd.DataFrame) -> pd.DataFrame:
    box_scores = box_scores.groupby(by=['SEASON', 'TEAM_ID', 'PLAYER_ID']).agg('mean')
    return box_scores


def add_season_to_box_scores(box_scores: pd.DataFrame, game_logs: pd.DataFrame) -> pd.DataFrame:
    box_scores = pd.merge(box_scores, game_logs, on=['GAME_ID', 'TEAM_ID'])
    return box_scores


def combine(player_stats: pd.DataFrame, box_scores: pd.DataFrame, adv_stats: pd.DataFrame) -> pd.DataFrame:
    # source: https://stackoverflow.com/questions/19125091/pandas-merge-how-to-avoid-duplicating-columns
    def merge_and_drop_dupe_cols(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        df1 = pd.merge(df1, df2, on=['SEASON', 'PLAYER_ID'], suffixes=('', '_y'))
        df1 = df1.drop(df1.filter(regex='_y$').columns, axis=1)
        return df1

    combined = merge_and_drop_dupe_cols(player_stats, box_scores)
    combined = merge_and_drop_dupe_cols(combined, adv_stats)
    return combined


def main():
    player_stats = pd.read_csv(f'{IN_DIR}/pre_allstar_player_stats.csv')
    adv_player_box_scores = pd.read_csv(f'{IN_DIR}/advanced_player_box_scores.csv')
    adv_player_stats = pd.read_csv(f'{IN_DIR}/advanced_player_stats.csv')
    game_logs = pd.read_csv('cleaned_data/cleaned_game_logs.csv')

    adv_player_box_scores = add_season_to_box_scores(adv_player_box_scores, game_logs)
    adv_player_box_scores = filter_box_scores(adv_player_box_scores)
    adv_player_box_scores = aggregate_player_box_scores(adv_player_box_scores)

    combined = combine(player_stats, adv_player_box_scores, adv_player_stats)
    combined = filter_combined_data(combined)
    combined.to_csv(f'{OUT_DIR}/final_player_stats.csv')


if __name__ == '__main__':
    main()
