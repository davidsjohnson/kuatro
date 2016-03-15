# theGlaser.py        Version 1.6     25-Jun-2015      Seth Stoudenmier and Bill Manaris
#
#
# The "Glaser" is a specific instrument designed in order to facilitate exploring various sounds and quickly
# manipulating their attributes (e.g., frequency, volume, and panning). It consists of three displays with a set number
# of faders each. These displays  work in parallel, i.e., the first slider (across all displays) controls the first assigned
# sound, whereas the second slider (across all displays) controls the second sound, and so on. "The Glaser" allows
# the user to control volume, frequency, and panning of the audio samples simultaneously. Each display's faders
# are oriented to match their natural orientation, i.e. frequency and volume are vertical (low to high), and panning
# is horizontal (left to right). As each fader is adjusted, the corresponding audio is altered accordingly and that
# value is displayed in a textual output window. It is important to note that this does not alter
# the actual audio file, but only what is heard dynamically. The outputted values may then be used in the code that
# drives the installation.
#
# NOTE: When using OSC the acceptable values to be passed in are as follow:
#              - volume is from 0 to 127
#              - frequency is from 1/2 to 2x the frequency of the aduisample for the specific fader
#              - panning is from 0 to 127
#       Failure to use these values will result in a ValueError to be thrown by the fader object being used
#
# OSC-IN ADDRESSES: The oscIn addresses for each sound (Fader IDs range from 1...number of faders)
#              -/volumeFader/<Fader ID>, oscSetVolume
#              -/frequencyFader/<Fader ID>, oscSetFrequency
#              -/panningFader/<Fader ID>, oscSetPanning
#              -/playAudio/<Fader ID>, oscPlayAudio
#              -/loopAudio/<Fader ID>, oscLoopAudio
#              -/stopAudio/<Fader ID>, oscStopAudio
#              -/pauseAudio/<Fader ID>, oscPauseAudio
#              -/resumeAudio/<Fader ID>, oscResumeAudio
#
#
# REVISIONS:
#
#  1.6      25-Jun-2015 (ss) Added more OSC features to Glaser to control each sound individually
#
#  1.5      18-Nov-2014 (ss) OSC is now properly working. Left out minor part that prohibited OSC from working
#                            properly the first time. All faders now print their corresponding value when the mouse
#                            button is released. However, the values are only printed when the faders are controlled
#                            from the panels.
#
#   1.4     15-Nov-2014 (ss) OSC is now running. When theGlaser is run osc will be ready for use on port 57110
#                            for if the user wants to use it. There are value ranges that must be followed if osc is
#                            being used as to avoid a ValueError from the fader. These values are specified above.
#
#   1.3     04-Nov-2014 (ss) Sizing of each display is now based on the number of audio samples in the audio list
#                            combined with the panelWidth and panelHeight that are provided.
#                            Also, the height to width ratio of the panning panel is now opposite of the ratio for the
#                            other two panels, volume and frequency.
#
#   1.2     11-Oct-2014 (ss) Changed the Glaser to accept an audioList (among other parameters) and create the
#                            three displays (volume, frequency, and panning) based on the length of the list.
#
#   1.1     21-Sept-2014 (ss) Now uses the updated guicontrols instead of rectangular sliders
#
#   1.0     16-Dec-2013 (ss, bm) Original implementation using the rectangular sliders
#
#
# TO-DO:
#
#

from music import *
from gui import *
from osc import *
from guicontrols import *

