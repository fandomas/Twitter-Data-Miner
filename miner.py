"""
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
max_tid=4		#we have 3 tokens
atoken=[getToken(curr_tid[0])]

startid="114524006"


start_time = time.time()

print "limit request"
limits=getRequestNumLeft()

limits_dict={}
limits_dict['followers_limit']=[limits['resources']['followers']['/followers/ids']['remaining'], long(limits['resources']['followers']['/followers/ids']['reset']),'/followers/ids']
limits_dict['following_limit']=[limits['resources']['friends']['/friends/ids']['remaining'],long(limits['resources']['friends']['/friends/ids']['reset']),'/friends/ids']
limits_dict['userinfo_limit']= [limits['resources']['users']['/users/show/:id']['remaining'],long(limits['resources']['users']['/users/show/:id']['reset']),'/users/show']

users={1:[startid]}
usersUnique={startid:True}
visited={}
restrictedUsers={}
specificUsers=[]

globalcurr=1

#how many users to fetch until stop
stopat=70


try:
	while stopat>0:
		globalcurr+=1
		firstKey=sorted(users.keys())[0]
		
		if len(users)==0:
			print "No more users"
			break
		else:
			DiscoveryPool=users[firstKey]
			if len(DiscoveryPool)==0:
				globalcurr-=1
				del users[firstKey]
				continue
			else:
				userid=users[firstKey][0]
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
			del users[firstKey][0]
			usersUnique[userid]=True
			#decrease limit - catch occured	- we decrease all beacause we didn't noted the function caused it
			limits_dict['followers_limit'][0]-=1
			limits_dict['following_limit'][0]-=1
			limits_dict['userinfo_limit'][0]-=1
			continue
		
		uname=uinfo['name'].replace(" ", "_")	#concacenate for networkx
		uscrname=uinfo['screen_name']
		uid=uinfo['id']
		
		visited[uid]={'followers':ufollowers['ids'], 'following':ufollowing['ids'], 'name':uname, 'uscrname':uscrname, 'uid':uid}
		del users[firstKey][0]
		usersUnique[userid]=True
		
		user_pool_followers=[]
		user_pool_following=[]
		
		#add followers to new users if they are not fetched yet
		for kid in ufollowers['ids']:
			if visited.has_key(kid)==False:
				if usersUnique.has_key(str(kid))==False:
					user_pool_followers.append(str(kid))
					usersUnique[str(kid)]=True
		
		#add followers users to new users if they are not fetched yet
		for kid in ufollowing['ids']:
			if visited.has_key(kid)==False:
				if usersUnique.has_key(str(kid))==False:
					user_pool_following.append(str(kid))
					usersUnique[str(kid)]=True
					
		
		if len(user_pool_followers)>0: 
			users[globalcurr]=user_pool_followers
			globalcurr+=1
		if len(user_pool_following)>0: users[globalcurr]=user_pool_following
		
		stopat-=1
		
		
except KeyboardInterrupt:
	print "Interrupted..."


elapsed_time = time.time() - start_time
print "Started before: ", elapsed_time, "Seconds"

#full graph with nodes and edges
#FullGraph()

#make connections from only fetched nodes
G=partialGraph(draw=True, snodes=600)

