# coding=utf-8
import re, time
import IRCClient
import ext
import utils, plugin
import logger, datetime, glob, imp, os, hashlib, sys, traceback, select, threading, readline, Queue, signal
execfile('config.py')

log = logger.Logger()
log.AddHandler(logger.ConsoleHandler())

class IRCBot(IRCClient.IRCClient):
	onChannel = False
	isRunning = True
	pluginManager = None
	mute = False
	signalBeingProceed = None
	
	def __init__(self, host, port, nick, channel, passwd=None):
		super(IRCBot, self).__init__(host, port, nick, channel, passwd)
		self.pluginManager = plugin.PluginManager()
		self.buf = ""
		self.commands = Queue.Queue()
		
	def reloadPlugins(self):
		self.pluginManager.reload()
	
	def handleSignal(self, signal, *args):
		if self.signalBeingProceed is not None: return
		for plugin in self.pluginManager.commands:
			if plugin["type"] == 2 and plugin["signal"] == signal:		
				self.signalBeingProceed = signal		
				try:
					plugin["func"](self, *args)
				except Exception as inst:
					log.LogWarn("Plugin handler {0} error: {1}".format(signal, inst))
					traceback.print_exc(file=sys.stdout)
				self.signalBeingProceed = None
	
	def onConnected(self):
		print "con!"
	def onJoined(self):
		self.onChannel = True
		print "join!"
	def onKick(self, who, why):
		self.onChannel = False		
	def onUserJoined(self, who):
		self.handleSignal("user_join", who)
		self.appendToIRCLog(u"--- {sender} entered the room".format(sender=who))
	def onUserLeave(self, who, why):
		self.handleSignal("user_leave", who, why)
		info = u""
		if len(why) > 0:
			info = u"(quit: {why})".format(why=why)
		self.appendToIRCLog(u"--- {sender} left the room".format(sender=who, info=info))
	def onUserKicked(self, whoKicked, who, why):
		#self.onChannel = False
		info = u""
		if len(why) > 0:
			info = u"({why})".format(why=why)
		self.appendToIRCLog(u"--- {who} left the room (Kicked by {whoKicked}{info})".format(who=who, whoKicked=whoKicked, info=info))
		
	def onServerMessage(self, message):
		log.LogInfo("--> " + message)
		pass
	def onSendServerMessage(self, message):
		log.LogInfo("<-- " + message)
		pass
	
	def onPublicMessage(self, channel, sender, message):
		self.appendToIRCLog(u"<{0}> {1}".format(sender, message))
		
		self.handleSignal("message_public", sender, message)
		
		if sender == self.getNick(): return
		
		managed = False
		for plugin in self.pluginManager.commands:
			if plugin["type"] == 1:
				res = re.match(plugin["regex"], message)
				if res:
					plugin["func"](self, res)
					managed = True
					break
		
		if not managed:
			cmd = None
			argsStr = None
			prompt = ""
			
			res = re.match("^([!\.])([a-zA-Z0-9]+)$", message)
			if res:
				prompt = res.group(1)
				cmd = res.group(2)
				argsStr = ""
			else:
				
				res = re.match("^([!\.])([a-zA-Z0-9]+) (.*)$", message)
				if res:
					prompt = res.group(1)
					cmd = res.group(2)
					argsStr = res.group(3)
					
			if cmd:
				for plugin in self.pluginManager.commands:
					if plugin["type"] == 0 and plugin["prompt"] == prompt and plugin["name"] == cmd:
						managed = True
						args = utils.ParseArgs(argsStr, plugin["argsCnt"])
						if plugin["argsCnt"] <= 0 or args:
							try:
								plugin["func"](self, args)
							except Exception as inst:
								log.LogWarn("Plugin {0} error: {1}".format(plugin["name"], inst))
								traceback.print_exc(file=sys.stdout)
						else:
							self.Reply(self.pluginManager.getUsage(plugin))
		if not managed:
			if cmd is not None:
				self.handleSignal("unknown_command", sender, prompt, cmd, argsStr)
			else:
				res = re.match("^([!\.])(.+)$", message)
				if res:
					prompt = res.group(1)
					text = res.group(2)
					self.handleSignal("unknown_message", sender, prompt, text)
			managed = True
	
	def onPrivateMessage(self, sender, message):
		if hashlib.md5(message.encode("utf-8")).hexdigest() == "11973b068362eb2e581f0de41b1e50f7":
			self.pluginManager.Reload()
		elif hashlib.md5(message.encode("utf-8")).hexdigest() == "1240835963712cdc4c5bcfbafc4764cb":
			self.Disconnect()
	
	def run(self):
		while self.connectionState != 4:
			if self.onChannel:
				for plugin in self.pluginManager.commands:
					if plugin["type"] == 3 and time.time() - plugin["lastDo"] > plugin["interval"] / 1000:
						print plugin
						try:
							plugin["func"](self)
						except Exception as inst:
							log.LogWarn("Plugin {0} error: {1}".format(plugin["name"], inst))
							traceback.print_exc(file=sys.stdout)
						plugin["lastDo"] = time.time()
			else:
				print "not on cha"
			
			self.process()

			time.sleep(0.05)
			
			# try:
				# cmd = self.commands.get_nowait()
				# try:
					# self.doCLICommand(cmd)
				# except Exception as inst:
					# traceback.print_exc(file=sys.stdout)
				# self.commands.task_done()
			# except Queue.Empty:
				# pass
			
	def appendToIRCLog(self, msg):
		self.handleSignal("log_line", msg)
		dateStr = datetime.datetime.today().strftime("%Y-%m-%d")
		file = open(logs_dir + "/" + dateStr + ".log", "ab")
		timeStr = datetime.datetime.now().strftime("%H:%M:%S")
		msg = "[{0}] {1}\r\n".format(timeStr, msg.encode("utf-8"))
		file.write(msg)
		file.close()
	
	def appendCLICommand(self, cmd):
		self.commands.put(cmd)
	
	def doCLICommand(self, cmd):
		if cmd == "quit":
			exit(0)
			
		p = cmd.split(" ", 1)
		cmd = p[0]
		args = []
		if len(p) > 1:
			args = utils.ParseArgs(p[1], -1)
		
		if cmd == "msg" and len(args) >= 1:
			self.sendServerMessage(args[0])
			
		if cmd == "kick" and len(args) >= 3:
			self.kick(args[0], args[1], args[2])
		
		if cmd == "whois" and len(args) >= 1:
			self.sendServerMessage("WHOIS "+args[0])

class CLI(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client
	
	def run(self):
		readline.parse_and_bind("")
		while True:
			try:
				cmd = raw_input("> ")
				self.client.appendCLICommand(cmd.strip())
				if cmd == "quit":
					break
			except:
				pass

# signal.signal(signal.SIGINT, signal.SIG_IGN)
#signal.signal(signal.SIGTERM, signal.SIG_IGN)

client = IRCBot("sendak.freenode.net", 6667, irc_nick, irc_channel)
ext.pm = client.pluginManager
client.reloadPlugins()

# c = CLI(client)
# c.start()

client.run()
