

import urllib, urllib2, base64, json
starter_user_infoisfetched=True

def get_All_tokens():
	return [getAccessToken("hN59d0y0g3rGUiJ957bZrrUEG","zTA6E2dHBJqtYFalXbqJ5BkrZ1vEs5YKseOeNt9sYLx2HvTKZZ"),	#twisna
	getAccessToken("ZRQNjjhKtk2N1J4VpMAu1rLv9","7srA5K2S7UcpOVSPW2uptvKooDHiqJBNABcpp8cn1U5AJFpAdy"),	#twitrenda
	getAccessToken("79fK73f9y5wM5pep0teL7Wfgq","JvfUPCLrXPFLgv9SADIGMwZlt17JWqUNbr2gBf2p1Sw7nbKRnH"),	#Academic Research SNA
	getAccessToken("w2BBOWamUqd9MfFrhLPxmWj4q","ZUB7OVrRuVDkceBkhsKFbg4hAMSp5Z4bpENVN9sbC22vAnSeLj"),	#hackevents
	getAccessToken("GAhHCrimC7PjahhVOCxByUVzQ","z9RCW0XakaFRXKAgnbZZWRFq5bX95pqlp7Oc62j0ifexr6CfcJ")]

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
	global alltokens
	#user n different applications - get things faster
	return alltokens[i-1]

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
	
	print 
	print limitMutable
	print
	
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

def zero_limits(limits, limitDict):
	limitDict['followers_limit']=[0, long(limits['resources']['followers']['/followers/ids']['reset']),'/followers/ids']
	limitDict['following_limit']=[0,long(limits['resources']['friends']['/friends/ids']['reset']),'/friends/ids']
	limitDict['userinfo_limit']= [0,long(limits['resources']['users']['/users/show/:id']['reset']),'/users/show']

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

def partialGraph(draw=False, save=True, snodes=300):
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
		if snodes != 300:
			nx.draw_networkx(G,node_size=snodes)
		else:
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

def readDiGraph(pfile):
	G=nx.read_adjlist(pfile,create_using=nx.DiGraph())
	return G
