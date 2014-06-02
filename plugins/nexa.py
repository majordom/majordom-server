# -*- coding: utf-8 -*-

from models import Information, Action, Protocol, Device, DeviceModel
from time import sleep
from random import random

class Nexa(Protocol):
	""" Main class of the Nexa protocol plugin.

	"""

	def __init__(self, kernel):
		super(Nexa, self).__init__()
		
		self.kernel = kernel
		self.id = 'Nexa'
		self.driver_type = 'radio_433'
		self.auto_detect = False		
		self.detected_devices = []
		
		self.set({	'name': "Nexa",
					'description': "Common home automation protocol",
					'driver': 'No driver specified yet.'})
		
		self.handled_devices = {'NexaDevice' : NexaDevice,
								'Nexa3ButtonRemote': Nexa3ButtonRemote,
								'Nexa2ButtonSwitch': Nexa2ButtonSwitch,
								'NexaMovementSensor': NexaMovementSensor,
								'NexaOpeningSensor': NexaOpeningSensor}
				
		# TODO: vérifier mais ça devrait être fait par SettableObject
		# self.settings = {}
		# TODO: vérifier mais ça devrait être fait par Protocol
		# self.driver = None
		# TODO: vérifier mais ça devrait être fait par Protocol
		# self.devices = []
		# TODO: vérifier mais c'est maintenant inutile avec les models de devices
		# self.handled_devices = [(NexaRemote, 0), (NexaDevice, 1)]
	
	def add_device(self, device_key, settings = None, switches = None):
		
		if device_key == 'NexaDevice':
			new_device = NexaDevice(self, settings = settings)
			for i in new_device.informations:
				self.kernel.add(i)
			for a in new_device.actions:
				self.kernel.add(a)
		elif device_key in ['NexaMovementSensor', 'NexaOpeningSensor']:
			new_device = self.handled_devices[device_key](self, settings = switches[0].settings)
			for i in new_device.informations:
				self.kernel.add(i)
		elif device_key in ['Nexa3ButtonRemote', 'Nexa2ButtonSwitch']:
			new_device = self.handled_devices[device_key](self, switches, settings = settings)
			for switch in new_device.base_switches:
				for i in switch.informations:
					self.kernel.add(i)
		
		self.kernel.add(new_device)
		self.devices.append(new_device)
		return new_device
	
	def process_message(self, message):
		""" Processes a radio message received by the radio modem 
		into a message understable by the protocol.
		The implementation of the message processing is , for the
		moment, a hard-coded finite-state machine.		
		
		TODO: translate into english
		Reçoit une trame identifiee comme destinee à ce driver et
		transmise par la couche inferieure. Cela suppose que la couche la
		plus basse a la capacite d'identifier le protocole du message et
		s'adresse ainsi directement à la methode decode_sequence du
		driver.
		La methode doit être specialisee pour traiter et decoder une trame Nexa
		Elle sera totalement redigee quand on saura sous quelle forme le message est obtenu
		"""
		
		state = 'unknown'
		
		def is_start(duration):
			return True if (1800 < duration*32) else False
		
		def is_short(duration):
			return True if (0 < duration*32 < 800) else False
		
		def is_long(duration):
			return True if (800 < duration*32 < 2000) else False
		
		def is_end(duration):
			return True if (2000 < duration*32) else False
		
		for i in message:
			if state == 'unknown':
				nexa_sequence = []
				if is_short(i):	state = 'start1'
			elif state == 'start1':
				if is_start(i): state = 'start2'
				else: state = 'unknown'				
			elif state == 'start2':
				if is_short(i): state = 'short'
				else: state = 'unknown'	
			elif state == 'short':
				if is_short(i): state = 'zero1'
				elif is_long(i): state = 'one1'
				elif is_end(i): state = 'end'
				else: state = 'unknown'	
			elif state == 'one1':
				if is_short(i): state = 'one2'
				else: state = 'unknown'	
			elif state == 'one2':
				if is_short(i): state = 'one_ok'
				else: state = 'unknown'	
			elif state == 'one_ok':
				nexa_sequence.append(1)
				if is_short(i): state = 'short'
				else: state = 'unknown'	
			elif state == 'zero1':
				if is_short(i): state = 'zero2'
				else: state = 'unknown'	
			elif state == 'zero2':
				if is_long(i): state = 'zero_ok'
				else: state = 'unknown'	
			elif state == 'zero_ok':
				nexa_sequence.append(0)
				if is_short(i): state = 'short'
				else: state = 'unknown'	
			elif state == 'end':
				break
		
		if len(nexa_sequence) == 32: # On s'assure qu'on a une sequence coherente
			
			# Converts a list of binary values to integer
			def from_bitfield_to_int(bitfield):
				return sum([i*2**(len(bitfield)-1-idi) for idi, i in enumerate(bitfield)])
			
			house_code = from_bitfield_to_int(nexa_sequence[0:26])
			group_code = nexa_sequence[26]
			command = nexa_sequence[27]
			unit_code = from_bitfield_to_int(nexa_sequence[28:32])
			
			device_found = False
			
			for device in self.devices:
				# Si la device est dejà dans la liste ET que ce n'est pas une NexaDevice, c'est que c'est une NexaRemote qu'on connait et on la met à jour
				if device.settings['house_code'] == house_code:
					device_found = True
					if NexaDevice not in device.__class__.__mro__:
						device.update(unit_code, command)
			
			if not device_found:
				if self.auto_detect:
					same_devices = [device for device in self.detected_devices if device.settings['house_code'] == house_code and device.settings['unit_code'] == unit_code]
					if len(same_devices) == 0: 
						settings = {'name' : "New Nexa Remote",
									'description' : "A new Nexa Remote has been detected and added to your devices.",
									'location' : "Specify a location.",
									'house_code': house_code,
									'group_code': group_code,
									'unit_code': unit_code}
						self.detected_devices.append(NexaBaseSwitch(self, settings = settings))
						print self.detected_devices
					
	def send_command(self, device, command):
		""" Method called when a device intends to send a message.
		It builds up the Nexa message according to the command 
		to be sent and the identity of the sending device. 
		
		"""
		# error_code = True
		
		symbols = ['1' + 10*'0',
				'10000010',
				'10100000',
				'1' + 40*'0']

		print type(device.settings['house_code'])
		print bin(device.settings['house_code'])
		print bin(device.settings['house_code'])[2:]
		
		bin_house_code = (26-len(bin(device.settings['house_code'])[2:]))*'0' + bin(device.settings['house_code'])[2:]
		bin_group_code = bin(device.settings['group_code'])[2:]
		bin_command = bin(command)[2:]
		bin_unit_code = (4-len(bin(device.settings['unit_code'])[2:]))*'0' + bin(device.settings['unit_code'])[2:]
	
		nexa_sequence = bin_house_code + bin_group_code + bin_command + bin_unit_code
		
		coded_sequence = [0]
		for char in nexa_sequence:
			if char == '1':
				coded_sequence += [1]
			else:
				coded_sequence += [2]
		coded_sequence += [3]
		
		call_arg = [16,250] + symbols + [coded_sequence]
		
		try:
			self.driver.send_message(call_arg)
		except Exception, e:
			raise e

