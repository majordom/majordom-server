# -*- coding: utf-8 -*-

from kernel import Protocol, Device, Information

class Oregon(Protocol):
	""" Main class of a protocol plugin.
	
	"""

	#---------------------------------------------------------------
	# Interface avec le kernel 
	#---------------------------------------------------------------

	def __init__(self, kernel):
		super(Oregon, self).__init__()
		
		self.id = 'oregon'
		self.kernel = kernel
		
		self.set({'name': "Oregon",
				'description': "Protocole domotique utilise par Oregon Scientific et OWL.",
				'driver': 'No modem specified'})
		
		self.driver_type = 'radio_433'
		self.driver = None

		self.devices = []
		
		self.handled_devices = [(THGR810, 0), (CMR160R, 1)]
					
	def decode_message(self, radio_sequence):
		""" Processes a radio sequence received by the radio modem 
		into a message understable by the protocol.
		The implementation of the sequence processing is , for the
		moment, a hard-coded finite-state machine.		
		
		"""
		
		state = 'unknown'
		cpt = 0
		
		def is_short(duration):
			return True if (duration < 20) else False
		
		def is_long(duration):
			return True if (20 < duration) else False
			
		for i in radio_sequence:
			#print state
			if state == 'unknown':
				sequence = []
				cpt = 0
				if is_long(i):
					state = 'sync'
					cpt += 1
			elif state == 'sync':
				if is_long(i): cpt += 1
				else: state = 'unknown'
				if cpt == 4: state = 'start_payload'				
			elif state == 'start_payload':
				if is_short(i): state = 'short_start_payload'
				elif is_long(i):
					sequence.append(0)
					state = 'payload'
				else: state = 'unknown'	
			elif state == 'short_start_payload':
				if is_short(i):
					sequence.append(1)
					state = 'payload'
				else: state = 'unknown'	
			elif state == 'payload':
				if len(sequence) < 68:
					if is_short(i): state = 'short'
					elif is_long(i): sequence.append((sequence[-1]+1)%2)
					else: state = 'unknown'
				else:
					state = 'end'
			elif state == 'short':
				if is_short(i): 
					state = 'payload'
					sequence.append(sequence[-1])
				else: state = 'unknown'
			elif state == 'end':
				break
		
		#print len(sequence)
		if len(sequence) == 68: # On s'assure qu'on a une sequence coherente
		
			# Converts a list of binary values to integer
			# From Bitfield To Int (FBTI)
			def fbti(bitfield):
				return sum([i*2**(len(bitfield)-1-idi) for idi, i in enumerate(bitfield)])
			
# 			def calc_checksum(nibbles):
# 				return sum(nibbles)
# # 				chksum = []
# # 				for i in range(8):
# # 					chksum.append(sum([seq[i + 8*j] for j in range(7)])%2)
# # 				return fbti(chksum)
# 			
			def reverse(my_list):
				return [i for i in reversed(my_list)]
			
			def convert_to_nibbles(bitfield):
				nibble = []
				for i in range(17):
					nibble.append(fbti(reverse(bitfield[4*i:4*(i+1)])))
				return nibble
			
# 			def from_nibble_to_int(nibble):
# 				return sum([i*16**(len(nibble)-1-idi) for idi, i in enumerate(nibble)])
# 			
			nibbles = convert_to_nibbles(sequence)
			print sequence
			print nibbles
# 			
			#sensor_id = from_bitfield_to_int(reverse(sequence[0:3]) + reverse(sequence[4:7]) + reverse(sequence[8:11]) + reverse(sequence[12:15]))
			sensor_id = fbti(reverse(sequence[0:15]))
			channel = fbti(reverse(sequence[16:19]))
			rolling_code = fbti(sequence[20:27])
			flags = fbti(sequence[28:31])
			temperature = 10*fbti(reverse(sequence[40:43])[0:3]) + fbti(reverse(sequence[36:39])[0:3]) + 0.1*fbti(reverse(sequence[32:35])[0:3])
			sign = fbti(sequence[44:47])
			humidity = 10*fbti(reverse(sequence[52:55])[0:3]) + fbti(reverse(sequence[48:51])[0:3])
			unknown = fbti(sequence[56:59])
			checksum = fbti(sequence[60:67])
			
			
			print "sensor_id: " + hex(sensor_id)
			print "channel: " + str(channel)
			print "rolling_code: " + hex(rolling_code)
			print "flags: " + hex(flags)
			print "temperature: " + str(temperature) + "°C"
			print "sign: " + str(sign)
			print "humidity: " + str(humidity) + "%"
			print "unknown: " + hex(unknown)
			print "checksum: " + hex(checksum)
			print "calculated checksum: " + str(hex(sum(nibbles)))


# TODO: implementer le decodage des messages dans les deux classes ci-dessou
class THGR810(Device):
	
	device_infos = {
				'name' : "THGR810 Temperature and Humidity Sensor",
				'description' : "The Oregon Scientific THGR810 sensor. In order to add it to the box, just wait for it to transmit (when the red LED flashes) and it will be automatically added to the system. Note that the only way to differentiate several THGR810 is to change their channel. Otherwise, they will be recognized as the same device.",
				'user-instantiable': False
				}
	
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
					'title': 'Sensor ID',
					'desc': 'The ID specific to a family of sensor',
					'key': 'sensor_id',
					'disabled': True },
					{ 'type': 'num_int',
					'title': 'Channel',
					'desc': 'It is the only way to differentiate several THGR810',
					'key': 'channel',
					'disabled': True 	}
					]
	
	def __init__(self, protocol, settings):
		"""
		"""
		
		self.protocol = protocol
		
		self.set(settings)
		
		self.battery = Information(
								{ 'name': "Etat des batteries du THGR810, channel " + self.settings['channel'],
								'description': "Permet de savoir s'il faut changer les batteries",
								'type': 'options'})
		
		self.temperature = Information(
									{ 'name': "Temperature donnee par le THGR810, channel " + self.settings['channel'],
									'description': "Temperature donnee par le capteur",
									'type': 'num_float'})
		
		self.humidity = Information(
								{ 'name': "Humidite donnee par le THGR810, channel " + self.settings['channel'],
								'description': "Humidite donnee par le capteur",
								'type': 'num_int'})
		
		self.humidity_options = Information(
										{ 'name': "Etat de l'humidite donnee par le THGR810, channel " + self.settings['channel'],
										'description': "Etat de l'humidite donnee par le capteur",
										'type': 'options'})
		
		self.informations = [self.battery, self.temperature, self.humidity, self.humidity_options]
		self.actions = []
	
	def update(self, new_message):
		""" Method called to update the state of the device. 
		It updates the linked Information accordingly.		
		
		"""
		pass
		

class CMR160R(Device):
	pass

""" Set of attributes which describe the plugin, in order 
to add it to the kernel and then be able to describe it
to the user.  

"""
plugin_type = 'plop'
#  "protocol"
# name = "Oregon"
# description = "A protocol plugin which enables the use of Oregon-powered devices. A compatible 433 MHz modem is needed for the protocol to function."
# protocol_class = Oregon    