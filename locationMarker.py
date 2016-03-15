# locationMarker.py    Version 0.5     29-May-2015
#     David Johnson

# LocationMarker is a class to handle the process of marking a specific location
# in a Kuatro virtual space. 
# The LocationMarker only uses the first user in the list of Users from the Kuatro 
# View. Therefore it is probably best if only one user is in the Kuatro Space during 
# configuration. In future, it may be nice to handle multiple users in the space....

from gui import *
from timer import *


class LocationMarker():

   def __init__(self, kuatroView, configTime=5):

      # Initialize Config values
      self.kuatroView = kuatroView
      self.configTime = configTime
      self.isConfiguring = False

      ##### INITIALIZE DISPLAY ######
      self.d = Display("Button Configuration", 400, 300, 450, 0, Color.BLACK)  # open window
      
      # prompt user to move to location and stand for 5 seconds
      labelTxt = "Click anywhere to start configuration Process."
      self.mainLabel = self.d.drawLabel(labelTxt, 10, 10, Color.WHITE, Font("SansSerif", Font.PLAIN, 16))
      self.mainLabel.setSize(400, 60)

      # setup events and buttons
      self.d.onMouseClick(self.clickCallback)
      closeBtn = Button("Close", self.btnCallback) # allow user to close window
      self.d.add(closeBtn, 160, 270)


      ##### INITIALIZE COUNTDOWN TIMER #####
      self.timerCountdown = self.configTime
      self.t = Timer(1000, self.timerFunction)
      self.timerLabel = None

      self.prevCoords = [0, 0, 0]  # initialize previous coord to all 0s

   def timerFunction(self):
      ''' Timer Function to countdown time for setting marker location'''

      if len(self.kuatroView.userCoordinates) > 0:
         userCoords = self.kuatroView.userCoordinates[0]  # for now defaulting to the first user...

         # get difference between current and prev coordinates
         xDiff = abs(userCoords[0] - self.prevCoords[0])
         yDiff = abs(userCoords[1] - self.prevCoords[1])

         self.prevCoords = userCoords # update prevCoords now that we've made the comparison

         if xDiff < 50 and yDiff < 50:
            # check if user has been in same spot (give or take)
            # if so decrement counter
            self.timerCountdown -= 1
         else:
            # if not reset the counter
            self.timerCountdown = self.configTime

         if self.timerCountdown == 0:
            # if countdown finished reset the tool
            self.d.setColor(Color.BLACK)
            text = "%d" % (self.timerCountdown)
            self.timerLabel.setText(text)
            self.timerCountdown = self.configTime

            # reset main label
            labelTxt = "<html><p>Marker Location Set.<br>Click anywhere to start configuration process again.</p></html>"
            self.mainLabel.setText(labelTxt)
            
            self.isConfiguring = False   # change state
            self.t.stop()                # make sure timer is stopped

            #  save button location
            self.kuatroView.setMarkerCoordinates(userCoords)

         else:
            # if countdown is still going 
            text = "%d" % (self.timerCountdown)   # update display
            self.timerLabel.setText(text)


   ## Click Display to Start/Stop Configuration
   def clickCallback(self, x, y):
      ''' Callback to start/stop configuration process'''

      if not self.isConfiguring:
         # if display is clicked and currently not configuring..
         self.d.setColor(Color.GREEN)
         labelTxt = "<html><p>Move to location you would like to mark. Stand in location for %s seconds. (Click anywhere to canel.)</p></html>" % (self.configTime)
         self.mainLabel.setText(labelTxt)
         self.isConfiguring = True     # move to state of configuration process

         # start timer
         if self.timerLabel:
            self.d.remove(self.timerLabel)
         text = "%d" % (self.timerCountdown)
         self.timerLabel = self.d.drawLabel(text, 170, 120, Color.WHITE, Font("SansSerif", Font.PLAIN, 60))
         self.t.start()

      elif self.isConfiguring:
         # if display is clicked and currently configuring..
         self.d.setColor(Color.BLACK)
         labelTxt = "Click anywhere to start configuration Process."
         self.mainLabel.setText(labelTxt)
         self.isConfiguring = False

         # reset timer
         self.t.stop()
         self.timerCountdown = self.configTime

         

   def btnCallback(self):
      ''' Callback function to close display window'''
         
      self.t.stop()  # closing window should stop Timer
      self.d.hide()