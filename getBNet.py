#!/opt/local/bin/python
# coding=utf-8
# vim:et:sts:sw=4:sts=4
# Last modified: 2012 May 02

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
defaultProfiles = [["Frozen", "2492514", "1", "eu"], 
                   ["Pain", "2874785", "1", "eu"],
                   ["http://eu.battle.net/sc2/en/profile/2104202/1/eXeNoLuck/"],
                   ["http://eu.battle.net/sc2/en/profile/2149899/1/CiderDad/"],
                   ["http://eu.battle.net/sc2/en/profile/822228/1/StupidBrit/"],
                   #["http://eu.battle.net/sc2/en/profile/574878/1/Zero/"],
                   ]

import sys
import argparse

import urllib, urlparse
import re

from BeautifulSoup import BeautifulSoup

def main():
    ap = argparse.ArgumentParser(description="Fetch SC2 character information from battle.net")
    ap.add_argument('-v','--verbose', default=0,
        help="Verbose output, add more v's for more verbosity", action="count")
    ap.add_argument('-c', '--character', metavar=("Name","BNet#","League 1/2/4", "eu/na"), nargs=4, action="append", help="Character details", default=None)
    ap.add_argument('-u', '--url', metavar=("Battle.net URL", "League 1/2/4"), help='Battle.net URL [optional league 1/2/4, default=1]', default=None, action="append", nargs='+')
    ap.add_argument('-f', '--find', metavar="Name", help='Specify a default profile to display', action="append", default=None)

    args = ap.parse_args()
    VERBOSE = args.verbose
    if VERBOSE: print "args", args

    profiles = []
    if args.character: [profiles.append(x) for x in args.character]
    if args.find:
        for f in args.find:
            [profiles.append(x) for x in defaultProfiles if re.search(f, x[0]) != None]
    if args.url: [profiles.append(x) for x in args.url]  
    if len(profiles) == 0: profiles = defaultProfiles

    if len(profiles) == 0:  # ie the defaultProfiles list was empty -- edge case
        print "Please specify at least one profile to look up.  Exiting."
        sys.exit(1)

    if VERBOSE: print "Profiles to fetch:", profiles
    # regex for ladder page
    r = re.compile(r"/sc2/en/profile/(\d+)/\d/(\S+)/")
    
    for curPlayer in profiles:
        #First find the league page
        if len(curPlayer) == 1:  # assume it's only a URL
            charURL = curPlayer[0]
            pLeague = "1" # URLS hard-coded to 1v1 for now
        elif len(curPlayer) == 2: # assume a URL and a league
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
        try:
            ladderURL = "http://%s.battle.net" % (pServer) + \
                p.find('div', {"class":"ladder", "data-tooltip":"#best-team-%s" % (pLeague)}).find('a')['href']
        except:
            if VERBOSE: print p.title
            print "%s: Couldn't determine ladder URL from b.net ('%s'), skipping" % (pName, p.title.string)
            continue # go to next character
            
        if VERBOSE: print "ladderURL", ladderURL
        
        # Read ladder page and parse it for current points standings
        raw = urllib.urlopen(ladderURL.encode('utf-8')).read()
        p = BeautifulSoup(raw)
        try:
            division = p.find('',{'class' : 'data-title'}).find(text=re.compile('Division'))
        except:
            print "%s: Couldn't read division information from b.net ('%s'), skipping" % (pName, p.title.string)
            continue # go to next character
            
        level = re.match(r"(\w+\s){2}",p.title.string).group(0).strip()
        if VERBOSE: print division, level
        
        ltable = p.find('table', {'class' : 'data-table ladder-table'}).findAll('td')
        
        if VERBOSE > 1: print ltable
        
        ranks = [x.string for x in p.findAll('td', {"class":"align-center", "style":True, "data-tooltip":None})]
        
        nums = [r.match(y).group(1) for y in [x['href'] for x in p.findAll('a', {"data-tooltip":re.compile("#player")})]]
        names = [r.match(y).group(2) for y in [x['href'] for x in p.findAll('a', {"data-tooltip":re.compile("#player")})]]
        points = [x.string for x in p.findAll('td', {"class":"align-center", "style":None})][::2]
        
        players = zip(ranks, nums, names, points)  
        playerIndex = nums.index(pNo)
            
        # Get match history
        matchURL = charURL + "matches"
        raw = urllib.urlopen(matchURL).read()
        p = BeautifulSoup(raw)
        matchType = {"1":"solo", "2":"twos", "4":"fours"}[pLeague]
        pMatches = p.findAll('tr',{"class":"match-row %s" % (matchType)})
        if VERBOSE: print "len(pMatches)", len(pMatches)
        
        matchScores = [int(x.find('span',{"class":re.compile("text-")}).string) for x in pMatches]
        matchWins = len([x for x in matchScores if x > 0])
        if VERBOSE: print "matchScores", matchScores
            
        if VERBOSE > 1: print "%d players" % (len(players)), players
        if VERBOSE > 1: print "playerIndex", playerIndex
        if VERBOSE: print players[playerIndex]
        
        def pprint(v):
            """ print player points for index v, surround with [] if it is current player
            """
            if (v == playerIndex): print "[%s]" % players[v][3],
            else: print "%s" % players[v][3],
        
        print "%s: %s in %s, " % (players[playerIndex][2], players[playerIndex][0], level), 
        
        if len(pMatches) > 0:
            print "won %d of %d (%d%%, %d pts) %s " % (matchWins, len(matchScores), \
                (matchWins / float(len(matchScores))) * 100, \
                sum(matchScores), \
                ''.join(["." if x < 0 else "|" for x in matchScores])),
        else:
            print "No matches found",
            
                    
        pprint(0)
        if playerIndex > 4: print "...",
        for x in range(max(1, playerIndex - 3), min(playerIndex + 3, len(players))):
            pprint(x)
        print

if __name__ == '__main__':
    main()

