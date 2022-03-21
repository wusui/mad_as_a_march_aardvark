# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Generate an html page (the whole purose of this exercise)
"""
import os
import json
from configparser import ConfigParser
from get_scores import get_team_info
from collect_entries import TOURNEY

def get_table_labels(tm_info):
    """
    @param tm_info dictionary data from get_team_info
    @return string of html data filling in the header of the table
    """
    wmax = 0
    tlist = []
    ostr = "<tr><th>NAME</th><th><div>Winning</div>"
    ostr += "<div>Outcomes</div></th><th><div>"
    ostr += "Probable</div><div>Payoff</div</th>\n"
    for tm_ind in tm_info:
        if tm_info[tm_ind]["wins"] > wmax:
            wmax = tm_info[tm_ind]["wins"]
    for tm_ind in tm_info:
        if tm_info[tm_ind]["wins"] ==  wmax:
            tlist.append(tm_info[tm_ind]['abbrev'])
    for indx in range(0, len(tlist), 2):
        ostr += "<th><div>" + tlist[indx] + "</div><div>"
        ostr += tlist[indx + 1] + "</div></th>\n"
    ostr += "</tr>\n"
    return ostr

def add_table_sq(entry, tm_info):
    """
    Fill in a cell in the next game section of the table

    @param dict entry this cell's data
    @param dict tm_info team info from get_team_info
    @return String html for this cell
    """
    if len(entry) == 1:
        tm_ind = list(entry.keys())[0]
        sq_val = '<td  style="background-color:#000000;color:#ffffff">'
        sq_val += tm_info[tm_ind]['abbrev'] + "</td>\n"
        return sq_val
    elist = []
    evalue = []
    for ekey in entry:
        elist.append(ekey)
        evalue.append(entry[ekey])
    diffy = evalue[0] - evalue[1]
    if diffy == 0:
        return "<td>*</td>"
    indx = elist[0]
    if diffy  < 0:
        indx = elist[1]
        diffy = 0 - diffy
    bcolor = get_ccode(diffy, evalue[0] + evalue[1])
    retv = f'<td style="background-color:{bcolor}">'
    retv += tm_info[indx]['abbrev'] + "</td>\n"
    return retv

def get_ccode(diffy, total):
    """
    Get the style color for a square on the table

    @param integer diffy difference between two team choices
    @param integer total total number of winning combinations
    @return RBG color code
    """
    coloff = 512 * diffy / total
    icol = int(coloff + .5)
    if icol < 256:
        red = icol
        green = 255
    else:
        red = 255
        green = max(511 - icol, 0)
    return f'#{red:02x}{green:02x}00'

def get_table_body(user_data, tm_info):
    """
    Wrapper to generate the table displayed

    @param user_data dictionary extracted from leaders.json
    @param tm_info dictionary from get_team_info so that numbers
           can be replaced by team names or abbreviations

    @return string of html code filling in the body of the table
    """
    ostr = ""
    for name in user_data:
        ostr += "<tr><td>" + name + "</td><td>"
        ostr += str(user_data[name]['wins']) + "</td><td>"
        pvalue = user_data[name]["pct"] / 32768.0
        ostr += f'{pvalue:10.5f}' + "</td>"
        for entry in user_data[name]['next_round']:
            ostr += add_table_sq(entry, tm_info)
        ostr += "<tr>\n"
    return ostr

def generate_display():
    """
    Generate an html file based on the data in leaders.json

    Produces NCAA_madness.html file
    """
    leaders = os.sep.join([TOURNEY, "leaders.json"])
    with open(leaders, 'r', encoding='utf-8') as ofile:
        user_data = json.load(ofile)
    tm_info = get_team_info()
    with open("header.txt", 'r', encoding="utf-8") as hfile:
        header = hfile.read()
    table_labels = get_table_labels(tm_info)
    table_body = get_table_body(user_data, tm_info)
    trailer = "</table></center></body></html>"
    out_string = header + table_labels + table_body + trailer
    config = ConfigParser()
    config.read('march_madness.ini')
    title = config["DEFAULT"]["group"].replace("_", " ")
    madness = os.sep.join([TOURNEY, "NCAA_madness.html"])
    with open(madness, "w", encoding="utf-8") as mfile:
        mfile.write(out_string % (title, title))

if __name__ == "__main__":
    generate_display()
