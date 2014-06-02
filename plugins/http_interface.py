# -*- coding: utf-8 -*-

from bottle import app, response, post, request
from copy import deepcopy
from datetime import datetime
from json import dumps
from threading import Thread

from models import Interface
from scenario import InputNode, OutputNode

class HTTPInterface(Interface):
	""" Class implementing the Interface interface to make Majordom accessible through HTTP. 
	"""
	
	def __init__(self, kernel):
		super(HTTPInterface, self).__init__()
		
		self.kernel = kernel
		self.id = 'httpinterface'
		self.app = app()
		post('/')(self.handle_request)
		t1 = Thread(target=self.run)
		t1.start()
		
	def run(self):
		""" Runs the Bottle server.
		
		"""
		#self.app.run()
		self.app.run(host='192.168.0.2', port=8080)
				
	def handle_request(self):
		""" Receives and processes the request received by the server.
		"""
		
		response.content_type = 'application/json'
		my_request = request.json				
		command = my_request['command']
		
		if command == 'get_list_ids':
			
			kernel_lists = {'scenarios': self.kernel.scenarios,
							'informations': self.kernel.infos,
							'actions': self.kernel.actions,
							'block_models': self.kernel.block_models,
							'devices': self.kernel.devices,
							'protocols': self.kernel.protocols,
							'drivers': self.kernel.drivers,
							'settables': self.kernel.protocols + self.kernel.drivers}
			
			return dumps([el.id for el in kernel_lists[my_request['list']]])
		
		elif command == 'get_settings':
			
			result = []
			for i in my_request['ids']:
				print i
				formatted_settings_format = deepcopy(self.kernel.get(i).settings_format)
				for f in formatted_settings_format:
					f['section'] = i
				print formatted_settings_format
				result.append([i, formatted_settings_format, self.kernel.get(i).settings])
				print result
				
			print result
			return dumps(result)

# 		elif command == 'get_settings':
# 			
# 			result = []
# 			for s in self.kernel.protocols + self.kernel.drivers:
# 				formatted_settings_format = deepcopy(self.kernel.get(i).get_settings_format())
# 				for f in formatted_settings_format:
# 					f['section'] = s.id
# 				result.append({'id': s.id,
# 							   'settings_format': formatted_settings_format,
# 							   'settings': s.settings})
# 			
# 			return dumps(result)
		
		elif command == 'set':
			
			self.kernel.get(my_request['id']).set(my_request['settings'])
			
		elif command == 'get_infos':
			
			return dumps([{'id': i.id,
						  'name': i.settings['name']}
						 for i in self.kernel.infos])			

		elif command == 'get_actions':
			
			return dumps([{'id': a.id,
						  'name': a.settings['name']}
						 for a in self.kernel.actions])
			
# 			result = []
# 			for i in my_request['ids']:
# 				action = self.kernel.get(i)
# 				result.append({ 'id': action.id,
# 								'name': action.settings['name'],
# 								'description': action.settings['description'],
# 								'args': action.callback_args_format})	
			
			

		elif command == 'get_block_models':
			
			print self.kernel.block_models
			return dumps([{'id': m.id,
						   'name': m.name,
						   'description': m.description}
					      for m in self.kernel.block_models])

		elif command == 'add_scenario':
			
			new_scenario = self.kernel.add_new_scenario(my_request['settings'])
			return new_scenario.id
			
		elif command == 'get_device_models':
			
