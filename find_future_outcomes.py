# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Collect data for winning entries for every possible future outcome
"""
import os
import itertools
import json
from get_scores import get_team_info
from score_group import calc_scores
from collect_entries import TOURNEY

def gen_future_outcomes():
    """
    Generate future outcomes.  For example, if there are 4 teams left there
    are eight possible outcomes.   If there are 16 teams left there are
    32,768 possible outcomes

    @return list of lists.  Each entry is one possible outcome in the set
            of possible outcomes
    """
    anslst = []
    ret_list = []
    data_so_far = get_team_info()
    for numb in range(0, 64):
        dnumb = numb + 1
        indx = f"{dnumb:02d}"
        if not data_so_far[indx]['out']:
            anslst.append(indx)
    for rcomb in list(itertools.product([0, 1], repeat=(len(anslst) - 1))):
        teams_left = anslst.copy()
        new_pattern = []
        rcind = 0
        while len(teams_left) > 1:
            nextt = []
            for indx2 in range(0, len(teams_left), 2):
                temp_tm = teams_left[indx2 + rcomb[rcind]]
                new_pattern.append(temp_tm)
                nextt.append(temp_tm)
                rcind += 1
            teams_left = nextt
        ret_list.append(new_pattern)
    return ret_list

def gen_panswers(gms_left):
    """
    Read picks.txt and parse out into a dictionary indexed by individual
    brackets.  Each entry is a list of picks (by team number) for the
    remaining games.

    @param gms_left integer number of total games left in the tournament
    @return dictionary list of relevant picks left, indexed by entrant
    """
    picks_txt = os.sep.join([TOURNEY, "picks.txt"])
    with open(picks_txt, "r", encoding="utf-8") as ofile:
        picdata = ofile.read()
    step1 = picdata.strip().split("\n")
    panswers = {}
    for pline in step1:
        pandp = pline.split(":")
        panswers[pandp[0]] = pandp[1].split("|")[-gms_left:]
    return panswers

def gen_comparisons():
    """
    Main find future routine.  For each possible combination of outputs,
    identify the winner, increase that winner's score, and save the
    combination of outcomes.  Sort the winner list.

    @return dictionary indexed by winning entrant
    """
    all_results = gen_future_outcomes()
    panswers = gen_panswers(len(all_results[0]))
    big_comp = {}
    pnt_tot = {}
    for entry in panswers:
        big_comp[entry] = [].copy()
        pnt_tot[entry] = 0.0
    startpts = calc_scores()
    for pos_out in all_results:
        maxv = 0
        pkey = []
        for indx, pansv in panswers.items():
            pts = startpts[indx] + comp_score(pansv, pos_out)
            if pts > maxv:
                maxv = pts
                pkey = [indx]
            if pts == maxv:
                pkey.append(indx)
        for entrant in pkey:
            pnt_tot[entrant] += 1.0 / len(pkey)
            big_comp[entrant].append(pos_out)
    pctwinsnum = {}
    for kindx in sorted(pnt_tot, key=pnt_tot.get, reverse=True):
        pctwinsnum[kindx] = pnt_tot[kindx]
    return consolidate(pctwinsnum, big_comp)

def comp_score(list1, list2):
    """
    Compute future scores

    Calculate further points in a future outcome

    @param list1 List of teams (entry's picks)
    @param list2 list of teams (possible future outcome)
    @return points scored for list1's set of picks if list2 is reality
    """
    spattern = 8 * [40] + 4 * [80] + 2 * [160] + [320]
    apattern = spattern[-len(list1):]
    total = 0
    for cnt, value in enumerate(apattern):
        if list1[cnt] == list2[cnt]:
            total += value
    return total

def consolidate(pctwinsnum, big_comp):
    """
    Consolidate data

    @param pctwinsnum dictionary sorted by entry name. Data saved is a
           raw payoff count for all possible results (wins are 1, ties
           are fractions of 1)
    @param big_comp dictionary sorted by entry name.  Data saved is a
           list winning outcomes.  Each winning outcome is a list of all
           game results that comprise this potential winning outcome.
    @return dictionary indexed by entry name.  Data is a dictionary
            containing winning outcome totals, expected payout, and
            a list of game information.  Each game information object is
            a dictionary indexed by team indicating the number of times
            a winning entry has this team
    """
    sbracket = {}
    for person in pctwinsnum:
        if pctwinsnum[person] == 0:
            break
        print(person, pctwinsnum[person], len(big_comp[person]))
        sbracket[person] = {"wins": len(big_comp[person]),
                            "pct": pctwinsnum[person]}
    for indx, person in sbracket.items():
        rsize = (len(big_comp[indx][0])+ 1) // 2
        gresults = [{} for _ in range(rsize)]
        for entry in big_comp[indx]:
            for cnt, gmres in enumerate(entry):
                if cnt >= rsize:
                    continue
                if gmres in gresults[cnt]:
                    gresults[cnt][gmres] += 1
                else:
                    gresults[cnt][gmres] = 1
        person["next_round"] = gresults
    return sbracket

def find_future_outcomes():
    """
    Stash future outcome data in leaders.json file
    """
    leaders = os.sep.join([TOURNEY, "leaders.json"])
    with open(leaders, 'w', encoding='utf-8') as file:
        json.dump(gen_comparisons(), file, ensure_ascii=False)

if __name__ == "__main__":
    find_future_outcomes()
