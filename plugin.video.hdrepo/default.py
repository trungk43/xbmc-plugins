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

HTTP_DESKTOP_UA = {
		'Host':'www.fshare.vn',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language': 'en_UK',
		'Referer':'https://www.fshare.vn/login.php',
		'Connection':'keep-alive',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'
}

SEARCH_URL='http://www.google.com/custom?hl=en&q=site:fshare.vn/%s+%s&num=%s&start=%s&as_qdr=%s'
MEDIA_EXT=['m2ts','aif','iff','m3u','m4a','mid','mp3','mpa','ra','wav','wma','3g2','3gp','asf','asx','avi','flv','mov','mp4','mpg','mkv','m4v','rm','swf','vob','wmv','bin','cue','dmg','iso','mdf','toast','vcd']
FSLINK='http://fslink.us'
searchList=[]

def _makeCookieHeader(cookie):
			cookieHeader = ""
			for value in cookie.values():
					cookieHeader += "%s=%s; " % (value.key, value.value)
			return cookieHeader

headers=HTTP_DESKTOP_UA

#cache.delete('cookie')

def login():
	return doLogin()

def doLogin():

	cookie = Cookie.SimpleCookie()
	#method = urlfetch.POST
	
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
		follow_redirects = False)

	cookie.load(response.headers.get('set-cookie', ''))
	headers['Cookie'] = _makeCookieHeader(cookie)
	
	if headers['Cookie'].find('-1')>0:
		xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Login failed. You must input correct FShare username/pass in Add-on settings', '15')).encode("utf-8"))	 
		return False
	else:
		# xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Login successful', '15')).encode("utf-8"))	 
		return headers['Cookie']
	
def make_request(url, headers=None):
				headers2 = {
						'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'
				}
				try:
						req = urllib2.Request(url,headers=headers2)
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
				add_dir('Search', '', 16, icon, query, type, 0)
				add_dir('Search folders', '', 1, icon, query, type, 0)
				add_dir('Search files', '', 9, icon, query, type, 0)
				add_dir('Top 250', "http://www.imdb.com/chart/top?languages=en", 6, icon)
				add_dir('imdb', '', 11, icon, query, type, 0)
				add_dir('Add-on settings', '', 10, icon, query, type, 0)

