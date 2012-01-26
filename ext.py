pm = None

def SetParam (f, param, value):
	global pm
	for cmd in pm.commands:
		if cmd["func"] == f:
			cmd[param] = value
			return
	pm.commands.append ({ 'func': f })
	SetParam (f, param, value)

def command (name, argsCnt):
	def command_make (f):
		SetParam (f, "type", 0)
		SetParam (f, "name", name)
		SetParam (f, "prompt", "!")
		SetParam (f, "argsCnt", argsCnt)
		return f
	return command_make
	
def command_regex (regex):
	def command_regex_make (f):
		SetParam (f, "type", 1)
		SetParam (f, "regex", regex)
		return f
	return command_regex_make
	
def handler (signal):
	def handler_make (f):
		SetParam (f, "type", 2)
		SetParam (f, "signal", signal)
		return f
	return handler_make
	
def timed (name, interval):
	def timer_make (f):
		SetParam (f, "type", 3)
		SetParam (f, "name", name)
		SetParam (f, "interval", interval)
		SetParam (f, "lastDo", -1)
		return f
	return timer_make
	
def desc (str):
	def func (f):
		SetParam (f, "desc", str)
		return f
	return func
	
def usage (str):
	def func (f):
		SetParam (f, "usage", str)
		return f
	return func
	
def prompt (str):
	def func (f):
		SetParam (f, "prompt", str)
		return f
	return func
