# coding=utf-8
import glob, os, logger, imp, json

log = logger.Logger()

class PluginManager:
	commands = []
	data = {}
	
	def reload(self):
		self.commands = []
		self.data = {}
		for filepath in glob.glob("plugins/*.py"):
			try:
				f = open(filepath, "rb")
				name = os.path.splitext(filepath)
				name = os.path.basename(name[0])
				print name, filepath
				m = imp.load_module(name, f, filepath,('.py', 'U', 1))
				f.close()
			except Exception as inst:
				log.LogWarn("Unable to load {0} error: {1}".format(filepath, inst))
		print "Reloaded"

	def getData(self, name, default=None):
		path = "plugins_data/" + name + ".txt"
		
		if name in self.data:
			return self.data[name]
		elif os.path.exists(path):			
			file = open(path, "r")
			data = json.load(file)
			file.close()
			self.data[name] = data
		else:
			self.data[name] = default
		
		return self.data[name]
			
	def saveData(self, name, data):
		path = "plugins_data/" + name + ".txt"
		
		self.data[name] = data
		
		file = open(path, "wb")
		json.dump(data, file)
		file.close()
		
	def getUsage(self, plugin):
		if "usage" in plugin:
			return "usage: " + plugin["usage"]
		
		res = plugin["prompt"] + plugin["name"]
		if plugin["argsCnt"] == -1:
			res += " arg0 arg1 arg2..."
		elif plugin["argsCnt"] > 0:
			for i in xrange(0, plugin["argsCnt"]):
				res += " arg" + str(i)
	
		return "usage: " + res
