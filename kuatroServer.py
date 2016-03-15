# kuatroServer.py       Version  1.2     28-Oct-2014
#     David Johnson, Bill Manaris, and Seth Stoudenmier
#
# The Kuatro Server receives x, y, z coordinates, via OSC, of users in a being 
# tracked in a space by one or more depth sensors, such as the Kinect.  The data
# received is coordinated in a Virtual World for use by Kuatro View.  The
# new Virtual World data is then sent, via OSC, to these views for use in their 
# interaction design.
#
# A Virtual World is an overhead representation of the space that is being tracked.
#
#     See README file for full instructions on using the Kuatro System
#
#
#  LOG:
#     13-Aug:  Updated Server so messages now require a unique client ID.  This allows
#              the server to track coordinates from multiple devices.  
#     14-Aug:  Updated OSC Addresses to be constants
#     28-Oct:  Updated to only allow one connection per view (i.e. only one entry into the viewPort list)
# 
#  TO DO:
#     1.



from osc import OscIn, OscOut
from gui import *
from music import *
import sys

class KuatroServer():

   ##### OSC Namespace #####
   NEW_USER_MESSAGE = "/kuatro/newUser"
   LOST_USER_MESSAGE = "/kuatro/lostUser"
   USER_COORDINATES_MESSAGE = "/kuatro/userCoordinates"
   REGISTER_DEVICE_MESSAGE = "/kuatro/registerDevice"
   CALIBRATE_DEVICE_MESSAGE = "/kuatro/calibrateDevice"
   REGISTER_VIEW_MESSAGE = "/kuatro/registerView"

   def __init__(self, port = 50505, verbose = 0):

      # *** add comments below
      self.nextUserID = 0              # used to find the next available user ID (this is never decremented so IDs are not reused)
      self.deviceUsers = {}            # maps a device user ID (combination of user ID and client ID) to a corresponding Virtual World user ID (This is needed so we can send views an integer value for the User ID)
      self.virtualUsers = {}           # stores Virtual World User IDs and each user's coordinates within the Virtual World 
      self.devices = []                # stores a list of the devices that are connected to the server
      self.viewInfo = []               # stores a tuple including the IP Address and Port of all registered view.  Used to ensure that that same view does not register multiple times. 
      self.viewPorts = []              # stores the OSC Port to all registered views
      self.deviceCalibrationData = {}  # stores calibration data from 

      # the max coordinates of the Virutal World
      self.virtualMaxX = 1000
      self.virtualMaxY = 750
      self.virtualMaxZ = 0    # Z is not supported at this time since Virtual World is 2D
      
      self.verbose = verbose  # turn on logging of user tracking. 0 = Off, 1 = User Tracking Data, 2 = User Tracking plus Echo OSC Messages


      # configure OSC protocol communication
      try:

         oscIn = OscIn(port)  

         # if verbose logging is set to 2 turn on echo message
         if verbose == 2:
            oscIn.onInput("/.*", self.echoMessage)
         
         # the Client-to-Server API
         oscIn.onInput(KuatroServer.NEW_USER_MESSAGE, self.addUser)
         oscIn.onInput(KuatroServer.LOST_USER_MESSAGE, self.removeUser)
         oscIn.onInput(KuatroServer.USER_COORDINATES_MESSAGE, self.moveUser)
         oscIn.onInput(KuatroServer.REGISTER_DEVICE_MESSAGE, self.registerDevice)
         oscIn.onInput(KuatroServer.CALIBRATE_DEVICE_MESSAGE, self.calibrateDevice)

         # the View-to-Server API
         oscIn.onInput(KuatroServer.REGISTER_VIEW_MESSAGE, self.registerView)

      except:
         print "Error:  Unable to setup OSC In port. Port may already be in use."


   #####################################
   ###### Kuatro Server Callbacks ######
   #####################################
   
   # These methods coordinate user data input from the view into
   # coordinates consistent with the virutal world.  And then send 
   # the new data to all registered views.  

   def echoMessage(self, message):
      '''Simply prints OSC address and arguments'''

      address = message.getAddress()
      args = message.getArguments()

      print "\nOSC Event:"
      print "OSC In - Address:", address,
      for i in range(len(args)):
         print ",Argument " + str(i) + ": " + str(args[i]),
      print


   def addUser(self, message):
      ''' Adds a user to the virtual world.  The OSC Message should contain
          the values:
               userID, x, y, z
      '''

      # parse arguments from OSC Message
      args = message.getArguments()
      userID = args[0]
      x = args[1]
      y = args[2]
      z = args[3]
      clientID = args[4]

      user = (userID, clientID)  # make user from each device unique by creating tuple with userID and client id
      #### Update Virutal World with new User
      if user not in self.deviceUsers:     # make sure user does not already exist


         virtualWorldUserID = self.nextUserID   # then get a new user ID for the virtual World
         self.nextUserID = self.nextUserID + 1  # increment user ID

         self.deviceUsers[user] = virtualWorldUserID  # map user to virtual world ID 
        
         newX, newY, newZ = self.calibrateUserCoordinates(x, y, z, clientID)   # get new set of user coordinates calibrated to the Virtual World
         self.virtualUsers[virtualWorldUserID] = (newX, newY, newZ)            # update User dictionary with new user and tuple of user coordinates

         self.sendMessage(KuatroServer.NEW_USER_MESSAGE, virtualWorldUserID, newX, newY, newZ)  # send message with calibrated user coordinates to registered views

         if self.verbose !=0:
            print "Added User:", virtualWorldUserID, "Coords:", newX, newY, newZ


   def removeUser(self, message):
      ''' Removes a user from the Virtual World and updates the registered views.
          The OSC Message should contain the value:
               userID
      '''

      # parse arguments from OSC Message
      args = message.getArguments()
      userID = args[0]
      clientID = args[1]

      user = (userID, clientID)

      ##### Remove user from Virtual World
      if user in self.deviceUsers:                     # verify that user exists in virtual world
         virtualWorldUserID = self.deviceUsers[user]      # then get the virtual world user ID           
         del self.virtualUsers[virtualWorldUserID]        # and remove user from user dictionaries
         del self.deviceUsers[user]

         self.sendMessage(KuatroServer.LOST_USER_MESSAGE, virtualWorldUserID)  # send lost user message to registered views 

         if self.verbose !=0:
            print "Removed User:", virtualWorldUserID


   def moveUser(self, message):
      ''' Moves a user to a new location in the virtual world. The OSC Message
          should contain the values:
               userID, x, y, z
       '''

      # parse arguments from OSC Message
      args = message.getArguments()
      userID = args[0]
      x = args[1]
      y = args[2]
      z = args[3]
      clientID = args[4]

      user = (userID, clientID)

      ##### Update User Coordinates      
      if user in self.deviceUsers:                           # verify that user exists in device users

         virtualWorldUserID = self.deviceUsers[user]                           # then get the virtual world user ID    
         newX, newY, newZ = self.calibrateUserCoordinates(x, y, z, clientID)   # get calibrated coordinates for user
         self.virtualUsers[virtualWorldUserID] = (newX, newY, newZ)            # add new coordinates user dictionary
         
         self.sendMessage(KuatroServer.USER_COORDINATES_MESSAGE, virtualWorldUserID, newX, newY, newZ)    # send message with calibrated user coordinates

         if self.verbose !=0:
            print "User:", virtualWorldUserID, "Coords:", newX, newY, newZ


   def registerDevice(self, message):
      ''' Registers a device with the Kuatro Server.  The OSC Message should
          contain the values: (Nothing uses devices list at this time...may remove)
               clientID, sensorType
      '''

      # parse the arguments from the OSC Message
      args = message.getArguments()
      clientID = args[0]

      self.devices.append(clientID)

      print "Client Registered:", clientID


   # *** describe how this works - it's the heart of the View-to-Server API
   def registerView(self, message):
      ''' Callback function for Kuatro View Registration. To register with this server,
          views send an OSC message containing the IP address and OSC Port of the view
          to the server.  The server then creates list of OSC connections to all registered
          views. '''

      # parse arguments from OSC Message
      args = message.getArguments()
      ipAddress = args[0]
      port = args[1]

      # When a view registers with the server an OSC Out port is created and added to the 
      # list of ports.  When sending OSC messages, the server will send the same message 
      # to all OSC Ports.  

      if (ipAddress, port) not in self.viewInfo:  # only add view if it is not already registered
         try:     
            self.viewInfo.append((ipAddress, port))          # add view details to 
            self.viewPorts.append(OscOut(ipAddress, port))   # configure OSC Out port and add to list of ports
            print "OSC Configured.  Sending messages to", ipAddress, "on", port
         except Exception, e:
            print e
            sys.exit(1)

            

   def calibrateDevice(self, message):
      '''Updates calibration data from client devices so the Kuatro Server can 
         normalize client data to Virtual World Coordinates. The OSC Message
         should contain the following values:
               deviceID, minX, minY, minZ, maxX, maxY, maxZ
      '''

      # parse arguments from OSC Message
      args = message.getArguments()
      clientID = args[0]
      minX = args[1]
      minY = args[2]
      minZ = args[3]
      maxX = args[4]
      maxY = args[5]
      maxZ = args[6]

      self.deviceCalibrationData[clientID] = (minX, minY, minZ, maxX, maxY, maxZ)


      if self.verbose !=0:
         print "Device", clientID, "calibrated"
         print minX, minY, minZ, maxX, maxY, maxZ
         print "-----------------------------------"



   #####################################
   ###### Kuatro Helper Functions ######
   #####################################


   def calibrateUserCoordinates(self, x, y, z, clientID):
      '''Takes User Coordinate data from a device and translates it to Virtual World 
         coordinates'''

      print self.deviceCalibrationData
      ### Get Coordination Data ###
      minX = self.deviceCalibrationData[clientID][0]
      minY = self.deviceCalibrationData[clientID][1]
      minZ = self.deviceCalibrationData[clientID][2]
      maxX = self.deviceCalibrationData[clientID][3]
      maxY = self.deviceCalibrationData[clientID][4]
      maxZ = self.deviceCalibrationData[clientID][5]


      # Now calibrate the input values
      # Since the Virtual World is an overhead view of the space we must 
      # transpose the Z values from the device to the Y values of the 
      # virtual world

      print x
      print minX
      print maxX
      print 0
      print self.virtualMaxX

      x = max(x, minX)   # keep x in range
      x = min(x, maxX)
      newX = mapValue(x, minX, maxX, 0.1, self.virtualMaxX)  # find the normalized value of X


      # transpose client Z data to Virtual World Y value
      z = max(z, minZ)   # keep z in range
      z = min(z, maxZ)
      newY = mapValue(z, minZ, maxZ, 0.1, self.virtualMaxY)
      print "z:", z, "minZ:", minZ, "maxZ:", maxZ
      print "New Y:", newY

      newZ = 0  # not support Virtual World Z at this moment

      return newX, newY, newZ


   def sendMessage(self, address, *args):
      '''Helper method to send OSC messages using OSC Out port.
         *args allows calling method to send any number of parameters'''


      if len(self.viewPorts) > 0:      # make sure at least one oscOut port is setup

         for oscOut in self.viewPorts:  # loop through all osc ports
            print "Sending message to:", address
            print "Data:", args
            oscOut.sendMessage(address, *args)  # send osc message through osc port

      else:
         print "No OSC out ports are setup"


##### Instantiate a Server
if __name__ == '__main__':
   kuatroServer = KuatroServer(verbose=1)