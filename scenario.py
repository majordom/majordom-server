# -*- coding: utf-8 -*-

from generic_models import IDableObject, SettableObject
from time import time

class Scenario(SettableObject):
	""" Within Majordom, Scenarios are used to implement the automatic behaviors of Majordom.
	
	A scenario is a model of automatic behavior: we chose to represent automatic behaviors with blocks which hace specific input and output nodes. Links can be drawn between these nodes. Once the scenario edition has been completed, the scenario can be activated and the system will behave accordingly to the way it was programmed.
	
	There are three main kinds of blocks: the actions, the infos and the (processing) blocks.
	
	* **Actions** only have inputs: one trigger and all the inputs corresponding to their execution arguments.
	* **Informations** only have a single output: it is the value of the information. The output node of an information if refreshed every time the information node is refreshed.
	* **Blocks** may have inputs and outputs. The value of their outputs are evaluated depending on the value of their inputs and the processing method implemented within the block. Blocks are written in Python, following a very simple programmation interface described below. 
	
	You can add as many blocks as you want in a scenario. Then, link their nodes with Links. When the scenario is activated, every Link of the scenario is consequently activated. When a Link is activated, it creates an observer-pattern relationship between the two linked nodes. This way, when the value of the source node of the link changes, the destination link knows about it and subsequently updates its own value. This mecanism ensures the propagation of the change of any of the system's inputs.
	
	"""
	
	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the scenario',
					'key': 'name' },
					{ 'type': 'string_long',
					'title': 'Description',
					'desc': 'Description of the scenario',
					'key': 'description' }
					]
	
	def __init__(self, kernel, next_block_id = 0, next_link_id = 0, *args, **kwargs):
		super(Scenario, self).__init__(*args, **kwargs)
		
		self.kernel = kernel
		self.actions = []
		self.infos = []
		self.blocks = []
		self.links = []
		self.positions = {}
		self.active = False
		
		self.next_block_id = next_block_id
		self.next_link_id = next_link_id
				
