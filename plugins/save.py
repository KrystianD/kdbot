# coding=utf-8
from ext import *
import os, datetime

lastLines = []
lastLinesNT = []

dataDir = "/home/krystiand/domains/hskrk/saves"

def appendLine(msg):
	global lastLines
	global lastLinesNT
	lastLines.append("[{0}] {1}".format(datetime.datetime.now().strftime("%H:%M:%S"), msg))
	lastLinesNT.append(msg)
	while len(lastLines) > 20: del lastLines[0]
	while len(lastLinesNT) > 20: del lastLinesNT[0]

@command("save", 0)
@desc("http://hskrk.krystiand.net/saves")
def c(ircbot, args):
	global lastLines
	sender = ircbot.getLastSender().nick
	i = 0
	while True:
		filePath = os.path.join(dataDir, "{0:04}.txt".format(i))
		i = i + 1
		if not os.path.exists(filePath):
			break
	file = open(filePath, "wb")
	file.write(sender + "\n")
	file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
	file.write("\n".join(lastLines).encode("utf-8"))
	file.close()	
	
	print(filePath)
	ircbot.reply("saved!")

@command("log", 0)
def c(ircbot, args):
	global lastLinesNT
	ircbot.reply(" | ".join(lastLinesNT[-5:]))

@handler("log_line")
def c(ircbot, msg):
	appendLine(msg)
