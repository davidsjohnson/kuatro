# kuatroBegin.py
# 
# This file starts all the components of the Kuatro.  
# To start up the Kuatro:
#     1. Open a Terminal
#     2. cd to the Kuatro directory.  eg.  cd Dropbox/kuatro
#     3. Issue the following command:  sh jython.sh kuatroBegin.py


from kuatroServer import * 
from kuatroBasicView import *
from kuatroKinectClient import *
from kuatroEscherView_v2 import *
from theGlaser import *

#####  Start the Server
server = KuatroServer(verbose = 1)

##### Start the Client ######
# import kuatroMouseClient
kinectClient = KuatroKinectClient() # Requires that a Kinect is connected to the computer.


###### Start the views ###### 
#### Setup and Run the Glaser to handling the audio view
audioList = []

#audioList.append(AudioSample("sounds/state0_mix.aif"))
#audioList.append(AudioSample("sounds/state1_mix.aif"))
#audioList.append(AudioSample("sounds/state2_mix.aif"))
#audioList.append(AudioSample("sounds/state3_mix.aif"))
#audioList.append(AudioSample("sounds/state4_mix.aif"))
#audioList.append(AudioSample("sounds/state5_mix.aif"))

audioList.append(AudioSample("sounds/state0_mix_loop.wav"))
audioList.append(AudioSample("sounds/state1_mix_loop.wav"))
audioList.append(AudioSample("sounds/state2_mix.wav"))
audioList.append(AudioSample("sounds/state3_mix_loop.wav"))
audioList.append(AudioSample("sounds/state4_mix.wav"))
audioList.append(AudioSample("sounds/state5_mix_loop.wav"))
audioList.append(AudioSample("sounds/button_sound.wav"))

glaserView = theGlaser(audioList, False, 400, 500)


##### Start the Escher Middleware
escherView = KuatroEscherView(50506)