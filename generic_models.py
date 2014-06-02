# -*- coding: utf-8 -*-

from types import IntType, StringType, FloatType, BooleanType, UnicodeType

class AttributeNotSet(Exception):
	""" Raised when an object tries to use an object whose an attribute essential to its working has not yet been 
	set. E.g. when you try sending a message with a modem whose COM port has not been set.
	
	"""
	pass

class IDableObject(object):
	""" Class of an object which is accessible through a unique ID. The ID is obtained according various processes wich depend on the class of the object. Though, in all cases, they are given so that they are unique.
	
	"""
	
	def __init__(self):
		pass
		#self.id = None
		
	def get_id(self):
		return self.id

class SettableObject(IDableObject):
	""" Class used to normalize the access to an object's settings.
	
	Within Majordom, many objects may need to be set by the user: protocols, devices or even blocks. But all the blocks or all the devices will **not** have the same settings: for instance, you can specify the value of a 'Constant Block' but a 'Multiply' Block will have no settings. Different devices, from different protocols, won't have the same settings either. 
	
	Yet, all these objects have to be settable. To do so, we introduced two attributes: :attr:`settings_format` and :attr:`settings`.
	
	The first one, :attr:`settings_format`, is a representation of the available settings of the given object. It can be a class attribute: every instance of a class should normally have the same settings format. The :attr:`settings_format` are a python list of python dictionaries. 
	
	Here is an example of format dictionary::
	
		{'key': 'name',
		 'type': 'string',
		 'disabled': False,
		 'name': 'Name of the device',
		 'desc': 'The display name of this device'}
	
	* the 'key' is a unique identifier for this particular settings
	* the 'type' can be 'string', 'string_long', 'num', 'num_int', 'bool' or 'options'. In the case of 'options', you have to add another 'options' field which will contain the list of all available options
	* the 'disabled' field tells whether or not the user can modify the settings (it is optional and defaults to True)
	* the 'name' field is the name of the given settings
	* the 'desc' field is a field describing what the setting is used for
	
	The second one, :attr:`settings`, is a python dictionary containing the settings themselves. The key in the dictionary is the corresponding key in the settings format.
	
	These two attributes are in fact a way to replace some instance attributes: the elements in :attr:`settings` would normally have been stored in the instance attributes. It is the need to be able to dynamically 'discover' one object's available :attr:`settings` which led us to this choice: this way, having exact knowledge of the class structures (in particular of its attributes) is not necessary to interact with it.
	"""
	
	settings_format = []
	""" The settings_format dictionary described above.
	
	"""
	
	def __init__(self, settings = None, *args, **kwargs):
		super(SettableObject, self).__init__(*args, **kwargs)
		
		self.settings = {}
		if settings != None: self.set(settings)
	
	def set(self, settings):
		""" Sets the SettableObject according to the settings given as argument. The setting dict given as argument must follow the format of the class attribute :attr:`settings_format`.

		If the `settings` given are not valid, they are ignored and 
		the method returns a dictionary containing the faulty keys.
		For instance, settings may not be valid if you try giving a 
		dictionary having a key which was not specified in :attr:`settings_format` or if the value of a setting
		does not tally with the type requested in :attr:`settings_format`.
		
		The `settings` dictionary given as argument may not contain every key
		specified in the format dictionary. In this case, all the specified 
		settings will me modified (on the condition they are valid) and the 
		others will be left unchanged. 
		
		:param settings: The python dictionary containing the settings to apply.
		:type settings: :class:`python dict`
		:return: True if the settings were correctly applied. A python dictionary containing the faulty settings otherwise.
		:rtype: :class:`boolean` or :class:`python dict`
		  
		"""
		
		# Dictionnaire de correspondance entre le type sp�cifi� dans settings_format 
		# et le type python attendu
		python_type = {
					'string': [StringType, UnicodeType],
					'string_long': [StringType, UnicodeType],
					'bool': [BooleanType, UnicodeType],
					'num_int': [IntType, UnicodeType],
					'num': [FloatType, IntType, UnicodeType],
					'options': [StringType, UnicodeType]
					}
		if settings != None:
			if settings.has_key('name'):
				print settings['name']
			try:
				for k, v in settings.iteritems():
					if k in [f['key'] for f in self.settings_format]:
						# On r�cup�re le type attendu pour ce r�glage
						value_type = [f['type'] for f in self.settings_format if f.has_key('key') and f['key'] == k][0]
						# Si c'est un champ de type 'options', la classe d�riv�e g�rera elle-m�me ce setting
						if value_type != 'options':
							# On v�rifie que le r�glage donn� est bien du type attendu
							if type(v) in python_type[value_type]:
								if type(v) == UnicodeType:
									if value_type in ['string', 'string_long', 'options']:
										self.settings[k] = v
									elif value_type == 'bool':
										self.settings[k] = bool(int(v))
									elif value_type == 'num_int':
										self.settings[k] = int(v) 
									elif value_type == 'num':
										self.settings[k] = float(v)
								else:
									self.settings[k] = v
			except Exception, e:
				raise e
		
# 	def get_settings_format(self):
# 		"""
# 		"""
# 		
# 		return self.settings_format

# 	def get_properties_format(self):
# 		properties_format = list(self.properties_format)
# 		for p in properties_format:
# 			if p['type'] != 'title':
# 				p['section'] = str(self.id)
# 		return properties_format

# 	def get_settings(self):
# 		""" Presents the available settings for this object and their
# 		respectives types. 
# 		
# 		For instance, the modem used to get radio messages
# 		has to be manually set by the user when he initializes the protocol 
# 		for the first time.
# 		
# 		:return: a dictionary describing the available settings and their type
# 		:rtype: :class:`dict`
# 		
# 		"""
# 		
# 		return self.settings