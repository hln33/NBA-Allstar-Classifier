import pandas as pd

# constants
IN_DIR = 'raw_data'
OUT_DIR = 'cleaned_data'


def clean_game_logs(games: pd.DataFrame) -> pd.DataFrame:
    games = games.copy(deep=True)

    games = games.drop_duplicates(subset='GAME_ID')
    games['GAME_ID'] = games['GAME_ID'].astype(str)
    games['GAME_ID'] = games['GAME_ID'].str.pad(width=10, fillchar='0')

    pre_allstar_regex = r'^(199[6-9]|200\d|201[0-9]|202[0-2])-(10|11|12|0[1-2])-.+'
    games = games[games['GAME_DATE'].str.contains(pre_allstar_regex, regex=True)]
    return games


def main():
    games = pd.read_csv(f'{IN_DIR}/game_logs.csv')

    games = clean_game_logs(games)
    print(games['GAME_ID'])

    games.to_csv(f'{OUT_DIR}/cleaned_game_logs.csv')


if __name__ == '__main__':
    main()
