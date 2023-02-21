# NCAA March Madness office Pool Display

Differences from previous versions:
  * Python +3.10
  * Uses Beautiful Soup
  * Uses selenium for data extraction

This version is much more fully automated than previous versions

## Use

### Before the tournament / Early in the tournament

create a march_madness.ini file in the source directory with the following text:

```
[DEFAULT]
username: <your ESPN login>
password: <your ESPN password>
group: <your group name using _ for blanks>
```

### Once the tournament starts (best after Sweet-16, Elite-8, and Final-4 are set):

```
python madness.py
```

That's pretty much it.  Output is a file named tourney/NCAA_madness.html

It is possible that when logging in to the ESPN website, you will need to use
two-factor authentication.  If so, fill in the key by hand and everything should
still work.

## Extra Stuff

Last updated in 2022. Knocking off the dust in 2023

This software is licensed under the MIT license.