# 	def get_new_id(self):
# 		""" *(Internal)* Returns an unique identifier in order to reference
# 		blocks and links. It gets the unique identifier from the kernel.
# 		
# 		"""
# 		
# 		return self.kernel.get_new_id()
	
	def get_block(self, searched_id):
		""" Returns the block whose id is the searched_id. 
		If this id is not found, it returns False.
		
		"""
		
		result = False
		for el in self.blocks + self.actions + self.infos:
			if el.id == searched_id:
				result = el
		return result
	
	def get_link(self, searched_id):
		""" Returns the link whose id is the searched_id. 
		If this id is not found, it returns False.
		
		"""
		
		result = False
		for el in self.links:
			if el.id == searched_id:
				result = el
		return result
	
	def get_node(self, searched_id):
		""" *(Internal)* Returns the node whose id is 
		the searched_id. If this id is not found, it 
		returns False.
		
		"""
		
		result = False
		for block in self.blocks + self.actions + self.infos:
			for node in block.nodes:
				if node.id == searched_id:
					result = node
		return result
	
	# In the case of an action or an information, the block and its nodes
	# have already obtained a unique identifier when they were added
	# to the kernel of the box itself 
	# There is therefore no need to give them an ID.
	
	def add_action(self, action_id):
		action = self.kernel.get_action(action_id)
		self.positions[action.id] = [0,0]
		self.actions.append(action)
		return action
		
	def add_info(self, info_id):
		info = self.kernel.get_info(info_id)
		self.positions[info.id] = [0,0]
		self.infos.append(info)
		return info 
	
	def add_block(self, block_model_id, settings, block_id = None):
		""" Adds the block given as argument to the scenario 
		and returns its ID within the scenario.
		
		"""
		block_model = self.kernel.get_block_model(block_model_id)
		
		if block_id == None:
			new_block_id = self.id + '_block' + str(self.next_block_id)
			self.next_block_id += 1
		else:
			new_block_id = block_id
		
		new_block = block_model.get_instance(settings, new_block_id)
		
		self.positions[new_block.id] = [0,0]
		
		self.blocks.append(new_block)
		
		return new_block
	
	def add_link(self, src_node_id, dst_node_id, link_id = None):
		""" Adds a link from the source port whose id has been given as first argumment to the destination port whose id has been given as second argument.
		
		"""
		
		result = False
		
		src_node = self.get_node(src_node_id)
		dst_node = self.get_node(dst_node_id)
		
		print src_node, dst_node
		# On verifie que:
		# * src_node est un node de sortie
		# * dst_node est un node d'entree
		# * si dst_node est un SimpleInputNode --> pas dejà d'autres liens dont il est la dst
		# * src_node et dst_node sont du même type
		check = [
				OutputNode in src_node.__class__.__mro__,
				InputNode in dst_node.__class__.__mro__,
				MultiInputNode in dst_node.__class__.__mro__ or dst_node.previous == None,
				src_node.type == dst_node.type
				]
		
		if False not in check:
			if link_id == None:
				new_link_id = self.id + '_link' + str(self.next_link_id)
				self.next_link_id += 1
			else:
				new_link_id = link_id
			
			new_link = Link(self, src_node, dst_node, new_link_id)
			self.links.append(new_link)
			result = new_link
		
		return result
	
	def remove_block(self, block_id):
		""" Removes the element (block or link) whose ID has been specified from
		the relevant list of this Scenario and returns the removed element.
		If the ID is not found, the method returns False.
		
		"""
		print 'removing block ' + block_id
		result = self.get_block(block_id)
		if result:
			# On retire le block
			if result in self.blocks:
				result.before_remove() 
				self.blocks.remove(result)
			elif result in self.actions: self.actions.remove(result)
			elif result in self.infos: self.infos.remove(result)
			
			# On retire aussi tous les liens qui vont ou
			# partent de l'un de ses nodes
			print [l.id for l in self.links]
			
			for l1 in list(self.links):
				print self.links
				print l1.id
				#if (l.src_node in result.nodes) or (l.dst_node in result.nodes):
				self.remove_link(l1.id) 
				print 'boucle'
				print self.links
			print [l.id for l in self.links]

		return result
	
	def remove_link(self, link_id):
		""" Removes the link whose ID has been specified from
		the list of links of this Scenario and returns the Link.
		If the ID is not found, the method returns False.
		
		"""
		
		print 'removing link ' + link_id
		result = self.get_link(link_id)
		print result
		if result:
			print "Je suis là"
			result.deactivate()
			print "Je suis arrivé ici"
			self.links.remove(result)
			print "presque"
		print "enfin"
		return result
	
	def activate(self):
		""" Activates this scenario, i.e. the links between ports
		of blocks become active: they are translated into 
		observer-observed relationships.
		
		"""
		
		print 'activating scenario ' + self.id
		for link in self.links:
			link.activate()
		self.active = True
		
	def deactivate(self):
		""" Deactivates this scenario, i. e. deletes all the 
		observer-observed relationships previously set.
		
		"""
		
		print 'deactivating scenario ' + self.id
		for link in self.links:
			link.deactivate()
		self.active = False
			
class Block(SettableObject):
	""" The Block class defines the minimum interface that any Block should implement.
	
	The purpose of the blocks are highlighted in the :class:`scenario.Scenario` class documentation.
	"""
	
	settings_format = [
					{ 'type': 'string',
					'title': 'Name',
					'desc': 'Name of the block',
					'key': 'name',
					'disabled': True }
					]
	
	def __init__(self, block_id, *args, **kwargs):
		super(Block, self).__init__(*args, **kwargs)
		
		self.id = block_id
		self.nodes = []
		
	def add_nodes(self, *args):
		""" Adds the nodes given as argument to the Block. Note that this function accepts as many arguments as you want, as long as they are all Nodes. 
		"""
		
		for arg in args:
			if Node in arg.__class__.__mro__:
				self.nodes.append(arg)
		
	def process(self, changed_input):
		""" *(abstract method)* This is the method that implements the logic of a block, i.e. that computes the output values of the node according to its inputs. It is triggered every time any of the block's inputs changes: the input which triggered the change is given as argument.
		
		"""
		pass
	
	def before_remove(self):
		""" *(abstract method)* Method used before a block is removed from the Scenario. Most of the time, this method will be empty. Sometimes, the block may need to delete other objects from Majordom before being removed. For instance, the :class:`base_blocks.InfoBlock` has to delete its corresponding information before being removed from its scenario.
		
		"""
		pass
	
