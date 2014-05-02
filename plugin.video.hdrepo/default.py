import CommonFunctions as common
import urllib
import urllib2
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import urlfetch
import Cookie
from BeautifulSoup import BeautifulSoup

try:
	import json
except:
	import simplejson as json

__settings__ = xbmcaddon.Addon(id='plugin.video.hdrepo')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
saveSearch = 'false'
freeAccount = __settings__.getSetting('freeAccount')
email = __settings__.getSetting('email')

if saveSearch=='true':
	cache = StorageServer.StorageServer("fshare2")


HTTP_DESKTOP_UA = {
	'Host':'www.fshare.vn',
	'Accept-Encoding':'gzip, deflate',
	'Referer':'https://www.fshare.vn/login.php',
	'Connection':'keep-alive',
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'
}

searchList=[]
headers = HTTP_DESKTOP_UA

def _makeCookieHeader(cookie):
	cookieHeader = ""
	for value in cookie.values():
		cookieHeader += "%s=%s; " % (value.key, value.value)
	return cookieHeader

def doLogin():

	cookie = Cookie.SimpleCookie()
	
	form_fields = {
		"login_useremail": __settings__.getSetting('username'),
		"login_password": __settings__.getSetting('password'),
		"url_refe": "https://www.fshare.vn/index.php"
	}

	form_data = urllib.urlencode(form_fields)
	
	response = urlfetch.fetch(
		url = 'https://www.fshare.vn/login.php',
		method='POST',
		headers = headers,
		data=form_data,
		follow_redirects = False
	)

	cookie.load(response.headers.get('set-cookie', ''))
	headers['Cookie'] = _makeCookieHeader(cookie)
	
	if headers['Cookie'].find('-1')>0:
		xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Login failed. You must input correct FShare username/pass in Add-on settings', '15')).encode("utf-8"))	 
		return False
	else:
		return headers['Cookie']
	
def make_request(url):
	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'
	}
	try:
		req = urllib2.Request(url,headers=headers)
		f = urllib2.urlopen(req)
		body=f.read()
		return body
	except urllib2.URLError, e:
		print 'We failed to open "%s".' % url
		if hasattr(e, 'reason'):
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
		if hasattr(e, 'code'):
			print 'We failed with error code - %s.' % e.code


def get_categories():
	if saveSearch=='true':
		add_dir('Search', '', 1, icon, query, type, 0)
	else:
		add_dir('Search', url, 2, icon, '', 'folder', 0)
	
	add_dir('Apple iTunes', 'apple_root', 14, icon, '', 'folder', 0)
	hdrepo('root','')

	add_dir('Add-on settings', '', 10, icon, query, type, 0)

def hdrepo(provider, param, start=0):

	if provider=='search':
		param = common.getUserInput('Search', '') 
		param = param.replace(' ', '%20')

	data = {'provider': provider, 'param': param, 'start': start}
	data = urllib.urlencode(data)
	result = json.load(urllib.urlopen('http://feed.hdrepo.com/v1/feed.php', data))
	for item in result:
		if item['type'] == 'fshare_folder':
			#add_dir(item['title'], item['param'], 5, item['thumb'])
			add_dir(item['title'], item['provider'], 12, item['thumb'], item['param'])
		else:
			if item['type'] == 'fshare_file' and item['title'] is not None:
				add_link(item['date'], item['title'], item['duration'], item['param'], item['thumb'], item['desc'])
			else:
				if item['type'] == 'folder':
					try:
						if 'start' in item:
							add_dir(item['title'], item['provider'], 12, item['thumb'], item['param'], '', item['start'])
						else:
							add_dir(item['title'], item['provider'], 12, item['thumb'], item['param'])
					except:
						pass

