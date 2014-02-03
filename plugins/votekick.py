# coding=utf-8
from ext import *
import datetime, re, time, select, random, os, json, time
from subprocess import *
import utils

voteKick = None

@command("votekick", 1)
def c(ircbot, args):
	global voteKick
	if voteKick != None and time.time() - voteKick["time"] >= 60:
		voteKick = None
		
	sender = ircbot.getLastSender()
			
	user = ircbot.getUserByNick(args[0])
	if user:
		if voteKick != None:
			if voteKick["target"] != sender:
				ircbot.reply("oh, damn :(")
				return
			if voteKick["target"] == sender:
				ircbot.reply("ofkoz.")
				return
		
		if user.nick == ircbot.getNick():
			ircbot.reply(u"a takiego wała!")
			return
		
		ircbot.reply("OK! let's try - everyone says y/n")
		
		nicksList = []
		for nick in ircbot.getNickList(): nicksList.append(nick.nick)
		nicksList.remove(user.nick)
		if sender in nicksList: nicksList.remove(sender)
		if ircbot.getNick() in nicksList: nicksList.remove(ircbot.getNick())
		
		voteKick = {
			"time": time.time(),
			"target": user.nick,
			"allowed": nicksList,
			"votesTotal": len(nicksList) + 1,
			"votesY": 1,
			"votesN": 0,
		}
		print voteKick
		#MODE #stosowana +b *!*@*

@handler("message_public")
def c(ircbot, sender, message):
	global voteKick
	if voteKick != None and time.time() - voteKick["time"] >= 60:
		voteKick = None
	
	sender = ircbot.getLastSender().nick
	if voteKick != None:
		if message == "y" or message == "n":			
			if sender in voteKick["allowed"]:
				if message == "y":
					voteKick["votesY"] += 1
					voteKick["allowed"].remove(sender)
					ircbot.reply("got it! ~~ {0}/{1}".format(voteKick["votesY"], voteKick["votesTotal"]))
				elif message == "n":
					voteKick["votesN"] += 1
					voteKick["allowed"].remove(sender)
					ircbot.reply("got it! ~~ {0}/{1}".format(voteKick["votesY"], voteKick["votesTotal"]))
			else:
				ircbot.reply(sender + ": ...")
		
		if voteKick["votesY"] > voteKick["votesTotal"] / 2:
			ircbot.Kick(irc_channel, voteKick["target"], "sorry, that's democracy!")
			voteKick = None
		
		print voteKick
