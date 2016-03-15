# kuatroKinectClient.py       Version 1.0     13-Aug-2014
#     David Johnson, Bill Manaris, and Seth Stoudenmier
#
# The Kuatro Client tracks the x, y, z coordinates of mulitple users 
# within range of a configured depth sensor.  The coordinates are sent via OSC messages
# to the Kuatro Server for coordination within a Virtual World, as defined by the server.  
# 
#  Supported Controllers for the Kautro Client are Microsoft Kinect, model 1414, 
#  and the Asus Xtion Pro.
#
#  See README file for full instructions on using the Kuatro System


from osc import OscOut
from osc import OscIn
from org.OpenNI import  *
from com.primesense.NITE import *
from threading import *
import sys
from gui import *
import pickle
import socket

class KuatroKinectClient():

   FRAME_RATE = 30   # frame rate used by the Kinect

   ##### OSC Namespace #####
   NEW_USER_MESSAGE = "/kuatro/newUser"
   LOST_USER_MESSAGE = "/kuatro/lostUser"
   USER_COORDINATES_MESSAGE = "/kuatro/userCoordinates"
   REGISTER_DEVICE_MESSAGE = "/kuatro/registerDevice"
   CALIBRATE_DEVICE_MESSAGE = "/kuatro/calibrateDevice"


   def __init__(self, serverIpAddress = "localhost", serverPort = 50505):


      self.clientID = socket.gethostbyname(socket.getfqdn())   # find the computer's IP Address to use as unique ID of this device used by Kuatro Server
      self.users = []         # list of users being tracked by this device

      self.isRunning = True   # value is set to false to turn off the thread that is running the Kinect


      self.configureKinect()  # configure and start the Kinect

      # set up calibration display
      self.display = Display("Calibrate Kuatro Client", 400, 400, 0, 0, Color.BLACK)

      # create Menu for calibration
      calibrateMenu = Menu("Calibrate") 
      calibrateMenu.addItemList(["Start", "Stop"], [self.calibrationStart, self.calibrationStop])
      self.display.addMenu(calibrateMenu)

      # add label for instructions
      self.instructions = self.display.drawLabel("Select Calibrate > Start to start the calibration proces.", 20, 175, Color.WHITE)

      # initiate Timer variable
      self.timer = None

      # once Kinect is started and display is setup, establish connection to server and register the client with the Kuatro Server
      self.oscServer = OscOut(serverIpAddress, serverPort)              # setup the OSC Connection to the Kuatro Server
      self.oscServer.sendMessage(KuatroKinectClient.REGISTER_DEVICE_MESSAGE, self.clientID)  # and now send message to register client with server

      # now its registered, calibrate the device with server
      self.calibrateWithServer()


   ##############################
   ###### Event Functions #######
   ##############################

   def addUser(self, userID):
      ''' Adds a new user to the Client when a new user is detected by the Kinect. 
          Send the corresponding OSC Message to the Kuatro Server '''

      if userID not in self.users:     # make sure user is not already being tracked.
         self.users.append(userID)        # then add it to the list of users

         # Delay sending the OSC message to the server so that coordinates are up to date.
         #  (this is necessary becuase Kinect coordinates are not available when user is first
         #   picked up by the Kinect)
         def delayNewUser(userID):
            point = self.userGen.getUserCoM(userID)            # get the location of the users Center of Mass
            x, y, z = point.getX(), point.getY(), point.getZ() # break it down into X, Y, Z values
            self.oscServer.sendMessage(KuatroKinectClient.NEW_USER_MESSAGE, userID, x, y, z, self.clientID)
            # print "User Added:", userID, "location", x, y, z

         delay = 100  # 1/10 of second in milliseconds
         timer = Timer(delay, delayNewUser, [userID], False)
         timer.start()

   def removeUser(self, userID):
      ''' Removes a user from the Client when a lost user is detected by the Kinect.  
          Send the corresponding OSC message to the Kuatro Server '''

      if userID in self.users:      # make sure user is being tracked
         self.users.remove(userID)     # then remove it

         self.oscServer.sendMessage(KuatroKinectClient.LOST_USER_MESSAGE, userID, self.clientID)


   def sendAllUserCoords(self):
      ''' Sends all user coordinates via OSC Messages to the Kuatro Server. 
          This happens for each Kautro Frame '''

      for userID in self.users:                       # for all users being tracked
         point = self.userGen.getUserCoM(userID)            # get the location of the users Center of Mass
         x, y, z = point.getX(), point.getY(), point.getZ() # break it down into X, Y, Z values

         # coordinates of 0, 0, 0 means user is temporarily lost
         # reduce OSC messages by not sending if all 3 are 0
         if x != 0 or y != 0 or z != 0:
            self.oscServer.sendMessage(KuatroKinectClient.USER_COORDINATES_MESSAGE, userID, x, y, z, self.clientID)  # and send it
            # print "User:", userID, "location", x, y, z

      

   ####################################
   ###### Calibration Process #########
   ####################################

   def calibrateWithServer(self):
      '''Calibrate the device with the Kuatro Server by finding the 
         minimum and maximum coordinate values that the device outputs'''

      # Try to load the file if it is there...
      try:
         # load serialized data
         hostname = socket.gethostname()  # find computers host name

         # Uncomment out if too many files are being created by pickle.
         # Make sure to uncomment the same line in calibrationStop
         hostname = hostname.split(".")[0]  # parse the hostname and get the first part of the name so that we just get the name of the computer and not the network domain.

         calibrationFile = open( hostname + ".calibrationData.p", "rb" )   # open the file to read calibration data (apend host name to file for unique ID)
         calibrationData = pickle.load( calibrationFile)       # read calibration data
         calibrationFile.close()                               # close the file

         # min and max values loaded from the file
         self.minX = calibrationData["minX"]
         self.minY = calibrationData["minY"]
         self.minZ = calibrationData["minZ"]
         self.maxX = calibrationData["maxX"]
         self.maxY = calibrationData["maxY"]
         self.maxZ = calibrationData["maxZ"]

         # send calibration info to server
         self.oscServer.sendMessage(KuatroKinectClient.CALIBRATE_DEVICE_MESSAGE, self.clientID, self.minX, self.minY, self.minZ, self.maxX, self.maxY, self.maxZ)
         
         print "Kinect Calibrated:", self.clientID
         print "Min Values", self.minX, self.minY, self.minZ
         print "Max Values", self.maxX, self.maxY, self.maxZ
      
      # The file was not there, so let the user know there is no calibration data
      except:
         # should only reach here if server has never been calibrated.
         self.display.drawLabel("No calibration data found.  Please run calibration process.", 20, 20, Color.WHITE)  # update user message to let them know they need to run the calibration process

         # Since there are no starting values initiate with arbitrary values UPDATE:  This should be standard kinect values to start with
         self.minX = 100000000000  # set min values to an arbitray high value so we know that min values will be smaller
         self.minY = 100000000000
         self.minZ = 100000000000
         self.maxX = -100000000000 # set max values to an arbitray low value so we know that max values will be larger
         self.maxY = -100000000000
         self.maxZ = -100000000000

         # There is no calibration data so let's send default values (default values are estimates of actual Kinect bounds)
         minX = -5000
         minY = -1000
         minZ = 0
         maxX = 5000
         maxY = -1000
         maxZ = 15000
         self.oscServer.sendMessage(KuatroKinectClient.CALIBRATE_DEVICE_MESSAGE, self.clientID, minX, minY, minZ, maxX, maxY, maxZ)



   def  calibrationStart(self):
      ''' This is the Calibration Start Menu Item Callback function. It is 
          used to calibrate the Kinect Device with the installation space. '''

      # remove initial instructions
      self.display.remove(self.instructions)

      # add label for instructions
      self.instructionsLine1 = self.display.drawLabel("Zig-Zag through the room for the system to find", 20, 175, Color.WHITE)
      self.instructionsLine2 = self.display.drawLabel("the space that it can sense (the light will be green).", 20, 200, Color.WHITE)
      self.instructionsLine3 = self.display.drawLabel("Select Calibrate > Stop when done.", 20, 225, Color.WHITE)

      # Recalibrating so reseting starting min and max values to arbitary high and low values
      self.minX = 100000000000  # set min values to an arbitray high value so we know that min values will be smaller
      self.minY = 100000000000
      self.minZ = 100000000000
      self.maxX = -100000000000 # set max values to an arbitray low value so we know that max values will be larger
      self.maxY = -100000000000
      self.maxZ = -100000000000

      ### Create a Timer to run the calibration ###

      def calibration():
         ''' Timer Function to run the calibration '''
         
         userInSpace = False  # assume there is a user not in the space (used to update background color)

         for userID in self.users:
            point = self.userGen.getUserCoM(userID)            # get the location of the users Center of Mass
            x, y, z = point.getX(), point.getY(), point.getZ() # break it down into X, Y, Z values

            # check if values are smaller than current min values
            self.minX = min(x, self.minX)
            self.minY = min(y, self.minY)
            self.minZ = min(z, self.minZ)

            # check if values are larger than current max values
            self.maxX = max(x, self.maxX)
            self.maxY = max(y, self.maxY)
            self.maxZ = max(z, self.maxZ)

            if x != 0 or y != 0 or z != 0:   # if any value is not 0 then there is a user in the space
               userInSpace = True

         if len(self.users) == 0:      # if there are no users being tracked then no users in space
            userInSpace = False

         if userInSpace:  # is a user in the kinect viewing space
            self.display.setColor(Color.GREEN)     # then make background green
         else:
            self.display.setColor(Color.RED)       # otherwise make it red



      # Create the timer
      delay = 1/KuatroKinectClient.FRAME_RATE  * 1000   # milliseconds per frame
      self.timer = Timer(delay, calibration)
      self.timer.start()  # and start it


   def calibrationStop(self):
      ''' Callback function for the Menu Item, Stop.  Stops the Calbration process 
          and sends the updated information to the server '''


      if self.timer:      # is there a time object (avoids null pointer issues)
         self.timer.stop() # if so then stop it

         # now that we are done remove labels
         self.display.remove(self.instructionsLine1)
         self.display.remove(self.instructionsLine2)
         self.display.remove(self.instructionsLine3)

         # and save data with pickle
         calibrationData = { "minX" : self.minX , "minY" : self.minY , "minZ" : self.minZ , "maxX" : self.maxX , "maxY" : self.maxY , "maxZ" : self.maxZ }
         hostname = socket.gethostname() # find computers host name

         # Uncomment out if too many files are being created by pickle.
         # Make sure to uncomment the same line in calibrateWithServer
         hostname = hostname.split(".")[0]  # parse the hostname and get the first part of the name so that we just get the name of the computer and not the network domain.


         calibrationFile = open( hostname + ".calibrationData.p", "wb" )   # open file to write data (apend host name to file for unique ID)
         pickle.dump( calibrationData,  calibrationFile)       # write calibration data
         calibrationFile.close()                               # close the file

         self.calibrateWithServer() # and recalibrate with the Server

         self.instructions = self.display.drawLabel("Calibration data saved and sent to server", 20, 200, Color.WHITE)
         print "Calibration data saved and sent to server"

         self.display.setColor(Color.BLACK)  # set background to black since we are no longer calibrating


   ####################################
   ######### Client Setup #############
   ####################################
   
   def configureKinect(self):
      '''Configure the Motion Sensing device with the OpenNI and Nite
         framework protocols'''

      try:
         # Configuration per OpenNI and NITE framework settings
         self.context = Context()
         license = License("PrimeSense", "0KOIk2JeIBYClPWVnMoRKn5cdY4=")
         self.context.addLicense(license)
         
         self.depthGen = DepthGenerator.create(self.context)
         mapMode = MapOutputMode(640, 480, KuatroKinectClient.FRAME_RATE)      # Requires 640 and 480 as x and y.  Will need to use mapValue to change to coords on current display.
         self.depthGen.setMapOutputMode(mapMode)

         self.context.setGlobalMirror(True)
         self.userGen = UserGenerator.create(self.context)
         
         self.context.startGeneratingAll()

         # setup Observers for new / lost Detection events
         self.userGen.getNewUserEvent().addObserver(NewUserDetector(self))             # new user enters the viewing area
         self.userGen.getLostUserEvent().addObserver(LostUserDetector(self))           # user leaves the viewing area

         # setup thread to run Device
         self.clientThread = Thread(target = self.run)

         self.start()
         print "Kuatro Device Configured and Started"

      except StatusException, e:
         print "Something went wrong.  Device not started."
         print e
         sys.exit(1)
      except Exception, e:
         print "Something went wrong.  Device not started."
         print e
         sys.exit(1) 




   def run(self):
      '''Start the Client via a seperate thread '''

      while self.isRunning:   # is the Kinect Running?
         try:
            self.context.waitAnyUpdateAll()  # then update the frame
            self.sendAllUserCoords()         # and send all coordinate values
            # raise StatusException()
         except:

            print errorStack
            sys.exit(1)
   
   def start(self):
      ''' Start the Kinect tracking '''

      self.isRunning = True
      self.clientThread.start()

   def stop(self):
      ''' Stop the Kinect tracking '''

      self.isRunning = False


#########################################################
####### User Detection Observers(Listeners) #############
#########################################################


# Observer class that detects when a new user enters the viewing space.  Upon detection
# of a new user the update method is called.  
class NewUserDetector(IObserver):

   def __init__(self, client):
      self.client = client

   def update(self, observable, args):

      try:

         # update kuatro client with new user id
         userID = args.getId()
         self.client.addUser(userID)

         print "New User Detected.  ID:", userID

      except Exception, e:

         print e

# Observer class that detects when a user exits the viewing space (there is a 10 second delay).
# Upon detection of a lost user the update method is called.  
class LostUserDetector(IObserver):

   def __init__(self, client):
      self.client = client
      

   def update(self, observable, args):

      # lost user so remove from kuatro client
      userID = args.getId()
      self.client.removeUser(userID)

      print "User", userID, "lost"


if __name__ == '__main__':
   kinectClient = KuatroKinectClient() # Create and start the Kinect Client
