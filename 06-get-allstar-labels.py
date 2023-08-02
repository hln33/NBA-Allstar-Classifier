# ADAPTED FROM: https://gist.github.com/cjporteo/90b3d56cc2b95c7f1fc120a82224c47c

from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import time
import requests
import csv
from unidecode import unidecode

# rows to ignore when iterating the roster tables
IGNORE_FIELDS = {'Team Totals', 'Reserves'}
START_YEAR, END_YEAR = 1996, 2024


# unidecode doesn't catch the accented c in Peja's last name (Stojakovic), fix it
# also overwrite any instance of Metta World Peace to Ron Artest
def fix_name(full_name):
    first_name = full_name.split(' ')[0]
    if first_name == 'Peja':
        return 'Peja Stojakovic'
    elif first_name == 'Metta':
        return 'Ron Artest'
    else:
        return unidecode(full_name)


def output_csv(allstar_set: defaultdict[set]):
    with open('final_data/allstars.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Player', 'Years'])
        for player, years in allstar_set.items():
            writer.writerow([player, ', '.join(map(str, years))])


def main():
    # this dictionary will map players to a set containing all the years in which they were
    # selected for an all-star game, either initially or as a replacement
    all_star_appearances = defaultdict(set)

    for year in range(START_YEAR, END_YEAR):
        # no ASG played in 1999 because of the lockout
        if year == 1999:
            continue

        print('Scraping ASG {} data...'.format(year))
        html = requests.get('https://www.basketball-reference.com/allstar/NBA_{}.html'.format(year)).content
        soup = BeautifulSoup(html, 'html.parser')
        all_stars_for_year = set([])

        # get the all-stars from teams 1 and 2
        s1, s2 = soup.findAll('table')[1:3]
        team1 = pd.read_html(str(s1))[0]
        team2 = pd.read_html(str(s2))[0]
        for team in [team1, team2]:
            for i, row in team.iterrows():
                if pd.notnull(row[0]) and row[0] not in IGNORE_FIELDS:
                    player = row[0]
                    all_stars_for_year.add(fix_name(player))

        # finds the li element that contains the data pertaining to injury related selections
        # - players who were selected but couldn't participate due to injury,
        #   and their respective replacements
        #
        # since all_stars is a hashset, we don't need to worry about accidentally double counting an all-star
        s3 = soup.findAll('li')
        for s in s3:
            if 'Did not play' in str(s):
                for player in [name.get_text() for name in
                               s.findAll('a')]:  # all the injured players and their replacements
                    all_stars_for_year.add(fix_name(player))
                break

        # update the appearances dictionary
        for player in all_stars_for_year:
            all_star_appearances[player].add(year)
        print(all_star_appearances)

        # sleep to prevent website from blocking us
        time.sleep(30)

    print('\nAll all-star appearances since 1970 (sorted by number of appearances):\n')
    sorted_all_star_appearances = sorted(
        [(player, sorted(list(appearances))) for player, appearances in all_star_appearances.items()],
        key=lambda x: -len(x[1])
    )
    for player, appearances in sorted_all_star_appearances:
        print('{}: {}'.format(player, appearances))

    # with open('final_data/allstars.csv', 'w', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['Player', 'Years'])
    #     for player, years in all_star_appearances.items():
    #         writer.writerow([player, ', '.join(map(str, years))])
    output_csv(all_star_appearances)


if __name__ == '__main__':
    main()