def apple(provider, param, start=0):
	if provider=='apple_root':
		add_dir('Genre', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/genres.json', 'folder', 0)
		add_dir('Action and Adventure', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/action_and_adventure.json', 'folder', 0)
		add_dir('Comedy', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/comedy.json', 'folder', 0)
		add_dir('Family', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/family.json', 'folder', 0)
		add_dir('Fantasy', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/fantasy.json', 'folder', 0)
		add_dir('Foreign', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/foreign.json', 'folder', 0)
		add_dir('Horror', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/horror.json', 'folder', 0)
		add_dir('Musical', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/musical.json', 'folder', 0)
		add_dir('Romance', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/romance.json', 'folder', 0)
		add_dir('Science Fiction', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/science_fiction.json', 'folder', 0)
		add_dir('Thriller', 'apple', 14, icon, 'http://trailers.apple.com/itunes/us/json/thriller.json', 'folder', 0)

	if provider=='apple':
		result = json.load(urllib.urlopen(param))
		if not 'data' in result:
			movies = result;
		else:
			movies = result['data'];
		for item in movies:
			if item.get('location') is None:
				add_dir(item['title'], 'search4', 12, 'http://trailers.apple.com/' + item['poster'], item['title'])
			else:
				add_dir(item['title'], 'search4', 12, 'http://trailers.apple.com/' + item['poster'], item['title'], thumbnailImage = 'http://trailers.apple.com' + item.get('location') + 'images/background.jpg')
			#print 'http://trailers.apple.com/' + item['location'] + 'images/background.jpg';

						
def sendLink(url):
	data = {'email': email, 'url': url}
	data = urllib.urlencode(data)
	try:
		response = urllib.urlopen('http://feed.hdrepo.com/sendlink.php', data)
		result = json.load(response)
		xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Download link', result['message'], '5000')).encode("utf-8"))	 
	except:
		xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Download link', 'Server only accepts 1 request/minute', '5000')).encode("utf-8"))	 
		
def addlib(url, name):
	print 'URL' + url
	id = url
	library_folder = __settings__.getSetting('library_folder')
	if library_folder == "":
		xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Add to your library', 'You need to setup library folder in Add-on Setting', '5000')).encode("utf-8"))
		return

	if not os.path.exists(library_folder):
		os.makedirs(library_folder)		
		
	if '/file/' in url:
		headers['Cookie'] = doLogin()

		response = urlfetch.get(url,headers=headers, follow_redirects=False)
		if response.status==302 and response.headers['location'].find('logout.php')<0:
			url=response.headers['location']

			k = url.rfind("/")
			filename = url[k+1:]
			
			k = filename.rfind(".")
			filename = filename[:k] + '.strm'
			
			target = open (library_folder + '/' + filename, 'w')
			target.write('plugin://plugin.video.hdrepo/?mode=4&url=' + id)
			target.close()
			return
		
	if '/folder/' in url:
		data = {'provider': 'fshare_folder', 'param': url, 'start': 0}
		data = urllib.urlencode(data)
		result = json.load(urllib.urlopen('http://feed.hdrepo.com/v1/feed.php', data))
		
		library_folder = library_folder + '/' + name
		os.makedirs(library_folder)		
		
		for item in result:
			url = item['title']
			id = item['param']

			k = url.rfind("/")
			filename = url[k+1:]
			
			k = filename.rfind("(")
			k = filename.rfind(".", 0, k)
			filename = filename[:k] + '.strm'
			
			target = open (library_folder + '/' + filename, 'w')
			target.write('plugin://plugin.video.hdrepo/?mode=4&url=' + id)
			target.close()
		return
		
def searchMenu(url, query = '', type='folder', page=0):
	add_dir('New Search', url, 2, icon, query, type, 0)
	add_dir('Clear Search', url, 3, icon, query, type, 0)

	searchList=cache.get('searchList').split("\n")
	for item in searchList:
		add_dir(item, url, 2, icon, item, type, 0)

def clearSearch():
	cache.set('searchList','')

def clearCache():
	cache.delete('http%')
	
def search(url, query = '', type='folder', page=0):
	if query is None or query=='':
		query = common.getUserInput('Search', '') 

	if query is None:
		return
	
	if saveSearch=='true':
		searchList = cache.get('searchList').split("\n")
		if not query in searchList:
			searchList.append(query)
			cache.set('searchList','\n'.join(searchList))

	hdrepo('search4', query)

def resolve_url(url):
	if freeAccount == 'true':
		response = urlfetch.fetch("http://feed.hdrepo.com/fshare.php")
		if response.status == 200:
			headers['Cookie'] = response.content
		else:
			xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Server only accepts 1 request/minute', '5000')).encode("utf-8"))	 
			return
	else:
		headers['Cookie'] = doLogin()

	response = urlfetch.get(url,headers=headers, follow_redirects=False)
	if response.status==302 and response.headers['location'].find('logout.php')<0:
		url=response.headers['location']
		# logout
		if freeAccount == 'true':
			cookie = Cookie.SimpleCookie()
			cookie.load(response.headers.get('set-cookie', ''))
			headers['Cookie'] = _makeCookieHeader(cookie)
			urlfetch.get("https://www.fshare.vn/logout.php",headers=headers, follow_redirects=False)
	else:
		if response.status==200:
			soup = BeautifulSoup(str(response.content), convertEntities=BeautifulSoup.HTML_ENTITIES)		
			item = soup.find('form', {'name' : 'frm_download'})
			if item:
				url = item['action']
		else:
			xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Login failed. You must input correct FShare username/pass in Add-on settings', '5000')).encode("utf-8"))	 
			return
	
	item = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def add_link(date, name, duration, href, thumb, desc):
	description = date+'\n\n'+desc
	u=sys.argv[0]+"?url="+urllib.quote_plus(href)+"&mode=4"
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Duration": duration})
	liz.setProperty('IsPlayable', 'true')
	if email != '' and freeAccount == 'true':
		liz.addContextMenuItems([('Send download link',"XBMC.RunPlugin(%s?mode=%s&url=%s) "%(sys.argv[0],13,href))])
	liz.addContextMenuItems([('Add to your library',"XBMC.RunPlugin(%s?mode=%s&url=%s) "%(sys.argv[0],15,href))])
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def add_dir(name,url,mode,iconimage,query='',type='folder',page=0, thumbnailImage=''):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&query="+str(query)+"&type="+str(type)+"&page="+str(page)#+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name} )
	liz.setProperty('Fanart_Image', thumbnailImage) 
	if url == 'fshare_folder':
		liz.addContextMenuItems([('Add to your library',"XBMC.RunPlugin(%s?mode=%s&url=%s&query=%s) "%(sys.argv[0], 15, query, name))])
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok


def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]

	return param

params=get_params()

url=''
name=None
mode=None
query=None
type='folder'
page=0

try:
	type=urllib.unquote_plus(params["type"])
except:
	pass
try:
	page=int(urllib.unquote_plus(params["page"]))
except:
	pass
try:
	query=urllib.unquote_plus(params["query"])
except:
	pass
try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass

if mode==10:
	__settings__.openSettings()
	mode=None

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	
if mode==None:
	get_categories()

elif mode==1:
	searchMenu(url, '', type, page)
elif mode==2:
	 search(url, query, type, page)
elif mode==3:
	clearSearch()
elif mode==4:
	resolve_url(url)
elif mode==9:
	searchMenu(url, '', 'file', page)
elif mode==10:
	__settings__.openSettings()
elif mode==12:
	hdrepo(url, str(query), str(page))
elif mode==13:
	sendLink(url)
elif mode==14:
	apple(url, str(query), str(page))
elif mode==15:
	addlib(url, query)

xbmcplugin.endOfDirectory(int(sys.argv[1]))