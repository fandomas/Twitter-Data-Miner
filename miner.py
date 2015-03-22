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


execfile('pytwitter.py')
import networkx as nx
import matplotlib.pyplot as plt
import time
import operator

curr_tid=[1]		#we start with token num 1
max_tid=3		#we have 3 tokens
atoken=[getToken(curr_tid[0])]

startid="114524006"

#take first followers more seriously (download first followers of first user) than the rest following
globalnum=10

start_time = time.time()

print "limit request"
limits=getRequestNumLeft()

limits_dict={}
limits_dict['followers_limit']=[limits['resources']['followers']['/followers/ids']['remaining'], long(limits['resources']['followers']['/followers/ids']['reset']),'/followers/ids']
limits_dict['following_limit']=[limits['resources']['friends']['/friends/ids']['remaining'],long(limits['resources']['friends']['/friends/ids']['reset']),'/friends/ids']
limits_dict['userinfo_limit']= [limits['resources']['users']['/users/show/:id']['remaining'],long(limits['resources']['users']['/users/show/:id']['reset']),'/users/show']

users={startid:time.time()}
visited={}
restrictedUsers={}
specificUsers=[]

#how many users to fetch until stop
stopat=50


try:
	while stopat>0:
		sorted_k = sorted(users.items(), key=operator.itemgetter(1))
		DiscoveryPool=[]
		for i, j in sorted_k: DiscoveryPool.append(i)
		
		if len(DiscoveryPool)==0:
			break
		else:
			userid=DiscoveryPool[0]
		try:
			print "Finding Followers of ",userid
			ufollowers= getAPIRequest("/1.1/followers/ids.json?user_id="+userid+"&count=5000", limits_dict, 'followers_limit', 'followers')
			
			print "Finding Following", userid
			ufollowing= getAPIRequest("/1.1/friends/ids.json?user_id="+userid+"&count=5000", limits_dict, 'following_limit', 'friends')
			
			print "Fetch user info", userid
			uinfo=getAPIRequest("/1.1/users/show.json?user_id="+userid+"&count=5000", limits_dict, 'userinfo_limit', 'users')
		except urllib2.HTTPError, err:
			print "Skipping... Restriction for user ",userid, " (or possible error) - ERR:"+str(err.code) #user accnt is not public
			visited[long(userid)]={}
			del users[userid]
			#decrease limit - catch occured	- we decrease all beacause we didn't noted the function caused it
			limits_dict['followers_limit'][0]-=1
			limits_dict['following_limit'][0]-=1
			limits_dict['userinfo_limit'][0]-=1
			continue
		
		uname=uinfo['name'].replace(" ", "_")	#concacenate for networkx
		uscrname=uinfo['screen_name']
		uid=uinfo['id']
		
		visited[uid]={'followers':ufollowers['ids'], 'following':ufollowing['ids'], 'name':uname, 'uscrname':uscrname, 'uid':uid}
		del users[str(uid)]
		
		userspectime=time.time()-globalnum*2
		#add followers to new users if they are not fetched yet
		for kid in ufollowers['ids']:
			if visited.has_key(kid)==False:
				users[str(kid)]=userspectime
				
		#add followers users to new users if they are not fetched yet
		for kid in ufollowing['ids']:
			if visited.has_key(kid)==False:
				users[str(kid)]=userspectime*1.5
		
		globalnum=1
		
		stopat-=1
		
except KeyboardInterrupt:
	print "Interrupted..."


elapsed_time = time.time() - start_time
print "Started before: ", elapsed_time, "Seconds"

#full graph with nodes and edges
#FullGraph()

#make connections from only fetched nodes
G=partialGraph(True)

