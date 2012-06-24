# Early Era bot http://turntable.fm/early_era

from ttapi import Bot
from printnesteddictionary import print_dict
import re
import random
from time import localtime, strftime
import sys
import os
import unicodedata
import threading
import pickle

eebot_auth = 'auth+live+xxxxxxxx'
eebot_userid = '4fdcd2f9aaa5cd1e7900032d'

lsk_userid = '4e7c70bc4fe7d052ef034402'

ee_roomid = '4fae71e0aaa5cd57e50011e1'
speakeasy_id = '4e8a63d614169c39fb79b09a'

AUTH   = eebot_auth
USERID = eebot_userid
ROOM   = ee_roomid

eebot = Bot(AUTH,USERID,ROOM)
banlistDir = 'M:\\Python\\TT bot\\eebotbanlist.txt'
bl = open(banlistDir,'r')
banlist = pickle.load(bl)
bl.close()
print 'Banlist: %s' % str(banlist)
songban = ['nigger']
songId  = ''
DJid = ''
addedSong = False
waitForSong = False
currUserIds = []
currDjs = []
djOnCmd = False
botPl = []
songMetaData = {}

eeMods = [u'4e225bb9a3f75169a6005f50', u'4f489c83590ca22efa000d8d', u'4e0f5b93a3f751670a0553a6', u'4f36c9a2590ca21631001607', u'4f8b121feb35c1026300018d', u'4e3f5465a3f7512f10015692', u'4fdcd2f9aaa5cd1e7900032d', u'4e7c70bc4fe7d052ef034402'] # since 6/20

lameGenres = ['rap','hip','elect','trance','house','j pop','j-pop','dub','metal','indie','alt']
lameArtists = ['skrillex',"lil' wayne",'lil wayne','astley','excision','various musique','cynic','fioko','mac miller','daft','goulding','basshunter','lmfao','wale','blige','drake','cudi','rick ross','birdman','m.o.p.','tribe called quest','peanut butter wolf','medina green','rhymefest','rza','guru','termanology','mob','kanye','mos def','slum','fiasco','doom','fatlip','smoke room','2pac','backstreet','adele','snoop dog','yankovic','beatles','fifty cent','50 cent','diplo','quintino','sandro silva','maroon 5','maroon five','larry platt','fiona apple','candlebox','filthy children','omc','o.m.c.','digital underground','lonely island','ratatat','akon','flo rida','nil admirari','mickey avalon','warp brothers','the holdup','billy joel','kid sister','roger miller','rihanna','daughtry','little boots','dubstep kings','pleq','roy orbison','cover nation','steven price','stray cats','young mc','kings of convenience','lil b',"lil' b",'john lennon','onerepublic','j-dash','david guetta','messiah','kilo','john denver','n.w.a.','nwa','deadmau','death','pumpkin','beatle','aerosmith','atilla','matthew herbert','electric swing circus','parov stela','diablo swing orchestra','tape five','jamie berry','esla','rube & dusty','rube and dusty','cloudfactory','ecklektic','cherry poppin'+"'"+' daddies','voodoo','big phat band','c2c','remix','penis','poop','anal ',' anal','shit','fuck','tits mcgee','tom petty','electric','waka','toilet']

