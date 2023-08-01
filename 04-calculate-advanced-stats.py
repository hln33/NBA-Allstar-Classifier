import pandas as pd

# constants
IN_RAW_DIR = 'raw_data'
IN_CLEAN_DIR = 'cleaned_data'
OUT_DIR = 'raw_data'


def get_adv_team_stats(game_logs: pd.DataFrame, box_scores: pd.DataFrame) -> pd.DataFrame:
    adv_stats = pd.merge(box_scores, game_logs, on=['GAME_ID', 'TEAM_ID'])
    adv_stats = adv_stats[['TEAM_ID', 'SEASON', 'PACE', 'OREB_PCT']]
    adv_stats = adv_stats.groupby(by=['TEAM_ID', 'SEASON']).mean()
    return adv_stats


def get_adv_player_stats(game_logs: pd.DataFrame, box_scores: pd.DataFrame) -> pd.DataFrame:
    adv_stats = pd.merge(box_scores, game_logs, on=['GAME_ID', 'TEAM_ID'])
    adv_stats = adv_stats[['PLAYER_ID', 'SEASON', 'POSS', 'PACE']]
    adv_stats = adv_stats.groupby(by=['PLAYER_ID', 'SEASON']).sum()
    return adv_stats


def calc_league_stats(teams: pd.DataFrame) -> pd.DataFrame:
    agg_dict = {col: 'mean' if col == 'PACE' else 'sum' for col in teams.columns}
    lg = teams.groupby('SEASON').agg(agg_dict)
    lg = lg[['GP', 'FGM', 'FGA', 'FTM', 'FTA', 'PF', 'PTS', 'AST', 'OREB', 'REB', 'TOV', 'PACE']]

    # used to calculate PER
    lg['factor'] = (2 / 3) - (0.5 * (lg['AST'] / lg['FGM'])) / (2 * (lg['FGM'] / lg['FTM']))
    lg['VOP'] = lg['PTS'] / (lg['FGA'] - lg['OREB'] + lg['TOV'] + 0.44 * lg['FTA'])
    lg['DRB%'] = (lg['REB'] - lg['OREB']) / lg['REB']

    # used to calculate WS
    lg['PPP_LG'] = lg['PTS'] / (lg['FGA'] + (0.44 * lg['FTA']) + lg['TOV'])
    lg['PPG_LG'] = lg['PTS'] / lg['GP']
    return lg


# calculate PER (player efficiency rating)
# source: https://www.basketball-reference.com/about/per.html
def calc_per(player: pd.DataFrame, team: pd.DataFrame, league: pd.DataFrame) -> pd.DataFrame:
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    player = pd.merge(player, league, on='SEASON', suffixes=('', '_L'))
    # print(player)

    player = player[player['MIN'] > 0]
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
    player['aPER'] = (player['PACE_L'] / player['PACE_TM']) * player['uPER']

    league_aPER_avg = player.groupby(by=['SEASON']).agg({'aPER': 'mean'})
    player = pd.merge(player, league_aPER_avg, on=['SEASON'], suffixes=('', '_L'))
    player['PER'] = player['aPER'] * (15 / player['aPER_L'])

    player = player[['PLAYER_ID', 'SEASON', 'PER']]
    return player


# calculate metrics that are used to calculate other advanced stats
def calc_metrics(player: pd.DataFrame, team: pd.DataFrame) -> pd.DataFrame:
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))

    player['Team_Scoring_Poss'] = (
            player['FGM_TM'] + (1 - (1 - (player['FTM_TM'] / player['FTA_TM'])) ** 2) * player['FTA_TM'] * 0.4
    )
    player['Team_Play%'] = player['Team_Scoring_Poss'] / (player['FGA_TM'] + player['FTA_TM'] * 0.4 + player['TOV_TM'])
    player['Team_ORB_Weight'] = (
                                        (1 - player['OREB_PCT']) * player['Team_Play%']) / (
                                        (1 - player['OREB_PCT']) * player['Team_Play%'] + player['OREB_PCT'] * (
                                        1 - player['Team_Play%'])
                                )
    player['qAST'] = (
            ((player['MIN'] / (player['MIN_TM'] / 5)) *
             (1.14 * ((player['AST_TM'] - player['AST']) / player['FGM_TM']))) +
            ((((player['AST_TM'] / player['MIN_TM']) * player['MIN'] * 5 - player['AST']) /
              ((player['FGM_TM'] / player['MIN_TM']) * player['MIN'] * 5 - player['FGM'])) *
             (1 - (player['MIN'] / (player['MIN_TM'] / 5))))
    )

    player['FG_Part'] = (
            player['FGM'] * (1 - 0.5 * ((player['PTS'] - player['FTM']) / (2 * player['FGA'])) * player['qAST'])
    )
    player['AST_Part'] = (
            0.5 * (((player['PTS_TM'] - player['FTM_TM']) - (player['PTS'] - player['FTM'])) /
                   (2 * (player['FGA_TM'] - player['FGA']))) * player['AST']
    )
    player['FT_Part'] = (1 - (1 - (player['FTM'] / player['FTA'])) ** 2) * 0.4 * player['FTA']
    player['ORB_Part'] = player['OREB'] * player['Team_ORB_Weight'] * player['Team_Play%']

    return player


