# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Extract "real world" information (update actual game scores from the ESPN
website)
"""
import re
import requests
from bs4 import BeautifulSoup

def find_wins(soup, tmname):
    """
    Get the number of wins a team has.  Adjust to make sure that play in
    wins are not counted.

    @param soup String xxx
    @param tmname String team name (number id)
    @param integer number of wins tmname has
    """
    retv = len(soup.find_all("a", {"title": tmname}))
    plyindivs = soup.find_all("div", id=re.compile("playingame*"))
    for plyin in plyindivs:
        retv -= len(plyin.find_all("a", {"title": tmname}))
    return retv - 1

def find_half_losers(soup, torb, indx, losers):
    """
    Scan game results for loser information.  Return list of teams that
    have lost in the tournament.  Easiest to do in two passes

    @param soup Beautiful Soup page information
    @param torb String top or bottom indicator (depends on pass)
    @param indx integer location of loser in game data
    @param losers List of losers (gets updated)
    @return updated loser list
    """
    games = soup.find_all("dl", {"class": torb})
    for game in games:
        ginf = game.find_all("a")
        if not ginf:
            continue
        losers.append(ginf[indx]["title"])
    return losers

def find_abbrev(soup, tmname):
    """
    Extract team abbreviation from web data

    @param soup Beautiful soup data from Espn bracket
    @param tmname String team name
    @return String abbrev or "-" if not needed (eliminated on first round)
    """
    matchups = soup.find_all("dl", {"class": "round2"})
    for game in matchups:
        ginf = game.find_all("a")
        if not ginf:
            continue
        for side in ginf:
            if side["title"] == tmname:
                return side.text
    return "-"

def get_team_info1():
    """
    Read the Espn website and convert the data to a dictionary indexed
    by team position number (position in the bracket)

    @returns dictionary containing real team data (name, abbreviations,
        an indicator if they are in or out, and a win counter)
    """
    response = requests.get(
        "http://www.espn.com/mens-college-basketball/tournament/bracket")
    soup = BeautifulSoup(response.content, 'html.parser')
    matchups = soup.find_all("dl", {"class": "round1"})
    tlist = []
    for teams in matchups:
        for side in teams.find_all("a"):
            tlist.append(side["title"])
    team_ids = {}
    llist = find_half_losers(soup, "winnerbot", 0, [])
    llist = find_half_losers(soup, "winnertop", 1, llist)
    for numb, tmname in enumerate(tlist):
        dnumb = numb + 1
        lossv = False
        if tmname in llist:
            lossv = True
        team_ids[f"{dnumb:02d}"] = {
            "team": tmname,
            "abbrev": find_abbrev(soup, tmname),
            "out": lossv,
            "wins": find_wins(soup, tmname)
        }
    return team_ids

def get_team_info():
    """
    Wrapper that keeps the interface the same if we get rid of fill_out_round_2
    and call get_team_info1 directly (renaming it get_team_info)
    """
    return fill_out_round_2(get_team_info1())

def fill_out_round_2(team_info):
    """
    Filter that insures that at least the sweet sixteen is reached during
    the first round.  Used for testing during initial development.  So far,
    this has been kept because it does not change things later, and future
    users may want to run this program a couple of days early to make sure
    everything works
    """
    mod_list = []
    for numb in range(0, 64):
        dnumb = numb + 1
        indx = f"{dnumb:02d}"
        if team_info[indx]['wins'] == 1 and not team_info[indx]['out']:
            mod_list.append(indx)
    for tindx in range(0, len(mod_list), 2):
        team_info[mod_list[tindx]]['wins'] = 2
        team_info[mod_list[tindx + 1]]['out'] = True
    return team_info

if __name__ == "__main__":
    print(get_team_info())