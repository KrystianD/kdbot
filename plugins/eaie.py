# coding=utf-8
from ext import *
import os, urllib2, urllib, re, json
import utils

#@timed ("eaie", 30000)
def c (ircbot):
	data = pm.GetData ("eaie", [])
	
	cnt = urllib2.urlopen ("http://www.eaie.agh.edu.pl/studia,informacje-dla-studentow.html").read ()

	entries = re.findall ("<a href = \"(.*?)\">(.*?)</a> - <em>(.*?)</em>", cnt, re.DOTALL)
	for entry in entries:
		url = entry[0].strip ().replace ("&amp;", "&")
		title = unicode (entry[1].strip (), "utf-8")
		date = entry[2].strip ()
		
		if not url in data:
			
			shortUrl = utils.GetShortLink ("http://www.eaie.agh.edu.pl/" + url)
				
			ircbot.SendChannelMessage ("stosowana", u"EAIiE: {0} - {1}".format (title, shortUrl))
			
			data.append (url)
	
	pm.SaveData ("eaie", data)
