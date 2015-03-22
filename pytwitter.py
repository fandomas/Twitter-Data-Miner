"""
The MIT License (MIT)

Copyright (c) 2015 Theodoros Danos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import urllib, urllib2, base64, json

def getAccessToken(consumer_key, consumer_secret):
	data = urllib.urlencode({'grant_type': 'client_credentials'})
	encoded=base64.b64encode(consumer_key+":"+consumer_secret)
	request = urllib2.Request("https://api.twitter.com/oauth2/token")
	request.add_header("Authorization", "Basic %s" % encoded) 
	request.add_header("POST", "/oauth2/token HTTP/1.1") 
	request.add_data(data)
	content = urllib2.urlopen(request).read()
	return json.loads(content)['access_token']

def getToken(i):
	#user n different applications - get things faster
	token=[getAccessToken("k1","s1"),	#twisna
	getAccessToken("k2","s2"),	#twitrenda
	getAccessToken("k3","s3")]	#Academic Research SNA
	return token[i-1]

def getSimpleAPIRequest(get):
	request = urllib2.Request("https://api.twitter.com"+get)
	request.add_header("Authorization", "Bearer %s" % atoken[0]) 
	content = urllib2.urlopen(request).read()
	return json.loads(content)

def getRequestNumLeft():
	resp=getSimpleAPIRequest("/1.1/application/rate_limit_status.json")
	return resp

def getAPIRequest(get, limitDict, funcKey, categKey):
	global atoken
	global curr_tid
	global max_tid
	decLimit=True
	limitMutable=limitDict[funcKey]
	timetoreset=limitMutable[1]
	timenow=int(time.time())
	
	print "currid="+str(curr_tid[0]), "limit="+str(limitMutable)
	
	if timenow-timetoreset <= 0 and limitMutable[0]==0:
		if curr_tid[0]>=max_tid:
			curr_tid[0]=1
			atoken[0]=getToken(curr_tid[0])
			limits=getRequestNumLeft()
			reset_limits(limits,limitDict)
			limitMutable=limitDict[funcKey]
			timetoreset=limitMutable[1]
			timenow=int(time.time())
			
			secs_sleep=timetoreset-timenow
			if timenow-timetoreset <= 0 and limitMutable[0]==0:
				if secs_sleep>0:
					print "Sleeping for limit. Sleeping for",secs_sleep,"seconds...", get, "TID:"+str(curr_tid[0])
					time.sleep(secs_sleep+2)
					limits=getRequestNumLeft()
					reset_limits(limits, limitDict)
					decLimit=False
		else:
			curr_tid[0]=curr_tid[0]+1
			atoken[0]=getToken(curr_tid[0])	#get next token
			limits=getRequestNumLeft()	#check if we can request to api
			reset_limits(limits,limitDict)
			limitMutable=limitDict[funcKey]
			timetoreset=limitMutable[1]
			timenow=int(time.time())
			
			secs_sleep=timetoreset-timenow
			if timenow-timetoreset <= 0 and limitMutable[0]==0:
				if secs_sleep>0:			#if we cannot yet request we wait (because next and previous tokens we would wait more)
					print "Sleeping for limit. Sleeping for",secs_sleep,"seconds...", get, "TID:"+str(curr_tid[0])
					time.sleep(secs_sleep+2)
					limits=getRequestNumLeft()
					reset_limits(limits, limitDict)
					decLimit=False
	
	request = urllib2.Request("https://api.twitter.com"+get)
	request.add_header("Authorization", "Bearer %s" % atoken[0]) 
	content = urllib2.urlopen(request).read()
	if decLimit==True: limitMutable[0]-=1
	return json.loads(content)

def reset_limits(limits, limitDict):
	limitDict['followers_limit']=[limits['resources']['followers']['/followers/ids']['remaining'], long(limits['resources']['followers']['/followers/ids']['reset']),'/followers/ids']
	limitDict['following_limit']=[limits['resources']['friends']['/friends/ids']['remaining'],long(limits['resources']['friends']['/friends/ids']['reset']),'/friends/ids']
	limitDict['userinfo_limit']=[limits['resources']['users']['/users/show/:id']['remaining'],long(limits['resources']['users']['/users/show/:id']['reset']),'/users/show']

def FullGraph(draw=False, save=True):
	G = nx.DiGraph()
	print "Calculating Graph..."
	for userid in visited.keys():
		userid=str(userid)
		if len(visited[long(userid)].keys())>0:			#check if its a restricted account
			followers=visited[long(userid)]['followers']
			following=visited[long(userid)]['following']
			username=visited[long(userid)]['name']
			for k in followers:
				if visited.has_key(k) == True and len(visited[k].keys())>0:
					otheruser=visited[k]['name']
				else:
					otheruser=str(k)
				G.add_edges_from([(otheruser,username)])
			
			for k in following:
				if visited.has_key(k) == True and len(visited[k].keys())>0:
					otheruser=visited[k]['name']
				else:
					otheruser=str(k)
				G.add_edges_from([(username,otheruser)])
	if save==True:	
		nx.write_adjlist(G,"Full_undirected_twitter.txt")
	
	if draw==True:
		nx.draw_networkx(G)
		plt.show()
	return G

def partialGraph(draw=False, save=True):
	G = nx.DiGraph()
	print "Calculating Partial Graph..."
	for userid in visited.keys():
		userid=str(userid)
		if len(visited[long(userid)].keys())>0:
			followers=visited[long(userid)]['followers']
			following=visited[long(userid)]['following']
			username=visited[long(userid)]['name']
			for k in followers:
				if visited.has_key(k) == True and len(visited[k].keys())>0:
					otheruser=visited[k]['name']
					G.add_edges_from([(otheruser,username)])
				else:
					otheruser=str(k)
			for k in following:
				if visited.has_key(k) == True and len(visited[k].keys())>0:
					otheruser=visited[k]['name']
					G.add_edges_from([(username,otheruser)])
				else:
					otheruser=str(k)
			
	if save==True:	
		nx.write_adjlist(G,"Partial_undirected_twitter.txt")
	
	if draw==True:
		nx.draw_networkx(G)
		plt.show()
	return G


def getOnlyLimits():
	l=getRequestNumLeft()
	lkeys=l['resources'].keys()
	for k in lkeys:
		skeys=l['resources'][k].keys()
		for sk in skeys:
			rem=l['resources'][k][sk]['remaining']
			lim=l['resources'][k][sk]['limit']
			if rem<lim: print l['resources'][k][sk], sk
