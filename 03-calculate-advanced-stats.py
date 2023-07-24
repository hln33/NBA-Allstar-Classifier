import pandas as pd
import sys

# constants
IN_DIR = 'raw_data'
OUT_DIR = 'final_data'


def calc_league_stats(teams: pd.DataFrame) -> pd.DataFrame:
    lg = teams.groupby('SEASON').agg('sum')
    lg = lg[['FGM', 'FGA', 'FTM', 'FTA', 'PF', 'PTS', 'AST', 'OREB', 'REB', 'TOV']]

    # used to calculate PER
    lg['factor'] = (2/3) - (0.5 * (lg['AST']/lg['FGM'])) / (2 * (lg['FGM']/lg['FTM']))
    lg['VOP'] = lg['PTS'] / (lg['FGA'] - lg['OREB'] + lg['TOV'] + 0.44 * lg['FTA'])
    lg['DRB%'] = (lg['REB'] - lg['OREB']) / lg['REB']

    return lg


# calculate PER (player efficiency rating)
# source: https://www.basketball-reference.com/about/per.html
def calc_per(player: pd.DataFrame, team: pd.DataFrame, league: pd.DataFrame):
    player = pd.merge(player, team, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    print(player)

    player['uPER'] = (1 / player['MIN']) * (
        player['FG3M']
        + (2/3) * player['AST']
        + (2 - league['factor'] * (player['AST_TM']/player['FGM_TM'])) * player['FGM']
        + (player['FTM'] * 0.5 *
            (1 + (1 - (player['AST_TM']/player['FGM_TM'])) + (2/3) * (player['AST_TM']/player['FGM_TM']))
           )
        - league['VOP'] * player['TOV']
        - league['VOP'] * league['DRB%'] * (player['FGA'] - player['FGM'])
        - league['VOP'] * 0.44 * (0.44 + (0.56 * league['DRB%'])) * (player['FTA'] - player['FTM'])
        + league['VOP'] * (1 - league['DRB%']) * (player['REB'] - player['OREB'])
        + league['VOP'] * league['DRB%'] * player['OREB']
        + league['VOP'] * player['STL']
        + league['VOP'] * league['DRB%'] * player['BLK']
        - player['PF'] * ((league['FTM']/league['PF']) - 0.44 * (league['FTA']/league['PF']) * league['VOP'])
    )
    print(player)


def main():
    player_stats = pd.read_csv(f'{IN_DIR}/{sys.argv[1]}')
    team_stats = pd.read_csv(f'{IN_DIR}/{sys.argv[2]}')
    print(player_stats)
    print(team_stats)

    league_stats = calc_league_stats(team_stats)
    print(league_stats)

    calc_per(player_stats, team_stats, league_stats)

    # player_team = pd.merge(player_stats, team_stats, on=['TEAM_ID', 'SEASON'], suffixes=('', '_TM'))
    # player_team.to_csv('test/player_team.csv')
    # print(player_team)


if __name__ == '__main__':
    main()
