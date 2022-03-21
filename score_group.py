# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Reduce the pick data into the number of wins for each team selected by an
individual entrant
"""
import os
from get_scores import get_team_info
from collect_entries import TOURNEY

def count_wins(teams):
    """
    Covert a list of teams into a histogram of the number of times that team
    appeared in the list

    @param teams list of teams
    @return dictionary indexed by team number whose values are the number of
            times that team number appeared in the teams list
    """
    wins = {}
    for numb in range(0, 64):
        dnumb = numb + 1
        wins[f"{dnumb:02d}"] = 0
    for entry in teams:
        wins[entry] += 1
    return wins

def score_group():
    """
    Read the picks.txt file and return a dictionary index by group entrant
    whose values are dictionaries.

    @return dictionary each entry in this dictionary is a dictionary of pick
            information (team 01 was picked twice, team 02 was picked 0 times,
            team 03 was picked once...)
    """
    picks_txt = os.sep.join([TOURNEY, "picks.txt"])
    with open(picks_txt, "r", encoding="utf-8") as ofile:
        picdata = ofile.read()
    indv_data = picdata.strip().split("\n")
    retv = {}
    for entry in indv_data:
        parts = entry.split(":")
        teams = parts[1].split("|")
        retv[parts[0]] = count_wins(teams)
    return retv

def calc_scores():
    """
    Calculate bracket scores. Return a dictionary indexed by group entrant
    whose value is their points scored so far.

    @return dictionary points for each entrant
    """
    user_info = score_group()
    real_info = get_team_info()
    score_table = [0, 10, 30, 70, 150, 310, 630]
    udata = {}
    for user in user_info.items():
        score = 0
        for numb in range(0, 64):
            dnumb = numb + 1
            windx = f"{dnumb:02d}"
            wins = real_info[windx]['wins']
            if user[1][windx] < wins:
                wins = user[1][windx]
            score += score_table[wins]
        udata[user[0]] = score
    return udata

if __name__ == "__main__":
    print(calc_scores())
