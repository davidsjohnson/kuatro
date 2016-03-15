# kuatroMouseClient.py
#
# It creates a GUI control surface for a Kuatro installation.
#
# The code below is setup to control the Kuatro Audio Server.
# With few modifications, it should be able to (also) control
# the visual side of things, as well.
#
# In particular, it creates a GUI control surface consisting of circles,
# one circle per Kuatro user (tracked person inside interaction space),
# and sets up an OSC client to send messages to the Kuatro Audio Server.
#
# INSTRUCTIONS:
# 
# Run this program *and* the Kuatro Audio Server.  Make sure the port below
# is set properly, and all should work fine, i.e., you should be able to control
# the Audio Server via the GUI control surface by moving circles around.  
#
 
from gui import *     # for circles, etc.
from music import *   # for mapValue
from osc import *     # for sending OSC messages

kuatroServerOSC_PORT = 50505    # port for outgoing Kuatro OSC Server messages
MAX_KuatroX = 1000              # max x coordinate for Kuatro virtual space
MAX_KuatroY = 1000              # max y coordinate for Kuatro virtual space

circleRadius = 30               # how wide user circles are (in pixels) 
circleColor  = Color.YELLOW     # and its color

nextUserID = 0         # used to create unique IDs for new users   

clientID = "asdfas"

####
#
# OSC Client
#
# Next, let's send OSC messages to the Kuatro Audio Server.
# 
# Outgoing OSC messages have the format:
#
# /kuatro/<event> , Argument 0: <userID> , Argument 1: <y_value> , Argument 2: <z_value>
#
# where <event> is "newUser", "lostUser", "userCoordinates", or "userZone",
#       <x_value> ranges from 0 to 1000, and
#       <y_value> ranges from 0 to 1000
#

##### create an OSC output object ######
oscOut = OscOut('localhost', kuatroServerOSC_PORT )  # send messages to OSC server on port 30303


####
#
# GUI control surface
#
# How to operate the interface:
#
# * Clicking on an empty display space creates a new circle (and sends a "newUser" OSC message).
#
# * Right-clicking on a circle, presents a pop-up menu to remove it (and sends a "lostUser" OSC message).
#
# * Dragging a cicle moves it around on the display (and sends an "userCoordinates" OSC message).
#

# create display
d = Display("Kuatro GUI Control", 800, 600, 0, 0, Color.BLACK)

d.drawRectangle(380, 280, 420, 320, Color.WHITE, True)

# simulate Kuatro user tracking
# list of current users (being tracked) - parallel lists
currentUsers       = []  # userIDs of current users
currentCoordinates = []  # coordinates of current users
currentUserCircles = []  # holds visual representation of current users

### create callback functions 
#
# NOTE:  Two of them have to be defined inside addUser() because they are
# associated with a specific circle - that's the ONLY way this can be achieved.
#
   
# 
# Clicking on an empty display space creates a new circle (and sends a "newUser" OSC message)
#
# When we create the circle, we also attach a pop-up menu with a callback function to be able to remove it,
# and also assign a callback function to move when dragging the mouse (see below).  Again, these two
# callback functions have to be defined inside 'addUser', where we have a handle on the specific circle.
#


# calibrating device
oscOut.sendMessage("/kuatro/calibrateDevice", clientID, 0, 0, 0, 800, 1, 600) 

