# coding=utf-8
from ext import *
import datetime, re, time, select, random, os, json, time, urllib2
from subprocess import *
import utils

@command("help", -1)
def c(ircbot, args):
	if args:
		for plugin in pm.commands:
			if plugin["type"] == 0 and plugin["name"] == args[0]:
				if "desc" in plugin:
					ircbot.reply("*" + plugin["name"] + "*: " + plugin["desc"])
				else:
					ircbot.reply("*" + plugin["name"] + "*: no description")
				return
	
	str = []	
	for plugin in pm.commands:
		if plugin["type"] == 0:
			str.append(plugin["prompt"] + plugin["name"])
	str = ", ".join(str)

	ircbot.reply(str)

@command("mute", 1)
def c(ircbot, args):
	if not ircbot.getLastSender().op:
		return
	
	if args[0] == "1":
		ircbot.mute = True
		ircbot.reply("muted")
	elif args[0] == "0":
		ircbot.mute = False
		ircbot.reply("unmuted")
		
@command("g", 1)
@desc("gugiel")
@usage("!g fraza")
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply("http://google.pl/search?q="+args[0].replace(" ", "+"))

@command("args", 2)
@usage("!args num arg0 arg1...")
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply(str(utils.ParseArgs(args[1], int(args[0]))))
	
@command("paste", 0)
@desc("2 pasty")
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply("http://pastebin.com http://pastebin.pl")
	
@command("data", 0)
@desc("data?")
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply(str(datetime.datetime.now()))
	
@command("rand", 0)
@desc(u"Zwraca losową liczbę z zakresu 1-6")
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply("4")

lastNick = None
lastNick2 = None
lastDMessage = ""

@command("makefun", 0)
def c(ircbot, args):
	global lastDMessage
	lastDMessage = ""
	
@handler("message_public")
def c(ircbot, sender, message):
	global lastNick, lastNick2, lastDMessage
	lastNick2 = lastNick
	lastNick = sender
	
	if ircbot.mute: return
	if sender == "kdbot":
		return
	nofun = False
	for c in message:
		if c != '.':
			nofun = True
		
	if not nofun:
		if len(message) != len(lastDMessage) + 1:
			ircbot.reply("fail")
		else:
			lastDMessage = message

@command("reverse", 1)
def c(ircbot, args):
	ircbot.reply(args[0][::-1])
	
@command("slap", 0)
def c(ircbot, args):
	if ircbot.mute: return
	global lastNick2
	if lastNick2 != None:
		msg = "slaps " + lastNick2
		ircbot.sendChannelMessage("#hackerspace-krk", "\x01ACTION {0}\x01".format(msg))

@command("board", 0)
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply("http://cosketch.com")

last = -1
@command("last", 0)
@desc("Time elapsed since previous call")
def c(ircbot, args):
	global last
	if ircbot.mute: return
	if last != -1:
		ircbot.reply(str(time.time() - last))
	last = time.time()

@command("say", 1)
def c(ircbot, args):
	if ircbot.mute: return
	ircbot.reply(ircbot.getLastSender().nick + " forced me to say: " + args[0])

@command("lisp", 0)
def c(ircbot, args):
	s = ""
	ob = 0
	for i in xrange(50):
		c = random.choice("()")
		s += c
		if c == "(":
			ob = ob + 1
		if c == ")":
			ob = ob - 1
			if ob < 0:
				s = "(" + s
				ob = ob + 1
	s = s + ")" * ob
	ircbot.reply(s)
