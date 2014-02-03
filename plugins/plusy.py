# coding=utf-8
from ext import *
import os

filePath = "a.txt"

@command_regex("^([^ +]{1,})\+\+")
def c(ircbot, match):
	nick = match.group(1)	
	user = ircbot.getUserByNick(nick)
	print(nick, user.nick, user.onChannel)
	if not user.onChannel:
		return

	if ircbot.getLastSender() != nick:
		data = pm.getData("plusy", [])
		done = False
		for rec in data:
			if rec[0] == nick:
				rec[1] = rec[1] + 1
				done = True
				break
		if not done:
			data.append([nick,1,0])
		pm.saveData("plusy", data)
	else:
		ircbot.reply("sure.")

@command_regex("^([^ -]{1,})\-\-")
def c(ircbot, match):
	ircbot.reply("no hablo")
		
@command("warn", 1)
def c(ircbot, args):
	nick = args[0]
	userObj = ircbot.getUserByNick(nick)
	if userObj:
		data = pm.getData("warny", [])
		done = False
		for rec in data:
			if rec[0] == nick:
				rec[2] = rec[2] + 1
				done = True
				break
		if not done:
			data.append([nick,0,1])
		pm.saveData("warny", data)
		ircbot.reply("i see you, "+nick+"..")

@command("plusy", 0)
def c(ircbot, args):
	data = pm.getData("plusy", [])
	lines = []
	for rec in sorted(data, key=lambda val: val[1], reverse=True):
		if rec[1] != 0:
			nick = rec[0]
			mid = int(len(nick) / 2)
			nick = nick[0:mid] + "\u200b" + nick[mid:]
			lines.append(nick+" = "+str(rec[1]))
	ircbot.reply(", ".join(lines))

@command("warny", 0)
def c(ircbot, args):
	data = pm.getData("warny", [])
	lines = []
	for rec in sorted(data, key=lambda val: val[2], reverse=True):
		if rec[2] != 0:
			nick = rec[0]
			mid = int(len(nick) / 2)
			nick = nick[0:mid] + "\u200b" + nick[mid:]
			lines.append(nick+" = "+str(rec[2]))
	ircbot.reply(", ".join(lines))
