from RiotAPI import RiotAPI
from collections import OrderedDict
import time
import json
import sys

user_api_key = 'bfbf03bb-ce02-434d-a86e-beed8a3602c6' # insert api key here
global_mid_list = []
global_sid_list = []
api = RiotAPI(user_api_key)
mid_index = 0

def getFirstId(ingamename):
    resp = api.get_summoner_by_name(ingamename)[0]
    return resp[ingamename]['id']


def getRecentGames(summid):
    resp = api.get_matchlist_by_summid(summid)[0]
    return resp


def addMatchIdToData(mid_set):
    global global_mid_list
    for match in mid_set:
        if match['queue'] == 'TEAM_BUILDER_DRAFT_RANKED_5x5':
            global_mid_list.append(match['matchId'])
    global_mid_list = list(OrderedDict.fromkeys(global_mid_list))

def getMatchData(mid_index):
    match = api.get_match(global_mid_list[mid_index])[0]
    getSummId(match)
    return match

def getSummId(match):
    global global_sid_list
    for i in range(10):
        global_sid_list.append(match['participantIdentities'][i]['player']['summonerId'])
    global_sid_list = list(OrderedDict.fromkeys(global_sid_list))

def nameToData(ingamename):
    sid = getFirstId(ingamename)
    mid_set = getRecentGames(sid)['matches']
    addMatchIdToData(mid_set)
    return sid

def loop(write_file, sid):
    global mid_index
    try:
        while mid_index<len(global_mid_list):
            num=0
            match = getMatchData(mid_index)
            partId = 0
            teamId = 0
            partValue = ''
            teamValue = ''
            for partIdentities in match['participantIdentities']:
                if partIdentities['player']['summonerId'] == sid:
                    partId = partIdentities['participantId']
                    
##            while True:
##                if len(match['participants']) == 1:
##                    break
##                popped = False
##                if match['participants'][0]['participantId'] == partId:
##                    popped = True
##                if popped:
##                    del match['participants'][1]
##                else:
##                    del match['participants'][0]
            for part in match['participants']:
                if part['participantId'] == partId:
                    partValue = part
                    teamId = part['teamId']
            del match['participants'][:]
            match['participants'].append(partValue)

            for part in match['participantIdentities']:
                if part['participantId'] == partId:
                    partValue = part
            del match['participantIdentities'][:]
            match['participantIdentities'].append(partValue)

            for team in match['teams']:
                if team['teamId'] == teamId:
                    teamValue = team
            del match['teams'][:]
            match['teams'].append(teamValue)
            
            write_file.write(json.dumps(match))
            if mid_index==len(global_mid_list)-1:
                write_file.write('\n');
            else:
                write_file.write('\n^')
            mid_index += 1
        
    except KeyError:
        print("Key Error")
        time.sleep(15)
        mid_index +=1
        loop(write_file, sid)
        

def main(initial_mid_index=0):
    try:
        ingamename = sys.argv[1].lower()
        write_file = open(ingamename + '.txt', 'a') #output file
#        write_file.write('^')
        sid = nameToData(ingamename)
        loop(write_file, sid) #player
        
    
    except IndexError:
        print("Index Error; argument required")
    
    finally:
        write_file.close()
        print("done")

    
if __name__ == "__main__":
    main()