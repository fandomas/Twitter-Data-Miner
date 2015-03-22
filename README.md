# Twitter-Data-Miner
A twitter data miner - Connects with api and make a networkx-based Directed graph, draw, and then saves the graph

Required
networkx
matplotlib

Tested on linux

This program gives the ability to fool limit, by choosing each time another access token. For that you will need more than one application registered to twitter (apps.twitter.com). 

You can choose how many nodes to fetch until stop

Also you can Save the Graph to a networkx-based text file and draw the Graph using matplotlib.pyplot

When the application reach the maxmimum limit (for all keys given) it finds the unix timestamp, and sleep until its time to wake up and communicate again to fetch the rest.

Dont forget to say thanks.
