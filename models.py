# -*- coding: utf-8 -*-

from generic_models import IDableObject, SettableObject
from scenario import Block, OutputNode, SimpleInputNode

class Protocol(SettableObject):
	""" In the model used to design the box, a class deriving from 
	:class:`models.Protocol` implements all the methods that are 
	necessary to make the box compatible with a new home automation
	protocol. For instance, every protocol class should implement
	the function processing an incoming message from the associated
	modem.
	
	The class :class:`models.Protocol` defines the minimal public 
	interface that any protocol class should implement, in order 
	to allow other entities to use it.  
	
	It should **not** be directly instantiated.
	
	Any protocol plugin should derive from it. To see what the actual
	implementation of a protocol looks like, you may for instance refer
	to the classes :class:`protocols.nexa.Nexa` and 
	:class:`protocols.oregon.Oregon`.    
	
	"""
	
	def get_settings_format(self):
		print 'setting settings_format'
		driver_options = []
		for driver in self.kernel.drivers:
			if driver.driver_type == self.driver_type:
				driver_options.append(driver.settings['name'])
		
		result = list(self._settings_format)
		result.append(
					{ 'type': 'options',
					'title': 'Driver',
					'desc': 'The driver used to send and receive radio signals',
					'options': driver_options,
					'key': 'driver' })
		
		return result

	def set_settings_format( self, value ):
		print 'getting settings_format'
		self._settings_format = value
	
	settings_format = property(get_settings_format, set_settings_format)

	def __init__(self):
		IDableObject.__init__(self)
		SettableObject.__init__(self)
		
		self.kernel = None
		
		self.driver = None
		self.driver_type = ''
		
		self.instantiable_devices = []
		self.devices = []
	
		self.settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the protocol',
					'key': 'name',
					'disabled': True },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the protocol',
					'key': 'description',
					'disabled': True }
					]

# 	def get_settings_format(self):
# 		""" Overrides the same method of the :class`SettableObject` in order 
# 		to dynamically add the available drivers to the settings_format.
# 		
# 		"""
# 
# 		driver_options = []
# 		for driver in self.kernel.drivers:
# 			if driver.driver_type == self.driver_type:
# 				driver_options.append(driver.settings['name'])
# 		
# 		result = list(self.settings_format)
# 		result.append(
# 					{ 'type': 'options',
# 					'title': 'Driver',
# 					'desc': 'The driver used to send and receive radio signals',
# 					'options': driver_options,
# 					'key': 'driver' })
# 		
# 		return result
	
	def set(self, settings):
		""" Overrides the same method of the :class`SettableObject` in order 
		to dynamically manage the 'driver' field of the settings that is specific
		to Protocols.
		
		"""
		
		# Cette methode implemente le traitement d'un setting de type 'option'
		super(Protocol, self).set(settings)
		
		if settings.has_key('driver'):
			if self.settings.has_key('driver'):
				for driver in self.kernel.drivers:
					if driver.settings['name'] == settings['driver']:
						self.driver = driver
						self.driver.bind(self)
						self.settings['driver'] = settings['driver']
			else:
				self.settings['driver'] = settings['driver']
	
	# def get_handled_devices(self):
		# """ Presents the different types of devices handled by this protocol.
		
		# It does not mean that the user can instantiate them himself: some may 
		# not need interventiion of the user on the software part to be added
		# to the system. Still, this method lets the user know what kinds of
		# devices this protocol added support for.
				
		# :return: A list of python dictionaries describing every type of device handled by this protocol
		
		# The format of each python dictionary returned is the following:
		
		# * name
		# * description
		# * user_instantiable
		# * (device_code)
		# * (settings)
		
		# The `user_instantiable` parameter is a :class:`boolean`. It specified whether
		# or not the user can instantiate himself the device. For instance, if we take 
		# into consideration the :class:`protocols.nexa.Nexa` protocol, the NexaRemote 
		# cannot be instantied by the user; they are automatically detected by the system
		# when the user presses one of the button of the actual remote. On the other side, 
		# a NexaDevice can be instantiated by the user himself and he will then sync/pair 
		# it to an actual Nexa actuator.
		
		# The two last keys of the dictionary only exist if the device can be instantiated 
		# by the user, that is when the user_instantiable value is :const:`True`. 
		
		# `device_code` is an integer which characterizes a type of device. It must be
		# given as first argument at the call of the :func:`models.Protocol.add_device`
		# method. This method creates a new device whose `device_code` is the
		# one given using the initial settings given as argument.
		
		# `settings` is a python dictionary describing the settings available for the 
		# given type of device. It is the same as the dictionary returned by the
		# :func:`models.Device.get_settings` method of a :class:`models.Device`.
		
		# """
	
		# return [i.device_infos for i in self.instantiable_devices]
	
	def add_device(self, device_key, settings):
		""" Creates and adds to the system a new device whose :const:`device_code` is
		the :const:`device_code` given as argument. The :const:`device_key` is known by 
		the associated Device Model.
		
		:param device_code: The device_key of the new device to create
		:type device_code: :class:`string`
		:param settings: The initial settings to apply to the newly instantiated Device.
		:type settings: :class:`dict`
		:return: :const:`True` if everything went well, :const:`False` if the device_code given does not exist or the python dictionary returned by :func:`models.Device.set` if something was wrong with the settings given.
		:rtype: :class:`bool` or :class:`dict`
		"""
		
		new_device = self.handled_devices[device_key](self, settings)
		
		self.devices.append(new_device)
		
		self.kernel.add(new_device)
		for i in new_device.informations:
			self.kernel.add(i)
		for a in new_device.actions:
			self.kernel.add(a)
					
		return new_device
	
	def get_devices(self):
		""" Get a list of devices currently managed by this protocol.
		
		:return: a list of devices currently managed by the protocol
		:rtype: :class:`list` of :class:`models.Device`
				
		"""
		
		return self.devices
	
	def process_message(self, message):
		""" *(abstract method)* Processes a message sent by the modem to which the Protcol is attached,
		through its Driver. When it receives an incoming message, the Driver calls
		the method :class:`models.Protocol.process_message` of every Protocol that
		has previously subscribed to it.
		
		The :const:`message` given as argument has a format that is known by the Protocol.
		A Protocol cannot work with any modem: it has a compatibility list and knows 
		therefore the format of message it is going to receive from its modem's Driver. 
		
		It **must** be implemented in any derived class.
		
		"""
		pass

