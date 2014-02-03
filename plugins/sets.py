# coding=utf-8
from ext import *
import datetime, re, time, select, random, os, json, time
import utils

@command("cntset", 0)
def c(ircbot, args):
	sets = pm.getData("sets", {})
	ircbot.reply("cnt: " + str(len(sets)))

@command("set", 2)
def c(ircbot, args):
	sets = pm.getData("sets", {})
	
	"""
	for key in sets.keys():
		val = sets[key]
		if type(val) != type(dict()):
			sets[key] = { "value": val }
	print sets
	pm.saveData("sets", sets)
	"""
	
	if args[0] in sets and sets[args[0]]["value"][0] == "@":
		ircbot.reply("locked!")
		return
	sets[args[0]] = { "value": args[1].lstrip("@"), "user": ircbot.getLastSender(), "time": time.time() }
	pm.saveData("sets", sets)

@command("unset", 1)
def c(ircbot, args):
	if not ircbot.getLastSender().op:
		return
	
	sets = pm.getData("sets", {})
	if args[0] in sets:
		del sets[args[0]]
		pm.saveData("sets", sets)

@command("lock", 1)
def c(ircbot, args):
	sets = pm.getData("sets", {})
	if args[0] in sets and sets[args[0]]["value"][0] != "@":
		sets[args[0]]["value"] = "@" + sets[args[0]]["value"]
		ircbot.reply("done!")
		pm.saveData("sets", sets)

lastRandSetMinute = -1
lastRandSetCount = 0
@command("randset", 0)
def c(ircbot, args):
	if ircbot.mute: return
	global lastRandSetMinute, lastRandSetCount
	
	minute = int(time.time() / 60)
	if lastRandSetMinute != minute:
		lastRandSetCount = 0
		lastRandSetMinute = minute
	
	lastRandSetCount += 1
	if lastRandSetCount > 3:
		ircbot.reply(u"Only 3 randsets per minute! ;p")
		return
	
	sets = pm.getData("sets", {})
	key = random.choice(sets.keys())
	entry = sets[key]
	val = entry["value"]
	if val[0] == "@":
		val = val[1:]
	ircbot.reply(u"{key} - {val}".format(key=key, val=val))

@command("infoset", 1)
def c(ircbot, args):
	sets = pm.getData("sets", {})
	key = args[0]
	if key in sets:
		entry = sets[key]
		val = entry["value"]
		if val[0] == "@":
			val = val[1:]
		infoStr = u""
		if "user" in entry:
			infoStr += entry["user"]
		if "time" in entry:
			infoStr += u" at " + datetime.datetime.fromtimestamp(entry["time"]).strftime("%Y-%m-%d %H:%M:%S")
		if len(infoStr) == 0:
			infoStr = "no info :("
		ircbot.reply(infoStr)

@handler("unknown_command")
def c(ircbot, sender, prompt, cmd, argsStr):
	c123(ircbot, sender, prompt,(cmd + " " + argsStr).strip())
	
@handler("unknown_message")
def c123(ircbot, sender, prompt, text):
	if ircbot.mute: return
	if prompt != "!": return
	sets = pm.getData("sets", {})
	parts = text.split(' ', 1)
	text = parts[0]
	argsStr = ""
	if len(parts) == 2:
		argsStr = parts[1]
	if text in sets:
		r = sets[text]["value"]
		if r[0] == "@":
			r = r[1:]
		args = argsStr.strip()
		if len(args) > 0:
			r = r.replace("***", args)
		
		if text == "KD2":
			ircbot.kick("stosowana", sender, u"ha! tego się nie spodziewałeś!")

		ircbot.reply(r)
