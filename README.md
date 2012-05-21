getBNet
=======

Fetch SC2 character information from battle.net

Shows position, win rate, wins and losses, and points.
Modify the 'defaultProfiles' array for the profiles you want to look up if no arguments are given.

Works for me under python 2.7 on OS X and requires BeautifulSoup

Run getBNet.py -h to show the usage.

Output looks like the following:

    Frozen: 7th in 1v1 Bronze, won 10 of 19 (52%, 25 pts) ..|||.|||.||..|...|  636 ... 525 523 519 [507] 507 492

Reading that from left to right, you have:
- Character name
- Rank and league
- Win/loss ratio from the games visible in your b.net profile, and the sum of your points
- Win/loss streak (dot = loss, pipe = win)
- Points in league.  In this case the league leader has 636 points, your own points are in square brackets, and you can see how many points the people around you have

Script can display information for multiple characters at once (one per line).  Can also display in bbcode format so you can easily post to a clan messageboard.