class Driver(SettableObject):
	""" In the model used to design the box, a class deriving from 
	:class:`models.Driver` implements the way the box communicates 
	with an external hardware part. Hardware parts may for instance 
	be radio modems, as it is the case with the 
	:class:`plugins.arduino_radio.ArduinoRadio` driver.
	
	In the case of the hardware being a modem, this class has then
	two main features to implement: the process of receiving a 
	message and the process of sending one.
	In the first case, the driver must implement the way it 
	communicates with hardware parts. For the example of the
	:class:`plugins.arduino_radio.ArduinoRadio`, the mini 
	communication protocol used is described in the :doc:`/arduino` section
	
	Then, once the message has been recovered from the hardware part,
	it must be transmitted to the protocols that use this 
	hardware as a communication medium in order to get the
	actual content of the message. This is implemented
	through a 'subscription' process: protocols subscribe to 
	the driver they want to get their messages from when
	their associated driver is set. 
	
	The class :class:`models.Driver` defines the minimal public 
	interface that any driver class should implement, in order 
	to allow other entities to use it.  
	
	It should **not** be directly instantiated.
	
	Any driver plugin should derive from it. To see what the actual
	implementation of a drivers looks like, you may for instance refer
	to the class :class:`plugins.arduino_radio.ArduinoRadio`.    
	
	"""
	def get_settings_format(self):
		return self._settings_format

	def set_settings_format( self, value ):
		self._settings_format = value
		
	settings_format = property(get_settings_format, set_settings_format)

	def __init__(self):
		IDableObject.__init__(self)
		SettableObject.__init__(self)
		
		self.settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the driver',
					'key': 'name',
					'disabled': True },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the driver',
					'key': 'description',
					'disabled': True }
					]

class Interface(SettableObject):
	""" The class :class:`models.Interface` defines the minimal public 
	interface that any interface class should implement, in order 
	to allow other entities to use it.  
	
	It should **not** be directly instantiated.
	
	Any interface plugin should derive from it. To see what the actual
	implementation of a drivers looks like, you may for instance refer
	to the class :class:`plugins.http_inferface.HTTPInterface`.    
	
	"""
	
	pass

class Device(SettableObject):
	""" The class :class:`models.Device` defines the minimal public 
	interface that any Device class should implement, in order 
	to allow other entities to use it.  
	
	It should **not** be directly instantiated.
	
	Any Device plugin should derive from it. To see what the actual
	implementation of a Device looks like, you may for instance refer
	to the class :class:`plugins.nexa.NexaDevice`.    
	
	"""
	
	pass