# 			result = []
# 			for m in self.kernel.device_models:
# 				if m.instantiable:
# 					result.append([m.id, m.description, m.instantiable, m.settings_format])
# 				else:
# 					result.append([m.id, m.description, m.instantiable])
# 
# 			return dumps(result)
			
			print dumps([{'id': dm.id,
					   	   'name': dm.name}
						 for dm in self.kernel.device_models])
			
			return dumps([{'id': dm.id,
					   	   'name': dm.name}
						 for dm in self.kernel.device_models])

		elif command == 'start_adding_process':
			print my_request['device_model_id']
			device_model = self.kernel.get_device_model(my_request['device_model_id'])
			print device_model.adding_type
			if device_model.adding_type == 'sync':
				new_device = device_model.add_instance()
				result = {'adding_type': 'sync',
						  'device_id': new_device.id} 
			elif device_model.adding_type == 'auto':
				device_model.start_auto_detect()
				result = {'adding_type': 'auto',
						  'instructions': device_model.instructions}
			print dumps(result)
			return dumps(result)
		
		elif command == 'get_device_settings':
			device = self.kernel.get_device(my_request['device_id'])
			return dumps({'id': device.id,
					   	  'name': device.settings['name'],
					      'settings': device.settings,
					      'settings_format': [dict(s_f.items() + [('section', device.id)]) for s_f in device.settings_format]})
		
		elif command == 'get_auto_add_instructions':
			device_model = self.kernel.get_device_model(my_request['device_model_id'])
			return dumps({'instructions': device_model.instructions})
		
		elif command == 'set_device':
			self.kernel.get_device(my_request['device_id']).set(my_request['settings'])
		
		elif command == 'get_sync_instructions':
			device_model = self.kernel.get_device_model(my_request['device_model_id'])
			return dumps({'instructions': device_model.sync_instructions})
		
		elif command == 'send_sync_signal':
			self.kernel.get_device(my_request['device_id']).sync({})
		
		elif command == 'check_if_device_detected':
			device_model = self.kernel.get_device_model(my_request['device_model_id'])
			new_device = device_model.is_detected()
			if new_device and new_device != None:
				device_model.stop_auto_detect()
				result = {'detected': True,
						  'device_id': new_device.id}
			else:
				result = {'detected': False}
			
			print dumps(result)
			return dumps(result)
		
		elif command == 'get_devices':
			
			nexa_controllers = ['Nexa3ButtonRemote',
								'Nexa2ButtonSwitch']
			
			nexa_sensors = ['NexaOpeningSensor',
							'NexaMovementSensor']
	
			nexa_devices = ['NexaDevice']
			
			result = []
			for device in self.kernel.devices:
				json_device = {}
				json_device['id'] = device.id
				json_device['device_key'] = device.device_key
				json_device['name'] = device.settings['name']
				if device.device_key in nexa_controllers:
					json_device['switches'] = []
					for switch in device.base_switches:
						json_device['switches'].append({'id': switch.id,
													    'state': switch.state.get_value()})
				elif device.device_key in nexa_sensors:
					if device.state.get_values() != None:
						timestamp = device.state.get_values()[-1]['date']
						last_activated = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
						json_device['last_activated'] = 'last activated ' + last_activated
					else:
						json_device['last_activated'] = 'never activated'
				elif device.device_key in nexa_devices:
					json_device['id'] = device.id
				result.append(deepcopy(json_device))
			
			return dumps(result)
		
		elif command == 'update_devices':
			
			nexa_controllers = ['Nexa3ButtonRemote',
								'Nexa2ButtonSwitch']
			
			nexa_sensors = ['NexaOpeningSensor',
							'NexaMovementSensor']
	
			nexa_devices = ['NexaDevice']
			
			result = []
			for device in self.kernel.devices:
				json_device = {}
				json_device['id'] = device.id
				json_device['device_key'] = device.device_key
				json_device['name'] = device.settings['name']
				if device.device_key in nexa_controllers:
					json_device['switches'] = []
					for switch in device.base_switches:
						json_device['switches'].append({'id': switch.id,
													    'state': switch.state.get_value()})
				elif device.device_key in nexa_sensors:
					if device.state.get_values() != None:
						timestamp = device.state.get_values()[-1]['date']
						last_activated = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
						json_device['last_activated'] = 'last activated ' + last_activated
					else:
						json_device['last_activated'] = 'never activated'
				elif device.device_key in nexa_devices:
					json_device = {'id': device.id,
								   'state': device.state.get_value()}
				result.append(deepcopy(json_device))
			
			print result
			
			return dumps(result)
		
		elif command == 'device_action':
			
			print 'device_action'	
			print my_request	
			if my_request['model'] == 'NexaDevice':
				for device in self.kernel.devices:
					if device.id == my_request['id']:
						if device.state.get_value():
							device.switch_off({})
						else:
							device.switch_on({})
		
		elif command == 'add_device':
			
			self.kernel.get(my_request['id']).add_instance(my_request['settings'])
			
		elif command == 'get_scenario':
			
			s = self.kernel.get(my_request['id'])
						
			blocks = [{'id': b.id,
					   'name': b.settings['name'],
					   'settings': b.settings,
					   'settings_format': [dict(s_f.items() + [('section', b.id)]) for s_f in b.settings_format],
					   'input_nodes': [{'id': n.id,
									   	'type': n.type,
									   	'multiplicity': n.multiplicity,
									   	'name': n.name}
									   for n in b.nodes if InputNode in n.__class__.__mro__],
					   'output_nodes': [{'id': n.id,
										 'type': n.type,
									   	 'multiplicity': n.multiplicity,
									   	 'name': n.name}
									    for n in b.nodes if OutputNode in n.__class__.__mro__],
					   'position': s.positions[b.id]}
					   for b in s.blocks + s.actions + s.infos]
			
			links = [{'id': l.id,
					  'src_node': l.src_node.id,
					  'dst_node': l.dst_node.id}
					 for l in s.links]
			
			return dumps({'id': s.id,
						  'settings': s.settings,
						  'active': s.active,
						  'blocks': blocks,
						  'links': links})
		
		elif command == 'add_block':
			
			scenario = self.kernel.get_scenario(my_request['scenario_id'])
			block_model = my_request['id']
			settings = my_request['settings']
			new_block = scenario.add_block(block_model, settings)
			return dumps({'id': new_block.id,
						  'name': new_block.settings['name'],
						  'settings': new_block.settings,
						  'settings_format': [dict(s_f.items() + [('section', new_block.id)]) for s_f in new_block.settings_format],
						  'input_nodes': [{'id': n.id,
										   'type': n.type,
										   'multiplicity': n.multiplicity,
										   'name': n.name}
									     for n in new_block.nodes if InputNode in n.__class__.__mro__],
						  'output_nodes': [{'id': n.id,
										    'type': n.type,
									   	    'name': n.name}
									      for n in new_block.nodes if OutputNode in n.__class__.__mro__],
					      'position': scenario.positions[new_block.id]})
		
		elif command == 'add_info':
			
			scenario = self.kernel.get_scenario(my_request['scenario_id'])
			info = scenario.add_info(my_request['id'])
			return dumps({'id': info.id,
						  'name': info.settings['name'],
						  'settings': {},
						  'settings_format': [],
						  'input_nodes': [],
						  'output_nodes': [{'id': n.id,
										    'type': n.type,
									   	    'name': n.name}
									      for n in info.nodes if OutputNode in n.__class__.__mro__],
					      'position': scenario.positions[info.id]})
		
		elif command == 'add_action':
			
			scenario = self.kernel.get_scenario(my_request['scenario_id'])
			action = scenario.add_action(my_request['id'])
			return dumps({'id': action.id,
						  'name': action.settings['name'],
						  'settings': {},
						  'settings_format': [],
						  'input_nodes': [{'id': n.id,
										   'type': n.type,
										   'multiplicity': n.multiplicity,
										   'name': n.name}
									     for n in action.nodes if InputNode in n.__class__.__mro__],
						  'output_nodes': [],
					      'position': scenario.positions[action.id]})
			
		elif command == 'add_link':
		
			scenario = self.kernel.get(my_request['scenario_id'])
			new_link = scenario.add_link(my_request['src_id'], my_request['dst_id'])
			print new_link
			return dumps({'id': new_link.id,
						  'src_node': new_link.src_node.id,
						  'dst_node': new_link.dst_node.id})

