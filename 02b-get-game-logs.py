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

    old_logs = playergamelogs.PlayerGameLogs(
        player_id_nullable='77116',
        season_nullable='1950-51',
        # season_segment_nullable=SeasonSegmentNullable.pre_all_star
    )
    old_logs = old_logs.get_data_frames()[0]
    print(old_logs)

    old_logs.to_csv('old_logs.csv')


if __name__ == '__main__':
    main()