class Link(IDableObject):
	""" The Links are used to connect nodes within a scenario. Their exact purpose are highlighted in the :class:`scenario.Scenario` class documentation.
	
	"""
	
	def __init__(self, scenario, src_node, dst_node, link_id):
		self.scenario = scenario
		self.src_node = src_node
		self.dst_node = dst_node
		self.id = link_id

	def activate(self):
		""" Activates the link, i.e. initializes the observer-pattern relationship between the source and the destination nodes.
		
		"""
		self.src_node.add_next(self.dst_node)
		self.dst_node.add_previous(self.src_node)
			
	def deactivate(self):
		""" Deactivates the link, i.e. removes the observer-pattern relationship between the source and the destination nodes.
		
		"""
		self.src_node.remove_next(self.dst_node)
		self.dst_node.remove_previous(self.src_node)

class Node(IDableObject):
	""" *(abstract class)* This is the base class for any Node subclass. It implements the minimum interface that any Node subclass should implement.
	
	"""
	
	multiplicity = 'simple'
	
	def __init__(self, block, node_id, name, value_type):
		
		self.id = block.id + '_' + node_id 
		self.type = value_type
		self.name = name
		self.block = block
		
	def get_value(self):
		""" Returns the last value of the node.
		
		"""
		pass
	
	def get_values(self, from_time = 0, to_time=None):
		""" Returns the values of the node whose timestamps are located between the given arguments :attr:`from_time` and :attr:`to_time`.
		
		"""
		pass
	
class OutputNode(Node):
	""" Implementation of the Node interface for an output node.
	"""
	
	def __init__(self, *args, **kwargs):
		super(OutputNode, self).__init__(*args, **kwargs)
		self.observers = []
		self.values = []
		
	def add_next(self, node):
		""" Adds an observer to this node. That is the function called when the scenario is activated.
		"""
		if node not in self.observers:
			self.observers.append(node)
		
	def remove_next(self, node):
		""" Removes an observer of this node. That is the function called when the scenario is deactivated.
		"""
		if node in self.observers:
			self.observers.remove(node)
	
	def add_value(self, new_value):
		""" Adds a value to the node and subsequently updates all the observers of the node.
		"""
		self.values.append({'value': new_value,
							'date': time()})
		for obs in self.observers:
			obs.update()
	
	def get_value(self):
		""" Returns the last value of the node.
		
		"""
		result = None
		if len(self.values) > 0:
			result = self.values[-1]['value'] 
		return result
	
	def get_values(self, from_time = 0, to_time=None):
		""" Returns the values of the node whose timestamps are located between the given arguments :attr:`from_time` and :attr:`to_time`.
		
		"""
		
		# We cannot put time() as the default value of the
		# to_time argument since it would *not* be reevaluated
		# at each function call
		if to_time == None: to_time = time()
		
		result = None
		if len(self.values) > 0:
			result = []
			for val in self.values:
				if from_time < val['date'] and val['date'] < to_time:
					result.append(val)
		return result

class InputNode(Node):
	""" *(abstract class)* Base class for any input node.
	
	"""
	
	def __init__(self, *args, **kwargs):
		super(InputNode, self).__init__(*args, **kwargs)
		self.previous = None
		
	def update(self):
		"""
		"""
		self.block.process(self)

class SimpleInputNode(InputNode):
	""" Implementation of the InputNode interface in the case of an input node which only accepts a single link. A single link has this kind of node as destination.
	
	"""	
	
	def __init__(self, *args, **kwargs):
		super(SimpleInputNode, self).__init__(*args, **kwargs)
		self.previous = None
	
	def add_previous(self, node):
		""" Adds an observed node to this node. SingleInputNodes can only have a single observed node.
		"""
		self.previous = node
		
	def remove_previous(self, node):
		""" Removes an observed node from this node.
		"""
		self.previous = None
		
	def get_value(self):
		""" Returns the last value of the node.
		
		"""
		result = None
		if self.previous != None:
			result = self.previous.get_value()
		return result
		
	def get_values(self, from_time, to_time):
		""" Returns the values of the node whose timestamps are located between the given arguments :attr:`from_time` and :attr:`to_time`.
		
		"""
		result = None
		if self.previous != None:
			result = self.previous.get_values(from_time, to_time)
		return result
		
