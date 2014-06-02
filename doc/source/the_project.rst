The Project
===========

Overview
--------

This project aims at designing a home automation control center. The main characteristics we identified as being essential are the following:

* adaptativeness as regards to home automation protocols
	
	Many protocols, open-source or proprietary, are today used in the field of home automation. To be competitive, a home automation control center must therefore ensure compatibility with all these protocols.
	
	Although, it doesn't seem nor reasonable nor interesting to have an exhaustive compatibility list from the first version of the system onwards. 
	
	That is why we chose to use a plugin system in which users (that is you) can improve the compatibility of their system by downloading and installing new plugins. These plugins extend the compatibility of the box to other protocols or to other hardware parts.
	
	With this system, any interested and motivated user (like you) can just develop new plugins and share them with the community: the only constraint is to respect the interfaces described in the :doc:`api_reference`. 

* remote access to the control center

	Such a system must imperatively be accessible from outside the house. At work or on vacation, the user must be able to keep an eye on the state of his house, but also to remotely modify the automatic working of his house to his liking.
	
	To make all that possible, the system must have an outer interface that other applications (a web server, an Android or iOS app...) can use. We developed a base API plugin, see :doc:`plugins/http_interface` 

	We also developed a cross-platform app using the `Kivy <http://www.kivy.org>`_ framework. The app is described in the :doc:`first_steps` and its python documentation is available : :doc:`majordom_app_api`.
	
* very easy-to-use scenarios creation system

	Once you have connected devices from various protocols to the box, you may want to do a little more than just watching them. 
	
	The idea is to gather the info coming from them and the actions made available by them in order to create custom automatic behaviours from the system, that we call scenarios.
	
	Scenarios consist of infos, actions and other blocks which allow to easily program new automatic behaviours, in a graphical way. In the scenario editor of the Majordom App, you add and move blocks, and create links between nodes. Once you are done building the scenario, you just have to activate it. The simplest scenario would be that a light switches on when a button is pressed. 
	
	To know more about scenarios, see :doc:`api/scenario`.
	
Features
--------

The present version of Majordom is a prototype, it only offers a limited set on features.

Home Automation Hardware Support
++++++++++++++++++++++++++++++++

* **handling of our custom Arduino RF 433MHz modem**
* **handling of the Nexa protocol and the main nexa devices**:
	* Nexa 3 Button Remote
	* Nexa 2 Button Switch
	* Nexa Opening Sensor
	* Nexa Movement Sensor
	* any Nexa-controlled device (remote-controlled plugs...)

Scenarios editing
+++++++++++++++++

* **build graphical scenarios** making use of:
	* the infos and actions made available by the connected devices
	* a set of base processing blocks available in the :doc:`plugins/base_blocks` plugin.
* activate scenarios and **make your home autonomous**

Majordom server interface and Majordom client app
+++++++++++++++++++++++++++++++++++++++++++++++++

* **http-based API** receiving and sending json messages on the server side
* **cross-platform Majordom client app** featuring:
	* **control panel**
		In a single panel, you can access the state of every device connected to Majordom. It also allows you to manually use connected devices.
	* **settings panel**
		It allows you to access the main settings of Majordom.
	* **step-by-step adding device wizard**
		Every action required to add a device to the system is carefully explained: without any previous knowledge of the home automation devices you are using, you are able to add them to Majordom.
	* **touch-optimized scenarios editor**
		This is the main feature of the system. It allows you to take fully control over your home, in a very simple manner.

.. _requirements:

Requirements
------------

In order to run the Majordom server, you need to have the following components installed on your computer:

* Python 2.7 (`Python Downloads <https://www.python.org/downloads/>`_ )
* the pyserial library (`on PyPi <https://pypi.python.org/pypi/pyserial>`_ )
* the bitarray library (`on PyPi <https://pypi.python.org/pypi/bitarray/>`_ )

In order to run the Majordom App, since it has not yet been cross-compiled, you need the Kivy Framework to run it:

* `Kivy Framework <http://kivy.org/#download>`_

.. _installation:

Installation
------------

To run the Majordom server and clients apps, please check first that you fullfil the requirements described above.

Once you do, go to our `GitHub repo <https://github.com/majordom/majordom-server>`_ and download the latest version of the Majordom server app. You then just have to run main.py to launch the system. If you let the :doc:`plugins/http_interface` plugin in the plugins directory, an http server should now be running on your machine.

Now, in order to actually use Majordom, download the client app on `our repo <https://github.com/majordom/majordom-app>`_. Then, follow Kivy's installation guide which matches your own test platform. Once you are able to launch a Kivy app on your platform, just launch the main.py file *the kivy way*.

References
----------

In order to develop Majordom, we used a various set of pre-existing technologies, that are worth checking out if you do not already know them. 

* Arduino

	The Arduino is *the* widest-spread open-source electronics prototyping board. Therefore, it comes with an enormous user community which has already made up solutions to almost all of your problems.
	Check their website at http://arduino.cc/.

* Python

	Python is an easy-to-use and yet powerful programming language. You can write code without knowing much about programming. But you won't either get bored or blocked if you try to build a more complex system with it.
	Check Python at https://www.python.org/.
	
* pySerial

	PySerial is a serial library for Python. It is therefore very useful in order to communicate with the Arduino. We only regret the lack of interruptions handling, which forces you to keep a thread polling the serial interface when you are waiting for an asynchronous communication.
	Check it at http://pyserial.sourceforge.net/.

* bitarray

	bitarray is a library which makes it easier to handle bits sequences in Python. Bits handling is indeed not as easy in Python as it is in C anda library becomes therefore necessary.
	Chech it at https://pypi.python.org/pypi/bitarray/.

* Kivy

	Kivy is an open-source and cross-platform framework for graphical user interfaces. It allows you to develop a single app and then compileit for Windows, Linux, iOS or Android. Its documentation is rather well written and the community using the framework is constantly growing.
	If you need to build an app, don't forget to check http://www.kivy.org.