class NexaDevice(Device):
	""" This is the class used to implement any Nexa-controlled device.
	 
	"""

	# Ce sont des attributs de classe, qui sont donc independants de 
	# toute instantiation de la classe
	
	device_key = 'NexaDevice'
		
	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the device',
					'key': 'name' },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the device',
					'key': 'description' },
					{ 'type': 'string',
					'title': 'Location',
					'desc': 'The place where the device is located',
					'key': 'location' },	
					{ 'type': 'num_int',
					'title': 'House code',
					'desc': 'Must be between 0 and 67 108 863',
					'key': 'house_code'	},
					{ 'type': 'num_int',
					'title': 'Group code',
					'desc': 'Must be either 0 or 1',
					'key': 'group_code'	},
					{ 'type': 'num_int',
					'title': 'Unit code',
					'desc': 'Must be between 0 and 15',
					'key': 'unit_code' }
					]
# 	
	def __init__(self, protocol, settings):
		""" The constructor only takes the protocol to which
		the device is linked as argument.
		
		
		"""
		super(NexaDevice, self).__init__()
		
		self.protocol = protocol
		
		# Si on ne les spécifie pas, ce sont des valeurs aléatoires
		self.settings['house_code'] = int(random()*67108863)
		self.settings['group_code'] = 0
		self.settings['unit_code'] = int(random()*15)
		
		self.settings['name'] = ''
		self.settings['description'] = ''
		self.settings['location'] = ''
		
		# On construit l'ID de sorte qu'il soit unique
		self.id = self.protocol.id + '_' + self.device_key + '_' + str(self.settings['house_code']) + '_' + str(self.settings['unit_code'])
		
		# On nomme explicitement l'info pour qu'elle soit plus simple à 
		# designer dans le code
		self.state = Information(key = 'state',
								 primary = True,
								 device = self,
								 value_type = 'bool',
								 settings = {'name': "State of the Nexa device " + str(self.settings['house_code']) + "/" + str(self.settings['unit_code']),
											 'description' : "Gives the state of the device."})		
		self.informations = [self.state]
		
		self.switch_on_action = Action(	key = 'on',
										primary = True,
										device = self,
										callback = self.switch_on,
										arguments = [],
										settings = {'name': "Switch Nexa " + str(self.settings['house_code']) + "/" + str(self.settings['unit_code']) + " on",
									 				'description': "Switch this device on."})
		self.switch_off_action = Action(key = 'off',
										primary = True,
										device = self,
										callback = self.switch_off,
										arguments = [],
										settings = {'name': "Switch Nexa " + str(self.settings['house_code']) + "/" + str(self.settings['unit_code']) + " of",
									 				'description': "Switch this device off."})
		self.sync_action = Action(	key = 'sync',
									primary = True,
									device = self,
									callback = self.sync,
									arguments = [],
									settings = {'name': "Sync Nexa " + str(self.settings['house_code']) + "/" + str(self.settings['unit_code']),
								 				'description': "Sync this device with Yeah!"})
		self.unsync_action = Action(	key = 'unsync',
										primary = True,
										device = self,
										callback = self.unsync,
										arguments = [],
										settings = {'name': "Unsync Nexa " + str(self.settings['house_code']) + "/" + str(self.settings['unit_code']),
									 				'description': "Unsync this device from Yeah!"})
		self.actions = [self.switch_on_action,
						self.switch_off_action,
						self.sync_action,
						self.unsync_action]
		
		self.set(settings)
		
	def switch_on(self, args):
		""" *(Internal)* Method called when the "on" action is triggered. 
		On the one side, it sends the radio command accordingly.
		On the other side, it updates the Information which 
		reflects the state of the device.
		
		"""
		
		self.protocol.send_command(self, 1)
		self.state.update(True)

	def switch_off(self, args):
		""" *(Internal)* Method called when the "off" action is triggered. 
		On the one side, it sends the radio command accordingly.
		On the other side, it updates the Information which 
		reflects the state of the device.
		
		"""
		
		self.protocol.send_command(self, 0)
		self.state.update(False)
	
	def sync(self, args):
		""" *(Internal)* Method called when the "sync" action is triggered. 
		It sends a series of "on" commands.
		
		"""
		
		for i in range(5):
			self.switch_on({})
			sleep(0.1)
			i += 1
		self.state.update(True)
	
	def unsync(self, args):
		""" *(Internal)* Method called when the "unsync" action is triggered. 
		It sends a series of "off" commands.
		
		"""
		
		for i in range(5):
			self.switch_off({})
			sleep(0.1)
			i += 1
		self.state.update(False)
	
	def set(self, settings):
		super(NexaDevice, self).set(settings)
		
		if settings != None:
			if settings.has_key('name'):
				self.state.set({'name': 'State of ' + self.settings['name']})
				self.switch_on_action.set({'name': 'Switch on ' + self.settings['name']})
				self.switch_off_action.set({'name': 'Switch off ' + self.settings['name']})
				self.sync_action.set({'name': 'Sync ' + self.settings['name']})
				self.unsync_action.set({'name': 'Unsync ' + self.settings['name']})

