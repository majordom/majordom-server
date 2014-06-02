# -*- coding: utf-8 -*-

from serial import Serial, SerialException
from threading import Thread
from bitarray import bitarray
from math import ceil, log
from time import sleep
from serial.tools.list_ports import comports
from Queue import Queue

from generic_models import AttributeNotSet
from models import Driver

class RadioSequenceReception(Thread):
	""" Subclass of :class:`threading.Thread`. It is the thread used to poll the Serial interface in order to detext whether or not an incoming message has arrived. If a new message is available, it is added to the driver's buffer to be subsequently sent to all the driver's observers by the RadioSequenceProcessing thread.
	
	"""
	
	def __init__(self, driver, serial):
		
		Thread.__init__(self)
		self.driver = driver
		self.serial = serial
		self.running = True
	
	def run(self):
		""" Function called when the thread is launched.
		"""
		
		while self.running:
			sleep(0.001)
			sequence = []
			if self.serial.inWaiting() > 0:
				byte = self.serial.read()
				if len(byte) > 0:
					while ord(byte) != 255:
						byte = self.serial.read()
						sequence.append(ord(byte))
					#self.processing_method(sequence)
					self.driver.reception_buffer.put(sequence)
	
	def stop(self):
		""" Function called to stop the thread.
		"""
		
		self.running = False

class RadioSequenceProcessing(Thread):
	""" Subclass of :class:`threading.Thread`. It is the thread that waits for incoming radio messages in the buffer and processes them one after the other.
	
	"""
	
	def __init__(self, driver):
		
		Thread.__init__(self)
		self.driver = driver
		self.running = True
	
	def run(self):
		""" Function called when the thread is launched.
		"""
		
		while self.running:
			current_sequence = self.driver.reception_buffer.get()
			print 'message received'
			for protocol in self.driver.protocols:
				protocol.process_message(current_sequence)
	
	def stop(self):
		""" Function called to stop the thread.
		"""
		
		self.running = False

# Plugin importable permettant à la centrale de communiquer en radio
class ArduinoRadio(Driver):
	""" Driver class implementing the interface between the computer
	running Majordom and the Arduino, which is used as 
	a 433MHz radio modem. 
	
	"""
	
	def get_settings_format(self):
				
		print 'setting settings_format'
		com_port_options = []
		for com_port in comports():
			com_port_options.append(com_port[1])
			
		result = list(self._settings_format)
		result.append(
					{ 'type': 'options',
					'title': 'COM Port',
					'desc': 'The COM port used to communicate with the hardware modem.',
					'options': com_port_options,
					'key': 'com_port' })
		
		return result

	def set_settings_format( self, value ):
		print 'getting settings_format'
		self._settings_format = value
	
	settings_format = property(get_settings_format, set_settings_format)
	
	driver_type = 'radio_433'
	
	def __init__(self):
		super(ArduinoRadio, self).__init__()
		
		self.id = 'arduino_radio'
		
		self.set({'name': 'Arduino Radio',
				'description': 'Driver enabling the use of the Arduino as 433 MHz AM radio transmitter.',
				'com_port': 'No COM port specified'})
		
		self.com_port = None
		self.serial = None
		self.reception_thread = None
		self.reception_buffer = Queue()
		self.protocols = []
		
		self.processing_thread = RadioSequenceProcessing(self)
		self.processing_thread.start()
				
