# -*- coding: utf-8 -*-

from pickle import dump, load

from kernel import Kernel
from models import Action, Information
from scenario import Scenario, OutputNode, InputNode

main_screen_elements = []

def clear():
	print "\n"*10

def set_setting(settable, setting_key):
	
	setting_format = [f for f in settable.get_settings_format() if f['key'] == setting_key][0]
	
	clear()
	print "p) Previous menu"
	if setting_format.has_key('disabled') and setting_format['disabled'] == True:
		choice = raw_input("Sorry, this setting cannot be changed! Just press any key to go back.")
	else:
		if setting_format['type'] == 'bool':
			print "1) True"
			print "2) False"
			choice = raw_input("Your choice for " + setting_format['title'] + "? ")
		elif setting_format['type'] in ['string', 'string_long']:
			choice = raw_input("Enter a string for " + setting_format['title'] + ": ")
		elif setting_format['type'] == 'num':
			choice = raw_input("Enter a number (may be non-integer) for " + setting_format['title'] + ": ")
		elif setting_format['type'] == 'num_int':
			choice = raw_input("Enter a number (must be an integer) for " + setting_format['title'] + ": ")
		elif setting_format['type'] == 'options':
			for i, o in enumerate(setting_format['options']):
				print str(i+1) + ") " + o
			choice = raw_input("Your choice for " + setting_format['title'] + "? ")
			
		if choice == 'p':
				pass
		else:
			if setting_format['type'] == 'bool':
				if choice == '1':
					settable.set({ setting_key: True})
				elif choice == '2':
					settable.set({ setting_key: False})
				else: 
					set_setting(settable, setting_format)
			elif setting_format['type'] in ['string', 'string_long']:
				settable.set({ setting_key: choice})
			elif setting_format['type'] == 'num':
				try:
					float_choice = float(choice)
				except:
					set_setting(settable, setting_format)
				else:
					settable.set({ setting_key: float_choice})
			elif setting_format['type'] == 'num_int':
				try:
					int_choice = int(choice)
				except:
					set_setting(settable, setting_format)
				else:
					settable.set({ setting_key: int_choice})
			elif setting_format['type'] == 'options':
				try:
					int_choice = int(choice)
				except:
					set_setting(settable, setting_format)
				else:
					if (int_choice-1) < len(setting_format['options']):
						option = setting_format['options'][int_choice-1]
						settable.set({ setting_key: option})
			
def manage_settable(settable):
	
	settings_keys = [s['key'] for s in settable.get_settings_format()]
	
	clear()
	print "p) Previous menu"
	for s in settable.get_settings_format():
		display = s['key'] + ") "  
		if settable.get_settings().has_key(s['key']):
			display += str(settable.get_settings()[s['key']])
		print display
	choice = raw_input("Go to: ")
	
	if choice == 'p':
			pass
	else:
		print settings_keys
		if choice in settings_keys:
			set_setting(settable, choice)
		manage_settable(settable)

def manage_settables(settables):
	
	clear()
	print "p) Previous menu"
	for i, settable in enumerate(settables):
		print str(i+1) + ") " + settable.settings['name']
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			manage_settable(settables[int_choice-1])
		
		manage_settables(settables)

