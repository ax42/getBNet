getBNet
=======

Fetch SC2 character information from battle.net

Shows position, win rate, wins and losses, and points.
Modify the 'defaultProfiles' array for the profiles you want to look up if no arguments are given.

Works for me under python 2.7 on OS X and requires BeautifulSoup

BUG: nonrandom Multiplayer still crashes the script (due to multiple player names)

Usage: getBNet.py [-h] [-v] [-c Name BNet# League Region] [-f KnownName]  
optional arguments:  
  -h, --help                    show this help message and exit  
  -v, --verbose                 Verbose output, add more v's for more verbosity  
  -c  Name BNet# League eu/na   Where BNet# is the one from your URL and League is 1/2/4  
  -f FIND, --find               Specify a profile from the defaults to display  

-f and -c can be repeated.  Edit the defaultProfiles array at the top of 
  the .py file for characters you use often.

Output looks like the following:

    Frozen: 7th in 1v1 Bronze, won 10 of 19 (52%, 25 pts) ..|||.|||.||..|...|  636 ... 525 523 519 [507] 507 492

Reading that from left to right, you have:
- Character name
- Rank and league
- Win/loss ratio from the games visible in your b.net profile, and the sum of your points
- Win/loss streak (dot = loss, pipe = win)
- Points in league.  In this case the league leader has 636 points, your own points are in square brackets, and you can see how many points the people around you have

Script can display information for multiple characters at once (one per line).