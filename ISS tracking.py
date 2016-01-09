"""

  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  +                                                                                                                      +   
  +  ISS Tracking Project    - Or The When to Give Tim Peake a Wave Project                                              +
  +                                                                                                                      +
  +  This has been written by Rebecca Ashworth To notify by IM text when the ISS is overhead inthe sky.                  +
  +  This program is designed to text users on our internal IM messaging system when the 							     +
  +  Interntional Space Station is overhead . 																			 +
  +  																	                                                 +
  +                                                                                                                      +
  +  The program is scheduled to run on a daily basis at 4pm and only sends a text if the ISS will be overhead that night+
  +  The setup we use with this with is 																				 +
  +	 -	Prosody IM server running on a raspberry pi 																	 +
  +  - 	Xapper client on our mobile devices 																			 +
  +  																													 +
  +  The code uses 																										 +
  +	- xmpp to connect to the prosody server																				 +
  + - A web resource to get the ISS fly over details for our geolocation 												 +
  + - Note we have had great variability with urllib depending which which version you are running 						 +
  +		of python, platform, urllib 																				     +
  +		we are running on raspberry pi, python2 and urlib ( not 2 or 3)													 +
  + - If the ISS is to be seen in the time window set then it texts us the details										 +
  +           																											 +
  + You can take this code and use for your own purposes 																 +
  + - if you just want to see how to track the ISS																		 +
  + - if you want to see how to connect to an IM Messaging service														 +
  +	- You could easily alter the code to use twitter as the messaging service											 +
  +																														 +
  +																														 +
  +  Author : Rebecca Ashworth                                                                                           +
  +  Date   : 24/10/2015                                                                                                 +
  +                                                                                                                      +
  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  
"""

import urllib, json, datetime
import xmpp

# set IM details
username = "<your username for IM server>"
imPwd = "<username pwd>"
fromUser = "<the user to send the message from>"

# set your geolocation
lat = "<set your lat>"
long = "<set your long>"
numPasses = "<set number of passes to retrieve>"  # we set 3
# set website to get info
url = "http://api.open-notify.org/iss-pass.json?lat=" + lat + "&lon=" + long + "&n=" + numPasses

def messageHandler(conn,mess_node): pass

# Create an xmpp client
cl=xmpp.Client("<Your IM server domain>",debug=[])
# ...connect it to SSL port directly
cl.connect(server=("<your IM server IP address>",<your IM server port no>))
if not cl.auth(username,imPwd):
    raise IOError('Can not auth with server.')

# ...register some handlers 
cl.RegisterHandler('message',messageHandler)

# ...become available 
cl.sendInitPresence()



#GMT, BST date changes
#Go back 25th October 2015
gmtStarts = datetime.date(2015,10,25)
#Go forward 27th March 2016
gmtEnds = datetime.date(2015,3,27)

#function to alter time to BST if necessary
def returnLocalTime(inTimestamp):
    #convert timestamp
    riseTimeDate = datetime.datetime.fromtimestamp(inTimestamp).strftime("%d-%m-%Y %H:%M")
    GmtTimeItAppears = datetime.datetime.fromtimestamp(inTimestamp)
    myDate = datetime.date.fromtimestamp(inTimestamp)

    if myDate < gmtStarts or myDate > gmtEnds:
        BST = True
    else:
        BST = False

    #if bst then date diff > 0, so add 1 hour
    if BST:
        BstTimeItAppears = GmtTimeItAppears + datetime.timedelta(hours=1)
        return (BstTimeItAppears,myDate)
    else:
        return (GmtTimeItAppears,myDate)



#go to website and get back response
response = urllib.urlopen(url)
data = json.load(response)

#parse the json for times of passes
for passes in data["response"]:
    LengthOfPassOver = passes["duration"]
    TimeItAppears = passes["risetime"]

    riseTime,thisDate = returnLocalTime(TimeItAppears)
    #print (riseTime)
    #print (thisDate)
    #print (LengthOfPassOver)

    dateDiff = datetime.date.today()-datetime.date.fromtimestamp(TimeItAppears)
    #print dateDiff.days

    if dateDiff.days == 0: # i.e. it is appearing that day it is run
        myMessage = ("todays time for the ISS pass is " + str(riseTime) + " " + str(LengthOfPassOver / 60) + " " + "minutes")
        # ...if connection is broken - restore it
        if not cl.isConnected(): cl.reconnectAndReauth()
        #Check status and send messages to online users
        for jid in cl.getRoster().getItems():
            status= str(cl.Roster.getStatus(jid))
            #print (jid)
            if (jid != fromUser) :
                #print 'Message sent to ' + jid
                #print (myMessage)
                cl.send(xmpp.Message(jid,myMessage))
        

# ...and then disconnect.
cl.disconnect()

