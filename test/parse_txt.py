import re
import csv

# Read the content of the text file
with open('../final_data/allstars_2020-2023.txt', 'r') as file:
    content = file.read()

# Find all the player entries using regular expressions
pattern = r"'(.*?)': \{(.*?)\}"
matches = re.findall(pattern, content)

# Create a dictionary from the matches
data_dict = {match[0]: set(map(int, match[1].split(', '))) for match in matches}

# Print the resulting dictionary
print(data_dict.items())

with open('../final_data/allstars.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Player', 'Years'])

    for player, years in data_dict.items():
        writer.writerow([player, ', '.join(map(str, years))])
