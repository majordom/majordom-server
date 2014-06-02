# -*- coding: utf-8 -*-

import os
from importlib import import_module
from types import ModuleType
from json import dumps, loads

from models import IDableObject, Information, Action, Device, DeviceModel, Interface, Protocol, Driver, BlockModel
from scenario import Scenario

class Kernel:
	""" The Kernel class is the core of the Majordom system. It is its only immutable class: every other functionalities are implemented by plugins.
	
	It is instantiated once at the beginning of the program and then gathers every handleable object in different lists, in order to make them accessible by other parts of the program (such as the User Interface):
	
	:ivar protocols: (:class:`models.Protocol list`) the list of protocols currently handled by the kernel
	:ivar drivers: (:class:`models.Driver list`) the list of hardware parts that may work with the system
	:ivar interfaces: (:class:`models.Interface list`) the list of available interfaces (http...)
	
	:ivar device_models: (:class:`models.DeviceModel list`) the list of device models available. This list allows the user to know which kind of devices he is able to add to Majordom. 
	:ivar block_models: (:class:`models.BlockModel list`) the list of block models available. This is the way for the user to know what blocks that may be used within a scenario
	
	:ivar devices: (:class:`models.Device list`) the list of devices currently connected to the system
	:ivar actions: (:class:`models.Action list`) the list of actions available and available to be used in a scenario 
	:ivar infos: (:class:`models.Information list`) the list of informations available and available to be used in a scenario
	:ivar scenarios: (:class:`scenario.Scenario list`) the scenarios created by the user (some may not be active)
	
	:ivar next_scenario_id: (:class:`scenario.Scenario list`) a counter of the number of the scenarios created until there: it is used to ID the scenario.
	
	"""
	
	def __init__(self):
		# élements uniques
		self.protocols = []	
		self.drivers = []
		self.interfaces = []
		
		# élements uniques non configurables
		self.device_models = []
		self.block_models = []
		
		# éléments non uniques
		self.devices = []
		self.actions = []
		self.infos = []
		self.scenarios = []
		
		# pour numéroter les scénarios
		self.next_scenario_id = 0
		
	def load_plugins(self):
		""" Loads all plugins available in the plugin package/subdirectory, i.e. instantiates an instance of the main class of the plugin. If a plugin has already been loaded, it is ignored.
		
		If the plugin is a protocol plugin, this function performs the following operations:
			* loading of the protocol class
			* loading of all the device models bundled within the protocol plugin
			
		If the plugin is an automation plugin, it loads every of the block models bundled within the plugin.
		
		If the plugin is either a driver or an interface plugin, it simply loads the plugin.
		
		.. note::
		
			Classes loaded through plugins are in fact singletons: they are only instantiated once by the kernel. Some kind of classes may obviously be instantiated several times in Majordom, such as the Device classes. You may have several instances of the same remote connected to Majordom: that is what Device Models are for: they are instantiated only once but allow you to instantiate the object they are 'modelling' (such as a Device for a Device Model or a Block for a Block Model) several times.
		
		"""

		for plugin_file in os.listdir('plugins'):
			if plugin_file != '__init__.py' and plugin_file[-3:] == '.py':
				plugin = import_module('plugins.' + plugin_file[:-3], package='plugins')
				if plugin.plugin_type == 'protocol':
					self.add(plugin.protocol_class(self))
					for device_model in plugin.device_models_classes:
						self.add(device_model(self))
				elif plugin.plugin_type == 'driver':
					self.add(plugin.driver_class())
				elif plugin.plugin_type == 'automation':
					for block_model in plugin.block_models_classes:
						self.add(block_model)
						if block_model.kernel_needed:
							block_model.set_kernel(self)
				elif plugin.plugin_type == 'interface':
					self.add(plugin.interface_class(self))
									
	def add(self, element):
		""" Adds the element given as argument to the corresponding objects list of the kernel.
		
		It auto-detects the type of the argument given and automatically appends to one of the lists of the kernel.	
		
		:param element: The element to add to the kernel
		:type element: :class:`models.Information` or :class:`models.Action` or :class:`models.Device` or :class:`models.Interface` or :class:`models.Protocol` or :class:`models.Driver` or :class:`scenario.Scenario` or :class:`models.BlockModel`
		:raises TypeError: if the element given as argument is of none of the types given above.
		 
		"""
		
		element_parents = element.__class__.__mro__
		try:
			if IDableObject not in element_parents:
				print element
				raise TypeError("Error while adding the element '" + str(element) + "' to the kernel. It is not an IDableObject.")
		except Exception, e:
			raise e
		else:
			try:
				if element is ModuleType: target_list = self.plugins
				elif Protocol in element_parents: target_list = self.protocols
				elif Driver in element_parents: target_list = self.drivers
				elif Interface in element_parents: target_list = self.interfaces
				elif DeviceModel in element_parents: target_list = self.device_models
				elif Device in element_parents: target_list = self.devices
				elif Action in element_parents: target_list = self.actions
				elif Information in element_parents: target_list = self.infos
				elif BlockModel in element_parents: target_list = self.block_models
				elif Scenario in element_parents: target_list = self.scenarios
				else:
					raise TypeError("The element you are trying to add to the kernel is not one of the possible types.")
			except Exception, e:
				raise e
			else:
				if element not in target_list:
					#element.id = self.get_new_id()
					target_list.append(element)
		
		print element.id
		return element.id
	
	def add_new_scenario(self, settings, yeah_id = None, next_block_id = 0, next_link_id = 0):
		""" Adds a new scenario to the kernel, using the settings given as argument. Other optional arguments may be given - they are only used when this function is used in the process of persistence: at restoration, we must ensure that scenarios have the same id than they had before saving.

		:param settings: The settings dictionary that will be used to initialize the scenario.
		:type element: :class:`python dict` 
		:param yeah_id: (optional) the id to give to the new scenario, only used in the process of persistence.
		:type element: :class:`string`
		:param next_block_id: (optional) used to set the next_block_id attribute of the new scenario, only used in the process of persistence
		:type element: :class:`int`
		:param next_link_id: (optional) sed to set the next_link_id attribute of the new scenario, only used in the process of persistence
		:type element: :class:`int`
		
		"""
		
		new_scenario = Scenario(self, settings = settings, next_block_id = next_block_id, next_link_id = next_link_id)
		
		if yeah_id == None:
			self.id = self.next_scenario_id
			new_scenario.id = 'scenario' + str(self.next_scenario_id)
			self.next_scenario_id += 1
		else:
			new_scenario.id = yeah_id
		
		self.add(new_scenario)
		return new_scenario
	
	def get_from_list(self, maj_id, kernel_list):
		""" Returns the element whose ID is maj_id if it is in the list kernel_list. Otherwise, it returns False.

		:param maj_id: the ID of the researched element
		:type element: :class:`string`
		:param maj_id: the list in which to look for the researched element
		:type element: :class:`python list`
		:return: the researched element or False
		:returntype: :class:`bool` or any Majordom class
		
		"""
	
		result = False
		for element in kernel_list:
			if element.id == maj_id:
				result = element
		return result
	
	def get(self, maj_id):
		""" Returns the element whose ID is maj_id if it is in any of the lists of the kernel.

		:param maj_id: the ID of the researched element
		:type element: :class:`string`
		:return: the researched element or False
		:returntype: :class:`bool` or any Majordom class
		
		"""
		
		return self.get_from_list(maj_id, self.protocols
										 + self.drivers
										 + self.interfaces
										 + self.devices
										 + self.device_models
										 + self.block_models
										 + self.infos
										 + self.actions
										 + self.scenarios)
	
	def get_protocol(self, yeah_id):
		return self.get_from_list(yeah_id, self.protocols)
	
	def get_driver(self, yeah_id):
		return self.get_from_list(yeah_id, self.drivers)
	
	def get_interface(self, yeah_id):
		return self.get_from_list(yeah_id, self.interfaces)
	
	def get_device(self, yeah_id):
		return self.get_from_list(yeah_id, self.devices)
	
	def get_device_model(self, yeah_id):
		return self.get_from_list(yeah_id, self.device_models)
	
	def get_block_model(self, yeah_id):
		return self.get_from_list(yeah_id, self.block_models)
	
	def get_info(self, yeah_id):
		return self.get_from_list(yeah_id, self.infos)
	
	def get_action(self, yeah_id):
		return self.get_from_list(yeah_id, self.actions)
	
	def get_scenario(self, yeah_id):
		return self.get_from_list(yeah_id, self.scenarios)

	def remove_from_list(self, yeah_id, kernel_list):
		""" Removes and returns the element whose ID is maj_id if it is in the list kernel_list. Otherwise, it returns False.

		:param maj_id: the ID of the researched element
		:type element: :class:`string`
		:param maj_id: the list in which to look for the researched element
		:type element: :class:`python list`
		:return: the researched element or False
		:returntype: :class:`bool` or any Majordom class
		
		"""
		result = False
		
		for element in kernel_list:
			if element.id == yeah_id:
				result = element
				kernel_list.remove(element)
			
		return result

	def remove(self, yeah_id):
		""" Removes and returns the element whose ID is maj_id if it is in any of the lists of the kernel.

		:param maj_id: the ID of the researched element
		:type element: :class:`string`
		:return: the researched element or False
		:returntype: :class:`bool` or any Majordom class
		
		"""
		
		return self.remove_from_list(yeah_id, self.protocols
											+ self.drivers
											+ self.interfaces
											+ self.devices
											+ self.device_models
											+ self.block_models
											+ self.infos
											+ self.actions
											+ self.scenarios)

	def remove_protocol(self, yeah_id):
		return self.remove_from_list(yeah_id, self.protocols)
	
	def remove_driver(self, yeah_id):
		return self.remove_from_list(yeah_id, self.drivers)
	
	def remove_interface(self, yeah_id):
		return self.remove_from_list(yeah_id, self.interfaces)
	
	def remove_device(self, yeah_id):
		return self.remove_from_list(yeah_id, self.devices)
	
	def remove_device_model(self, yeah_id):
		return self.remove_from_list(yeah_id, self.device_models)
	
	def remove_block_model(self, yeah_id):
		return self.remove_from_list(yeah_id, self.block_models)
	
	def remove_info(self, yeah_id):
		return self.remove_from_list(yeah_id, self.infos)
	
	def remove_action(self, yeah_id):
		return self.remove_from_list(yeah_id, self.actions)
	
	def remove_scenario(self, yeah_id):
		return self.remove_from_list(yeah_id, self.scenarios)

	def save(self):
		""" *(Do not use)* Function written to enable persistence, i.e. capability to save and then restore the state of the Majordom system. Due to software architecture evolutions, this method has become obsolete and should therefore **not be used**. It will be fixed in next versions but was not a priority for the release of the 0.0.9 version.
		
		"""
		
		save = {'protocols': [],
				'drivers': [],
				'interfaces': [],
				'devices': [],
				'next_scenario_id': self.next_scenario_id,
				'scenarios': []}
		
		for protocol in self.protocols:
			save['protocols'].append({'id': protocol.id,
									  'settings': protocol.settings})
		for driver in self.drivers:
			save['drivers'].append({'id': driver.id,
									'settings': driver.settings})
		
		for interface in self.interfaces:
			save['interfaces'].append({'id': interface.id,
									   'settings': interface.settings})
		
		for device in self.devices:
			save['devices'].append({'protocol': device.protocol.id,
									'device_key': device.device_key,
									'settings': device.settings})
		
		for scenario in self.scenarios:
			save['scenarios'].append({'id': scenario.id,
									  'settings': scenario.settings,
									  'next_block_id': scenario.next_block_id,
									  'next_link_id': scenario.next_link_id,
									  'active': scenario.active,
									  'blocks': [{'id': b.id,
												  'settings': b.settings,
												  'block_model_id': b.block_model.id} 
												for b in scenario.blocks],
									  'links': [{'id': l.id,
												 'src_node_id': l.src_node.id,
												 'dst_node_id': l.dst_node.id} 
											   for l in scenario.links]})
		
		f = open('savefile', 'w')
		f.write(dumps(save))
	
	def restore(self):
		""" *(Do not use)* Similarly to the save function above, this function was written to enable persistence. Due to software architecture evolutions, this method has become obsolete and should therefore **not be used**. It will be fixed in next versions but was not a priority for the release of the 0.0.9 version.
		
		"""
		
		f = open('savefile', 'r')
		save = loads(f.read())
		
		for protocol in self.protocols:
			for protocol_save in save['protocols']:
				if protocol.id == protocol_save['id']:
					protocol.set(protocol_save['settings'])
		for driver in self.drivers:
			for driver_save in save['drivers']:
				if driver.id == driver_save['id']:
					driver.set(driver_save['settings'])
		for interface in self.interfaces:
			for interface_save in save['interfaces']:
				if interface.id == interface_save['id']:
					interface.set(interface_save['settings'])
			
		for device_save in save['devices']:
			protocol = self.get_protocol(device_save['protocol'])
			device_key = device_save['device_key']
			settings = device_save['settings']
			protocol.add_device(device_key, settings = settings)
		
		# The restoration of scenarios must be done carefully
		# First, all the *blocks* of *all* tht scenarios must be restored.
		# Only then, all the links of *all* the scenario can be restored.
		# New infos or actions can indeed be restored when blocks are restored.
		self.next_scenario_id = save['next_scenario_id']
		
		for scenario_save in save['scenarios']:	
			new_scenario = self.add_new_scenario(scenario_save['settings'], 
												 yeah_id = scenario_save['id'],
												 next_block_id = scenario_save['next_block_id'],
												 next_link_id = scenario_save['next_link_id'])
					
			for block_save in scenario_save['blocks']:
				new_scenario.add_block(block_save['block_model_id'], block_save['settings'], block_id = block_save['id'])
		
		for scenario_save in save['scenarios']:
			for link_save in scenario_save['links']:
				new_scenario.add_link(link_save['src_node_id'], link_save['dst_node_id'], link_id = link_save['id'])
		
		for scenario_save in save['scenarios']:
			if scenario_save['active']:
				self.get_scenario(scenario_save['id'].activate())
		
