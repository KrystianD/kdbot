# coding=utf-8
from socket import *
from select import *
import re, time

class Nick:
	nick = ""
	op = False
	voice = False

class IRCClient(object):
	def __init__ (self, nick, channel, passwd=None):
		self.connectionState = 0 # 0 - nie połączony, 1 - połączony, 2 - na kanale, 3 - wyłączenie, 4 - wyłączony
		self.joinState = 0
		self.data = ""
		self.sock = None
		self.nickList = []
		self.nick = nick
		self.channel = channel
		self.passwd = passwd
		self.lastTarget = None
		self.lastSender = None
		self.lastPing = -1

	def Connect (self):
		self.sock = socket (AF_INET, SOCK_STREAM)

		try:
			self.sock.connect (('chat.freenode.net', 6667))
			self.lastPing = time.time ()
			self.connectionState = 1
			self.joinState = 0
			self.data = ""
			self.nickList = []

			self.SendServerMessage ("USER "+self.nick+" 8 * :"+self.nick)
			self.SendServerMessage ("NICK "+self.nick)
		except:			
			return
	
	def Disconnect (self):
		self.connectionState = 3
		self.SendServerMessage ("QUIT :It's not a bug! [It's a feature]")
		
	def ProcessMessage (self, msg):
		self.OnServerMessage (msg)
		
		self.lastPing = time.time ()
		# Polaczenie
		res = re.match ("^([^ ]+) :(.+)$", msg)
		# PING
		if res:
			cmd = res.group (1)
			if cmd == "PING":
				self.lastPing = time.time ()
				self.SendServerMessage ("PONG")
		
		res = re.match ("^:([^ ]+) ([0-9]+) "+self.nick+" (.+)$", msg)
		# Wiadomosci serwerowe
		if res:
			code = int(res.group (2))
			msg = res.group (3)
			if code == 4:
				self.connectionState = 2
				self.OnConnected ()
				if self.passwd is not None:
					self.SendServerMessage ("PRIVMSG NickServ :id " + self.passwd)
			elif code == 353:
				# Sprawdzenie czy lista nickow
				res2 = re.match ("^[@=] #"+self.channel+" :(.+)$", msg)
				if res2:
					#print "Nicki ok"
					# Pobranie listy nickow i utworzenie obiektow
					list = res2.group (1)
					nickList = list.split (" ")
					self.nickList = []
					for nick in nickList:
						senderObj = Nick()
						if nick[0] == "@":
							senderObj.nick = nick[1:]
							senderObj.op = True
						elif nick[0] == "+":
							senderObj.nick = nick[1:]
							senderObj.voice = True
						else:
							senderObj.nick = nick
						self.nickList.append (senderObj);
			
			elif code == 433:
				if "Nickname is already in use." in msg:
					print "Nick in use"
		
		# Wiadomosci do bota
		res = re.match ("^:([^!]+)!([^ ]+) (.+)$", msg)
		if res:
			senderNick = res.group (1)
			senderObj = self.GetUserByNick (res.group (1))
			host = res.group (2)
			msg = res.group (3)			
			
			res2 = re.match ("^([A-Z]+) (.+)$", msg)
			if res2:
				cmd = res2.group (1)
				cmdVal = res2.group (2)
				
				# PART
				if cmd == "PART":
					self.RequestNickList ()
					self.OnUserLeave (senderNick, "")
					
				# JOIN
				elif cmd == "JOIN":
					self.RequestNickList ()					
					res3 = re.match ("^:?#(.+)$", cmdVal)
					if res3:
						channel = res3.group (1)
						if senderNick == self.nick:
							self.joinState = 2
							self.OnJoined ()
						else:
							self.OnUserJoined (senderNick)
					
				# QUIT
				# QUIT :Quit: Leaving.
				elif cmd == "QUIT":
					if senderNick == self.nick:
						if self.connectionState == 3:
							self.joinState = 0
							self.connectionState = 4
						else:
							self.joinState = 0
							self.connectionState = 0
					else:
						self.RequestNickList ()					
						res3 = re.match ("^:(.+)$", cmdVal)
						if res3:
							quitMsg = res3.group (1)
							self.OnUserLeave (senderNick, quitMsg)
				
				# NICK
				elif cmd == "NICK":
					self.RequestNickList ()
					res3 = re.match ("^:(.+)$", cmdVal)
					if res3:
						newNick = res3.group (1)
						if senderNick == self.nick:
							self.nick = newNick
							print "CHANGED"
							
				# MODE
				elif cmd == "MODE":
					self.RequestNickList ()
				
				# PRIVMSG
				elif cmd == "PRIVMSG":
					self.lastSender = senderNick
					# Wiadomosc publiczna
					res3 = re.match ("^#([^ ]+) :(.+)$", cmdVal)
					if res3:
						channel = res3.group (1)
						message = res3.group (2)
						res4 = re.match ("\x01ACTION (.*)\x01", message)
						if res4 is not None:
							print "Me: " + res4.group (1)
						else:
							self.lastTarget = "#"+channel
							self.OnPublicMessage (channel, senderNick, message)
					else:
						res3 = re.match ("^([^ ]+) :(.+)$", cmdVal)
						if res3:
							target = res3.group (1)
							message = res3.group (2)
							self.lastTarget = senderNick
							self.OnPrivateMessage (target, message)				
					
				# KICK
				elif cmd == "KICK":
					res3 = re.match ("^#([^ ]+) ([^ ]+) :(.+)$", cmdVal)
					if res3:
						channel = res3.group (1)
						whoIsKicked = res3.group (2)
						why = res3.group (3)
						
						if whoIsKicked == self.nick:
							self.joinState = 0
							self.OnKick (senderObj, why)
						else:
							self.RequestNickList ()
							self.OnUserKicked (senderNick, whoIsKicked, why)

	def Do (self):
		if self.connectionState == 0:
			self.Connect ()
			return
			
		if time.time () - self.lastPing > 10 * 60:
			self.connectionState = 0
			self.joinState = 0
			return
			
		if self.connectionState == 2:
			if self.joinState == 0:
				self.SendServerMessage ("JOIN #"+self.channel)
				self.joinState = 1
				return
		
		
		test = [self.sock]
		try:
			ready_read, r1, r2 = select (test, [], [], 0.1)
		except:
			return
		if self.sock in ready_read:
			newData = self.sock.recv (100)
			if len (newData) == 0:
				self.joinState = 0
				self.connectionState = 0
				return
			self.data += newData
		
		idx = self.data.find ("\n")
		if idx != -1:
			self.ProcessMessage (self.data[:idx - 1].decode ("utf-8", "ignore"))
			self.data = self.data[idx + 1:]
	
	def SendServerMessage (self, msg):
		msg = msg.replace ("\n", " ")
		if len(msg) == 0: return
		if not self.OnBeforeSendServerMessage (msg):
			return
		self.sock.send (msg.encode ("utf-8")+"\r\n")
		self.OnSendServerMessage (msg)
	def RequestNickList (self):
		self.SendServerMessage ("NAMES #"+self.channel)
	
	# Handlery
	def OnConnected (self): pass
	def OnJoined (self): pass
	def OnKick (self, who, why): pass
	def OnUserJoined (self, who): pass
	def OnUserLeave (self, who, why): pass
	def OnUserKicked (self, whoKicked, who, why): pass
	def OnServerMessage (self, message): pass
	def OnBeforeSendServerMessage (self, message): return True
	def OnSendServerMessage (self, message): pass
	def OnPublicMessage (self, channel, senderObj, message): pass
	def OnPrivateMessage (self, senderObj, message): pass
	
	# Akcesory
	def GetNickList (self): return self.nickList
	def GetNick (self): return self.nick
	def GetUserByNick (self, nick):
		for nickObj in self.nickList:
			if nickObj.nick == nick:
				return nickObj
		return None
	def GetLastSender (self): return self.lastSender
	def GetLastSenderObj (self): return self.GetUserByNick (self.lastSender)
	
	# Komendy
	def SendChannelMessage (self, channel, msg):
		if len(msg) == 0: return
		if isinstance (msg, str):
			msg = unicode(msg)
		self.SendServerMessage ("PRIVMSG #"+self.channel+" :"+msg)
		self.OnPublicMessage (self.channel, self.nick, msg)
	def Reply (self, msg):
		if isinstance (msg, str):
			msg = unicode(msg)
		self.SendServerMessage ("PRIVMSG "+self.lastTarget+" :"+msg)
		if self.lastTarget[0] == "#":
			self.OnPublicMessage (self.channel[1:], self.nick, msg)
	def ChangeNick (self, nick):		
		self.SendServerMessage ("NICK "+nick)
	def Kick (self, channel, nick, comment=""):
		if len(comment) > 0:
			self.SendServerMessage ("KICK #"+channel+" "+nick+" :"+comment)
		else:
			self.SendServerMessage ("KICK #"+channel+" "+nick)
