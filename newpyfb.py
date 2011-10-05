'''
David Gaynor Copyright 2010

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


LOG:

11/28/10:  Ran into some issues with posting files.  
Turns out neither httplib or the urllibs support 
multipart/form posting.  There are a couple of
modules online which I found, the may be helpful,
however, it would be best if at some point there
could be fix for this in the api which does not
involve another external library. For not though
the API will use Chris Atlees poster module.

Make sure you pass in an open file (open('path/example.jpg')
into an mpPOST method (multipart/form post method) as your 
source.  Alternatively, as is done in the move method for a photo, 
you can pass in a StringIO object. Just make sure you give 
the StringIO object a "name" attribute first, using setattr,
or else the multipart encoder wont be able to determine 
the files type, and facebook will return an error 400.

12/1/10: Just remembered, i edited the code last time so that if facebook
returns an empty list as a response the API returns None, instead of a dictionar
y with a value which is empty.  I find this less confusing to debug, so that if 
you a try to work with the empty value it will tell you straight up its empty,
instead of just saying that it doesnt have any of the attributes you want.

12/5/10: Note:I should probably fix tags so it returns a list of
tags, instead of just a dictionary with the key 'data' and then a list of tags,
would save alot of debuggin for the user.  Just cant do it now.

12/9/10:  An odd issue popped up when we put the server today. The server was running
an earlier version of python, 2.5, I think its urllib2 was different, it wouldnt accept a
url with // after http://, which I had in a few cases, as a matter of convenience, if an
argument in the url was not required for a certain post.  So I fixed these cases. 

'''
import sys
for p in newpath:
    sys.path.append(p)
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
import urllib2
import urllib
import httplib
import simplejson as json
from encode import multipart_encode
from streaminghttp import register_openers
import StringIO

Properties = {'likes':'user',
              'from':'user',
              }

Namespace = {'user':
             {'':('json','req'),
             'home':('post','req'),
             'feed':('post','req'),
             'tagged':('post','req'),
             'posts':('post','req'),
             'picture':('302','req'),
             'friends':('user','req'),
             'activities':('json','req'),
             'interests':('json','req'),
             'music':('json','req'),
             'books':('json','req'),
             'movies':('json','req'),
             'television':('json','req'),
             'likes':('json','req'),
             'photos':('photo','req'),
             'albums':('album','req'),
             'videos':('video','req'),
             'groups':('json','req'),
             'statuses':('status','req'),
             'links':('link','req'),
             'notes':('note','req'),
             'events':('json','req'),
             'inbox':('threads','req'),
             'outbox':('messages','req'),
             'updates':('messages','req'),
             'accounts':('json','req'),
             'checkins':('checkin','req'),
             'platformrequests':('requests','req'),
             'make_albums':('json','POST'),
             'make_feed':('status','POST')}, 
             'status':
                 {'':('json','req')},
             'video':
                 {'comments':('comment','req'),
                  'picture': ('302','req'),
                  '':('json','req')},
             'comment':
                 {'':('json','req')},
             'event':
                 {'feed':('post','req'),
                  'noreply':('json','req'),
                  'maybe':('json','req'),
                  'invited':('json','req'),
                  'attending':('json','req'),
                  'declined':('json','req'),
                  'picture':('302','req'),
                  '':('json','req')},
             'page':
                 {'feed':('post','req'),
                  'tagged':('post','req'),
                  'picture':('302','req'),
                  'photos':('photo','req'),
                  'albums':('album','req'),
                  'videos':('video','req'),
                  'groups':('json','req'),
                  'statuses':('status','req'),
                  'links':('link','req'),
                  'notes':('note','req'),
                  'events':('json','req'),
                  'posts':('post','req'),
                  'events':('event','req'),
                  'checkins':('checkin','req'),
                  '':('json','req')},
             'photo':
                 {'likes':('json','req'),
		  'post_photos':('photo','mpPOST'),
                  '':('json','req')},
             'album':
                  {'comments':('comment','req'),
                  'photos':('photo','req'),
                  'picture':('302','req'),
                  'post_photos':('photo','mpPOST'),
                  '':('json','req')},
             'Graph':
                 {'make_events':('event','POST'),
                  'make_albums':('album','POST'),
                  'make_feed':('status','POST'),
                  'post_photos':('photo','mpPOST'),
		  '':('user','req')}
             }