def speak(data):
    global banlist,songId,addedSong,voteScore,genre,album,artist,song,songId,djOnCmd,ROOM,ee_roomid
    name = data['name']
    userid = data['userid']
    text = data['text']
    if name[0]=='@':
        name = name[1:]
    if re.match('(ee bot |/)help',text.lower()):
        eebot.speak('@%s. The rules for this room are in the room description. Type /commands for bot commands. Please note that we take trolling and racism very seriously. If you troll or play a racist song, be prepared to be banned without warning.' % name)
    if re.match('/commands',text.lower()):
        eebot.speak('Current commands: "DJ on", "DJ off", "/skip", "/album", "/genre", "/bop" (room vote at or above 60%), "/lame" (vote < or = 45%), "/banlist" Mod commands: "EE Bot ban username", "EE Bot add song", "EE Bot unban username"')
    if re.match('((ee )?bot )?dj on',text.lower()):
        if ROOM == ee_roomid:
            djOnCmd = True
            eebot.addDj()
        else:
            eebot.speak('I can\'t DJ in this room!')
    if re.match('((ee )?bot )?dj off',text.lower()):
        eebot.remDj()
    if re.match('(ee bot |/)skip',text.lower()):
        eebot.stopSong()
    if re.match('/ban( )?list',text.lower()):
        nameBans = []
        for i in range(len(banlist)):
            nameBans.append(banlist[i]['name'])
        eebot.speak('Ban list: %s' % ', '.join(nameBans))
    if re.match('/album',text.lower()):
        if album != '':
            eebot.speak('This song appears to be from the album "%s".' % album)
        else:
            eebot.speak("The album name couldn't be identified.")
    if re.match('/genre',text.lower()):
        if genre != '':
            eebot.speak('This song is classified as %s.' % genre)
        else:
            eebot.speak("The genre couldn't be identified.")
    if re.match('(ee )?(bot )?/bop',text.lower()):
        if voteScore >= .6:
            eebot.vote('up')
        else:
            if userid in eeMods:
                eebot.vote('up')
            else:
                def modOrVotes(data):
                    if userid in data['room']['metadata']['moderator_id'] or userid == lsk_userid:
                        eebot.vote('up')
                eebot.roomInfo(False,modOrVotes)
    if re.match('(ee )?(bot )?/lame',text.lower()):
        if voteScore <= .45:
            eebot.vote('down')
        else:
            if userid in eeMods:
                eebot.vote('down')
            else:
                def modOrVotes(data):
                    if userid in data['room']['metadata']['moderator_id'] or userid == lsk_userid or data['room']['metadata']:
                        eebot.vote('down')
                eebot.roomInfo(False,modOrVotes)
    if text.lower() == 'ee bot add song':
        if ROOM == ee_roomid:
            def checkMod(data):
                if userid in data['room']['metadata']['moderator_id'] or userid == lsk_userid:
                    addSnag()
            eebot.roomInfo(False,checkMod)
        elif userid in eeMods:
            addSnag()
    if re.match('ee bot ban (.+)',text.lower()):
        def checkMod(data):
            if userid in data['room']['metadata']['moderator_id']:
                def getId(userdata):
                        if userdata['success']:
                            if userdata['userid'] in data['room']['metadata']['moderator_id']:
                                eebot.speak("I can't ban mods!")
                            else:
                                eebot.bootUser(userdata['userid'],'You have been banned by %s!' % name)
                                def getName(namedata):
                                    global banlistDir
                                    banlist.append({'userid':userdata['userid'],'name':namedata['name']})
                                    bl = open(banlistDir,'w')
                                    pickle.dump(banlist,bl)
                                    bl.close()
                                    print 'Wrote new banlist: %s' % str(banlist)
                                    eebot.speak('Banned %s!' % namedata['name'])
                                eebot.getProfile(userdata['userid'],getName)
                        else:
                            eebot.speak("I couldn't find the user!")
                eebot.getUserId(text[11:],getId)
        eebot.roomInfo(False,checkMod)
    if re.match('ee bot unban (.+)',text.lower()):
        def checkMod(data):
            if userid in data['room']['metadata']['moderator_id']:
                beginLen = len(banlist)
                for i in range(len(banlist)):
                    if banlist[i]['name'].lower()==text[13:].lower():
                        eebot.speak('Unbanned %s.' % banlist[i]['name'])
                        banlist.remove(banlist[i]) #remove that current value
                        global banlistDir
                        bl = open(banlistDir,'w')
                        pickle.dump(banlist,bl)
                        bl.close()
                        print 'Wrote new banlist: %s' % str(banlist)                        
                        break
                if beginLen-1 != len(banlist):
                    eebot.speak('Couldn\'t remove the user from the ban list.')
        eebot.roomInfo(False,checkMod)

def roomChanged(data):
    global currUserIds,currDjs,botPl
    eebot.modifyLaptop('mac')
    users = data['users']
    for i in range(len(users)):
        currUserIds.append(users[i]['userid'])
    currDjs = data['room']['metadata']['djs']
    def setPl(data):
        global botPl
        botPl = data['list']
        print 'Bot playlist set!'
    eebot.playlistAll(setPl)
    #if len(currDjs)==0:
    #    eebot.addDj()
    #if len(currDjs)==1:
    #    eebot.addDj()
    #    eebot.speak('Looks like you could use a friend!')
    newSong(data) #passing data to newSong function