class MultiInputNode(InputNode):
	""" Implementation of the InputNode interface in the case of an input node which accepts several links. Several links may have this node as destination node. It may be used for blocks such as 'Logical And': you have no reason to limit the number of values of which you compute the logical and.
	
	"""
	
	multiplicity = 'multiple'
	
	def __init__(self, *args, **kwargs):
		super(MultiInputNode, self).__init__(*args, **kwargs)
		self.previous = []
	
	def add_previous(self, node):
		""" Adds an observed node to this node. MultiInputNodes can have several observed nodes.
		"""
		if node not in self.previous:
			self.previous.append(node)
	
	def remove_previous(self, node):
		""" Removes an observed node from this node. 
		"""
		if node in self.previous:
			self.previous.remove(node)
		
	def get_value(self):
		""" Returns the last value of the node.
		
		"""
		result = None
		if len(self.previous) > 0:
			result = []
			for node in self.previous:
				result.append(node.get_value())
		return result
		
	def get_values(self, from_time, to_time):
		""" Returns the values of the node whose timestamps are located between the given arguments :attr:`from_time` and :attr:`to_time`.
		
		"""
		result = None
		if len(self.previous) > 0:
			result = []
			for node in self.previous:
				result.append(node.get_values(from_time, to_time))
		return result

# class Observer(object):
# 	
# 	def notify(self, observable):
# 		# the content of the method is very specific 
# 		# to a given Observer
# 		pass
# 	
# class Observable(object):
# 
# 	def attach(self, observer):
# 		if not observer in self._observers:
# 			self._observers.append(observer)
# 
# 	def detach(self, observer):
# 		try:
# 			self._observers.remove(observer)
# 		except ValueError:
# 			pass
# 
# 	def notify_observers(self, modifier=None):
# 		for observer in self._observers:
# 			if modifier != observer:
# 				observer.notify(self)
# 
# class SimpleNode(Node, Observer, Observable):
# 	
# 	def __init__(self, name, value_type):
# 		super(SimpleNode, self).__init__(name, value_type)
# 		self.value = None
# 		
# 	def notify(self, observable):
# 		self.value = observable.value
# 
# class CompositeNode(Node):
# 
# 	def __init__(self, name, value_type):
# 		super(CompositeNode, self).__init__(name, value_type)
# 		self.nodes = []
# 	
# 	def add_node(self):
# 		new_node = SimpleNode(self.name, self.value_type)
# 		self.nodes.append(new_node)
# 		return new_node
# 
# 
# 
# class SimpleBlock(Block, Observer):
# 	pass
# 
# class CompositeBlock(Block):
# 	
# 	def __init__(self):
# 		self.blocks = {}
# 		self.links = []
#
#	
# class Settable(object):
# 	
# 	properties_format = {
# 						'name': (True, types.StringType, None),
# 						'id': (False, types.IntType, None),
# 						'description': (True, types.StringType, None),
# 						'location': (True, types.StringType, None),
# 						'protocol': (False, types.StringType, None), 
# 						}
# 	
# 	@classmethod
# 	def get_properties_format(cls):
# 		return cls.properties_format
# 	
# 	def set_properties(self, properties):
# 		# On parcourt l'ensemble du dictionnaire fourni
# 		for key in properties.iter:
# 			# On v�rifie pour chaque cl� qu'elle correspond � une propri�t� existante
# 			if key in self.__class__.properties_format.iter:
# 				# On v�rifie que cette propri�t� est effectivement modifiable et que la nouvelle valeur est valide
# 				if self.check(properties[key], self.__class__.properties_format[key]): 
# 					# Si c'est le cas, on assigne la nouvelle valeur
# 					self.properties[key] = properties[key]
# 	
# 	def check_format(self, arg, arg_format):
# 		check = True
# 		(allow_user, arg_type, arg_range) = arg_format
# 		if allow_user:
# 			if type(arg) == arg_type:
# 				if arg_type == types.StringType:
# 					pass
# 				elif arg_type == types.IntType or arg_type == types.FloatType:
# 					if arg_range[0] <= arg <= arg_range[1]:
# 						pass
# 					else: # L'argument n'est pas dans les limites donn�es
# 						check = False
# 			else: # Le type de donn�e propos� n'est pas bon
# 				check = False
# 		else: # Cette propri�t� n'est pas modifiable par l'utilisateur
# 			check = False
# 		return check