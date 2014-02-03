# coding=utf-8
from ext import *
import datetime, re, time, select, random, os, json, time, urllib2
from subprocess import *
import utils
	
@command("rrs", 0)
def c(ircbot, args):
	global rr1, rr2
	
	#if rr1 != 0 and rr2 != 0:
	#	ircbot.reply(";> .. the last one first ;>")
	#	return
	
	rr2 = random.randint(2, 10)
	rr1 = random.randint(1, rr2 - 1)
	ircbot.reply("done!({0} .. {1})".format(rr1, rr2))
	
	#return
	
	#try:
	#	_rr1 = int(args[0])
	#	_rr2 = int(args[1])
	#except ValueError:
	#	ircbot.reply("fakaf!")
	#	return
	#if _rr1 > 10 or _rr2 > 10 or _rr1 < 1 or _rr2 < 1 or _rr1 > _rr2:
	#	ircbot.reply("fakaf!")
	#	return
	#rr1 = _rr1
	#rr2 = _rr2
	#ircbot.reply("done!")

rr1 = rr2 = 0
@command("rr", 0)
def c(ircbot, args):
	global rr1, rr2
	
	if rr1 == 0 or rr2 == 0:
		ircbot.reply("empty!")
		return
	
	if rr1 == rr2 or random.randint(1, rr2) <= rr1:
		rr1 = rr1 - 1
		rr2 = rr2 - 1
		ircbot.reply("chlip " + random.choice([":D", ":/", "/:|", ";p", "<3", "3<"]))
	else:
		rr2 = rr2 - 1
	ircbot.reply("...({0} .. {1})".format(rr1, rr2))