def parse(resp,proptype,propNamespace):
        '''
        parses the response from facebook to assign properties and
        assemble appropiate objects.  It recursively checks to see if 
	the properties in th dictionary sent back from the methods of 
	the facebook objects are other facebook objects.  If so, then it
	creates new python objects to wrap this facebook data.  Anything
	it cant wrap in a python object it returns as a dictionary
	of values and labels.  
        '''
        Properties = propNamespace
       
        if not (resp.get('data',1) == 1):
            dicto = resp['data']
        else:
            dicto = resp

        if not dicto:
            return []
        
        if proptype == 'json':
            objlist = []
            if type(dicto) == list:
                
                for obj in dicto:
                    
                    wrap = {}
                    for prop,val in obj.items():
                        propwrap= Properties.get(prop,None)
                        if propwrap:
                            fullobj = parse(val,propwrap,propNamespace)
                            wrap[prop] = fullobj
                        else:
                            wrap[prop] = val
                    objlist.append(wrap)
            else:
                wrap = {}
                for prop,val in dicto.items():
                    propwrap= Properties.get(prop,None)
                    if propwrap:
                        fullobj = parse(val,propwrap,propNamespace)
                        wrap[prop] = fullobj
                    else:
                        wrap[prop] = val
                objlist.append(wrap)
            return dicto

        else:
            objlist = []
            if type(dicto) == list:
                for obj in dicto:
                    wrap = eval(proptype)()
                    for prop,val in obj.items():
                        propwrap= Properties.get(prop,None)
                        if propwrap:
                            fullobj = parse(val,propwrap,propNamespace)
                            setattr(wrap,prop,fullobj)
                        else:
                            setattr(wrap,prop,val)
                    objlist.append(wrap)
            else:
                wrap = eval(proptype)()
                for prop,val in dicto.items():
                    propwrap= Properties.get(prop,None)
                    if propwrap:
                        fullobj = self.parse(val,propwrap,propNamespace)
                        setattr(wrap,prop,fullobj)
                    else:
                        setattr(wrap,prop,val)
                objlist.append(wrap)
        return objlist
             
class user():
    def __init__(self,access=None,oid = None):
        buildmethods(self,Namespace,Properties)
    
        if oid:
            self.id = oid
            self.settup(access)
        
    def settup(self,access,oid = None):
        if oid:
            self.id = oid
        else:
            try:
                self.id
            except AttributeError:
                raise AttributeError('settup requires facebook item oid')
        propertydict = self.info(access,self.id)
        for prop,val in propertydict.items():
            setattr(self,prop,val)
        
    def __str__(self):
        return 'user'

class photo():
    def __init__(self,access=None,oid = None):
        buildmethods(self,Namespace,Properties)
        
        if oid:
            self.id = oid
            self.settup(access)
        
    def move(self,access,aid,message):
        '''
	A method which copies a photo already on facebook to another
	album, does not delete it from the original album.  If you want
        to post to the default album for your app pass in the aid (album id)
        as the user id and facebook will do it automatically.
	'''
        im = urllib2.urlopen(self.source).read()
        ext = self.source.split('.')[-1]
        
	imm = StringIO.StringIO(im)
	setattr(imm,'name',"blah."+ext)
	resp = self.post_photos({'source':imm,'message':message},access,aid)
	return resp

    def settup(self,access,oid = None):
        if oid:
            self.id = oid
        else:
            try:
                self.id
            except AttributeError:
                raise AttributeError('settup requires facebook item id')
        propertydict = self.info(access,self.id)
        for prop,val in propertydict.items():
            setattr(self,prop,val)
        
    def __str__(self):
        return 'photo'

class album():
    def __init__(self,access=None,oid = None):
        buildmethods(self,Namespace,Properties)
        
        if oid:
            self.id = oid
            self.settup(access)
        
    def settup(self,access,oid = None):
        if oid:
            self.id = oid
        else:
            try:
                self.id
            except AttributeError:
                raise AttributeError('settup requires facebook item id')    
        propertydict = self.info(access,self.id)
        for prop,val in propertydict.items():
            setattr(self,prop,val)
        
    def __str__(self):
        return 'album'    

