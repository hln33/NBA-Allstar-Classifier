import pandas as pd

# constants
IN_RAW_DIR = 'raw_data'
IN_CLEAN_DIR = 'cleaned_data'
OUT_DIR = 'raw_data'


def calc_league_stats(teams: pd.DataFrame) -> pd.DataFrame:
    agg_dict = {col: 'mean' if col == 'PACE' else 'sum' for col in teams.columns}
    lg = teams.groupby('SEASON').agg(agg_dict)
    lg = lg[['FGM', 'FGA', 'FTM', 'FTA', 'PF', 'PTS', 'AST', 'OREB', 'REB', 'TOV', 'PACE']]

    # used to calculate PER
    lg['factor'] = (2 / 3) - (0.5 * (lg['AST'] / lg['FGM'])) / (2 * (lg['FGM'] / lg['FTM']))
    lg['VOP'] = lg['PTS'] / (lg['FGA'] - lg['OREB'] + lg['TOV'] + 0.44 * lg['FTA'])
    lg['DRB%'] = (lg['REB'] - lg['OREB']) / lg['REB']
    return lg


def get_adv_team_stats(team_stats: pd.DataFrame, game_logs: pd.DataFrame, box_scores: pd.DataFrame) -> pd.DataFrame:
    box_scores = pd.merge(box_scores, game_logs, on=['GAME_ID', 'TEAM_ID'])
    box_scores = pd.merge(box_scores, team_stats, on=['TEAM_ID', 'SEASON'])

    team_pace = box_scores[['TEAM_ID', 'SEASON', 'PACE', 'OREB_PCT']]
    team_pace = team_pace.groupby(by=['TEAM_ID', 'SEASON']).mean()
    return team_pace


# calculate PER (player efficiency rating)
# source: https://www.basketball-reference.com/about/per.html
def calc_per(player: pd.DataFrame, team: pd.DataFrame, league: pd.DataFrame) -> pd.DataFrame:
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    player = pd.merge(player, league, on='SEASON', suffixes=('', '_L'))

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

    player = player[['PLAYER_ID', 'SEASON', 'PER']]
    return player


# Source:
# https://www.basketball-reference.com/about/ratings.html?__hstc=213859787.4cbbc20946b7a9135a926d6b4d34b58f.1690838112167.1690838112167.1690838112167.1&__hssc=213859787.1.1690838112168&__hsfp=2926660606
def calc_points_produced(player: pd.DataFrame, team: pd.DataFrame) -> pd.DataFrame:
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))

    player['Team_Scoring_Poss'] = (
            player['FGM_TM'] + (1 - (1 - (player['FTM_TM'] / player['FTA_TM']))**2) * player['FTA_TM'] * 0.4
    )
    player['Team_Play%'] = player['Team_Scoring_Poss'] / (player['FGA_TM'] + player['FTA_TM'] * 0.4 + player['TOV_TM'])
    player['Team_ORB_Weight'] = (
            ((1 - player['OREB_PCT']) * player['Team_Play%']) /
            ((1 - player['OREB_PCT']) * player['Team_Play%'] * (1 - player['Team_Play%']))
    )
    player['qAST'] = (
            ((player['MIN'] / (player['MIN_TM'] / 5)) * (1.14 * ((player['AST_TM'] - player['AST']) / player['FGM_TM'])))
            + ((((player['AST_TM'] / player['MIN_TM']) * player['MIN'] * 5 - player['AST']) /
                ((player['FGM_TM'] / player['MIN_TM']) * player['MIN'] * 5 - player['FGM']))
               * (1 - (player['MIN'] / (player['MIN_TM'] / 5))))
    )

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
            player['OREB'] * player['Team_ORB_Weight'] * player['Team_Play%'] *
            (player['PTS_TM'] / (player['FGM_TM'] + (1 - (1 - (player['FTM_TM'] / player['FTA_TM']))**2)
            * 0.4 * player['FTA_TM']))
    )
    player['PProd'] = (
            (player['PProd_FG_Part'] + player['PProd_AST_Part'] + player['FTM']) *
            (1 - (player['OREB_TM'] / player['Team_Scoring_Poss']) * player['Team_ORB_Weight'] * player['Team_Play%']) +
            player['PProd_ORB_Part']
    )

    player = player[['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'PProd']]
    player = player.sort_values(by=['PProd'], ascending=False)
    player.to_csv('test/pprod_players.csv')
    print(player)
    # return player


def main():
    player_stats = pd.read_csv(f'{IN_RAW_DIR}/pre_allstar_player_stats.csv')
    team_stats = pd.read_csv(f'{IN_RAW_DIR}/pre_allstar_team_stats.csv')
    game_logs = pd.read_csv(f'{IN_CLEAN_DIR}/cleaned_game_logs.csv')
    box_scores = pd.read_csv(f'{IN_RAW_DIR}/advanced_team_box_scores.csv')

    adv_team_stats = get_adv_team_stats(team_stats, game_logs, box_scores)
    # print(adv_team_stats)
    team_stats = pd.merge(team_stats, adv_team_stats, on=['TEAM_ID', 'SEASON'])
    league_stats = calc_league_stats(team_stats)

    player_PER = calc_per(player_stats, team_stats, league_stats)
    player_PProd = calc_points_produced(player_stats, team_stats)

    adv_player_stats = pd.merge(player_stats, player_PER, on=['PLAYER_ID', 'SEASON'])
    adv_player_stats = adv_player_stats.sort_values('PER', ascending=False)
    adv_player_stats = adv_player_stats[['PLAYER_NAME', 'PLAYER_ID', 'SEASON', 'PER']]
    print(adv_player_stats)

    adv_player_stats.to_csv(f'{OUT_DIR}/advanced_player_stats.csv')


if __name__ == '__main__':
    main()