def newSong(data):
    global banlist,songban,genre,album,artist,song,songId,addedSong,voteScore,DJid,ROOM,ee_roomid,songMetaData,lameGenres,lameArtists
    songData = data['room']['metadata']['current_song']
    DJid = songData['djid']
    DJname = songData['djname']
    artist = songData['metadata']['artist']
    song = songData['metadata']['song']
    genre = songData['metadata']['genre']
    album = songData['metadata']['album']
    songId = songData['_id']
    songMetaData = songData['metadata']
    print DJid, DJname
    voteScore = .5
    addedSong = False
    punished = False
    if addedSong and DJid == eebot_userid:
        eebot.stopSong()
    print 'Song id is %s' % songId
    for i in range(len(songban)):
        if songban[i].lower() in song.lower():
            eebot.bootUser(DJid,'No racist songs allowed! You have been banned from this room!')
            banlist.append({'userid':DJid,'name':DJname})
            punished = True
            break
    if (re.match('(.+)never (gonna|going to) give you up(.+)',song.lower()) or 'tits mcgee' in artist.lower()) and not(punished):
        alreadyvoted = True
        eebot.bootUser(DJid,'Haha very funny.')
    if not(punished):
        for i in range(len(lameGenres)):
            if lameGenres[i].lower() in genre.lower():
                eebot.remDj(DJid)
                eebot.speak('%s is not allowed!' % genre)
                punished = True
                break
    if not(punished):
        for i in range(len(lameArtists)):
            if lameArtists[i].lower() in artist.lower():
                eebot.remDj(DJid)
                eebot.speak('This kind of music is not allowed!')
                punished = True
                break
            
def endedSong(data):
    global addedSong,waitForSong,botPl,eebot_userid
    if waitForSong:
        eebot.speak("Looks like you two have it covered up there. I'll step down.") #waitForSong is so the bot doesn't step down in the middle of its song.
        eebot.remDj()        
        waitForSong=False
    if data['room']['metadata']['current_song']['djid']==eebot_userid:
        botPl.remove(botPl[0])
        botPl.append(data['room']['metadata']['current_song']['metadata'])

def userDereg(data):
    global currUserIds
    currUserIds.remove(data['user'][0]['userid'])
    if len(currUserIds) == 1:
        eebot.remDj()
    
def userReg(data):
    global banlist,currUserIds,ROOM,ee_roomid
    idBanList = []
    userid = data['user'][0]['userid']
    name = data['user'][0]['name']
    if not(data['user'][0]['userid']==eebot_userid): #This event happens before roomchanged so if this was left out, eebot would be in the userlist twice.
        currUserIds.append(data['user'][0]['userid'])
    for i in range(len(banlist)):
        idBanList.append(banlist[i]['userid'])
    if userid in idBanList:
        eebot.bootUser(userid,'Banned!')
    if ROOM == ee_roomid:
        eebot.pm('Hey there. Type EE Bot DJ on in the chat to ask me to DJ or /commands (also in the chat) for a list of my commands. Have fun!',userid)
        
