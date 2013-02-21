import CommonFunctions as common
import urllib
import urllib2
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import StorageServer
import urlfetch
import Cookie
#import subtitles
from BeautifulSoup import BeautifulSoup

__settings__ = xbmcaddon.Addon(id='plugin.video.4share')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
cache = StorageServer.StorageServer("my_4share", 1)

HTTP_DESKTOP_UA = {
    'Host':'www.fshare.vn',
    'Accept-Encoding':'gzip, deflate',
    'Referer':'https://www.fshare.vn/login.php',
    'Connection':'keep-alive',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
	'Content-Type': 'application/x-www-form-urlencoded'
}

SEARCH_URL='http://www.google.com/custom?hl=en&q=site:fshare.vn/%s+%s&num=%s&start=%s&as_qdr=%s'
MEDIA_EXT=['aif','iff','m3u','m4a','mid','mp3','mpa','ra','wav','wma','3g2','3gp','asf','asx','avi','flv','mov','mp4','mpg','mkv','m4v','rm','swf','vob','wmv','bin','cue','dmg','iso','mdf','toast','vcd']
FSLINK='http://phimnet.us'
searchList=[]

def _makeCookieHeader(cookie):
      cookieHeader = ""
      for value in cookie.values():
          cookieHeader += "%s=%s; " % (value.key, value.value)
      return cookieHeader

headers=HTTP_DESKTOP_UA

def login():

  if cache.get('cookie') is not None and cache.get('cookie')<>'':
    print 'Cache ' + cache.get('cookie')
    return True

  cookie = Cookie.SimpleCookie()
  
  form_fields = {
   "inputUserName": __settings__.getSetting('username'),
   "inputPassword": __settings__.getSetting('password')
  }

  form_data = urllib.urlencode(form_fields)

  response = urlfetch.fetch(
    url = 'http://up.4share.vn/?control=login',
	method='POST',
    headers = headers,
	data=form_data,
    follow_redirects = False)

  cookie.load(response.headers.get('set-cookie', ''))
  headers['Cookie'] = _makeCookieHeader(cookie)

  print 'Cache ' + headers['Cookie']
  cache.set('cookie',headers['Cookie'])
  print 'Cache ' + cache.get('cookie')
  if response.status_code<>302:
    xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Login failed. You must input correct FShare username/pass in Add-on settings', '15')).encode("utf-8"))   
    return False
  else:
    xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % ('Login', 'Login successful', '15')).encode("utf-8"))   
    return True
  
def make_request(url, headers=None):
        if headers is None:
            headers2 = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
                       'Referer' : 'http://www.google.com'}
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
        add_dir('phimnet.us', FSLINK+'/phim-anh.html', 6, icon)
        add_dir('Search', '', 1, icon, query, type, 0)
        add_dir('Search files', '', 9, icon, query, type, 0)
        add_dir('Clear cache', '', 10, icon, query, type, 0)

def searchMenu(url, query = '', type='folder', page=0):
  add_dir('New Search', url, 2, icon, query, type, 0)
  add_dir('Clear Search', url, 3, icon, query, type, 0)

  searchList=cache.get('searchList').split("\n")
  for item in searchList:
    add_dir(item, url, 2, icon, item, type, 0)

def clearSearch():
  cache.delete('searchList')

def clearCache():
  cache.delete('%')
  
def search(url, query = '', type='folder', page=0):

  if query is None or query=='':
    query = common.getUserInput('Search', '') 
    if query is None:
      return
  
    searchList=cache.get('searchList').split("\n")
    if not query in searchList:
      searchList.append(query)
      cache.set('searchList','\n'.join(searchList))
  
  url=SEARCH_URL % (type,query.replace(' ', '+'),__settings__.getSetting('search_num'),str(int(__settings__.getSetting('search_num'))*page),'all')
  soup = BeautifulSoup(str(make_request(url)), convertEntities=BeautifulSoup.HTML_ENTITIES)		
  results=soup.findAll('div', {'class': 'g'})
  if type=='folder':
    for folder in results:
      a=folder.find('a')
      name=a.text.encode("utf-8").replace('  ',' ')
      href=a['href']
      add_dir(name, href, 5, icon)
  else:
    for folder in results:
      a=folder.find('a')
      name=a.text.encode("utf-8").replace('  ',' ')
      href=a['href']
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
#      if (name is not None) and (len(name)>3) and (name[-3:] in MEDIA_EXT): 
      add_link(date, name.strip(), duration, href, thumb, desc)

	  
  add_dir('Page 1', url, 2, icon, query, type, 0)
  add_dir('Page 2', url, 2, icon, query, type, 1)
  add_dir('Page 3', url, 2, icon, query, type, 2)
  add_dir('Page 4', url, 2, icon, query, type, 3)
  add_dir('Page 5', url, 2, icon, query, type, 4)
  
  