class NexaDeviceModel(DeviceModel):
	
	id = 'NexaDeviceModel'
	protocol_id = 'Nexa'
	name = 'Nexa Device'
	adding_type = 'sync'
	device_key = 'NexaDevice'	
	sync_instructions = 'In order to sync your new Nexa device, press the sync button below. From there, you have 10 seconds to plug your new Nexa device to a power source. If you hear a repetitive jingling, that should be it.'
	
class NexaBaseSwitch(Device):

	# Ce sont des attributs de classe, qui sont donc independants de 
	# toute instantiation de la classe
	device_key = 'NexaBaseSwitch'
	
	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the device',
					'key': 'name' },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the device',
					'key': 'description' },	
					{ 'type': 'num_int',
					'title': 'House code',
					'desc': 'Must be between 0 and 67 108 863',
					'key': 'house_code',
					'disabled': True },
					{ 'type': 'num_int',
					'title': 'Group code',
					'desc': 'Must be either 0 or 1',
					'key': 'group_code',
					'disabled': True 	},
					{ 'type': 'num_int',
					'title': 'Unit code',
					'desc': 'Must be between 0 and 15',
					'key': 'unit_code',
					'disabled': True  }
					]

	def __init__(self, protocol, settings):
		"""
		"""
# 		""" The constructor does not only take the protocol but also 
# 		the house_code, the group_code and the unit_code of the newly
# 		discovered remote as arguments since they will always remain
# 		the same.
# 		
# 		"""
		
		super(NexaBaseSwitch, self).__init__()
		self.protocol = protocol
		
		self.set(settings)
		
		self.id = self.protocol.id + '_' + self.device_key + '_' + str(self.settings['house_code']) + '_' + str(self.settings['unit_code'])
				
		
		
		self.state = Information('state',
								 True,
								 'bool',
								 {'name': '',
								  'description' : ''},
								 device = self)
		
		self.informations = [self.state]
		self.actions = []
		
		
		
	def update(self, unit_code, new_command):
		""" Method called to update the state of the device. 
		It updates the linked Information accordingly.		
		
		"""
		
		print unit_code
