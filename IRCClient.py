# coding=utf-8
from socket import *
from select import *
import re, time

class Nick:
	nick = ""
	op = False
	voice = False
	host = ""

DISCONNECTED = 0
CONNECTED = 1
ON_CHANNEL = 2
CLOSING = 3
CLOSED = 4

class IRCClient(object):
	def __init__(self, host, port, nick, channel, passwd=None):
		self.host = host
		self.port = port
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
		self.lastConnectTime = 0

	def connect(self):
		if time.time() - self.lastConnectTime < 2:
			return

		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.settimeout(30)

		try:
			print("connecting to {}:{}...".format(self.host, self.port))
			self.sock.connect((self.host, self.port))
			self.lastPing = time.time()
			self.connectionState = 1
			self.joinState = 0
			self.data = ""
			self.nickList = []

			self.sendServerMessage("USER "+self.nick+" 8 * :"+self.nick)
			self.sendServerMessage("NICK "+self.nick)
		except KeyboardInterrupt:
			raise
		except Exception as e:
			print("unable to connect: " + str(e))
			self.lastConnectTime = time.time()
			return
	
	def disconnect(self):
		self.connectionState = 3
		self.sendServerMessage("QUIT :It's not a bug! [It's a feature]")
		
	def processMessage(self, msg):
		self.onServerMessage(msg)
		
		self.lastPing = time.time()
		# Polaczenie
		res = re.match("^([^ ]+) :(.+)$", msg)
		# PING
		if res:
			cmd = res.group(1)
			if cmd == "PING":
				self.lastPing = time.time()
				self.sendServerMessage("PONG")
		
		res = re.match("^:([^ ]+) ([0-9]+) "+self.nick+" (.+)$", msg)
		# Wiadomosci serwerowe
		if res:
			code = int(res.group(2))
			msg = res.group(3)
			if code == 4:
				self.connectionState = 2
				self.onConnected()
				if self.passwd is not None:
					self.sendServerMessage("PRIVMSG NickServ :id " + self.passwd)
			elif code == 353:
				# Sprawdzenie czy lista nickow
				res2 = re.match("^. #"+self.channel+" :(.+)$", msg)
				if res2:
					#print "Nicki ok"
					# Pobranie listy nickow i utworzenie obiektow
					list = res2.group(1)
					nickList = list.split(" ")
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
						self.nickList.append(senderObj);
			
			elif code == 433:
				if "Nickname is already in use." in msg:
					print "Nick in use"
		
		# Wiadomosci do bota
		res = re.match("^:([^!]+)!([^ ]+) (.+)$", msg)
		if res:
			senderNick = res.group(1)
			senderObj = self.getUserByNick(res.group(1))
			if senderObj is not None: senderObj.host = res.group(2)
			msg = res.group(3)
			
			res2 = re.match("^([A-Z]+) (.+)$", msg)
			if res2:
				cmd = res2.group(1)
				cmdVal = res2.group(2)
				
				# PART
				if cmd == "PART":
					self.requestNickList()
					self.onUserLeave(senderNick, "")
					
				# JOIN
				elif cmd == "JOIN":
					self.requestNickList()					
					res3 = re.match("^:?#(.+)$", cmdVal)
					if res3:
						channel = res3.group(1)
						if senderNick == self.nick:
							self.joinState = 2
							self.onJoined()
						else:
							self.onUserJoined(senderNick)
					
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
						self.requestNickList()					
						res3 = re.match("^:(.+)$", cmdVal)
						if res3:
							quitMsg = res3.group(1)
							self.onUserLeave(senderNick, quitMsg)
				
				# NICK
				elif cmd == "NICK":
					self.requestNickList()
					res3 = re.match("^:(.+)$", cmdVal)
					if res3:
						newNick = res3.group(1)
						if senderNick == self.nick:
							self.nick = newNick
							print "CHANGED"
							
				# MODE
				elif cmd == "MODE":
					self.requestNickList()
				
				# PRIVMSG
				elif cmd == "PRIVMSG":
					self.lastSender = senderNick
					# Wiadomosc publiczna
					res3 = re.match("^#([^ ]+) :(.+)$", cmdVal)
					if res3:
						channel = res3.group(1)
						message = res3.group(2)
						res4 = re.match("\x01ACTION (.*)\x01", message)
						if res4 is not None:
							print "Me: " + res4.group(1)
						else:
							self.lastTarget = "#"+channel
							self.onPublicMessage(channel, senderNick, message)
					else:
						res3 = re.match("^([^ ]+) :(.+)$", cmdVal)
						if res3:
							target = res3.group(1)
							message = res3.group(2)
							self.lastTarget = senderNick
							self.onPrivateMessage(target, message)				
					
				# KICK
				elif cmd == "KICK":
					res3 = re.match("^#([^ ]+) ([^ ]+) :(.+)$", cmdVal)
					if res3:
						channel = res3.group(1)
						whoIsKicked = res3.group(2)
						why = res3.group(3)
						
						if whoIsKicked == self.nick:
							self.joinState = 0
							self.onKick(senderObj, why)
						else:
							self.requestNickList()
							self.onUserKicked(senderNick, whoIsKicked, why)

	def process(self):
		if self.connectionState == 0:
			self.connect()
			return
			
		if time.time() - self.lastPing > 10 * 60:
			self.connectionState = 0
			self.joinState = 0
			return
			
		if self.connectionState == 2:
			if self.joinState == 0:
				self.sendServerMessage("JOIN #"+self.channel)
				self.joinState = 1
				return
		
		test = [self.sock]
		try:
			ready_read, r1, r2 = select(test, [], [], 0.1)
		except KeyboardInterrupt:
			raise
		except Exception:
			return
		if self.sock in ready_read:
			try:
				newData = self.sock.recv(100)
			except KeyboardInterrupt:
				raise
			except:
				self.joinState = 0
				self.connectionState = 0
				return
			if len(newData) == 0:
				self.joinState = 0
				self.connectionState = 0
				return
			self.data += newData
		
		idx = self.data.find("\n")
		if idx != -1:
			self.processMessage(self.data[:idx - 1].decode("utf-8", "ignore"))
			self.data = self.data[idx + 1:]

	
	def sendServerMessage(self, msg):
		msg = msg.replace("\n", " ")
		if len(msg) == 0: return
		if not self.onBeforeSendServerMessage(msg):
			return
		self.sock.send(msg.encode("utf-8")+"\r\n")
		self.onSendServerMessage(msg)
	def requestNickList(self):
		self.sendServerMessage("NAMES #"+self.channel)
	
	# Handlery
	def onConnected(self): pass
	def onJoined(self): pass
	def onKick(self, who, why): pass
	def onUserJoined(self, who): pass
	def onUserLeave(self, who, why): pass
	def onUserKicked(self, whoKicked, who, why): pass
	def onServerMessage(self, message): pass
	def onBeforeSendServerMessage(self, message): return True
	def onSendServerMessage(self, message): pass
	def onPublicMessage(self, channel, senderObj, message): pass
	def onPrivateMessage(self, senderObj, message): pass
	
	# Akcesory
	def getNickList(self): return self.nickList
	def getNick(self): return self.nick
	def getUserByNick(self, nick):
		for nickObj in self.nickList:
			if nickObj.nick == nick:
				return nickObj
		return None
	def getLastSender(self): return self.lastSender
	def getLastSenderObj(self): return self.getUserByNick(self.lastSender)
	
	# Komendy
	def sendChannelMessage(self, channel, msg):
		if len(msg) == 0: return
		if isinstance(msg, str):
			msg = unicode(msg)
		self.sendServerMessage("PRIVMSG #"+self.channel+" :"+msg)
		self.onPublicMessage(self.channel, self.nick, msg)
	def reply(self, msg):
		if isinstance(msg, str):
			msg = unicode(msg)
		self.sendServerMessage("PRIVMSG "+self.lastTarget+" :"+msg)
		if self.lastTarget[0] == "#":
			self.onPublicMessage(self.channel[1:], self.nick, msg)
	def changeNick(self, nick):		
		self.sendServerMessage("NICK "+nick)
	def kick(self, channel, nick, comment=""):
		if len(comment) > 0:
			self.sendServerMessage("KICK #"+channel+" "+nick+" :"+comment)
		else:
			self.sendServerMessage("KICK #"+channel+" "+nick)
	def setBan(self, channel, mask):
			self.sendServerMessage("MODE #"+channel+" +b "+pattern)
	def unsetBan(self, channel, mask):
			self.sendServerMessage("MODE #"+channel+" -b "+pattern)