class page():
    def __init__(self,access=None,oid = None):
        buildmethods(self,Namespace,Properties)
       
        if oid:
            self.id = oid
            self.settup(access)
        
    def settup(self,access,oid = None):
        if oid:
            self.id = oid
        else:
            try:
                self.id
            except AttributeError:
                raise AttributeError('settup requires facebook item id')

        propertydict = self.info(access,self.id)
        for prop,val in propertydict.items():
            setattr(self,prop,val)
 
        
    def __str__(self):
        return 'page'

class comment():
    def __init__(self,access=None,oid = None):
        buildmethods(self,Namespace,Properties)
        self.id = oid
      
        if oid:
            self.id = oid
            self.settup(access)
        
    def settup(self,access,oid = None):
        if oid:
            self.id = oid
        else:
            try:
                self.id
            except AttributeError:
                raise AttributeError('settup requires facebook item id')

        propertydict = self.info(access,self.id)
        for prop,val in propertydict.items():
            setattr(self,prop,val)
        
    def __str__(self):
        return 'comment'

class status():
    def __init__(self,oid=None,access = None):
        buildmethods(self,Namespace,Properties)
    
        if oid:
            self.id = oid
            self.settup(access)
        
    def settup(self,access,oid = None):
        if oid:
            self.id = oid
        else:
            try:
                self.id
            except AttributeError:
                raise AttributeError('settup requires facebook item id')

        propertydict = self.info(access,self.id)
        for prop,val in propertydict.items():
            setattr(self,prop,val)

    def __str__(self):
        return 'status'

class Graph():
    '''
    The class which stores information about a user's facebook session.  The first argument auth is either False, if
    you want to get authorization upon initialzing an instance.  If auth is not false it should be a tuple of an 
    access token and user id which has been through an earlier authorization request.
    '''	
    def __init__(self,auth,request=None, apikey=None,secret=None,extperms = 0):
	    buildmethods(self,Namespace,Properties)
	    if not auth:
		    self.secret = secret
		    self.apikey = apikey
		    self.request = request
		    self.sessionkey = request.GET.get('fb_sig_session_key')
		    a = self.auth(extperms)
            	    if (not type(a)==str) and (not type(a)==unicode):
            	        self.redirect = a  
            	    else:
            	        self.redirect = 0           
	            self.uid = request.GET.get('fb_sig_user')
	    else:
		    self.access = auth[0]
		    self.uid = auth[1]
	    
    def user(self):
	    return self.info(self.access,self.uid)[0]
	    
    def auth(self,extperms):
	    '''
	    attempts to run 3 different authorization schemas, in order
	    from fastest to slowest, in order to set the session's access
	    token, which is required for most calls to facebook's server.
	    '''

	    code = self.request.GET.get('code',None)  
	    try:
		    if self.sessionkey and not extperms:
			    expermstr = ''
			    if extperms:
				    for i,perm in enumerate(extperms):
					    if i == (len(extperms)-1):
						    expermstr = expermstr +perm
					    else:
						    expermstr = expermstr + perm + ','
				    data = {'client_id':self.apikey,'client_secret':self.secret,'sessions':self.sessionkey,'scope':expermstr}
			    else:
				    data = {'client_id':self.apikey,'client_secret':self.secret,'sessions':self.sessionkey}
			    dataen = urllib.urlencode(data)
			    conn = httplib.HTTPSConnection("graph.facebook.com")
			    conn.request("POST", '/oauth/exchange_sessions', dataen)
			    resp = conn.getresponse().read()
			    parse = json.loads(resp)
		            
			    access = parse[0]['access_token']
		    else:
			    a = urllib2.urlopen('https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=http://apps.facebook.com/captionroulette/&client_secret=%s&code=%s' % (self.apikey,self.secret,code))
			    access0 = a.read()
			    acess1 = ''.join(access0.split('&')[:-1])
			    acess2 = ''.join(acess1.split('=')[1:])
			    access = acess2
		    
	    except urllib2.HTTPError:
		    expermstr = ''
		    
		    if self.sessionkey and not extperms:
			    if extperms:
				    for perm in extperms:
					    if i == (len(extperms)-1):
						    expermstr = expermstr +perm
					    else:
						    expermstr = expermstr + perm + ','
				    data = {'client_id':self.apikey,'client_secret':self.secret,'sessions':self.sessionkey,'scope':expermstr}
			    else:
				    data = {'client_id':self.apikey,'client_secret':self.secret,'sessions':self.sessionkey}
			    dataen = urllib.urlencode(data)
			    conn = httplib.HTTPSConnection("graph.facebook.com")
			    conn.request("POST", '/oauth/exchange_sessions', dataen)
			    resp = conn.getresponse().read()
			    parse = json.loads(resp)
		            
			    access = parse[0]['access_token']
		    else:
			    if extperms:
				    expermstr += '&scope='
				    for perm in extperms:
					    expermstr = expermstr + perm + ','
			    auth =('https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=http://apps.facebook.com/captionroulette/%s' % (self.apikey,expermstr))
		    
			    return HttpResponseRedirect(auth)
	    self.access = access
	    return access
    
    def __str__(self):
	    return 'Graph'