# 		elif command == 'set_block_position':
# 			
# 			scenario = self.kernel.get(my_request['scenario_id'])
# 			scenario.positions[my_request['block_id']] = my_request['position']
		
		elif command == 'update_block_positions':
			
			scenario = self.kernel.get(my_request['scenario_id'])
			for block_position in my_request['block_positions']:
				scenario.positions[block_position['block_id']] = block_position['position']
		
		elif command == 'set_block':
			
			scenario = self.kernel.get_scenario(my_request['scenario_id'])
			block = scenario.get_block(my_request['block_id'])
			block.set(my_request['settings'])
		
		elif command == 'remove_block':
			
			self.kernel.get(my_request['scenario_id']).remove_block(my_request['block_id'])
		
		elif command == 'remove_link':
			
			self.kernel.get(my_request['scenario_id']).remove_link(my_request['link_id'])
		
		elif command == 'toggle_scenario':
			
			scenario = self.kernel.get(my_request['id'])
			if my_request['active']: scenario.activate()
			else: scenario.deactivate()
			return dumps({'active': scenario.active})	
					

""" Set of attributes which describe the plugin, in order 
to add it to the kernel and then be able to describe it
to the user.  

"""
plugin_type = "interface"
name = "HTTP Interface"
description = "A basic HTTP interface to control Yeah!"
interface_class = HTTPInterface   