def pmreply(data):
    global banlist,songId,ROOM,songId
    userid = data['senderid']
    message = data['text']

    if re.match('(ee )?(bot )?add song',message.lower()):
        if ROOM == ee_roomid:
            def checkMod(data):
                if userid in data['room']['metadata']['moderator_id'] or userid == lsk_userid:
                    addSnag()
            eebot.roomInfo(False,checkMod)
        elif userid in eeMods:
            addSnag()
    if re.match('info of (.+)',message.lower()):
        eebot.getProfile(message[8:],printReg)
    if re.match('(/)?mods',message.lower()):
        def replyMods(data):
            eebot.pm('%s mods: %s' % (len(str(data['room']['metadata']['moderator_id'])),str(data['room']['metadata']['moderator_id'])),userid) #len mods
        eebot.roomInfo(replyMods)
    if re.match('room data',message.lower()):
        eebot.getProfile(message[8:],printReg)
    if re.match('name of (.+)',message.lower()):
        if len(message)==32:
            def profName(data):
                if data['success']:
                    eebot.pm('The name of the user is %s.' % data['name'],userid)
                else:
                    eebot.pm('Error: %s' % data['err'],userid)
            eebot.getProfile(message[8:],profName)
        else:
            eebot.pm('That is an invalid userid.',userid)
            
    if userid == lsk_userid:
        if message.lower()=='snag':
            eebot.pm('Snag attempt...',lsk_userid)
            eebot.snag()
        if re.match('echo (.+)',message.lower()):
            eebot.pm(message[5:],lsk_userid)
        if re.match('/say (.+)',message.lower()): #Now this is cool. If I type /say and then something into the pm, the bot will say it in the chat.
            eebot.speak(message[5:])
        if message.lower() == 'ban list':
            eebot.pm(str(banlist),lsk_userid)
    
def updateVotes(data):
    global voteScore
    upVotes = data['room']['upvotes']
    dnVotes = data['room']['downvotes']
    listeners = data['room']['listeners']
    if listeners<2:
        listeners = 2
    voteScore = .5*(1+(upVotes-dnVotes)/(listeners-1))
        
def removedDj(data):
    global currDjs,ROOM,ee_roomid
    currDjs.remove(data['user'][0]['userid'])
    if len(currDjs)==1 and not(eebot_userid == data['user'][0]['userid'] or data.has_key('modid')): # If the user was escorted off or booed off, don't jump off of the DJ stand
        t = threading.Timer(1,eebot.remDj)
        t.start() # When the bot jumps right off after another user does, the bot's song starts playing so we give it a second to allow TT to "catch up".
    if len(currDjs)==1 and not(eebot_userid in currDjs) and not(eebot_userid == data['user'][0]['userid']) and ROOM == ee_roomid:
        eebot.addDj()
        eebot.speak("Looks like you could use a friend up there.")        
            
def addedDj(data):
    global currDjs,DJid,eebot_userid,waitForSong,djOnCmd,ROOM,ee_roomid
    currDjs.append(data['user'][0]['userid'])
    if len(currDjs)<=1 and not(eebot_userid in currDjs) and not(eebot_userid == data['user'][0]['userid']) and ROOM == ee_roomid:
        eebot.addDj()
        eebot.speak("Looks like you could use a friend up there.")
    if len(currDjs) >=3 and eebot_userid in currDjs and not(djOnCmd): # 3 because the bot will be considered a dj
        if DJid == eebot_userid:
            waitForSong = True
        else:
            eebot.speak("Looks like you two have it covered up there. I'll step down.")
            eebot.remDj()
    djOnCmd = False

def addSnag():
    print 'Add song attempt...'
    global addedSong,songId,botPl,songMetaData
    if addedSong:
        eebot.speak(u'Oh I JUST added this one. Good tune though!')
    else:
        alreadyInPl = False
        for i in range(len(botPl)):
            if songId==botPl[i]['_id']:
                alreadyInPl = True
                eebot.speak('I already have this song!')
                eebot.vote('up')
                break
        if not(alreadyInPl):
            addedSong = True
            eebot.playlistAdd(songId,len(botPl))
            botPl.append(songMetaData)
            eebot.speak('Added song...')
            eebot.vote('up')
            eebot.snag()
            #mtbtmr = threading.Timer(5,moveToBottom)
            #mtbtmr.start()
        
def moveToBottom():
    global botPl,songMetaData
    eebot.playlistReorder(0,len(botPl))
    botPl.remove(songMetaData)
    botPl.append(songMetaData)
    print 'Last song: ',botPl[len(botPl)-1]

def printReg(data):
    print data

eebot.on('add_dj',addedDj)
eebot.on('rem_dj',removedDj)
eebot.on('pmmed',pmreply)
eebot.on('endsong',endedSong)
eebot.on('registered',userReg)
eebot.on('deregistered',userDereg)
eebot.on('roomChanged',roomChanged)
eebot.on('speak',speak)
eebot.on('newsong',newSong)
eebot.on('update_votes',updateVotes)
eebot.start()