class theGlaser:
   
   def __init__(self, audioList, showPanels=True, panelWidth=400, panelHeight=600):

      # initialize the OSC for this instance of theGlaser
      self.oscIn = OscIn(57115)
      
      # initialize the list of audio samples
      self.audioList = audioList

      # initialize the min and max volume range
      self.minVolume = 0
      self.maxVolume = 127

      # start the loop for each sound in the audioList; set starting volume at 0
      # for i in self.audioList:
      #    i.setVolume(self.minVolume)
      #    i.loop()
      
      # initialize the min and max panning range
      self.minPanning = 0
      self.maxPanning = 127

      # saving whether or not to show panels
      self.showPanels = showPanels

      if (self.showPanels):

         # initialize all of the lists to hold the faders
         self.volumeFaders = []
         self.frequencyFaders = []
         self.panningFaders = []


         # saves the panelWidth and panelHeight
         self.panelWidth = panelWidth
         self.panelHeight = panelHeight

         # determine the sizing of each fader depending on width and height of the panels
         self.gap = int(self.panelWidth / (3 * len(self.audioList) + 1))
         self.faderWidth = self.gap * 2
         self.faderHeight = int(self.panelHeight - (self.gap * 2.0))

         # initializing the colors used for each panel and their faders
         self.panelBackground = Color.BLACK

         self.faderBackground = Color(20, 20, 20)    # each panel's faders have the same background color
         self.volumeOutline = Color(0, 150, 0)
         self.volumeForeground = Color(0, 255, 0)
         self.frequencyOutline = Color(150, 0, 0)
         self.frequencyForeground = Color(255, 0, 0)
         self.panningOutline = Color(150, 150, 0)
         self.panningForeground = Color(255, 255, 0)

         # creates the displays
         self.__createVolumeDisplay__(self.audioList)
         self.__createFrequencyDisplay__(self.audioList)
         self.__createPanningDisplay__(self.audioList)

      # initialize the osc capabilities
      # loops for each audiosample creating an osc function for volume, frequency, and panning
      # that is referenced by a oscIn.onInput() statement
      for i in range(len(audioList)):

         # osc volume function for the fader at position i in the audioList
         def oscSetVolume(message, audioIndex=i):
            args = message.getArguments()
            volume = args[0]

            if self.showPanels:
               self.audioList[audioIndex].setVolume(volume)
               self.volumeFaders[audioIndex].setValue(volume)
            else:
               self.audioList[audioIndex].setVolume(volume)

         # osc frequency function for the fader at position i in the audioList
         def oscSetFrequency(message, audioIndex=i):
            args = message.getArguments()
            frequency = args[0]
            if self.showPanels:
               self.audioList[audioIndex].setFrequency(frequency)
               self.frequencyFaders[audioIndex].setValue(frequency)
            else:
               self.audioList[audioIndex].setFrequency(frequency)

            print("Audio " + str(audioIndex+1) + " frequency set:", frequency)

         # osc panning function for the fader at position i in the audioList
         def oscSetPanning(message, audioIndex=i):
            args = message.getArguments()
            panning = args[0]
            if self.showPanels:
               self.audioList[audioIndex].setPanning(panning)
               self.panningFaders[audioIndex].setValue(panning)
            else:
               self.audioList[audioIndex].setPanning(panning)

         # osc play function for audiosamples assigned to each fader
         def oscPlayAudio(message, audioIndex=i):
            audioList[audioIndex].play()
            print("Audio " + str(audioIndex) + " play")

         # osc loop function for audiosamples assigned to each fader
         def oscLoopAudio(message, audioIndex=i):
            audioList[audioIndex].loop()
            print("Audio " + str(audioIndex) + " loop")

         # osc stop function for audiosamples assigned to each fader
         def oscStopAudio(message, audioIndex=i):
            audioList[audioIndex].stop()
            print("Audio " + str(audioIndex) + " stop")

         # osc puase function for audiosamples assigned to each fader
         def oscPauseAudio(message, audioIndex=i):
            audioList[audioIndex].pause()
            print("Audio " + str(audioIndex) + " pause")

         # osc resume function for audiosamples assigned to each fader
         def oscResumeAudio(message, audioIndex=i):
            audioList[audioIndex].resume()
            print("Audio " + str(audioIndex) + " resume")

         # oscIn.onInput() statements made for each audiosample and fader combination
         self.oscIn.onInput("/volumeFader/" + str(i +1), oscSetVolume)
         self.oscIn.onInput("/frequencyFader/" + str(i +1), oscSetFrequency)
         self.oscIn.onInput("/panningFader/" + str(i +1), oscSetPanning)
         self.oscIn.onInput("/playAudio/" + str(i +1), oscPlayAudio)
         self.oscIn.onInput("/loopAudio/" + str(i +1), oscLoopAudio)
         self.oscIn.onInput("/stopAudio/" + str(i +1), oscStopAudio)
         self.oscIn.onInput("/pauseAudio/" + str(i +1), oscPauseAudio)
         self.oscIn.onInput("/resumeAudio/" + str(i +1), oscResumeAudio)


   # creates the volume display relative to the number of audio samples
   def __createVolumeDisplay__(self, audioList):
      volumeDisplay = Display("Volume", self.panelWidth, self.panelHeight)
      volumeDisplay.setColor(self.panelBackground)
      x1 = self.gap        # the coordinates for the first VFader; x1 and x2 will be
      y1 = self.gap        # incremented with the addition of more VFaders
      x2 = x1 + self.faderWidth
      y2 = y1 + self.faderHeight
      for i in range(len(self.audioList)):
         fader = VFader(x1, y1, x2, y2, self.minVolume, self.maxVolume, self.minVolume, audioList[i].setVolume,
                       self.volumeOutline, self.faderBackground, self.volumeForeground)
         self.volumeFaders.append(fader)
         volumeDisplay.add(fader)
         x1 += self.gap + self.faderWidth
         x2 += self.gap + self.faderWidth

         # function created when the faders are each created so that when the onMouseUp event is triggered for a fader
         # it will call this function and print the value of the fader
         def printValue(x, y, faderIndex=i):
            print "Volume fader " + str(faderIndex +1) + " value: " + str(self.volumeFaders[faderIndex].getValue())

         # displays the value of the fader when the mouse is released;
         # using onDrag interrupts the fader's change in value and using onClick or onDown
         # only show the initial value before the user changes the value
         fader.onMouseUp(printValue)
      
   # creates the frequency display relative to the number of audio samples
   def __createFrequencyDisplay__(self, audioList):
      frequencyDisplay = Display("Frequency", self.panelWidth, self.panelHeight)
      frequencyDisplay.setColor(self.panelBackground)
      x1 = self.gap        # the coordinates for the first VFader; x1 and x2 will be
      y1 = self.gap        # incremented with the addition of more VFaders
      x2 = x1 + self.faderWidth
      y2 = y1 + self.faderHeight
      for i in range(len(self.audioList)):
         minFrequency = audioList[i].getFrequency() /2
         maxFrequency = audioList[i].getFrequency() *2
         print i, "orig freq:", self.audioList[i].getFrequency()
         fader = VFader(x1, y1, x2, y2, minFrequency, maxFrequency, minFrequency, audioList[i].setFrequency,
                                            self.frequencyOutline, self.faderBackground, self.frequencyForeground)
         self.frequencyFaders.append(fader)
         frequencyDisplay.add(fader)
         x1 += self.gap + self.faderWidth
         x2 += self.gap + self.faderWidth

         # function created when the faders are each created so that when the onMouseUp event is triggered for a fader
         # it will call this function and print the value of the fader
         def printValue(x, y, faderIndex=i):
            print "Frequency fader " + str(faderIndex +1) + " value: " + str(self.frequencyFaders[faderIndex].getValue())

         # displays the value of the fader when the mouse is released;
         # using onDrag interrupts the fader's change in value and using onClick or onDown
         # only show the initial value before the user changes the value
         fader.onMouseUp(printValue)

   # creates the panning display relative to the number of audio samples;
   # since panning is thought of in a horizontal notion the faderWidth is used for the fader's height
   # and the faderHeight is used for the fader's width
   def __createPanningDisplay__(self, audioList):
      panningDisplay = Display("Panning", self.panelHeight, self.panelWidth)
      panningDisplay.setColor(self.panelBackground)
      x1 = self.gap        # the coordinates for the first VFader; x1 and x2 will be
      y1 = self.gap        # incremented with the addition of more VFaders
      x2 = x1 + self.faderHeight
      y2 = y1 + self.faderWidth
      for i in range(len(self.audioList)):
         fader = HFader(x1, y1, x2, y2, self.minPanning, self.maxPanning, (int)(self.maxPanning /2),
                        audioList[i].setPanning, self.panningOutline, self.faderBackground, self.panningForeground)
         self.panningFaders.append(fader)
         panningDisplay.add(fader)
         y1 += self.gap + self.faderWidth
         y2 += self.gap + self.faderWidth

         # function created when the faders are each created so that when the onMouseUp event is triggered for a fader
         # it will call this function and print the value of the fader
         def printValue(x, y, faderIndex=i):
            print "Panning fader " + str(faderIndex +1) + " value: " + str(self.panningFaders[faderIndex].getValue())

         # displays the value of the fader when the mouse is released;
         # using onDrag interrupts the fader's change in value and using onClick or onDown
         # only show the initial value before the user changes the value
         fader.onMouseUp(printValue)


if __name__ == "__main__":
   oscOut = OscOut("localhost", 57115)

   audio1 = AudioSample("audio/audio1.wav")
   audio2 = AudioSample("audio/audio2.wav")
   audio3 = AudioSample("audio/audio3.wav")
   audio4 = AudioSample("audio/audio4.wav")
   audio5 = AudioSample("audio/audio5.wav")
   audio6 = AudioSample("audio/audio6.wav")
   audio7 = AudioSample("audio/audio7.wav")
   audio8 = AudioSample("audio/audio8.wav")
   theGlaser([audio1, audio2, audio3, audio4, audio5], True, 400, 500)

   oscOut.sendMessage("/volumeFader/3", 80)
   oscOut.sendMessage("/volumeFader/2", 80)
   oscOut.sendMessage("/volumeFader/1", 80)
   # oscOut.sendMessage("/frequencyFader/2", 1.5)
   oscOut.sendMessage("/panningFader/3", 25)
