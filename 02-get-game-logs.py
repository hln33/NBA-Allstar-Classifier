import pathlib
import pandas as pd
from nba_api.stats.endpoints import playergamelogs
from nba_api.stats.library.parameters import SeasonSegmentNullable

# constants
IN_DIR = 'data'
OUT_DIR = 'data'


def main():
    input_dir = pathlib.Path(IN_DIR)
    output_dir = pathlib.Path(OUT_DIR)

    kareem_logs = playergamelogs.PlayerGameLogs(
        player_id_nullable='76003',
        season_nullable='1969-70',
        season_segment_nullable=SeasonSegmentNullable.pre_all_star
    )
    kareem_logs = kareem_logs.get_data_frames()[0]
    print(kareem_logs)

    kareem_logs.to_csv('kareem.csv')


if __name__ == '__main__':
    main()
