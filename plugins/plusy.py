# coding=utf-8
from ext import *
import os

filePath = "a.txt"

def LoadData ():
	data = []
	if os.path.exists (filePath):
		file = open (filePath, "r")
		for line in file.readlines ():
			line2 = line.strip ()
			if len(line2) == 0: continue
			parts = line2.split (",")
			data.append ([parts[0], int(parts[1]), int(parts[2])])
		file.close ()
	return data
def SaveData (data):
	file = open (filePath, "wb")
	for record in data:
		file.write ("{0},{1},{2}\n".format (record[0], record[1], record[2]))
	file.close ()

@command_regex ("^([^ +]{1,})\+\+")
def c (ircbot, match):
	nick = match.group (1)	
	userObj = ircbot.GetUserByNick (nick)
	print nick, userObj

	if userObj and ircbot.GetLastSenderObj ():
		if ircbot.GetLastSender () != nick:
			data = LoadData ()
			done = False
			for rec in data:
				if rec[0] == nick:
					rec[1] = rec[1] + 1
					done = True
					break
			if not done:
				data.append ([nick,1,0])
			SaveData (data)
		else:
			ircbot.Reply ("sure.")

@command_regex ("^([^ -]{1,})\-\-")
def c (ircbot, match):
	ircbot.Reply ("no hablo")
	# nick = match.group (1)	
	# userObj = ircbot.GetUserByNick (nick)

	# if userObj and ircbot.GetLastSenderObj () and ircbot.GetLastSender () != nick:
		# if not ircbot.GetLastSenderObj ().op:
			# ircbot.Reply ("not this way !! - become a god!")
			# return
		# data = LoadData ()
		# done = False
		# for rec in data:
			# if rec[0] == nick:
				# rec[1] = rec[1] - 1
				# done = True
				# break
		# if not done:
			# data.append ([nick,-1,0])
		# SaveData (data)
		# ircbot.Reply ("ye!!")
		
@command ("warn", 1)
def c (ircbot, args):
	nick = args[0]
	userObj = ircbot.GetUserByNick (nick)
	if userObj:
		data = LoadData ()
		done = False
		for rec in data:
			if rec[0] == nick:
				rec[2] = rec[2] + 1
				done = True
				break
		if not done:
			data.append ([nick,0,1])
		SaveData (data)
		ircbot.Reply ("i see you, "+nick+"..")

# @command ("kajtekzero", 0)
# def c (ircbot, args):
	# data = LoadData ()
	# for rec in data:
		# if rec[0] == "Kajtek" and rec[1] > 0:
			# rec[1] = 0
			# break
	# SaveData (data)
	# ircbot.Reply ("tak")
	
@command ("plusy", 0)
def c (ircbot, args):
	data = LoadData ()
	lines = []
	for rec in sorted (data, key=lambda val: val[1], reverse=True):
		if rec[1] != 0:
			nick = rec[0]
			mid = int(len(nick) / 2)
			nick = nick[0:mid] + u"\u200b" + nick[mid:]
			lines.append (nick+" = "+str(rec[1]))
	ircbot.Reply (", ".join (lines))

@command ("warny", 0)
def c (ircbot, args):
	data = LoadData ()
	lines = []
	for rec in sorted (data, key=lambda val: val[2], reverse=True):
		if rec[2] != 0:
			nick = rec[0]
			mid = int(len(nick) / 2)
			nick = nick[0:mid] + u"\u200b" + nick[mid:]
			lines.append (nick+" = "+str(rec[2]))
	ircbot.Reply (", ".join (lines))
