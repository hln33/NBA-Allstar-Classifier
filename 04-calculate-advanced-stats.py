import pandas as pd

# constants
IN_RAW_DIR = 'raw_data'
IN_CLEAN_DIR = 'cleaned_data'
OUT_DIR = 'final_data'


def calc_league_stats(teams: pd.DataFrame) -> pd.DataFrame:
    agg_dict = {col: 'sum' if col != 'PACE' else 'mean' for col in teams.columns}
    lg = teams.groupby('SEASON').agg(agg_dict)
    lg = lg[['FGM', 'FGA', 'FTM', 'FTA', 'PF', 'PTS', 'AST', 'OREB', 'REB', 'TOV', 'PACE']]

    # used to calculate PER
    lg['factor'] = (2 / 3) - (0.5 * (lg['AST'] / lg['FGM'])) / (2 * (lg['FGM'] / lg['FTM']))
    lg['VOP'] = lg['PTS'] / (lg['FGA'] - lg['OREB'] + lg['TOV'] + 0.44 * lg['FTA'])
    lg['DRB%'] = (lg['REB'] - lg['OREB']) / lg['REB']
    return lg


def get_team_pace(team_stats: pd.DataFrame, game_logs: pd.DataFrame, box_scores: pd.DataFrame) -> pd.DataFrame:
    box_scores = pd.merge(box_scores, game_logs, on=['GAME_ID', 'TEAM_ID'])
    box_scores = pd.merge(box_scores, team_stats, on=['TEAM_ID', 'SEASON'])

    team_pace = box_scores[['TEAM_ID', 'SEASON', 'PACE']]
    team_pace = team_pace.groupby(by=['TEAM_ID', 'SEASON']).mean()
    return team_pace


# calculate PER (player efficiency rating)
# source: https://www.basketball-reference.com/about/per.html
def calc_per(player: pd.DataFrame, team: pd.DataFrame, league: pd.DataFrame):
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    player = pd.merge(player, league, on='SEASON', suffixes=('', '_L'))
    print(player)

    player['uPER'] = (1 / player['MIN']) * (
            player['FG3M']
            + (2 / 3) * player['AST']
            + (2 - player['factor'] * (player['AST_TM'] / player['FGM_TM'])) * player['FGM']
            + (player['FTM'] * 0.5 *
               (1 + (1 - (player['AST_TM'] / player['FGM_TM'])) + (2 / 3) * (player['AST_TM'] / player['FGM_TM']))
               )
            - player['VOP'] * player['TOV']
            - player['VOP'] * player['DRB%'] * (player['FGA'] - player['FGM'])
            - player['VOP'] * 0.44 * (0.44 + (0.56 * player['DRB%'])) * (player['FTA'] - player['FTM'])
            + player['VOP'] * (1 - player['DRB%']) * (player['REB'] - player['OREB'])
            + player['VOP'] * player['DRB%'] * player['OREB']
            + player['VOP'] * player['STL']
            + player['VOP'] * player['DRB%'] * player['BLK']
            - player['PF'] * (
                        (player['FTM_L'] / player['PF_L']) - 0.44 * (player['FTA_L'] / player['PF_L']) * player['VOP'])
    )

    player['aPER'] = (player['PACE_L'] / player['PACE']) * player['uPER']
    league_aPER_avg = player.groupby(by=['SEASON']).agg({'aPER': 'mean'})
    player = pd.merge(player, league_aPER_avg, on=['SEASON'], suffixes=('', '_L'))
    player['PER'] = player['aPER'] * (15 / player['aPER_L'])

    player = player.sort_values('PER', ascending=False)
    player = player[['PLAYER_NAME', 'SEASON', 'PER']]
    player.to_csv('test/player_stats_per.csv', index=False)


def main():
    player_stats = pd.read_csv(f'{IN_RAW_DIR}/pre_allstar_player_stats.csv')
    team_stats = pd.read_csv(f'{IN_RAW_DIR}/pre_allstar_team_stats.csv')
    game_logs = pd.read_csv(f'{IN_CLEAN_DIR}/cleaned_game_logs.csv')
    box_scores = pd.read_csv(f'{IN_RAW_DIR}/advanced_box_scores.csv')
    # print(player_stats)
    # print(team_stats)
    # print(box_scores)

    team_pace = get_team_pace(team_stats, game_logs, box_scores)
    team_stats = pd.merge(team_stats, team_pace, on=['TEAM_ID', 'SEASON'])
    # team_stats.to_csv('test/team_pace_stats.csv', index=False)
    league_stats = calc_league_stats(team_stats)
    # print(league_stats)
    # print(league_stats['PACE'])

    calc_per(player_stats, team_stats, league_stats)

    # player_team = pd.merge(player_stats, team_stats, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    # player_team.to_csv('test/player_team.csv')
    # print(player_team)


if __name__ == '__main__':
    main()