def imdb_cat():
				add_dir('TV series', "http://www.imdb.com/search/title?num_votes=5000,&sort=user_rating,desc&title_type=tv_series&ref_=nb_tv_3_srs", 6, icon)
				add_dir('Top 250', "http://www.imdb.com/chart/top", 6, icon)
				add_dir('Action', "http://www.imdb.com/search/title?genres=action&sort=moviemeter,asc", 6, icon)
				add_dir('Adventure', "http://www.imdb.com/search/title?genres=adventure&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Animation', "http://www.imdb.com/search/title?genres=animation&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Biography', "http://www.imdb.com/search/title?genres=biography&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Comedy', "http://www.imdb.com/search/title?genres=comedy&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Crime', "http://www.imdb.com/search/title?genres=crime&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Documentary', "http://www.imdb.com/search/title?genres=documentary&sort=moviemeter,asc", 6, icon)
				add_dir('Drama', "http://www.imdb.com/search/title?genres=drama&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Family', "http://www.imdb.com/search/title?genres=family&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Fantasy', "http://www.imdb.com/search/title?genres=fantasy&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Film-Noir', "http://www.imdb.com/search/title?genres=film_noir&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('History', "http://www.imdb.com/search/title?genres=history&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Music', "http://www.imdb.com/search/title?genres=music&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Musical', "http://www.imdb.com/search/title?genres=musical&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Mystery', "http://www.imdb.com/search/title?genres=mystery&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Romance', "http://www.imdb.com/search/title?genres=romance&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Sci-Fi', "http://www.imdb.com/search/title?genres=sci-fi&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Short', "http://www.imdb.com/search/title?genres=short&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Sport', "http://www.imdb.com/search/title?genres=sport&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Thriller', "http://www.imdb.com/search/title?genres=thriller&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('War', "http://www.imdb.com/search/title?genres=war&title_type=feature&sort=moviemeter,asc", 6, icon)
				add_dir('Western', "http://www.imdb.com/search/title?genres=western&title_type=feature&sort=moviemeter,asc", 6, icon)
		
		
def searchMenu(url, query = '', type='folder', page=0):
	add_dir('New Search', url, 2, icon, query, type, 0)
	add_dir('Clear Search', url, 3, icon, query, type, 0)

def clearSearch():
	cache.set('searchList','')

def clearCache():
	cache.delete('http%')
	
def search(url, query = '', type='folder', page=0):

	if query is None or query=='':
		query = common.getUserInput('Search', '') 
		if query is None:
			return
	
	url=SEARCH_URL % (type,query.replace(' ', '+'),__settings__.getSetting('search_num'),str(int(__settings__.getSetting('search_num'))*page),'all')
	soup = BeautifulSoup(str(make_request(url)), convertEntities=BeautifulSoup.HTML_ENTITIES)		
	results=soup.findAll('div', {'class': 'g'})
	for folder in results:
		a=folder.find('a')
		href=a['href']
		if '/folder/' in href:
			name=a.text.encode("utf-8").replace('	',' ')
			add_dir(name, href, 5, icon)
		else:
			name=a.text.encode("utf-8").replace('	',' ')
			thumb = ''
			date = ''
			duration = 0
			desc = ''
			if name.find('Fshare - Dich vu chia se')==0:
				span=folder.find('span', {'class':'s'})
				str2=span.text
				if str2.find(' tin:')>=0:
					name=str2[str2.find(' tin:')+5:str2.find('Dung l')-2]
				else:
					name=str2[0:str2.find('Dung l')-2]
		
			if name.find('- Fshare - Dich')>0:
				name=name[:name.find('- Fshare - Dich')]
#			if (name is not None) and (len(name)>3) and (name[-3:] in MEDIA_EXT): 
			add_link(date, name.strip(), duration, href, thumb, desc)

	results=soup.findAll('div', {'id': 'nn'})
	if len(results)>0:
		add_dir('Next page >>', url, 2, icon, query, type, page+1)
	
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
	if '/file/' in href:
		soup = BeautifulSoup(make_request(href), convertEntities=BeautifulSoup.HTML_ENTITIES)
		name = soup.find('title').text
		name = name.replace('[Fshare] ', '')
		results=soup.findAll('div', {'style': 'width: 330px;'})
		if len(results)>0:
			results = results[0].findAll('p')
			name = name + ' (' + results[1].text[11:] + ')'

	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Duration": duration})
	liz.setProperty('IsPlayable', 'true')
	if email != '' and freeAccount == 'true':
		liz.addContextMenuItems([('Send download link',"XBMC.RunPlugin(%s?mode=%s&url=%s) "%(sys.argv[0],13,href))])
		
	liz.addContextMenuItems([('Add to your library',"XBMC.RunPlugin(%s?mode=%s&url=%s&query=%s) "%(sys.argv[0],15,href,name)),('Find similar movies',"XBMC.Container.Update(%s?mode=%s&url=%s&query=%s) "%(sys.argv[0],16,href,name))])
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)


def add_dir(name,url,mode,iconimage,query='',type='folder',page=0, thumbnailImage=''):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&query="+str(query)+"&type="+str(type)+"&page="+str(page)#+"&name="+urllib.quote_plus(name)
	ok=True
	if '/folder/' in url:
		soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
		results=soup.findAll('li', {'class': 'w_80pc'})
		if len(results)<1:
			return ok
		name = soup.find('title').text + ' (' + str(len(results)) + ')'
		name = name.replace(' --', '')
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name} )
	liz.setProperty('Fanart_Image', thumbnailImage) 
	if '/folder/' in url:
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

#http://www.fshare.vn/folder/T3C031J6NT
def fshare_get_video_list(url, title=None):
				soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
				#items = soup('li', {'class' : 'w_80pc'})
				items = soup.findAll('li', {'class' : 'w_80pc'})
				#items = soup.find('ul')
				video_list = []
				if (title is not None) and len(items)>5:
						add_dir(title, url, 5, '')
						return
				for i in items:
						href = i.a['href']
						spans = i('span')
						span = i.find('span',{'class':'__cf_email__'})
						#print span['data-cfemail']
						if span is None:
							name = spans[0].text
							size = spans[1].text
						else:
							str3=''
							str2=span.get('data-cfemail')
							r=int(str2[0:2], 16)
							ran=len(str2)/2
							for num in range(1,ran):
								str3=str3+chr( int(str2[num*2:num*2+2], 16)^r)
							start = spans[0].text.find("[")-1 #str3
							end = spans[0].text.rfind("]")+1 #str3
							name = spans[0].text[0:start]+spans[0].text[end:]
							size = spans[2].text
						if name is None:
							name='Unknown'
						thumb = ''
						date = ''
						duration = 0
						desc = ''
						if (name is not None) and (len(name)>3) and ((name[-3:] in MEDIA_EXT) or (name[-4:] in MEDIA_EXT)): 
								add_link(date, name+ '	(' + size + ')', duration, href, thumb, desc)

