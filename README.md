getBNet
=======

Fetch SC2 character information from battle.net

Shows position, win rate, wins and losses, and points.
Modify the 'defaultProfiles' array for the profiles you want to look up if no arguments are given.

Works for me under python 2.7 on OS X and requires BeautifulSoup

Run getBNet.py -h to show the usage.

Output looks like the following:

     Frozen : 33rd in 1v1 Gold 694 ... 520 517 515 [515] 512 505
        won 8 of 16 over last 7 days (50%, +66 pts) +.++....++.++.+.

Reading that from left to right, you have:
- Character name
- Rank and league
- Points in league.  In this case the league leader has 636 points, your own points are in square brackets, and you can see how many points the people around you have
- Win/loss ratio from the games visible in your b.net profile, and the sum of your points
- Win/loss streak (dot = loss, plus = win, "x" = bailed)


Script can display information for multiple characters at once (one per line).  Can also display in bbcode, wiki and simple html format so you can easily post to a clan messageboard.