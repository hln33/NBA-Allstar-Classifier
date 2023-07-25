import pandas as pd
import random
import time
import requests.exceptions
from nba_api.stats.endpoints import boxscoreadvancedv2

# constants
HARD_COOLDOWN = 150
CACHE_THRESHOLD = 100
RELOAD_ALL_BOX_SCORES = False


# source:https://github.com/swar/nba_api/issues/159
def cooldown_api():
    api_cooldown = random.gammavariate(alpha=0.9, beta=0.4)
    time.sleep(api_cooldown)


def get_box_score(game_id):
    # API may time out, so we can try making the same call after waiting some time
    try:
        data = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)
    except requests.exceptions.ReadTimeout:
        print('request timed out')
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
def main():
    game_logs = pd.read_csv('cleaned_data/cleaned_game_logs.csv', dtype={'GAME_ID': str})
    already_loaded_box_scores = pd.read_csv('raw_data/advanced_box_scores.csv', dtype={'GAME_ID': str})

    counter = 0
    box_scores = pd.DataFrame() if RELOAD_ALL_BOX_SCORES else already_loaded_box_scores
    game_ids = game_logs['GAME_ID']
    for _, game_id in game_ids.items():
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
            box_scores.to_csv('raw_data/advanced_box_scores.csv')

    box_scores.to_csv('raw_data/advanced_box_scores.csv')


if __name__ == '__main__':
    main()