class DeviceModel(IDableObject):
	""" The DeviceModel class is particularly important in Majordom: it is the way we chose to show the user what devices he was able to add to his home automation system. Moreover, the device models are highly important in the process of adding the device to the system: it is the device models that are called when you want to add a device to Majordom. To sum up, they offer the necessary abstraction layer to the user so that he can know what devices he can add to his system and how to do it.

	In particular, the :attr:`adding_type` specifies if the corresponding device must be synced or if will be automatically detected by the system. It is hughly important when it comes to the adding device wizard of the graphical user interface.
	
	The class :class:`models.DeviceModel` defines the minimal public 
	interface that any device model class should implement, in order 
	to allow other entities to use it.  
	
	It should **not** be directly instantiated.
	
	Any other device model should derive from it. To see what the actual
	implementation of a device model looks like, you may for instance refer
	to the class :class:`plugins.nexa.NexaDeviceModel`.    
	
	"""
	
	id = ''
	protocol_id = ''
	name = ''
	adding_type = ''
	device_key = ''
	instructions = ''
	
	def __init__(self, kernel):
		
		super(DeviceModel, self).__init__()
		self.kernel = kernel
		self.protocol = self.kernel.get_protocol(self.protocol_id)
		
	def add_instance(self, settings = None):
		
		# TODO: vérifier l'intégrité des settings
		new_device = self.protocol.add_device(self.device_key, settings)
		return new_device

	def start_auto_detect(self):
		self.protocol.auto_detect = True
	
	def stop_auto_detect(self):
		del self.protocol.detected_devices[:]
		self.protocol.auto_detect = False

class Action(Block):
	""" Class used to wrap an action made available by a device.
	
	"""

	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the action',
					'key': 'name' },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the action',
					'key': 'description' }
					]
	
	def __init__(self, key, primary, callback, arguments, settings, device = None, block = None):
		
		Block.__init__(self, settings)
		
		self.key = key
		self.primary = primary
		self.device = device
		self.block = block
		self.callback = callback
		self.callback_args_format = arguments
		self.set(settings)
		
		if self.primary:
			self.id = self.device.id + "_" + self.key
		else:
			self.id = self.block.id + "_" + self.key
		
		# Definition de l'interface de type "Block", c'est-à-dire 
		# de tous les noeuds d'entree de l'action  
		self.trigger_input = SimpleInputNode(self, 'trigger', 'trigger', 'bool')
		self.nodes = [self.trigger_input]
		for arg in self.callback_args_format:
			self.nodes.append(SimpleInputNode(self, arg['key'], arg['type'], arg['name']))

	def execute(self, arguments):
		""" Execute the action with the given arguments.
		
		"""
		
		print 'executing action ' + self.id
		# TODO: verifier que la structure des arguments method_args_format est bien respectee 
		self.callback(arguments)
		
	def process(self, changed_input):
		""" Part of the Block facet of an Action: it is the method called when one of the inputs
		of the Action (considered as a Block) changes. 
		
		If the inputs of the action block are relevant, then the action is executed, using the values of the corresponding input nodes as parameters for the execution.
		
		"""
		
		if changed_input == self.trigger_input and self.trigger_input.get_value():
			execute_arguments = []
			check_args = True
			for n in self.nodes:
				if n != self.trigger_input:
					if n.get_value() == None:
						check_args = False
					else:
						execute_arguments.append((n.key, n.get_value()))
			if check_args:
				self.execute(dict(execute_arguments))

class Information(Block):
	""" Class used to wrap an information made available by a device.
	
	"""
	
	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the information',
					'key': 'name' },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the information',
					'key': 'description' },
					{ 'type': 'string',
					'title': 'Type',
					'desc': 'Type of the information',
					'key': 'type',
					'disabled': True}
					]
	
	def __init__(self, key, primary, value_type, settings, device = None, block = None):
		
		Block.__init__(self, settings)
		
		self.key = key
		self.type = value_type
		self.primary = primary
		self.device = device
		self.block = block
		self.set(settings)
		
		if self.primary:
			self.id = self.device.id + "_" + self.key
		else:
			self.id = self.block.id + "_" + self.key
		
		# Definition de l'interface Block de l'info : c'est un bloc avec un seul output		
		self.output = OutputNode(self, 'output', 'Value', self.type)
# 		self.output = OutputNode(key = 'output',
# 								 value_type = self.type,
# 								 name = 'Value',
# 								 block = self)
		self.nodes = [self.output]
		
	def update(self, new_value):
		""" Updates the Information with a new value.
		
		"""
		
		print 'updating info ' + self.id
		result = False
		if self.check_value(new_value):
			self.output.add_value(new_value)
			result = True
		return result
		
	def check_value(self, new_value):
		""" *(Internal)* Checks if the new value given to update is ok.
		
		"""
		
		# TODO: verifier que la nouvelle valeur donnee est du bon type
		return True
	
	def get_value(self):
		""" Returns the last value of the information.
		"""
		
		return self.output.get_value()
	
	def get_values(self):
		""" Returns the values of the information between the *start_time* and the *ed_time* parameters.
		
		"""
		
		return self.output.get_values()
				
class BlockModel(IDableObject):
	""" Similarly to the DeviceModel, the BlockModel is used to show the users the available blocks that he can use is his scenarios. Once again, they represent an abstraction layer between the real block and the user.
	
	"""
	
	kernel_needed = False
	
	def __init__(self, yeah_id, name, description, block_class):
		
		IDableObject.__init__(self)
		self.id = yeah_id
		self.name = name
		self.description = description
		self.block_class = block_class
	
	def get_instance(self, settings, block_id):
		
		return self.block_class(block_id, settings = settings)