def fslink_get_video_categories(url):
				soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
				items = soup.findAll('a')

				for item in items:
						if (item['href'] is not None) and (item['href'].startswith('/title') and len(item.text)>1):
							try:
								add_dir(item.text, '', 2, '', item.text, 'folder', 0)
							except:
								pass
						if (item['href'] is not None) and (item.text.startswith('Next')):
							try:
								add_dir(item.text, 'http://www.imdb.com' + item['href'], 6, '')
							except:
								pass

				return
		
#http://fslink.us/category/phim-2/phim-le/				
def fslink_get_video_list(url):
				soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
				items = soup.findAll('h3', {'class' : 'entry-title'})

				for item in items:
					#print item
					#print item.a
					#print item.nextSibling().img('src')
					add_dir(item.a.text.encode("utf-8").replace('	',' '), item.a['href'], 8, icon)
				
				items = soup.find('div', {'class' : 'wp-pagenavi'})

				for item in items.findAll('a'):
						try:
							add_dir(item.string, item['href'], 7, icon)
						except:
							pass				

#http://fslink.us/2013/02/04/tro-ve-qua-khu-timeline-2003/				
def fslink_get_video(url):
				soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
				items = soup.findAll('a')

				for item in items:
						try:
							if item['href'].find('fshare.vn/folder')>0:
								add_dir(item.text, item['href'], 5, icon)
							if item['href'].find('fshare.vn/file')>0:
								thumb = ''
								date = ''
								duration = None
								desc = ''
								add_link(date, item.text, duration, item['href'], thumb, desc)
						except:
							pass
				
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
		filename = name
		
		k = filename.rfind("(")
		k = filename.rfind(".", 0, k)
		filename = filename[:k] + '.strm'
		
		target = open (library_folder + '/' + clearstring(filename), 'w')
		target.write('plugin://plugin.video.hdrepo/?mode=4&url=' + id)
		target.close()
		return
		
	if '/folder/' in url:
		data = {'provider': 'fshare_folder', 'param': url, 'start': 0}
		data = urllib.urlencode(data)
		result = json.load(urllib.urlopen('http://feed.hdrepo.com/v1/feed.php', data))
		
		library_folder = library_folder + '/' + clearstring(name)
		os.makedirs(library_folder)		
		
		for item in result:
			url = item['title']
			id = item['param']

			k = url.rfind("/")
			filename = url[k+1:]
			
			k = filename.rfind("(")
			k = filename.rfind(".", 0, k)
			filename = filename[:k] + '.strm'
			
			target = open (library_folder + '/' + clearstring(filename), 'w')
			target.write('plugin://plugin.video.hdrepo/?mode=4&url=' + id)
			target.close()
		return
		
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "type: "+str(type)
print "page: "+str(page)
print "query: "+str(query)

if mode==None:
	#if not login():
	#	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	#else:		
	get_categories()

elif mode==1:
	 search(url, '', type, page)

elif mode==2:
	 search(url, query, type, page)

elif mode==3:
		clearSearch()

elif mode==4:
		resolve_url(url)
elif mode==5:
		fshare_get_video_list(url)
elif mode==6:
		fslink_get_video_categories(url)
elif mode==7:
		fslink_get_video_list(url)
elif mode==8:
		fslink_get_video(url)
elif mode==9:
	 search(url, '', 'file', page)
elif mode==10:
	 __settings__.openSettings()
elif mode==11:
	imdb_cat()	 
elif mode==15:
	addlib(url, query)
elif mode==16:
	 search(url, '', '', page)
	
xbmcplugin.endOfDirectory(int(sys.argv[1]))