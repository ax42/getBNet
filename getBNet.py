#!/opt/local/bin/python
# coding=utf-8
# vim:et:sts:sw=4:sts=4
# Last modified: 2012 May 02

""" Module Docstring
Fetch SC2 character information from battle.net.
Shows position, win rate, wins and losses, and points.
Modify the 'defaultProfiles' array for the profiles you want to look up if no arguments are given.

BUG: nonrandom Multiplayer still crashes the script (due to multiple player names)
"""

# profile: Name, Number, League type (1,2,3,4)
defaultProfiles = [["Frozen", "2492514", "1", "eu"], 
                   ["Pain", "2874785", "1", "eu"],
                   ]

import sys
import argparse

import urllib, urlparse
import re

from BeautifulSoup import BeautifulSoup

def main():
    DEBUG = 0

    ap = argparse.ArgumentParser(description="Fetch SC2 character information from battle.net")
    ap.add_argument('-v','--verbose', default=0,
        help="Verbose output, add more v's for more verbosity", action="count")
    ap.add_argument('-c', '--character', help="Name BNet# League eu/na", nargs=4, action="append", default=None)
    ap.add_argument('-f', '--find', help='Specify a default profile to display', action="append", default=None)

    args = ap.parse_args()
    if DEBUG: print "args", args
    DEBUG = args.verbose

    if args.character: profiles = args.character
    elif args.find: 
        profiles = [x for x in defaultProfiles if (x[0] in args.find)]
        if profiles == []: 
            print "None of the character(s) %s are in the default profile list, exiting." % args.find
            sys.exit(1)
    else: profiles = defaultProfiles

    # regex for ladder page
    r = re.compile(r"/sc2/en/profile/(\d+)/\d/(\S+)/")
    
    for curPlayer in profiles:
        #First find the league page
        charURL = "http://%s.battle.net/sc2/en/profile/%s/1/%s/" % (curPlayer[3], curPlayer[1], curPlayer[0])
        if DEBUG: print charURL
    
        # Open profile page, figure out ladder URL
        raw = urllib.urlopen(charURL).read()
        if DEBUG > 2: print raw
        p = BeautifulSoup(raw)
        ladderURL = "http://%s.battle.net" % (curPlayer[3]) + \
            p.find('div', {"class":"ladder", "data-tooltip":"#best-team-%s" % (curPlayer[2])}).find('a')['href']
        if DEBUG: print ladderURL
        
        # Read ladder page and parse it for current points standings
        raw = urllib.urlopen(ladderURL.encode('utf-8')).read()
        p = BeautifulSoup(raw)
        division = p.find('',{'class' : 'data-title'}).find(text=re.compile('Division'))
        level = re.match(r"(\w+\s){2}",p.title.string).group(0).strip()
        if DEBUG: print division, level
        
        ltable = p.find('table', {'class' : 'data-table ladder-table'}).findAll('td')
        
        if DEBUG > 1: print ltable
        
        ranks = [x.string for x in p.findAll('td', {"class":"align-center", "style":True, "data-tooltip":None})]
        
        nums = [r.match(y).group(1) for y in [x['href'] for x in p.findAll('a', {"data-tooltip":re.compile("#player")})]]
        names = [r.match(y).group(2) for y in [x['href'] for x in p.findAll('a', {"data-tooltip":re.compile("#player")})]]
        points = [x.string for x in p.findAll('td', {"class":"align-center", "style":None})][::2]
        
        players = zip(ranks, nums, names, points)  
        playerIndex = nums.index(curPlayer[1])
            
            
        # Get match history
        matchURL = charURL + "matches"
        raw = urllib.urlopen(matchURL).read()
        p = BeautifulSoup(raw)
        matchType = {"1":"solo", "2":"twos", "4":"fours"}[curPlayer[2]]
        pMatches = p.findAll('tr',{"class":"match-row %s" % (matchType)})
        if DEBUG: print "pMatches", len(pMatches)
        
        matchScores = [int(x.find('span',{"class":re.compile("text-")}).string) for x in pMatches]
        matchWins = len([x for x in matchScores if x > 0])
        if DEBUG: print matchScores
            
        if DEBUG > 1: print "%d players" % (len(players)), players
        if DEBUG > 1: print "playerIndex", playerIndex
        if DEBUG: print players[playerIndex]
        
        def pprint(v):
            """ print player points for index v, surround with [] if it is current player
            """
            if (v == playerIndex): print "[%s]" % players[v][3],
            else: print "%s" % players[v][3],
        
        print "%s: %s in %s, won %d of %d (%d%%, %d pts) %s " % \
            (players[playerIndex][2], players[playerIndex][0], level, \
            matchWins, len(matchScores), (matchWins / float(len(matchScores))) * 100, \
            sum(matchScores), \
            ''.join(["." if x < 0 else "|" for x in matchScores])),
                    
        pprint(0)
        if playerIndex > 4: print "...",
        for x in range(max(1, playerIndex - 3), min(playerIndex + 3, len(players))):
            pprint(x)
        print

if __name__ == '__main__':
    main()