# Source:
# https://www.basketball-reference.com/about/ratings.html?__hstc=213859787.4cbbc20946b7a9135a926d6b4d34b58f.1690838112167.1690838112167.1690838112167.1&__hssc=213859787.1.1690838112168&__hsfp=2926660606
def calc_points_produced(player: pd.DataFrame, team: pd.DataFrame) -> pd.DataFrame:
    player = calc_metrics(player, team)

    player['PProd_FG_Part'] = (
            2 * (player['FGM'] + 0.5 * player['FG3M']) *
            (1 - 0.5 * ((player['PTS'] - player['FTM']) / (2 * player['FGA'])) * player['qAST'])
    )
    player['PProd_AST_Part'] = (
            2 * ((player['FGM_TM'] - player['FGM'] + 0.5 * (player['FG3M_TM'] - player['FG3M'])) /
                 (player['FGM_TM'] - player['FGM'])) * 0.5 *
            (((player['PTS_TM'] - player['FTM_TM']) - (player['PTS'] - player['FTM'])) /
             (2 * (player['FGA_TM'] - player['FGA']))) * player['AST']
    )
    player['PProd_ORB_Part'] = (
            player['OREB'] * player['Team_ORB_Weight'] * player['Team_Play%'] * (
            player['PTS_TM'] / (player['FGM_TM'] + (1 - (1 - (player['FTM_TM'] / player['FTA_TM'])) ** 2) *
                                0.4 * player['FTA_TM']))
    )
    player['PProd'] = (
            (player['PProd_FG_Part'] + player['PProd_AST_Part'] + player['FTM']) * (
            1 - (player['OREB_TM'] / player['Team_Scoring_Poss']) * player['Team_ORB_Weight'] *
            player['Team_Play%']) + player['PProd_ORB_Part']
    )

    player = player[['PLAYER_ID', 'SEASON', 'PProd']]
    return player


# source:
# https://www.basketball-reference.com/about/ratings.html?__hstc=213859787.73afc6f4f4ed6dbb1e6b3d078b2de816.1690920199732.1690920199732.1690920199732.1&__hssc=213859787.3.1690920199732&__hsfp=2926660606
def calc_total_possessions(player: pd.DataFrame, team: pd.DataFrame) -> pd.DataFrame:
    player = calc_metrics(player, team)

    player['ScPoss'] = (
            (player['FG_Part'] + player['AST_Part'] + player['FT_Part']) *
            (1 - (player['OREB_TM'] / player['Team_Scoring_Poss']) * player['Team_ORB_Weight']
             * player['Team_Play%']) + player['ORB_Part']
    )
    player['FGxPoss'] = (player['FGA'] - player['FGM']) * (1 - 1.07 * player['OREB_PCT'])
    player['FTxPoss'] = ((1 - (player['FTM'] / player['FTA'])) ** 2) * 0.4 * player['FTA']
    player['TotPoss'] = player['ScPoss'] + player['FGxPoss'] + player['FTxPoss'] + player['TOV']

    player = player[['PLAYER_ID', 'SEASON', 'TotPoss']]
    return player


# calculate WS (win shares)
# source: https://www.basketball-reference.com/about/ws.html
def calc_ws(player: pd.DataFrame, team: pd.DataFrame, league: pd.DataFrame) -> pd.DataFrame:
    player_PProd = calc_points_produced(player, team)
    player_TotPoss = calc_total_possessions(player, team)

    player = pd.merge(player, league, on=['SEASON'], suffixes=('', '_LG'))
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    player = pd.merge(player, player_PProd, on=['PLAYER_ID', 'SEASON'])
    player = pd.merge(player, player_TotPoss, on=['PLAYER_ID', 'SEASON'])

    player['Marginal_Offense'] = player['PProd'] - 0.92 * player['PPP_LG'] * player['TotPoss']
    player['Marginal_PPW'] = 0.32 * player['PPG_LG'] * (player['PACE_TM'] / player['PACE_LG'])
    player['WS'] = player['Marginal_Offense'] / player['Marginal_PPW']

    player = player.sort_values('WS', ascending=False)
    player = player[['PLAYER_ID', 'SEASON', 'WS']]
    # print(player)
    # print(player[player['PLAYER_NAME'] == 'LeBron James'])
    # player.to_csv('test/win_shares.csv')

    return player


def main():
    player_stats = pd.read_csv(f'{IN_RAW_DIR}/pre_allstar_player_stats.csv')
    team_stats = pd.read_csv(f'{IN_RAW_DIR}/pre_allstar_team_stats.csv')
    game_logs = pd.read_csv(f'{IN_CLEAN_DIR}/cleaned_game_logs.csv')

    team_box_scores = pd.read_csv(f'{IN_RAW_DIR}/advanced_team_box_scores.csv')
    adv_team_stats = get_adv_team_stats(game_logs, team_box_scores)

    adv_team_stats = pd.merge(adv_team_stats, team_stats, on=['TEAM_ID', 'SEASON'])
    league_stats = calc_league_stats(adv_team_stats)

    player_box_scores = pd.read_csv(f'{IN_RAW_DIR}/advanced_player_box_scores.csv')
    adv_player_stats = get_adv_player_stats(game_logs, player_box_scores)
    adv_player_stats = pd.merge(player_stats, adv_player_stats, on=['PLAYER_ID', 'SEASON'])

    player_PER = calc_per(adv_player_stats, adv_team_stats, league_stats)
    # print(player_PER)
    player_WS = calc_ws(adv_player_stats, adv_team_stats, league_stats)
    adv_player_stats = pd.merge(adv_player_stats, player_PER, on=['PLAYER_ID', 'SEASON'])
    adv_player_stats = pd.merge(adv_player_stats, player_WS, on=['PLAYER_ID', 'SEASON'])

    adv_player_stats = adv_player_stats.sort_values('WS', ascending=False)
    adv_player_stats = adv_player_stats[['PLAYER_NAME', 'PLAYER_ID', 'SEASON', 'PER', 'WS']]
    # print(adv_player_stats)

    adv_player_stats.to_csv(f'{OUT_DIR}/advanced_player_stats.csv')


if __name__ == '__main__':
    main()
