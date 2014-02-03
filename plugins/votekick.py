# coding=utf-8
from ext import *
import datetime, re, time, select, random, os, json, time
from subprocess import *
import utils

voteKick = None

@command ("votekick", 1)
def c (ircbot, args):
	global voteKick
	if voteKick != None and time.time () - voteKick["time"] >= 60:
		voteKick = None
		
	sender = ircbot.getLastSender ()
			
	userObj = ircbot.getUserByNick (args[0])
	if userObj:
		if voteKick != None:
			if voteKick["target"] != sender:
				ircbot.Reply ("oh, damn :(")
				return
			if voteKick["target"] == sender:
				ircbot.Reply ("ofkoz.")
				return
		
		if userObj.nick == "kdbot":
			ircbot.Reply (u"a takiego wała!")
			return
		
		ircbot.Reply ("OK! let's try - everyone says y/n")
		
		nicks = ircbot.getNickList ()
		nicks2 = []
		for nick in nicks: nicks2.append (nick.nick)
		nicks2.remove (userObj.nick)
		if sender in nicks2: nicks2.remove (sender)
		if "kdbot" in nicks2: nicks2.remove ("kdbot")
		if "kdbot2" in nicks2: nicks2.remove ("kdbot2")
		
		voteKick = {
			"time": time.time (),
			"target": userObj.nick,
			"allowed": nicks2,
			"votesTotal": len(nicks2) + 1,
			"votesY": 1,
			"votesN": 0,
		}
		print voteKick
		#MODE #stosowana +b *!*@*

@handler ("message_public")
def c (ircbot, sender, message):
	global voteKick
	if voteKick != None and time.time () - voteKick["time"] >= 60:
		voteKick = None
	
	sender = ircbot.getLastSender ()
	if voteKick != None:
		if message == "y" or message == "n":			
			if sender in voteKick["allowed"]:
				if message == "y":
					voteKick["votesY"] += 1
					voteKick["allowed"].remove (sender)
					ircbot.Reply ("got it! ~~ {0}/{1}".format (voteKick["votesY"], voteKick["votesTotal"]))
				elif message == "n":
					voteKick["votesN"] += 1
					voteKick["allowed"].remove (sender)
					ircbot.Reply ("got it! ~~ {0}/{1}".format (voteKick["votesY"], voteKick["votesTotal"]))
			else:
				ircbot.Reply (sender + ": ...")
		
		if voteKick["votesY"] > voteKick["votesTotal"] / 2:
			ircbot.Kick ("hackerspace-krk", voteKick["target"], "sorry, that's democracy!")
			voteKick = None
		
		print voteKick
