import pandas as pd
import sys

# constants
IN_DIR = 'raw_data'
OUT_DIR = 'final_data'


def calc_league_stats(teams: pd.DataFrame) -> pd.DataFrame:
    lg = teams.groupby('SEASON').agg('sum')
    lg = lg[['FGM', 'FGA', 'FTM', 'FTA', 'PF', 'PTS', 'AST', 'OREB', 'REB', 'TOV']]

    # used to calculate PER
    lg['FACTOR'] = (2/3) - (0.5 * (lg['AST']/lg['FGM'])) / (2 * (lg['FGM']/lg['FTM']))
    lg['VOP'] = lg['PTS'] / (lg['FGA'] - lg['OREB'] + lg['TOV'] + 0.44 * lg['FTA'])
    lg['DRB%'] = (lg['REB'] - lg['OREB']) / lg['REB']

    return lg


# calculate PER (player efficiency rating)
# source: https://www.basketball-reference.com/about/per.html
def calc_per(player_stats: pd.DataFrame, league_totals: pd.DataFrame):
    # player_stats['uPER'] = (1 / player_stats['MIN']) * (
    #     player_stats['FG3M']
    #     + (2/3) * player_stats['AST']
    #     + (2)
    # )
    pass


def main():
    player_stats = pd.read_csv(f'{IN_DIR}/{sys.argv[1]}')
    team_stats = pd.read_csv(f'{IN_DIR}/{sys.argv[2]}')
    print(player_stats)
    print(team_stats)

    league_stats = calc_league_stats(team_stats)
    print(league_stats)


if __name__ == '__main__':
    main()
