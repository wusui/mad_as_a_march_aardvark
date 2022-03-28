# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Extract "real world" information (update actual game scores from the ESPN
website)
"""
from configparser import ConfigParser
import requests
from bs4 import BeautifulSoup

class RealWorld():
    """
    Read the "real world" data

    real_team_info -- data extracted from Espn information
    soup -- Beautiful Soup information from Espn site
    rev_info -- local table to get index from team name
    """
    def __init__(self):
        response = requests.get(
            "http://www.espn.com/mens-college-basketball/tournament/bracket")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        self.real_team_info = {}
        matchups = self.soup.find_all("dl", {"class": "round1"})
        for cnt, teams in enumerate(matchups):
            for cnt2, side in enumerate(teams.find_all("a")):
                dnumb = 2 * cnt + cnt2 + 1
                self.real_team_info[f"{dnumb:02d}"] = {
                    "team": side["title"],
                    "abbrev": side.text,
                    "out": False,
                    "wins": 0
                }
        self.rev_indx = {}
        for entry in self.real_team_info.items():
            self.rev_indx[entry[1]['abbrev']] =  entry[0]
        for dep in range(1, 7):
            for tag in ['dl', 'div']:
                for pos in ['top', 'bot']:
                    self.add_gm_info(tag, dep, pos)
        self.normalize()
        config = ConfigParser()
        config.read('march_madness.ini')
        parse_info = config["DEFAULT"]
        if "level" in parse_info:
            self.flatten(int(parse_info["level"]))

    def add_gm_info(self, tag, dep, pos):
        """
        Add win count and still active indicator into get_team_info data

        @param tag (div or dl)
        @param dep round number (1 through 6)
        @param pos 'top' or 'bot']
        """
        wind = 0
        if pos == "bot":
            wind = 1
        for entry in self.soup.select(f'{tag}.round{dep}.winner{pos}'):
            temp = entry.find_all('a')
            winner = self.rev_indx[temp[wind].text]
            loser = self.rev_indx[temp[1 - wind].text]
            self.real_team_info[winner]['wins'] += 1
            self.real_team_info[loser]['out'] =  True

    def flatten(self, games_played):
        """
        Flatten all game info so that every team has played the same
        number of games.

        @param games_played int Number of games each survivor played
        """
        for team in self.real_team_info.items():
            if team[1]['wins'] >= games_played:
                team[1]['wins'] = games_played
                team[1]['out'] = False

    def normalize(self):
        """
        Find minimum games played by surviving team and back up all teams
        to that value.
        """
        minp = 6
        for team in self.real_team_info.items():
            if team[1]['wins'] < minp:
                if not team[1]['out']:
                    minp = team[1]['wins']
        self.flatten(minp)

if __name__ == "__main__":
    TEMP = RealWorld()
    TEMP.flatten(2)
    print(TEMP.real_team_info)
