# coding=utf-8
from ext import *
import os, urllib2, urllib, re, json, cookielib
import utils
execfile ('config.py')

@command ("follow", 1)
def c (ircbot, args):
	link = args[0]
	
	m = re.match ("^http://(www.)?forum\.stosowana\.pl/viewtopic\.php\?f=\d+&t=\d+", link)
	if m is None: return
	
	link = m.group (0)
	
	data = pm.GetData ("follows", [[], []])
	for item in data[0]:
		if item["link"] == link:
			ircbot.Reply ("exists!")
			return
	if len(data[0]) == 4:
		ircbot.Reply ("too many!")
		return;
	data[0].append ({ "link": link, "first": True, "title": "--- unknown ---" })
	pm.SaveData ("follows", data)

	ircbot.Reply ("ok")
	
@command ("follows", 0)
def c (ircbot, args):
	data = pm.GetData ("follows", [[], []])
	str = []
	for i in xrange (0, len(data[0])):
		print type(data[0][0]["title"])
		str.append (u"{0}: {1}".format (i, data[0][i]["title"]))
	ircbot.Reply (u" ||| ".join (str))

@command ("unfollow", 1)
def c (ircbot, args):
	data = pm.GetData ("follows", [[], []])
	try:
		idx = int(args[0])
	except:
		return
	if idx < 0 or idx >= len(data[0]):
		return
	del data[0][idx]
	
	pm.SaveData ("follows", data)
	ircbot.Reply ("ok")
	
@timed ("eaiefollow", 60000)
def c (ircbot):
	print stos_user
	data = pm.GetData ("follows", [[], []])

	cj = cookielib.LWPCookieJar ("followercookie.txt")
	opener = urllib2.build_opener (urllib2.HTTPCookieProcessor (cj))

	if os.path.exists ("followercookie.txt"):
		cj.load ()
	resp = opener.open ("http://www.forum.stosowana.pl/index.php", None, 20)
	cnt = resp.read ();

	if cnt.find ("Zaloguj") != -1:
		print "Logowanie..."
		login_data = urllib.urlencode ({ "username": stos_user, "password": stos_pass, "autologin": "0", "login": "Zaloguj" })
		resp = opener.open ("http://www.forum.stosowana.pl/ucp.php?mode=login", login_data, 20)

	cj.save ()

	for linkData in data[0]:
		link = linkData["link"]
		link = link + "&st=0&sk=t&sd=a&start=99999"
		resp = opener.open (link, None, 20)
		cnt = resp.read ();
		
		m = re.search ("<title>Forum dyskusyjne studentów IS EAIiE AGH &bull; Zobacz wątek - (.*?)</title>", cnt)
		if m:
			linkData["title"] = m.group (1).decode ("utf-8")
		
		idx = 0
		while True:
			m = re.search ("<a name=\"(p\d+)\"></a>", cnt[idx:])
			if m is None: break
			idx = idx + m.end ()
			
			id = m.group (1)
			
			m = re.search ("<b class=\"postauthor\"[^>]*>(.*?)</b>", cnt[idx:], re.S)
			if m is None: break
			idx = idx + m.end ()
			
			author = m.group (1).decode ("utf-8")
			author = re.sub ("<[^>]+>", "", author)
			author = author.strip ()
						
			destLink = link + "#" + id
			if destLink not in data[1]:
				if not linkData["first"]:
					shortUrl = utils.GetShortLink (destLink)
					ircbot.SendChannelMessage ("#stosowana", u"Nowy post: #{0}# @{2}@ --- {1}".format (linkData["title"], shortUrl, author))
				
				data[1].append (destLink)
		
		linkData["first"] = False
			
	pm.SaveData ("follows", data)
