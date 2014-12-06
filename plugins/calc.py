# coding=utf-8
from ext import *
import datetime, re, time, select, random, os, json, time, urllib.request, urllib.error, urllib.parse
from subprocess import *
import utils

# @command("c", 1)
def c(ircbot, args):
	if ircbot.mute: return
	p = Popen(["/usr/bin/bc", "-l"], stdout=PIPE, stdin=PIPE, stderr=PIPE, bufsize=0)
	p.stdin.write((args[0] + "\n").encode("ascii"))
	p.stdin.close()
	out = ""
	err = ""

	startTime = time.time()
	lastRead = time.time()
	while time.time() - lastRead < 0.5 and time.time() - startTime < 1:
		p.poll()
		print ("ret:", p.returncode)
		
		q = select.select([p.stdout, p.stderr], [], [], 0.2)
		if p.stdout in q[0]:
			buf = p.stdout.read(100).decode("ascii")
			if len(buf) > 0:
				out += buf
				lastRead = time.time()
				print("out:", out)
			else:
				print("out stop")
				break
		if p.stderr in q[0]:
			buf = p.stderr.read(100).decode("ascii")
			if len(buf) > 0:
				err += buf
				lastRead = time.time()
				print("err:", err)
			else:
				print("err stop")
				break

	p.poll()
	print("Ret: ", p.returncode)
	if p.returncode == None and len(out) == 0:
		print("kill")
		res = "timeout!"		
		if len(err) > 0:
			res += " (err: {0})".format(err)
		p.kill()
	else:
		res = out
		if len(err) > 0:
			res = "!!! (err: {0})".format(err)
	
	if len(res) > 100:
		res = res[100:]
	ircbot.reply("> " + res.strip())