# 	def get_settings_format(self):
# 		""" Overrides the same method of the :class`SettableObject` in order 
# 		to dynamically add the available COM ports to the settings_format.
# 		
# 		"""
# 
# 		com_port_options = []
# 		for com_port in comports():
# 			com_port_options.append(com_port[1])
# 			
# 		result = list(self.settings_format)
# 		result.append(
# 					{ 'type': 'options',
# 					'title': 'COM Port',
# 					'desc': 'The COM port used to communicate with the hardware modem.',
# 					'options': com_port_options,
# 					'key': 'com_port' })
# 		
# 		return result
	
	def set(self, settings):
		""" Overrides the same method of the :class`SettableObject` in order 
		to dynamically manage the 'com_port' field of the settings that is specific
		to Drivers.
		
		"""
		
		# Cette methode implemente le traitement d'un setting de type 'option'
		super(ArduinoRadio, self).set(settings)
		
		if settings.has_key('com_port'):
			if self.settings.has_key('com_port'):
				for com_port in comports():
					if settings['com_port'] == com_port[1]:
						self.com_port = com_port[0]
						self.settings['com_port'] = settings['com_port']
						self.initialize_radio_reception()
			else:
				self.settings['com_port'] = settings['com_port']
	
	def initialize_radio_reception(self):
		""" Sets the serial communication used by the domotic 
 		box to communicate with the Arduino. If the given COM
 		port number is not valid (i.e. it raises a SerialException
 		when we try to open the connection) the method raises 
 		the same serial.SerialException.

		"""
		
		# On cree une nouvelle instance de la classe Serial qui gère la connexion serie
		new_serial = Serial()
		
		# On specifie tous ses paramètres avant d'ouvrir le port serie
		new_serial.port = self.com_port
		new_serial.baudrate = 9600
		new_serial.timeout = 1
		new_serial.setDTR(False) # Necessaire pour que l'Arduino ne se reset pas à chaque fois que l'ordi lui envoie un message
		
		# L'ouverture du port peut lever une exception serial.SerialException qu'il faut gerer
		try:
			new_serial.open()
		except SerialException, e:
			raise e # On traitera le cas d'erreur en amont
		else:
			self.serial = new_serial
		
			if self.reception_thread != None:
				self.reception_thread.stop()
							
			self.reception_thread = RadioSequenceReception(self, self.serial)
			self.reception_thread.start()
	
	def bind(self, protocol):
		""" Adds the protocol object given as argument
		to the list of protocols that receive their messages
		through this modem. 
		When the modem receives a radio sequence, it will 
		send it to the whole list of its observers.
		   
		"""
		
		if not protocol in self.protocols:
			self.protocols.append(protocol)
			
	def unbind(self, protocol):
		"""
		"""
		
		if protocol in self.protocols:
			self.protocols.remove(protocol) 
	
	def notify_protocols(self, message):
		""" *(Internal)* Notifies all the protocols that are observing this
		modem that an incoming radio message has arrived.
		The received sequence is given as argument so that each
		protocol can handle the decoding.
		
		"""
		
		for protocol in self.protocols:
			protocol.process_message(message)
	
	def format_arg(self, binary):
		""" *(Internal)* Formats a binary sequence so that it fits the format 
		of the parameters of a command sent to the Arduino. This
		method is called by the send_sequence method.

		"""
		
		formatedArg = (7-len(binary)%7)*'0' + binary
		loop_range = reversed(range(len(formatedArg)/7-1))
		for i in loop_range:
			formatedArg = formatedArg[0:7*(i+1)] + '0' + formatedArg[7*(i+1):]
		formatedArg = '11111' + (3-len(bin((7-len(binary)%7))[2:]))*'0' + bin((7-len(binary)%7))[2:] + '0' + formatedArg
		return formatedArg

	
	def send_message(self, message):
		""" Sends the radio message given as an argument.
		
		The *message* dictionary must have the following format :
		
		+-----------------------------------------+---------------+
		| Key                                     | Type          | 
		|                                         |               | 
		+=========================================+===============+
		| number_of_repetitions                   | int           | 
		+-----------------------------------------+---------------+
		| base_radio_pulse_length_in_microseconds | int           |
		+-----------------------------------------+---------------+
		| symbol_1                                | binary_string |
		+-----------------------------------------+---------------+
		| symbol_2                                | binary_string |
		+-----------------------------------------+---------------+
		| ...                                     | binary_string |
		+-----------------------------------------+---------------+
		| symbol_n                                | binary_string |
		+-----------------------------------------+---------------+
		| symbol_coded_message                    | symbols_list  |
		+-----------------------------------------+---------------+
		
		"""

		try:
			if self.serial == None: 
				raise AttributeNotSet("The serial interface of the 433 Mhz modem has not been set.")
			
			args = [bin(message[0])[2:], bin(message[1])[2:]]
			args += message[2:len(message)-1]
			
			bin_coded_message = ''
			for sym in message[len(message)-1]:
				bin_coded_message += (int(ceil(log((len(message)-3),2))) - len(bin(sym)[2:]))*'0' + bin(sym)[2:]
			
			args += [bin_coded_message]
			
			serial_message = '10000010'
			for arg in args:
				serial_message += self.format_arg(arg)
			
			serial_message += '11111111'
			byte_sequence = bitarray(serial_message).tobytes()
			
			for i in range(5):
				for byte in byte_sequence:
					self.serial.write(byte)
				i += 1
				sleep(0.1)
				
		except Exception, e:
			raise e


""" Set of attributes which describe the plugin, in order 
to add it to the kernel and then be able to describe it
to the user.  

"""
plugin_type = "driver"
name = "Arduino Radio"
description = "A driver plugin which allows the use of the Arduino (correctly configured) as a radio 433MHz AM transmitter."
driver_class = ArduinoRadio