def resolve_url(url):
  headers['Cookie'] = cache.get('cookie')
  response = urlfetch.fetch(url,headers=headers, follow_redirects=True)
  soup = BeautifulSoup(response.content, convertEntities=BeautifulSoup.HTML_ENTITIES)
  for item in soup.findAll('a'):
    if item['href'].find('?i=')>0:
      url=item['href']
  print url
  item = xbmcgui.ListItem(path=url)
  xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
  #subtitles.Main().PlayWaitSubtitles(common.args.url)

def add_link(date, name, duration, href, thumb, desc):
        description = date+'\n\n'+desc
        u=sys.argv[0]+"?url="+urllib.quote_plus(href)+"&mode=4"
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
        liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Duration": duration})
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)



def add_dir(name,url,mode,iconimage,query='',type='folder',page=0):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&query="+str(query)+"&type="+str(type)+"&page="+str(page)#+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
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
def fshare_get_video_list(url):
        soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        #items = soup('li', {'class' : 'w_80pc'})
        items = soup.findAll('li', {'class' : 'w_80pc'})
        #items = soup.find('ul')
        video_list = []
        for i in items:
            href = i.a['href']
            spans = i('span')
            span = i.find('span',{'class':'__cf_email__'})
            #print span['data-cfemail']
            if span is None:
              name = spans[0].text
            else:
              str3=''
              str2=span.get('data-cfemail')
              r=int(str2[0:2], 16)
              ran=len(str2)/2
              for num in range(1,ran):
                str3=str3+chr( int(str2[num*2:num*2+2], 16)^r)
              name = str3
            if name is None:
              name='Unknown'
            thumb = ''
            date = ''
            duration = 0
            desc = ''
            if (name is not None) and (len(name)>3) and (name[-3:] in MEDIA_EXT): 
                add_link(date, name+ '  (' + spans[1].text + ')', duration, href, thumb, desc)

#http://phimnet.us/phim-anh.html
def fslink_get_video_categories(url):
        soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        items = soup.find('div', {'class' : 'box box_menu'})
        #items = items('li')
        video_list = []
		
        for item in items.findAll('a'):
            if item.string is not None:
              href = FSLINK+item['href']
              name = item.string
              if name is None:
                name='Unknown'
              thumb = ''
              date = ''
              duration = None
              desc = ''
              try:
                add_dir(name, href, 7, icon)
              except:
                pass
				
#http://phimnet.us/phim-anh/hanh-dong.html
def fslink_get_video_list(url):
        soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        items = soup.findAll('a', {'class' : 'title t'})

        for item in items:
          #print item
          #print item.a
          #print item.nextSibling().img('src')
          add_dir(item.text.encode("utf-8").replace('  ',' '), FSLINK+item['href'], 8, icon)
			  
        items = soup.find('div', {'class' : 'pager'})

        for item in items.findAll('a'):
            try:
              add_dir(item.string, FSLINK+item['href'], 7, icon)
            except:
              pass				

#http://phimnet.us/movie/a/8373/Silent_Code_2012.html
def fslink_get_video(url):
        soup = BeautifulSoup(make_request(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        items = soup.findAll('textarea')

        for item in items:
          for filename in item.text.split('\n'):
              if filename.find('.file')==0:
                add_dir(item.text, item['href'], 5, icon)
              if filename.find('.file')>0:
                thumb = ''
                date = ''
                duration = None
                desc = ''
                title=filename[filename.rfind('/')+1:len(filename)-5]
                add_link(date, title, duration, filename, thumb, desc)
			  
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
  if not login():
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
  else:    
	get_categories()

elif mode==1:
    searchMenu(url, '', type, page)

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
   searchMenu(url, '', 'file', page)
elif mode==10:
   clearCache()
   
xbmcplugin.endOfDirectory(int(sys.argv[1]))