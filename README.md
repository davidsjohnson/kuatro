##Kuatro Framework

###The Kuatro Framework is a framework for developing interactive art and sound installations using motion sensors and other interactive controllers.

For more detailed information, please read LINK TO PAPERS

####Prerequisites:
Kuatro Source Files
Kinect Installation (To use the default Kuatro Client with a Kinect)
	Mac OS X - http://developkinect.com/resource/mac-os-x/install-openni-nite-and-	sensorkinect-mac-os-x
	Windows - http://www.codeproject.com/Articles/148251/How-to-Successfully-Install-	Kinect-on-Windows-Open

	The following files/folders must be in your CLASSPATH:
		com.primesense.NITE.jar
		org.OpenNI.jar

Implementation in Jython:
To help implement the Kuatro Framework in Jython, we provide 3 abstract classes, one for each type of Kuatro Component, Client, Server, and View.  There are also default implementations of these classes that can be used as is.  The abstract classes handle the implementation of the OSC protocol so developers only need to implement the user interaction methods, addUser, moveUser and removeUser.

Abstract Classes:

OscClient:

OscServer:

OscView:


Default Implementations:

KinectClient:

KuatroServer:

BasicView:

Implementation in other languages or by using OSC:
To implement in a language other than Jython, developers can use the following OSC Messaging Protocol.