# 		try:
		if unit_code == self.settings['unit_code']:
			if new_command == 1:
				self.state.update(True)
			elif new_command == 0:
				self.state.update(False)
			else:
				raise ValueError("The new state was neither 0 nor 1.")
# 		except Exception, e:
# 			raise e
	
	def set(self, settings):
		super(NexaBaseSwitch, self).set(settings)
		
		if settings.has_key('name') and hasattr(self, 'state'):
			self.state.set({'name': 'State of ' + self.settings['name']})

class NexaController(Device):
	
	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the device',
					'key': 'name' },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the device',
					'key': 'description' },	
					{ 'type': 'num_int',
					'title': 'House code',
					'desc': 'Must be between 0 and 67 108 863',
					'key': 'house_code',
					'disabled': True }
					]
		
	def __init__(self, protocol, switches, *args, **kwargs):
		super(NexaController, self).__init__(*args, **kwargs)
		
		self.base_switches = sorted(switches, key=lambda switch: switch.settings['unit_code'])
		
		self.id = 'nexa_remote_' + str(self.base_switches[0].settings['house_code'])
		
		self.set({'name': 'new nexa device',
				 'description': '',
				 'house_code': self.base_switches[0].settings['house_code']})
		
	def set(self, settings):
		super(NexaController, self).set(settings)
		
		if settings.has_key('name'):
			for i, switch in enumerate(self.base_switches):
				switch.set({'name': 'Button ' + str(i+1) + ' of ' + self.settings['name']})
	
	def update(self, unit_code, command):
		for switch in self.base_switches:
			switch.update(unit_code, command)
			
class Nexa3ButtonRemote(NexaController):
	
	device_key = 'Nexa3ButtonRemote'

