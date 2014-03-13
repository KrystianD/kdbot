# coding=utf-8
from ext import *
import os, json, datetime, re
import utils

@command("note", 2)
@usage("!note nick message")
def c(ircbot, args):
	sender = ircbot.getLastSender().nick
	target = utils.nickBasename(args[0])
	message = args[1]
	
	data = pm.getData("notes", [])
	data.append([sender, target, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
	pm.saveData("notes", data)
	
	message2 = message
	if len(message2) > 5:
		message2 = message2[:5] + "..."
	ircbot.reply("Note for {0}: {1} saved!".format(utils.noHL(target), message2))
	
	print(sender, target, message)
	
@handler("message_public")
def c(ircbot, sender, message):
	if sender == "kdbot": return
	sender = utils.nickBasename(sender.lower())
	data = pm.getData("notes", [])
	newData = []
	for rec in data:
		recNick = rec[1].lower()
		if recNick.startswith(sender) or sender.startswith(recNick):
			ircbot.reply("{0}->{1}: {2} (at {3})".format(utils.noHL(rec[0]), rec[1], rec[2], rec[3]))
		else:
			newData.append(rec)
	if len(data) != len(newData):
		pm.saveData("notes", newData)

@handler("user_join")
def c(ircbot, who):
	sender = who
	sender = utils.nickBasename(sender.lower())
	data = pm.getData("notes", [])
	newData = []
	for rec in data:
		recNick = rec[1].lower()
		if recNick.startswith(sender) or sender.startswith(recNick):
			ircbot.reply("{0}->{1}: {2} (at {3})".format(utils.noHL(rec[0]), rec[1], rec[2], rec[3]))
		else:
			newData.append(rec)
	if len(data) != len(newData):
		pm.saveData("notes", newData)

@command("test", 1)
def c(ircbot, args):
	nick = utils.nickBasename(args[0])

	ircbot.reply(nick)
