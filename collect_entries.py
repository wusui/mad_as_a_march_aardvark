# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Main section of code that follows website links and extracts the pick data.
Pick data is saved in picks.json
"""
import os
import re
import time
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from get_espn_driver import get_espn_driver_wrap, wait_get

TRAILER = "- Tournament Challenge - ESPN"
TOURNEY = "tourney"

def get_root_site():
    """
    Return the url of the tournament site for this year

    @return String Url pointing to tournament webpage
    """
    header = "https://fantasy.espn.com/tournament-challenge-bracket"
    ldate = datetime.now().date()
    year = ldate.strftime("%Y")
    return f"{header}/{year}/en/"

def handle_a_webpage(driver, page_url, filen=""):
    """
    Extract the text of a website using the selenium driver

    @param driver object selenium driver
    @param page_url string webpage being operated on
    @param filen string name of file to store data (if blank, don't store)

    @return contents of webpage
    """
    driver.get(page_url)
    wait_get(4, driver, (By.ID, "main-container"))
    wpage = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(wpage, 'html.parser')
    if filen:
        with open(filen, "w", encoding="utf-8") as ofile:
            ofile.write(soup.prettify())
    return soup

def parse_group_table(driver):
    """
    Extract innerHTML from the group table wrapper

    @param driver Object Selenium driver used
    @return BeautifulSoup version of the innerHTML data
    """
    grp_tbl_wrpr = driver.find_element(By.ID, "groupTableWrapper")
    tableinf = grp_tbl_wrpr.get_attribute('innerHTML')
    return BeautifulSoup(tableinf, 'html.parser')

def save_bracket_files(driver, root_site, answer):
    """
    Write files in the tourney directory.  Each file is a bracket entry
    and is named by the ESPN entry number

    @param driver Object Selenium driver used
    @param root_site String URL of the parent ESPN tournament websitefi
    @param answer String link to individual user's bracket page
    """
    ginfo = root_site + answer
    handle_a_webpage(driver, ginfo)
    pcntr = driver.find_elements(By.CLASS_NAME, "navigationLink")
    for _ in range(0, len(pcntr) - 1):
        soup = parse_group_table(driver)
        elist = []
        for atag in soup.find_all('a'):
            hrefv = atag.get("href")
            if hrefv.startswith("entry?entryID"):
                elist.append(hrefv)
        for entry in elist:
            number = entry.split("=")[-1]
            dfname = os.sep.join([TOURNEY, f'un1q___{number}'])
            urlv = root_site + entry
            print(f'Saving entry {number}')
            handle_a_webpage(driver, urlv, dfname)
        handle_a_webpage(driver, ginfo)
        xpcntr = driver.find_elements(By.CLASS_NAME, "navigationLink")
        xpcntr[-1].click()
        time.sleep(4) # kludge
    driver.close()

def extract_pick_data():
    """
    Collect pick data from saved files and compress that information into
    the picks.json file
    """
    pick_dict = {}
    for entry in os.listdir(TOURNEY):
        if not entry.startswith('un1q___'):
            continue
        infile = f'{TOURNEY}{os.sep}{entry}'
        with open(infile, "r", encoding="utf-8") as fdesc:
            linez = fdesc.readlines()
            tname = ''
            for rline in linez:
                if rline.find(TRAILER) > 0:
                    tname = rline.split(TRAILER)[0].strip()
                if rline.startswith("espn.fantasy.maxpart.config.pickString"):
                    answer = rline.split("=")[-1].strip()[0:-2][1:]
                    if len(answer) > 100:
                        pick_dict[tname] = answer.split("|")
                    break
    picks_json = os.sep.join([TOURNEY, "picks.json"])
    with open(picks_json, 'w', encoding='utf-8') as pfile:
        json.dump(pick_dict, pfile, ensure_ascii=False)

def extract_players():
    """
    Log in to ESPN, navigate to this group, and extract the pick
    information from peoples' brackets.
    """
    driver, pgroup, pnumb = get_espn_driver_wrap()
    root_site = get_root_site()
    answer = ''
    if pnumb:
        answer = f"group?groupID={pnumb}"
    else:
        pgroup = pgroup.replace("_", " ")
        soup = handle_a_webpage(driver, root_site)
        for lst_ind in soup.find_all('li'):
            gfound = lst_ind.find(href=re.compile(r"group\?groupID=*"))
            if gfound:
                if pgroup in gfound.get_text():
                    answer = gfound["href"]
                    break
    if answer:
        save_bracket_files(driver, root_site, answer)
    extract_pick_data()

def collect_entries():
    """
    Make sure the tourney directory exists before extracting player info
    """
    if not os.path.exists(TOURNEY):
        os.mkdir(TOURNEY)
    extract_players()

if __name__ == "__main__":
    collect_entries()