class Nexa3ButtonRemoteModel(DeviceModel):
	
	id = 'Nexa3ButtonRemoteModel'
	protocol_id = 'Nexa'
	name = 'Nexa 3 Button Remote'
	adding_type = 'auto'
	device_key = 'Nexa3ButtonRemote'
	instructions = 'In order to automatically add your Nexa 3 Button Remote to Majordom, simply press each of the three buttons of the remote.'
	
	def is_detected(self):
		result = False
		for device in self.protocol.detected_devices:
			if not result:
				current_house_code = device.settings['house_code']
				nexa_switches = [device]
				for other_device in self.protocol.detected_devices:
					if other_device.settings['house_code'] == current_house_code and other_device not in nexa_switches:
						nexa_switches.append(other_device)
				if len(nexa_switches) == 3:
					new_device = self.protocol.add_device('Nexa3ButtonRemote', switches = nexa_switches)
					result = new_device
		return result

class Nexa2ButtonSwitch(NexaController):
	
	device_key = 'Nexa2ButtonSwitch'
	
class Nexa2ButtonSwitchModel(DeviceModel):
	
	id = 'Nexa2ButtonSwitchModel'
	protocol_id = 'Nexa'
	name = 'Nexa 2 Button Switch'
	adding_type = 'auto'
	device_key = 'Nexa2ButtonSwitch'
	instructions = 'In order to automatically add your Nexa 2 Button Switch to Majordom, simply press each of the two buttons of the switch.'
	
	def is_detected(self):
		result = False
		for device in self.protocol.detected_devices:
			if not device:
				current_house_code = device.settings['house_code']
				nexa_switches = [device]
				for other_device in self.protocol.detected_devices:
					if other_device.settings['house_code'] == current_house_code:
						nexa_switches.append(other_device)
				if len(nexa_switches) == 2:
					new_device = self.protocol.add_device('Nexa2ButtonSwitch', switches = nexa_switches)
					result = new_device
		return result
	
class NexaOpeningSensor(NexaBaseSwitch):
	
	device_key = 'NexaOpeningSensor'
	
# 	def update(self, unit_code, new_command):
# 		""" Method called to update the state of the device. 
# 		It updates the linked Information accordingly.		
# 		
# 		"""
# 		
# 		if unit_code == self.settings['unit_code']:
# 			if new_command == 1:
# 				self.state.update(True)

class NexaOpeningSensorModel(DeviceModel):
	
	id = 'NexaOpeningSensorModel'
	protocol_id = 'Nexa'
	name = 'Nexa Opening Sensor'
	adding_type = 'auto'
	device_key = 'NexaOpeningSensor'
	instructions = 'In order to automatically add your opening sensor to Majordom, simply move closer and then move away the two parts of the sensor.'
	
	def is_detected(self):
		result = False
		if len(self.protocol.detected_devices) > 0:
			new_device = self.protocol.add_device('NexaOpeningSensor', switches = self.protocol.detected_devices)
			result = new_device
		return result

class NexaMovementSensor(NexaBaseSwitch):
	
	device_key = 'NexaMovementSensor'
		
	def update(self, unit_code, new_command):
		""" Method called to update the state of the device. 
		It updates the linked Information accordingly.		
		
		"""
		
		if unit_code == self.settings['unit_code']:
			if new_command == 1:
				self.state.update(True)
		
class NexaMovementSensorModel(DeviceModel):
	
	id = 'NexaMovementSensorModel'
	protocol_id = 'Nexa'
	name = 'Nexa Movement Sensor'
	adding_type = 'auto'
	device_key = 'NexaMovementSensor'
	instructions = 'In order to automatically add your movement sensor to Majordom, simply wave your hand in front of it.'
	
	def is_detected(self):
		result = False
		if len(self.protocol.detected_devices) > 0:
			new_device = self.protocol.add_device('NexaMovementSensor', switches = self.protocol.detected_devices)
			result = new_device
		return result
		
""" Set of attributes which describe the plugin, in order 
to add it to the kernel and then be able to describe it
to the user.  

"""
plugin_type = "protocol"
name = "Nexa"
description = "A protocol plugin which enables the use of Nexa-powered devices. A compatible 433 MHz modem is needed for the protocol to function."
protocol_class = Nexa
device_models_classes = [NexaDeviceModel, 
						 Nexa3ButtonRemoteModel, 
						 Nexa2ButtonSwitchModel, 
						 NexaOpeningSensorModel, 
						 NexaMovementSensorModel]