def add_info_block_to(scenario):
	
	clear()
	print "p) Previous menu"
	for info in kernel.infos:
		print str(info.id) + ") " + info.settings['name']
	choice = raw_input("Add: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			add_info_block_to(scenario)
		else:
			if int_choice in [info.id for info in kernel.infos]:
				scenario.add_info_action_block(kernel.get_by_id(int_choice))
			else:
				add_info_block_to(scenario)

def add_action_block_to(scenario):
	clear()
	print "p) Previous menu"
	for action in kernel.actions:
		print str(action.id) + ") " + action.settings['name']
	choice = raw_input("Add: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			add_action_block_to(scenario)
		else:
			if int_choice in [action.id for action in kernel.actions]:
				scenario.add_info_action_block(kernel.get_by_id(int_choice))
			else:
				add_action_block_to(scenario)

def add_processing_block_to(scenario):
	
	clear()
	print "p) Previous menu"
	for block_model in kernel.block_models:
		print str(block_model.id) + ") " + block_model.name
	choice = raw_input("Add: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			add_processing_block_to(scenario)
		else:
			if int_choice in [block_model.id for block_model in kernel.block_models]:
				scenario.add_block(kernel.get_by_id(int_choice))
			else:
				add_processing_block_to(scenario)

def add_block_to(scenario):
	clear()
	print "p) Previous menu"
	print "1) Add info block"
	print "2) Add action block"
	print "3) Add processing block"
	choice = raw_input("Choose: ")
	
	if choice == 'p':
		pass
	else:
		if choice == '1':
			add_info_block_to(scenario)
		elif choice == '2':
			add_action_block_to(scenario)
		elif choice == '3':
			add_processing_block_to(scenario)
		else:
			add_block_to(scenario)

def add_link_to_dst(scenario, src):
	
	clear()
	print "p) Previous menu"
	for block in scenario.blocks:
		for node in block.nodes:
			if InputNode in node.__class__.__mro__:
				print str(node.id) + ") " + node.name
	choice = raw_input("Choose: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			add_link_to_dst(scenario, src)
		else:
			scenario.add_link(src, int_choice)

def add_link_to(scenario):
	
	clear()
	print "p) Previous menu"
	for block in scenario.blocks:
		for node in block.nodes:
			if OutputNode in node.__class__.__mro__:
				print str(node.id) + ") " + node.name
	choice = raw_input("Choose: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			add_link_to(scenario)
		else:
			add_link_to_dst(scenario, int_choice)
			
def remove_block_from(scenario):
	
	clear()
	print "p) Previous menu"
	for i, block in enumerate(scenario.blocks):
		print str(i+1) + ") " + block.settings['name']
	choice = raw_input("Remove: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			scenario.remove_block(scenario.blocks[int_choice-1].id)
			
		remove_block_from(scenario)

def remove_link_from(scenario):
	
	clear()
	print "p) Previous menu"
	for i, link in enumerate(scenario.links):
		print str(i+1) + ") " + link.src_node.name + " --> " + link.dst_node.name
	choice = raw_input("Remove: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			scenario.remove_link(scenario.links[int_choice-1].id)
			
		remove_link_from(scenario)

def manage_scenario(scenario):
	
	clear()
	print "p) Previous menu"
	print "1) Change name/description"
	print "2) Add a block to the scenario"
	print "3) Add a link to the scenario"
	print "4) Remove a block from the scenario"
	print "5) Remove a link from the scenario"
	print "6) Activate the scenario"
	print "7) Deactivate the scenario"
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		if choice == '1':
			manage_settable(scenario)
		elif choice == '2':
			add_block_to(scenario)
		elif choice == '3':
			add_link_to(scenario)
		elif choice == '4':
			remove_block_from(scenario)
		elif choice == '5':
			remove_link_from(scenario)
		elif choice == '6':
			scenario.activate()
		elif choice == '7':
			scenario.deactivate()
			
		manage_scenario(scenario)


def manage_scenarios():
	
	clear()
	print "p) Previous menu"
	for i, scenario in enumerate(kernel.scenarios):
		print str(i+1) + ") " + scenario.settings['name']
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			manage_scenario(kernel.scenarios[int_choice-1])
			
		manage_scenarios()
	
def manage_menu():
	
	clear()
	print "p) Previous menu"
	print "1) ... protocols"
	print "2) ... drivers"
	print "3) ... devices"
	print "4) ... informations"
	print "5) ... actions"
	print "6) ... scenarios"
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		if choice == '1':
			manage_settables(kernel.protocols)
		elif choice == '2':
			manage_settables(kernel.drivers)
		elif choice == '3':
			manage_settables(kernel.devices)
		elif choice == '4':
			manage_settables(kernel.infos)
		elif choice == '5':
			manage_settables(kernel.actions)
		elif choice == '6':
			manage_scenarios()
		manage_menu()

def add_info_to_main_screen():
	
	clear()
	print "p) Previous menu"
	for i, info in enumerate(kernel.infos):
		display = str(i+1) + ") "
		display += info.settings['name']
		print display
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			main_screen_elements.append(kernel.infos[int_choice-1])		

def add_action_to_main_screen():
	
	clear()
	print "p) Previous menu"
	for i, act in enumerate(kernel.actions):
		display = str(i+1) + ") "
		display += act.settings['name']
		print display
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			main_screen_elements.append(kernel.actions[int_choice-1])

def add_to_main_screen():
	
	clear()
	print "p) Previous menu"
	print "1) Information"
	print "2) Action"
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		if choice == '1':
			add_info_to_main_screen()
		elif choice == '2':
			add_action_to_main_screen()
		main_screen()
		

def main_screen():
	
	clear()
	print "p) Previous menu"
	print "add) Add an element to the main screen"
	for i, el in enumerate(main_screen_elements):
		display = str(i+1) + ") "
		display += el.settings['name']
		if Information in el.__class__.__mro__:
			display += ": " + str(el.nodes[0].get_value())
		print display
	choice = raw_input("Choice: ")
	
	if choice == 'p':
		pass
	elif choice == 'add':
		add_to_main_screen()
	else:
		try:
			int_choice = int(choice)
		except:
			pass
		else:
			if Action in main_screen_elements[int_choice-1].__class__.__mro__:
				main_screen_elements[int_choice-1].execute({})
		
		main_screen()
		

def add_device():
	
	clear()
	print "p) Previous menu"
	for i, device_model in enumerate(kernel.device_models):
		display = str(i+1) + ") "
		display += str(device_model.name)
		print display 
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		try:
			int_choice = int(choice)
		except:
			add_device()
		else:
			if (int_choice-1) < len(kernel.device_models):
				if kernel.device_models[int_choice-1].instantiable:
					new_device_id = kernel.device_models[int_choice-1].add_instance({})
					manage_settable(kernel.get_by_id(new_device_id))
				else:
					print kernel.device_models[int_choice-1].description
					raw_input("Press any key to continue...")
			else:
				pass
		add_device()

def add_scenario():
	
	new_scenario = Scenario(kernel)
	kernel.add(new_scenario)
	manage_scenario(new_scenario)	

def add_menu():
	
	clear()
	print "p) Previous menu"
	print "1) ... a device"
	print "2) ... a scenario"
	choice = raw_input("Go to: ")
	
	if choice == 'p':
		pass
	else:
		if choice == '1':
			add_device()
		elif choice == '2':
			add_scenario()
		add_menu()
		
def main_menu():
	
	clear()
	print "q) Quit"
	print "s) Save"
	print "r) Restore"
	print "1) Main screen"
	print "2) Manage..."
	print "3) Add..."
	choice = raw_input("Go to: ")
	
	if choice == 'q':
		pass
	else:
		if choice == 's':
			kernel.save()
		if choice == 'r':
			kernel.restore()
		if choice == '1':
			main_screen()
		elif choice == '2':
			manage_menu()
		elif choice == '3':
			add_menu()
		
		main_menu()
	
def initialize_defaults():
	arduino = [d for d in kernel.drivers if d.settings['name'] == 'Arduino Radio'][0]
	arduino.set({ 'com_port': 'Arduino Uno (COM5)'})	

	nexa = [p for p in kernel.protocols if p.settings['name'] == 'Nexa'][0]
	nexa.set({ 'driver': 'Arduino Radio'})
	
	light_model = [m for m in kernel.device_models if m.name == 'Nexa Device'][0]
	light_model.add_instance({'name': 'Halog�ne', 'house_code': 11111, 'group_code': 0, 'unit_code': 0})

def save():
	f = open('persistence', 'w')
	dump(kernel, f)

def restore():
	f = open('persistence', 'r')
	global kernel
	kernel = load(f)

if __name__ == '__main__':
	
	def _pickle_method(method):
		func_name = method.im_func.__name__
		obj = method.im_self
		cls = method.im_class
		return _unpickle_method, (func_name, obj, cls)
	
	def _unpickle_method(func_name, obj, cls):
		for cls in cls.mro():
			try:
				func = cls.__dict__[func_name]
			except KeyError:
				pass
			else:
				break
		return func.__get__(obj, cls)
	
	import copy_reg
	import types
	copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
	
	kernel = Kernel()
	
	#f = open('persistence', 'r')
	#kernel = load(f)
	
	kernel.load_plugins()
	#initialize_defaults()
	main_menu()
	
# 	f = open('persistence', 'w')
# 	dump(kernel, f)
# 	
	
	