# 	def remove_by_id(self, searched_id):
# 		""" Remove the element whose ID has been given as argument
# 		from the kernel and returns it.
# 		
# 		:param int searched_id: The ID of the element to remove
# 		:return: The removed element or false 
# 		:rtype: :class:`models.Information` or :class:`models.Action` or :class:`models.Device` or :class:`models.Interface` or :class:`models.Protocol` or :class:`models.Driver` or :class:`scenario.Scenario` or :class:`models.BlockModel` or :class:`boolean`
# 		
# 		"""

# 	def get_by_id(self, searched_id):
# 		""" Get an element previously added to the kernel by providing
# 		its id. 
# 		
# 		:param int searched_id: The ID of the element which is searched.
# 		:return: the searched object or False if it has not been found
# 		:rtype: :class:`int` or :class:`bool`
# 
# 		"""
# 		
# 		# self.plugins, 
# 		lists = (self.protocols, self.drivers, self.interfaces, self.devices, self.device_models, self.actions, self.infos, self.block_models, self.scenarios)
# 		methodReturn = False
# 		for li in lists:
# 			for el in li:
# 				if el.id == searched_id:
# 					methodReturn = el
# 		return methodReturn
#
# 	def get_new_id(self):
# 		""" *(Internal)* Get an identifier that we know being unique. It is used 
# 		by the :func:`add` so that any object added to the kernel gets
# 		its own identifier.
# 		
# 		It is particularly useful when it comes	to user interfaces.
# 		
# 		:return: A unique identifier
# 		:rtype: :class:`int`
# 		"""
# 		# TODO: à proteger par un semaphore
# 		new_id = self.next_id
# 		self.next_id += 1
# 		return new_id