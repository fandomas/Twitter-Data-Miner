
execfile('pytwitter.py')
import networkx as nx
import matplotlib.pyplot as plt
import time
import operator

alltokens=get_All_tokens()

curr_tid=[1]		#we start with token # n
max_tid=5			#we have m tokens
atoken=[getToken(curr_tid[0])]



#getOnlyLimits()
#exit()

start_time = time.time()

print "limit request"
limits=getRequestNumLeft()

limits_dict={}
limits_dict['followers_limit']=[limits['resources']['followers']['/followers/ids']['remaining'], long(limits['resources']['followers']['/followers/ids']['reset']),'/followers/ids']
limits_dict['following_limit']=[limits['resources']['friends']['/friends/ids']['remaining'],long(limits['resources']['friends']['/friends/ids']['reset']),'/friends/ids']
limits_dict['userinfo_limit']= [limits['resources']['users']['/users/show/:id']['remaining'],long(limits['resources']['users']['/users/show/:id']['reset']),'/users/show']

print limits_dict


try:
	userstart_name=raw_input("Give Username to start (case sensitive):")
	print "Fetch user info", userstart_name
	uinfo=getAPIRequest("/1.1/users/show.json?screen_name="+userstart_name+"&count=5000", limits_dict, 'userinfo_limit', 'users')
	startid=str(uinfo['id'])
	
except urllib2.HTTPError, err:
	print "Error fetching user", userstart_name
	exit()


#manually start with user id
#startid="114524006"

users={1:[startid]}
usersUnique={startid:True}
visited={}
restrictedUsers={}


globalcurr=1

#how many users to fetch until stop
stopat=75

#STOP LEVEL
#remember, the level 3 its the starting user
#after that, the level is count as 2
#eg. 5= scan the ego network of the START user, and next scans the followers and following users of the START user
stoplevel=3

#limit how many followers or 'follow users' to keep for each user (eg. if someone has 1000, we only save (for scan later) a small number of them
keep_users=5000

try:
	while stopat>0 and stoplevel>0:
		globalcurr+=1
		
		try:
			firstKey=sorted(users.keys())[0]
		except IndexError:
			print "ERROR OCCURED [RESTRECTION ON USER ACCOUNT] OR [TWITTER BLOCKED YOUR REQUEST] - "
			break
		
		if len(users)==0:
			print "No more users"
			break
		else:
			DiscoveryPool=users[firstKey]
			if len(DiscoveryPool)==0:
				globalcurr-=3	#followers and following of the previous +1 in the start of the loop
				del users[firstKey]
				globalcurr+=2	#reset global current counter (only followers and following, we do not add the start value because it will be added in the beginning)
				stoplevel-=1
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
			if err.code == 429:
				print "Twitter problem!! 429 Error"
				break
			
			print "Skipping... Restriction for user ",userid, " - ERR:"+str(err.code),err.read() #user accnt is not public
			
			visited[long(userid)]={}
			del users[firstKey][0]
			usersUnique[userid]=True
			
			globalcurr-=1
			
			#decrease limit - catch occured	- we decrease all beacause we didn't noted the function caused it
			limits_dict['followers_limit'][0]-=1
			limits_dict['following_limit'][0]-=1
			limits_dict['userinfo_limit'][0]-=1
			continue
		
		uname=uinfo['name'].replace(" ", "_")	#concacenate for networkx
		uscrname=uinfo['screen_name']
		uid=uinfo['id']
		
		print "Fetched: ",uname
		
		visited[uid]={'followers':ufollowers['ids'], 'following':ufollowing['ids'], 'name':uname, 'uscrname':uscrname, 'uid':uid}
		del users[firstKey][0]
		usersUnique[userid]=True
		
		user_pool_followers=[]
		user_pool_following=[]
		
		#add followers to new users if they are not fetched yet
		count_followers=0
		for kid in ufollowers['ids']:
			if visited.has_key(kid)==False:
				if usersUnique.has_key(str(kid))==False:
					if count_followers<=keep_users:
						count_followers+=1
						user_pool_followers.append(str(kid))
						usersUnique[str(kid)]=True
					else:
						break
		
		#add followers users to new users if they are not fetched yet
		count_follow=0
		for kid in ufollowing['ids']:
			if visited.has_key(kid)==False:
				if usersUnique.has_key(str(kid))==False:
					if count_follow<=keep_users:
						count_follow+=1
						user_pool_following.append(str(kid))
						usersUnique[str(kid)]=True
					else:
						break
					
		
		users[globalcurr]=user_pool_followers
		globalcurr+=1
		users[globalcurr]=user_pool_following
		
		stopat-=1
		
		
except KeyboardInterrupt:
	print "Interrupted..."


elapsed_time = time.time() - start_time
print "Started before: ", elapsed_time, "Seconds"

#full graph with nodes and edges
#FullGraph()

#make connections from only fetched nodes
G=partialGraph(draw=True, snodes=600)