def buildmethods(fbobject1,namespace,propNamespace):

    '''
    builds the methods to be stored in the given class "fboject".  Connection 
    is the method to be built, formats is a tuple.  formats[0] contains the 
    response formatting, json, object array etc.  formats[1] indicates whether
    the method is to make a get req using http, or make a POST to the graph server, 
    'req' indicates a get request, 'POST' indicates a POST, and mPOST indicates a 
    multiform post, such as uploading a file.   fbobject1 is the actual
    class instance being passed in, while fbobject is the string of the fb name
    of the object.
    '''
    
    fbobject = str(fbobject1)
    methods = {}
    requrl = 'https://graph.facebook.com'
    posturl = 'graph.facebook.com'
    print fbobject
    for connection, formats in namespace[fbobject].items():
        if formats[1] == 'POST':
            funheader = 'def %s(self,args,access,oid): \n\
\tdata ={}\n\
\tdata["access_token"]=access\n'  % connection
            makedata = '\tfor arg, val in args.items(): \n\
\t\tdata[arg] = val \n'
            encodedata = '\tencodedata=urllib.urlencode(data) \n'
            conn = '\tconn = httplib.HTTPSConnection("%s") \n' % posturl
            request =  '\tconn.request("POST", "/"+oid+"/%s", encodedata) \n' % connection.split('_')[1]
            resp = '\tresp = conn.getresponse() \n'
            jsn = '\tjsn = json.loads(resp.read())\n'
            parse = '\tparsed = parse(jsn,"%s",%s)\n' % (formats[0],propNamespace)
            ret = '\treturn parsed'
            func=funheader+makedata+encodedata+conn+request+resp+jsn+parse+ret
            exec(func)
            #print fbobject, func
            setattr(eval(fbobject),connection,eval(connection))
        elif formats[1] == 'mpPOST':
            funheader = 'def %s(self,args,access,oid): \n\
\tdata ={}\n\
\tregister_openers()\n\
\tdata["access_token"]=access\n'  % connection
            makedata = '\tfor arg, val in args.items(): \n\
\t\tdata[arg] = val \n'
            encodedata = '\tencodedata,headers=multipart_encode(data) \n'
            
            request =  '\trequest = urllib2.Request("%s/"+oid+"/%s", encodedata,headers) \n' % (requrl,connection.split('_')[1])
            resp = '\tresp = urllib2.urlopen(request) \n'
            jsn = '\tjsn = json.loads(resp.read())\n'
            parse = '\tparsed = parse(jsn,"%s",%s)\n' % (formats[0],propNamespace)
            ret = '\treturn parsed'
            func=funheader+makedata+encodedata+request+resp+jsn+parse+ret
            exec(func)
            #print fbobject, func
            setattr(eval(fbobject),connection,eval(connection))
            
        else:
            if connection:
                funheader = 'def %s(self,access,oid): \n'  % connection
                name = connection
            else:
                funheader = 'def %s(self,access,oid): \n'  % 'info'
                name = 'info'
                 
            data = '\tdata = urllib.urlencode({"access_token":access}) \n'
            url = '\turl= "%s/"+oid+"/%s?"+data \n' % (requrl,connection)
            resp = '\tresp = urllib2.urlopen(url)\n'#"https://graph.facebook.com/"+oid+"/%s?"+"access_token="+access) \n'
            if formats[0] == '302':
                jsn = ''
                parse = ''
                ret = '\treturn resp.geturl()'
            else:
                jsn = '\tjsn = json.loads(resp.read())\n'
                parse = '\tparsed = parse(jsn,"%s",%s)\n' % (formats[0],propNamespace)
                ret = '\treturn parsed'
            func = funheader+data+url+resp+jsn+parse+ret
            exec(func)
            #self.__dict__[name] = eval(func)
            setattr(eval(fbobject),name,eval(name))
