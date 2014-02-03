# coding=utf-8
from ext import *
import os, json, datetime

@command("note", 2)
def c(ircbot, args):
	sender = ircbot.getLastSender()
	target = args[0]
	message = args[1]
	
	data = pm.getData("notes", [])
	data.append([sender, target, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
	pm.saveData("notes", data)
	
	message2 = message
	if len(message2) > 5:
		message2 = message2[:5] + "..."
	ircbot.reply(u"Note for {0}: {1} saved!".format(target, message2))
	
	print sender, target, message
	
@handler("message_public")
def c(ircbot, sender, message):
	if sender == "kdbot": return
	data = pm.getData("notes", [])
	newData = []
	for rec in data:
		if rec[1].startswith(sender) or sender.startswith(rec[1]):
			ircbot.reply(u"{0}->{1}: {2}(at {3})".format(rec[0], rec[1], rec[2], rec[3]))
		else:
			newData.append(rec)
	if len(data) != len(newData):
		pm.saveData("notes", newData)

@handler("user_join")
def c(ircbot, who):
	if who == "marchewa":
		ircbot.reply(u"marchewa: cycki!")

@handler("user_join")
def c(ircbot, who):
	sender = who
	data = pm.getData("notes", [])
	newData = []
	for rec in data:
		if rec[1].startswith(sender) or sender.startswith(rec[1]):
			ircbot.reply(u"{0}->{1}: {2}(at {3})".format(rec[0], rec[1], rec[2], rec[3]))
		else:
			newData.append(rec)
	if len(data) != len(newData):
		pm.saveData("notes", newData)
