#!/usr/bin/env python
#!/opt/local/bin/python
# coding=utf-8
# vim set et sts sw=4 sts=4 pymode_lint_ignore="E701"
# Last modified: 2016 Apr 17

""" Module Docstring
Fetch SC2 character information from battle.net.
Shows position, win rate, wins and losses, and points.
Modify the 'defaultProfiles' array for the profiles you want to look up if no arguments are given.

BUG: nonrandom Multiplayer still crashes the script (due to multiple player names)

Source: https://github.com/ax42/getBNet
Contact: sc2.frozen@fastmail.fm

"""

# profile either:
# Name, Number, League (1,2,4), Server
# URL, [optional League, default is "1"]
defaultProfiles = [
                   ["Frozen", "2492514", "1", "eu"],
                   ["Pain", "2874785", "1", "eu"],
                   ["http://us.battle.net/sc2/en/profile/4317361/1/Jenny/"],
                   ["http://us.battle.net/sc2/en/profile/4723309/1/Zergling/"]
                ]

import sys
import argparse
import urllib
import re
from datetime import datetime
from BeautifulSoup import BeautifulSoup


def main():
    ap = argparse.ArgumentParser(description="Fetch SC2 character information from battle.net")
    ap.add_argument('-v', '--verbose', default=0, help="Verbose output, add more v's for more verbosity", action="count")
    ap.add_argument('-d', '--date', help="Print date at start of output", action="store_true")
    ap.add_argument('-c', '--character', metavar=("Name", "BNet#", "League 1/2/4", "eu/na"), nargs=4, action="append", help="Character details", default=None)
    ap.add_argument('-u', '--url', metavar=("Battle.net URL", "League 1/2/4"), help='Battle.net URL [optional league 1/2/4, default=1]', default=None, action="append", nargs='+')
    ap.add_argument('-f', '--find', metavar="Name", help='Specify one of the builtin profiles to display', action="append", default=None)

    outputFormat = ap.add_mutually_exclusive_group()
    outputFormat.add_argument('-ob', '--output-bbcode', help="Output in BBCode markup", action="store_true")
    outputFormat.add_argument('-oh', '--output-html', help="Output with html markup", action="store_true")
    outputFormat.add_argument('-ow', '--output-wikia', help="Output with wikia markup", action="store_true")

    args = ap.parse_args()
    VERBOSE = args.verbose
    if VERBOSE: print "args", args

    profiles = []
    if args.character: [profiles.append(x) for x in args.character]
    if args.find:
        for f in args.find:
            [profiles.append(x) for x in defaultProfiles if re.search(f, x[0]) is not None]
    if args.url: [profiles.append(x) for x in args.url]
    if len(profiles) == 0: profiles = defaultProfiles

    if len(profiles) == 0:  # ie the defaultProfiles list was empty -- edge case
        print "Please specify at least one profile to look up.  Exiting."
        sys.exit(1)

    if VERBOSE: print "Profiles to fetch:", profiles
    # regex for ladder page
    r = re.compile(r"/sc2/en/profile/(\d+)/\d/(\S+)/")

    if args.date: print datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    for curPlayer in profiles:
        #First find the league page
        if len(curPlayer) == 1:  # assume it's only a URL
            charURL = curPlayer[0]
            pLeague = "1"  # URLS hard-coded to 1v1 for now
        elif len(curPlayer) == 2:  # assume a URL and a league
            charURL = curPlayer[0]
            pLeague = curPlayer[1]
        else:
            charURL = "http://%s.battle.net/sc2/en/profile/%s/1/%s/" % (curPlayer[3], curPlayer[1], curPlayer[0])
            pLeague = curPlayer[2]
        if VERBOSE: print "charURL", charURL

        pServer, pNo, pName = re.match(r"http://(..)\.battle\.net/sc2/en/profile/(\d+)/\d/(\S+)/", charURL).groups()
        if VERBOSE: print pServer, pNo, pName, pLeague

        # Open profile page, figure out ladder URL
        raw = urllib.urlopen(charURL).read()
        if VERBOSE > 2: print raw
        p = BeautifulSoup(raw)

        divisionFound = False

        ladderURL = charURL+"ladder/leagues"
        if VERBOSE: print "ladderURL", ladderURL

        # Read ladder page and parse it for current points standings
        raw = urllib.urlopen(ladderURL.encode('utf-8')).read()
        p = BeautifulSoup(raw)

        # 1v1 division is 4th menu item on left menu
        try:
            matchURL = charURL + "ladder/" + p.find('ul', id="profile-menu").findAll('a')[3]['href']
            if VERBOSE: print "matchURL", matchURL
        except:
            pass

        try:
            division = p.find('',{'class' : 'data-title'}).find(text=re.compile('Division'))
            divisionFound = True
        except:
            division = ""  # Some occurred while fetching the division's page from b.net
            if VERBOSE: print "Error: Couldn't read division information from b.net for %s ('%s'), skipping" % (pName, p.title.string)

        if divisionFound:
            league = re.match(r"(\w+\s){2}",p.title.string).group(0).strip()
            if VERBOSE: print division, ":", league

            if division == None:
                divisionFound = False
            else:
                try:
                    bonusPool = int(p.find('span', {"id":"bonus-pool"}).find('span').string)
                except:
                    bonusPool = 0
                    if VERBOSE: print "bonusPool not found, assuming 0"

                if VERBOSE: print bonusPool
                ltable = p.find('table', {'class' : 'data-table ladder-table'}).findAll('td')

                if VERBOSE > 2: print ltable

                ranks = [x.string for x in p.findAll('td', {"class":"align-center", "style":True, "data-tooltip":None})]

                names = [r.match(y).group(2) for y in [x['href'] for x in p.findAll('a', {"data-tooltip":re.compile("#player")})]]
                nums = [r.match(y).group(1) for y in [x['href'] for x in p.findAll('a', {"data-tooltip":re.compile("#player")})]]
                points = [x.string for x in p.findAll('td', {"class":"align-center", "style":None})][::3]

                players = zip(ranks, nums, names, points)
                playerIndex = nums.index(pNo)
                if VERBOSE > 1: print "%d players" % (len(players)), players
                if VERBOSE > 1: print "playerIndex", playerIndex
                if VERBOSE: print players[playerIndex]

        # Get match history
        matchURL = charURL + "matches"
        raw = urllib.urlopen(matchURL).read()
        p = BeautifulSoup(raw)
        matchType = {"1":"solo", "2":"twos", "4":"fours"}[pLeague]
        pMatches = p.findAll('tr',{"class":"match-row %s" % (matchType)})
        if VERBOSE: print "len(pMatches)", len(pMatches), p.title.string

        if pServer == "eu": dtFormat = "%d/%m/%Y"
        elif pServer == "us": dtFormat = "%m/%d/%Y"

        matchDates = [datetime.strptime(x.find('',{"class":"align-right"}).string.strip(), dtFormat) for x in pMatches]
        matchScores = []
        matchOutcomes = []
        for x in pMatches:
            try:
                matchScores.append(int(x.find('span',{"class":re.compile("text-")}).string))
            except AttributeError:
                matchScores.append(0)
            try:
                matchOutcomes.append(x.find('span',{"class":re.compile("match-")}).string)
            except AttributeError:
                matchOutcomes.append(0)

        #matchScores = [int(x.find('span',{"class":re.compile("text-")}).string) for x in pMatches]
        matchWins = len([x for x in matchOutcomes if x == "Win"])

        if VERBOSE: print "matchScores", matchScores
        if VERBOSE: print "matchOutcome", matchOutcomes
        if VERBOSE: print "matchDates", matchDates

        def pprint(v):
            """ print player points for index v, surround with [] if it is current player
            """
            if (v == playerIndex):
                if args.output_bbcode: print "[color=#dd2423][%s][/color]" % players[v][3],
                elif args.output_html: print '<span class="hilight">[%s]</span>' % players[v][3],
                elif args.output_wikia: print '<u>[%s]</u>'  % players[v][3],
                else: print '[%s]' % players[v][3],
            else: print "%s" % players[v][3],

        if args.output_bbcode:
            oName = "[url=%s]%s[/url]" % (charURL, pName)
            if divisionFound:
                oLeague = "[color=#dd2423]%s[/color] in [url=%s]%s[/url]" % \
                    (players[playerIndex][0], ladderURL, league)
        elif args.output_html:
            oName = '<a href="%s">%s</a>' % (charURL, pName)
            if divisionFound:
                oLeague = '<span class="hilight">%s</span> in <a href=%s>%s</a>' % \
                    (players[playerIndex][0], ladderURL, league)
        elif args.output_wikia:
            oName = '[%s %s]' % (charURL, pName)
            if divisionFound:
                oLeague = '%s in [%s %s]' % \
                    (players[playerIndex][0], ladderURL, league)
        else:
            oName = pName
            if divisionFound:
                oLeague = "%s in %s" % (players[playerIndex][0], league)

        if not divisionFound:
            if division == None:
                oLeague = "Not yet placed"
            else:
                oLeague = "Could not read ladder info from b.net"


        print "%s" % (";" if args.output_wikia else "") ,oName, ":", oLeague,

        if divisionFound:
            pprint(0)
            if playerIndex > 4: print "...",
            for x in range(max(1, playerIndex - 3), min(playerIndex + 3, len(players))):
                pprint(x)
            print "(Bonus Pool %d)" % bonusPool,
        print

        if args.output_wikia:
            print ":",
        else:
            print ' ' * (len(pName)+1),

        if len(pMatches) > 0:
            matchPeriod = (datetime.today() - matchDates[-1]).days +1
            if args.output_bbcode:
                oWinRate = "[url=%s]%d%%[/url]" % (matchURL, matchWins / float(len(matchScores)) * 100)
            elif args.output_html:
                oWinRate = '<a href="%s">%d%%</a>' % (matchURL, matchWins / float(len(matchScores)) * 100)
            elif args.output_wikia:
                oWinRate = '[%s %d%%]' % (matchURL, matchWins / float(len(matchScores)) * 100)
            else:
                oWinRate = "%d%%" % ((matchWins / float(len(matchScores))) * 100)

            if args.output_html: print "<br>"
            print "won %d of %d over last %d day%s (%s, %+d pts)"  % (matchWins, len(matchScores), \
                matchPeriod, "s" if matchPeriod > 1 else "", \
                oWinRate,
                sum(matchScores)),
            print ''.join(["+" if x == "Win" else "." for x in matchOutcomes])
        else:
            if args.output_bbcode: print "[url=%s]No %sv%s matches found[/url]" % (matchURL, pLeague, pLeague)
            elif args.output_html: print '<a href="%s">No %sv%s matches found</a>' % (matchURL, pLeague, pLeague)
            elif args.output_wikia: print '[%s No %sv%s matches found]' % (matchURL, pLeague, pLeague)
            else: print "No %sv%s matches found" % (pLeague, pLeague)
        if args.output_html: print "<br><br>"

    if args.output_wikia: print "~~~~"
if __name__ == '__main__':
    main()