def addUser(x, y):
   """Called when clicking on an empty display space.
      It creates a new circle at the click coordinates,
      and sends a "newUser" OSC message.
   """
   
   global nextUserID    # holds usedID for the new user
   
   # create new user representation (a filled circle)
   userCircle = d.drawCircle(x, y, circleRadius, circleColor, True)
   
   # map display coordinates to Kuatro virtual space coordinates
   # xValue = mapValue(x, 0, d.getWidth()-1, 0, MAX_KuatroX)
   # yValue = mapValue(y, 0, d.getHeight()-1, MAX_KuatroY, 0)  # invert y coordinate!

   xValue = x
   yValue = y

   # add user to local data structure
   currentUsers.append( nextUserID ) 
   currentCoordinates.append( [xValue, yValue] )
   currentUserCircles.append( userCircle )
   
   # send OSC message - /kuatro/newUser + userID + x, y coordinates
   oscOut.sendMessage("/kuatro/newUser", nextUserID, xValue, 0, yValue, clientID)
   
   print "--> new user", nextUserID, xValue, yValue

   # create ID for next user (if any)
   nextUserID = nextUserID + 1 
   
   #### Define internal callback functions to attach to this circle
   
   ####
   # Dragging a cicle moves it around on the display (and sends an "userCoordinates" OSC message).

   # create a callback function to move this user / circle
   def updateUserCoordinates(x, y):
      """Called when dragging a circle.
         It moves the circle to the new position,
         and sends a "userCoordinates" OSC message.
      """
  
      # NOTE: By defining the function inside the addUser() function, we are 
      # capturing and preserving the current value of 'userCircle' 
      # in this function definition.  This function will be defined again
      # and again, once for each circle created (user added).  It will always
      # remember the proper user / circle to delete, as explained here.
      
      # the x, y coordinates are internal to the circle frame (0, 0 is at the top
      # left corner of the circle's enclosing rectangle), so
      # convert them to display coordinates
      x = userCircle.x - circleRadius + x
      y = userCircle.y - circleRadius + y
         
      # move circle to new coordinates
      d.move( userCircle, x, y)
      
      # print "move user", x, y

      # through the userCircle, find user index in parallel data structure
      userIndex = currentUserCircles.index( userCircle )

      # map display coordinates to Kuatro virtual space coordinates
      xValue = mapValue(x, 0, d.getWidth()-1, 0, MAX_KuatroX)
      yValue = mapValue(y, 0, d.getHeight()-1, MAX_KuatroY, 0)  # invert y coordinate!

      # update user cordinates in local data structure
      currentCoordinates[ userIndex ] = [xValue, yValue]  # update coordinates

      # retrieve userID   
      userID = currentUsers[ userIndex ]
   
      # send OSC message - /kuatro/userCoordinates + userID + new coordinates
      oscOut.sendMessage("/kuatro/userCoordinates", userID, xValue, 0, yValue, clientID)

      # print "   ", userID, xValue, yValue

      # *** NEW, MORE EFFICIENT WAY -- send OSC message - /kuatro/userCoordinates + userID + new coordinates
#      oscOut.sendMessage("/kuatro/userCoordinates" + str(userID), xValue, yValue)
#
#      print "    " + str(userID), xValue, yValue

   # now, register this callback function with the current circle
   userCircle.onMouseDrag( updateUserCoordinates )
   

   ####
   # Right-clicking on a circle, presents a pop-up menu to remove it (and sends a "lostUser" OSC message).

   # create a callback function to eventually delete this user / circle
   def lostUser():
      """Called when selecting a circle's pop-up menu to remove it.
         It removes the circle at the click coordinates,
         and sends a "lostUser" OSC message.
      """
   
      global nextUserID    # holds usedID for the next new user

      # NOTE: By defining the function inside the addUser() function, we are 
      # capturing and preserving the current value of 'userCircle' 
      # in this function definition.  This function will be defined again
      # and again, once for each circle created (user added).  It will always
      # remember the proper user / circle to delete, as explained here.
         
      # through the userCircle, find user index in parallel data structure
      userIndex = currentUserCircles.index( userCircle )
   
      # send OSC message - /kuatro/lostUser + userID + last known coordinates
      oscOut.sendMessage("/kuatro/lostUser", currentUsers[ userIndex ], clientID)
                      
      print "<-- lost user", currentUsers[ userIndex ]

      # create ID for next user (if any) - we reuse earlier IDs
      nextUserID = nextUserID - 1 

      # delete circle
      d.remove( userCircle )
   
      # and remove user from local data structure
      currentUsers.pop( userIndex ) 
      currentCoordinates.pop( userIndex )
      currentUserCircles.pop( userIndex )

      
   # now, create a pop-up menu to be able to delete this user by right clicking on the circle
   menu = Menu("Popup Menu")
   menu.addItem("remove", lostUser)
   userCircle.addPopupMenu(menu)

# register callback function
d.onMouseClick(addUser)
     



