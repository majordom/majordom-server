# -*- coding: utf-8 -*-

from scenario import Block, SimpleInputNode, MultiInputNode, OutputNode
from models import BlockModel
from models import Information

class Multiply(Block):
		
	def __init__(self, *args, **kwargs):
		super(Multiply, self).__init__(*args, **kwargs)
		self.set({ 'name' : 'Multiply' })
		
		self.operands = MultiInputNode(self, 'operands', 'in', 'numeric')
		self.result = OutputNode(self, 'result', 'out', 'numeric')
		
		self.add_nodes(self.operands,
					   self.result)
		
	def process(self, changed_input):
		result = 1
		for value in self.operands.get_value():
			result *= value
		self.result.add_value(result)
					
class Not(Block):
	
	def __init__(self, *args, **kwargs):
		super(Not, self).__init__(*args, **kwargs)
		self.set({ 'name' : 'Not' })
		
		self.input = SimpleInputNode(self, 'input', 'in', 'bool')
		self.output = OutputNode(self, 'output', 'out', 'bool')
		
		self.add_nodes(self.input,
					   self.output)
		
	def process(self, changed_input):
		self.output.add_value(not self.input.get_value())

class BooleanConstant(Block):
	
	settings_format = Block.settings_format + [{'type': 'bool',
												'title': 'Constant',
												'desc': 'The constant value',
												'key': 'value'},
											   {'type': 'num',
												'title': 'Test',
												'desc': 'Just to test the settings',
												'key': 'test_value'}]
	
	def __init__(self, *args, **kwargs):
		super(BooleanConstant, self).__init__(*args, **kwargs)
		
		self.set({'name': 'Boolean Constant'})
		
		self.output = OutputNode(self, 'output', 'out', 'bool')
		if not self.settings.has_key('value'):
			self.set({'value': False,
					  'test_value': 36})
		
		self.output.add_value(self.settings['value'])
		self.add_nodes(self.output)
	
	def set(self, settings):
		super(BooleanConstant, self).set(settings)
		
		print settings
				
		if self.settings.has_key('value'):
			self.output.add_value(self.settings['value'])
	
class Or(Block):
	
	def __init__(self, *args, **kwargs):
		super(Or, self).__init__(*args, **kwargs)
		self.set({ 'name' : 'Or' })
		
		self.input1 = SimpleInputNode(self, 'input1', 'in1', 'bool')
		self.input2 = SimpleInputNode(self, 'input2', 'in2', 'bool')
		self.output = OutputNode(self, 'output', 'out', 'bool')
		
		self.add_nodes(self.input1,
					   self.input2,
					   self.output)
		
	def process(self, changed_input):
		self.output.add_value(self.input1.get_value() or self.input2.get_value())
	
class And(Block):
	
	def __init__(self, *args, **kwargs):
		super(And, self).__init__(*args, **kwargs)
		self.set({ 'name' : 'And' })
		
		self.input1 = SimpleInputNode(self, 'input1', 'in1', 'bool')
		self.input2 = SimpleInputNode(self, 'input2', 'in2', 'bool')
		self.output = OutputNode(self, 'output', 'out', 'bool')
		
		self.add_nodes(self.input1,
					   self.input2,
					   self.output)
		
	def process(self, changed_input):
		self.output.add_value(self.input1.get_value() and self.input2.get_value())

class TriggerOnAlarm(Block):
	
	def __init__(self, *args, **kwargs):
		super(TriggerOnAlarm, self).__init__(*args, **kwargs)
		self.set({ 'name' : 'Trigger on alarm' })
		
		self.alarm = SimpleInputNode(self, 'alarm', 'alarm', 'bool')
		self.trigger = SimpleInputNode(self, 'trigger', 'trigger', 'bool')
		self.output = OutputNode(self, 'output', 'out', 'bool')
		
		self.add_nodes(self.alarm,
					   self.trigger,
					   self.output)
		
	def process(self, changed_input):
		if changed_input == self.alarm:
			if not self.alarm.get_value():
				self.output.add_value(False)
		elif changed_input == self.trigger:
			if self.trigger.get_value() and self.alarm.get_value():
				self.output.add_value(True)
				
class InfoBlock(Block):
	
	settings_format = Block.settings_format + [{'type': 'string',
												'title': 'Info name',
												'desc': 'Name of the new info',
												'key': 'info_name'}]
	
	def __init__(self, kernel, *args, **kwargs):
		super(InfoBlock, self).__init__(*args, **kwargs)
			
		self.kernel = kernel
		
		self.input = SimpleInputNode(self, 'input', 'in', 'bool')
		
		self.state = Information('state',
								 False,
								 'bool',
								 {'name': '',
								  'description' : ''},
								 block = self)
		
		self.kernel.infos.append(self.state)
		
		self.nodes = [self.input]
		
		self.set({'name': 'Info block', 
				  'info_name': 'new virtual info'})
		
	def process(self, changed_input):
		self.state.update(self.input.get_value())

	def set(self, settings):
		super(InfoBlock, self).set(settings)
		
		if settings.has_key('info_name'):
			self.state.set({'name': settings['info_name']})

	def before_remove(self):
		self.kernel.remove(self.state)
		# TODO: il faut aussi enlever tous les liens qui vont vers un de ses noeuds

class InfoBlockModel(BlockModel):
	
	kernel_needed = True
	
	def __init__(self, *args, **kwargs):
		super(InfoBlockModel, self).__init__(*args, **kwargs)
		
		self.block_class = InfoBlock
		self.kernel = None
		
	def get_instance(self, settings, block_id):
		
		return self.block_class(self.kernel, block_id, settings = settings)

	def set_kernel(self, kernel):
		self.kernel = kernel

""" Set of attributes which describe the plugin, in order 
to add it to the kernel and then be able to describe it
to the user.  

"""
plugin_type = "automation"
name = "Base blocks"
description = "A couple of base blocks useful for the creation of simple scenarios."
block_models_classes = [BlockModel('multiply', "Multiply", "Multiplies its inputs", Multiply),
						BlockModel('not', "Not", "Inverts its boolean input", Not),
						BlockModel('boolean_constant', "Boolean Constant", "A simple Boolean constant", BooleanConstant),
						BlockModel('or', "Or", "A simple logical or", Or),
						BlockModel('and', "And", "A simple logical and", And),
						BlockModel('triggeronalarm', "Trigger on alarm", "Use a specific trigger when your alarm is on.", TriggerOnAlarm),
						InfoBlockModel('info_block', "Info block", "A block simulating a new info", InfoBlock)]    