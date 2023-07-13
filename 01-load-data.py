import pandas as pd
from nba_api.stats.endpoints import playercareerstats

def main():
    # Nikola Jokić
    career = playercareerstats.PlayerCareerStats(player_id='203999')

    # pandas data frames (optional: pip install pandas)
    df = career.get_data_frames()[0]
    print(df)


if __name__ == '__main__':
    main()
