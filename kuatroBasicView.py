# kuatroBasicView.py       Version  1.0    14-Aug-2014
#     David Johnson, Bill Manaris, and Seth Stoudenmier
#
# The Basic Kuatro View is a simple view that recieves OSC Messages
# from the Kuatro Server and displays the users and their positions as 
# circles on a display Window.
#
#   See README file for full instructions on using the Kuatro System

from gui import *
from osc import OscIn, OscOut 
import socket
import sys


class KuatroBasicView():

   ##### OSC Namespace ######
   NEW_USER_MESSAGE = "/kuatro/newUser"
   LOST_USER_MESSAGE = "/kuatro/lostUser"
   USER_COORDINATES_MESSAGE = "/kuatro/userCoordinates"
   REGISTER_VIEW_MESSAGE = "/kuatro/registerView"

   def __init__(self, incomingPort = 60606, kuatroServerIP = "localhost", kuatroServerOscPort = 50505):


      self.circleRadius = 30               # how wide user circles are (in pixels) 
      self.circleColor  = Color.YELLOW     # and its color


      ######### Server-to-View API ############
      try:
         print "Trying on port:", incomingPort
         oscIn = OscIn(incomingPort)

         oscIn.onInput("/.*", self.echoMessage)
         oscIn.onInput(KuatroBasicView.NEW_USER_MESSAGE, self.addUser)
         oscIn.onInput(KuatroBasicView.LOST_USER_MESSAGE, self.removeUser)
         oscIn.onInput(KuatroBasicView.USER_COORDINATES_MESSAGE, self.moveUser)

      except:
         print "Error:  Unable to setup OSC In port. Port may already be in use."


      ####### Register View with Server ######

      # ipAddress = socket.gethostbyname(socket.getfqdn())   # find the computer's IP Address
      ipAddress = "localhost"

      # Setup OSC Out and send the message
      try:
         oscOut = OscOut(kuatroServerIP, kuatroServerOscPort)           # configure OSC Out port and add to list of ports
         print "OSC Out Configured.  Sending messages to", kuatroServerIP, "on", kuatroServerOscPort

         oscOut.sendMessage(KuatroBasicView.REGISTER_VIEW_MESSAGE, ipAddress, incomingPort)         # send osc message through osc port
         print "\nSent message to:", kuatroServerIP
         print "  Data:", ipAddress, incomingPort

      except Exception, e:
         print e
         sys.exit(1)


      ########## Create Display ############
      self.display = Display("Kuatro View", 1000, 750, 0, 0, Color(50,50,50))  # create the display with a Gray Background


      ##### Setup User Data Structures #########
      self.currentUsers = []
      self.currentUserCircles = []
      self.currentUserCoordinates = []



   #####################################
   ###### Kuatro View Callbacks ######
   #####################################

   # These methods coordinate user data input from the view into
   # coordinates consistent with the virutal world

   def echoMessage(self, message):
      '''Simply prints OSC address and arguments'''

      address = message.getAddress()
      args = message.getArguments()

      print "\nKuatro View - OSC Event:"
      print "OSC In - Address:", address,
      for i in range(len(args)):
         print ",Argument " + str(i) + ": " + str(args[i]),
      print


   def addUser(self, message):
      ''' Callback function for NEW USER messages.  Adds a new user to the view '''

      # parse arguments from OSC Message
      args = message.getArguments()
      userID = args[0]
      x = args[1]
      y = args[2]
      z = args[3]

      # add user to user data structure
      if userID not in self.currentUsers: # first check to make sure userID doesn't already exist (we don't want duplicates)

         self.currentUsers.append(userID)
         self.currentUserCoordinates.append([x,y,z])

         userCircle = self.display.drawCircle(x, y, self.circleRadius, self.circleColor, True)  # add the new user to the display
         self.currentUserCircles.append(userCircle)

         print "Added User:", userID, "Location:", x, y, z


   def removeUser(self, message):
      ''' Callback function for LOST USER messages.  Removes the specified user from the display '''

      # parse arguments from OSC Message
      args = message.getArguments()
      userID = args[0]

      # remove user from user data structure
      if userID in self.currentUsers:  # first check to make sure userID exists

         userIndex = self.currentUsers.index(userID)  # find the index of the current user
         self.currentUsers.pop(userIndex)
         self.currentUserCoordinates.pop(userIndex)

         userCircle = self.currentUserCircles.pop(userIndex) # get the user circle
         self.display.remove(userCircle)                    # and remove it

         print "Removed User:", userID


   def moveUser(self, message):
      ''' Callback function for USER COORDINATES message.  Moves the specified user on the display '''

      # parse arguments from the OSC Message.
      args = message.getArguments()
      userID = args[0]
      x = args[1]
      y = args[2]
      z = args[3]

      # move user and update data structure
      if userID in self.currentUsers: # first check to make sure userID exists

         userIndex = self.currentUsers.index(userID)     # find the index of the current user
         userCircle = self.currentUserCircles[userIndex] # get the user circle
         self.display.move(userCircle, x, y)             # now move it
         self.currentUserCoordinates[userIndex] = [x, y, z] # and update the user coordinates

         print "Moved User:", userID, "Location:", x, y, z


#### Instantiate the Basic Kuatro View
if __name__ == '__main__':
   basicView = KuatroBasicView()
