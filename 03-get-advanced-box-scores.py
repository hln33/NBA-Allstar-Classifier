import sys
import pandas as pd
import random
import time
import requests.exceptions
from nba_api.stats.endpoints import boxscoreadvancedv2

# constants
IN_DIR = 'cleaned_data/'
OUT_DIR = 'raw_data/'
HARD_COOLDOWN = 150
CACHE_THRESHOLD = 100
RELOAD_ALL_BOX_SCORES = False


# source:https://github.com/swar/nba_api/issues/159
def cooldown_api():
    api_cooldown = random.gammavariate(alpha=0.9, beta=0.4)
    time.sleep(api_cooldown)


def get_box_score(game_id):
    try:
        data = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)
    except requests.exceptions.ReadTimeout:
        print(f'request timed out; Trying again after {HARD_COOLDOWN} secs')
        time.sleep(HARD_COOLDOWN)
        data = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)
    cooldown_api()

    # sometimes no data is returned from API call, so we must handle it
    try:
        team_box_score = data.team_stats.get_data_frame()
        return team_box_score
    except IndexError as e:
        print('IndexError occurred:', e)
    return None


# get advanced box score stats to be used in the calculation of advanced stats
# ** this step may take a long time to run (hours) since the api acts as a bottleneck **
def main(input_path, output_path):
    game_logs = pd.read_csv(input_path, dtype={'GAME_ID': str})
    already_loaded_box_scores = pd.read_csv(output_path, dtype={'GAME_ID': str})

    box_scores = pd.DataFrame() if RELOAD_ALL_BOX_SCORES else already_loaded_box_scores
    counter = len(box_scores.index)
    for _, game_id in game_logs['GAME_ID'].items():
        print(game_id)

        already_loaded = game_id in already_loaded_box_scores['GAME_ID'].values
        if not RELOAD_ALL_BOX_SCORES and already_loaded:
            print("box score already loaded")
            continue

        team_box_score = get_box_score(game_id)
        if team_box_score is None:
            print("api returned no data:", game_id)
            continue
        box_scores = pd.concat([box_scores, team_box_score], ignore_index=True)

        counter += 1
        print(counter)
        if counter % CACHE_THRESHOLD == 0:
            print('saving intermediate results')
            box_scores.to_csv(output_path, index=False)

    box_scores.to_csv(output_path, index=False)


if __name__ == '__main__':
    input_path = IN_DIR + sys.argv[1]
    output_path = OUT_DIR + sys.argv[2]
    main(input_path, output_path)
