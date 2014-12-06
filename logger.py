import datetime

ERROR = 1
WARNING = 2
INFO = 3
DEBUG = 4

class Logger:
	handlers = []
	
	def AddHandler (self, handler):
		self.handlers.append (handler)
	
	def Log (self, level, msg):
		for h in self.handlers:
			h.Log (level, msg)
		
	def LogError (self, msg): self.Log (ERROR, msg)
	def LogWarn (self, msg): self.Log (WARNING, msg)
	def LogWarning (self, msg): self.Log (WARNING, msg)
	def LogInfo (self, msg): self.Log (INFO, msg)
	def LogDebug (self, msg): self.Log (DEBUG, msg)

class LogHandler:
	def Log (self, level, message):
		pass

class ConsoleHandler:
	def Log (self, level, message):
		print((datetime.datetime.now ().strftime ("[%H:%M:%S] ") + message).encode("utf-8"))
